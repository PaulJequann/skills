#!/usr/bin/env python3
"""Find the agent sessions that used a skill, and condense them for analysts.

  retro.py find <skill> [--repo DIR] [--home DIR] [--since YYYY-MM-DD] [--manifest FILE]
  retro.py extract <manifest> <outdir> [--kinds use,mention] [--batch-chars N]
  retro.py verify <manifest> <report>...
  retro.py table <manifest> <report>...
"""

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from collections import Counter, namedtuple
from datetime import datetime, timezone
from pathlib import Path

INJECTED = re.compile(r"\s*(<(?!command-)[\w-]+>|# AGENTS\.md)")
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
WRITE_TOOL = re.compile(r"edit|write|patch|str_replace", re.I)
LIMITS = {"user": 6000, "assistant": 12000, "meta": 1500, "call": 400, "result": 600, "before": 600}
DETAIL_AFTER = 150
QUOTE = re.compile(r"^QUOTE (\S+) \| (.+)$", re.M)
SESSION = re.compile(r"^SESSION (\S+) \| (.+)$", re.M)
SKILL_TOOLS = ("Skill", "skill_view", "skill")

Session = namedtuple("Session", "cwd origin events")


def squash(text):
    return " ".join(str(text).split())


def user_role(text):
    """Harness text arrives in the user role: skill bodies, context blocks, subagent reports."""
    return "meta" if INJECTED.match(text) or "<INSTRUCTIONS>" in text[:300] else "user"


def jsonl(path):
    with open(path, errors="ignore") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def iso(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat() if isinstance(ts, (int, float)) else ts


def parse_time(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def git(repo, *args):
    run = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return run.stdout if run.returncode == 0 else ""


def lead(text):
    body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
    para = []
    for line in body.splitlines():
        if line.startswith("#") or not line.strip():
            if para:
                break
            continue
        para.append(line)
    return squash(" ".join(para))[:60] or None


def fingerprints(skill, repo, home):
    """Lead sentences of every known version of the skill body, and the last commit date."""
    texts, last_edit = [], None
    for f in (repo / "skills" / skill / "SKILL.md", repo / skill / "SKILL.md", home / ".agents/skills" / skill / "SKILL.md"):
        if f.is_file():
            texts.append(f.read_text())
    rel = next((p for p in (f"skills/{skill}/SKILL.md", f"{skill}/SKILL.md") if (repo / p).is_file()), None)
    if rel:
        for entry in git(repo, "log", "--follow", "--name-only", "--format=%x00%H %cI", "--", rel).split("\0"):
            lines = entry.strip().splitlines()
            if not lines:
                continue
            sha, date = lines[0].split()
            last_edit = last_edit or date
            texts.append(git(repo, "show", f"{sha}:{lines[-1]}"))
    return sorted({lead(t) for t in texts} - {None}), last_edit


def claude_session(paths):
    cwd, origin, events = None, None, []
    for path in paths:
        sidechain = "/subagents/" in str(path)
        for rec in jsonl(path):
            role = rec.get("type")
            if role not in ("user", "assistant"):
                continue
            cwd = cwd or rec.get("cwd")
            origin = origin or rec.get("entrypoint")
            ts = rec.get("timestamp")
            content = (rec.get("message") or {}).get("content")
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            meta = role == "user" and (sidechain or rec.get("isMeta") or rec.get("isCompactSummary"))
            for block in content or []:
                kind = block.get("type")
                if kind == "text":
                    text = block.get("text", "")
                    events.append(("meta" if meta else user_role(text) if role == "user" else role, text, None, ts))
                elif kind == "tool_use":
                    events.append(("call", json.dumps(block.get("input")), block.get("name"), ts))
                elif kind == "tool_result":
                    out = block.get("content")
                    if isinstance(out, list):
                        out = "\n".join(x.get("text", "") for x in out if isinstance(x, dict))
                    events.append(("result", str(out or ""), None, ts))
    events.sort(key=lambda e: e[3] or "")
    return Session(cwd, origin, events)


def codex_session(path):
    cwd, origin, events = None, None, []
    for rec in jsonl(path):
        payload, ts = rec.get("payload") or {}, rec.get("timestamp")
        if rec.get("type") == "session_meta":
            cwd, origin = payload.get("cwd"), payload.get("originator")
        if rec.get("type") != "response_item":
            continue
        kind = payload.get("type")
        if kind == "message":
            role = payload.get("role")
            if role not in ("user", "assistant"):
                continue
            text = "\n".join(c.get("text", "") for c in payload.get("content") or [] if isinstance(c, dict))
            events.append((user_role(text) if role == "user" else role, text, None, ts))
        elif kind in ("function_call", "custom_tool_call"):
            events.append(("call", str(payload.get("arguments") or payload.get("input") or ""), payload.get("name"), ts))
        elif kind in ("function_call_output", "custom_tool_call_output"):
            out = payload.get("output")
            events.append(("result", out if isinstance(out, str) else json.dumps(out), None, ts))
    return Session(cwd, origin, events)


def hermes_session(db, sid):
    """A root session with its subagent sessions folded in."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    row = con.execute("select cwd, source from sessions where id = ?", (sid,)).fetchone() or (None, None)
    events = []
    rows = con.execute("with recursive tree(id) as (select ? union select s.id from sessions s"
                       " join tree on s.parent_session_id = tree.id)"
                       " select session_id, role, content, tool_calls, tool_name, timestamp from messages"
                       " where session_id in (select id from tree) order by timestamp, id", (sid,)).fetchall()
    for session, role, content, calls, tool, ts in rows:
        ts = iso(ts)
        if role == "tool":
            events.append(("result", content or "", tool, ts))
        elif role in ("user", "assistant"):
            if content:
                events.append(("assistant" if role != "user" else "meta" if session != sid else user_role(content),
                               content, None, ts))
            try:
                calls = json.loads(calls or "[]")
            except ValueError:
                calls = []
            for call in calls:
                fn = call.get("function") or {}
                events.append(("call", str(fn.get("arguments", "")), fn.get("name"), ts))
    con.close()
    return Session(*row, events)


def opencode_session(db, sid):
    """A root session with its subagent sessions folded in, as Claude subagents are."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    cwd = con.execute("select directory from session where id = ?", (sid,)).fetchone()
    rows = con.execute("with recursive tree(id) as (select ? union select s.id from session s join tree on s.parent_id = tree.id)"
                       " select p.session_id, m.data, p.data, p.time_created from part p join message m on m.id = p.message_id"
                       " where p.session_id in (select id from tree) order by p.time_created, p.id", (sid,)).fetchall()
    con.close()
    events = []
    for session, message, part, ts in rows:
        role, part, ts = json.loads(message).get("role"), json.loads(part), iso(ts / 1000)
        if part.get("type") == "text":
            text = part.get("text", "")
            events.append(("assistant" if role != "user" else "meta" if session != sid else user_role(text), text, None, ts))
        elif part.get("type") == "tool":
            state = part.get("state") or {}
            events.append(("call", json.dumps(state.get("input")), part.get("tool"), ts))
            events.append(("result", str(state.get("output") or ""), part.get("tool"), ts))
    return Session(cwd[0] if cwd else None, None, events)


def opencode_roots(db, skill):
    """Root ids of the sessions whose parts name the skill."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute("with recursive up(id, parent) as (select id, parent_id from session where id in"
                       " (select distinct session_id from part where data like ?)"
                       " union select s.id, s.parent_id from session s join up on s.id = up.parent)"
                       " select id from up where parent is null", (f"%{skill}%",)).fetchall()
    con.close()
    return [r[0] for r in rows]


def pi_session(path):
    cwd, events = None, []
    for rec in jsonl(path):
        if rec.get("type") == "session":
            cwd = rec.get("cwd")
        if rec.get("type") != "message":
            continue
        msg, ts = rec.get("message") or {}, rec.get("timestamp")
        role, content = msg.get("role"), msg.get("content")
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        for block in content or []:
            kind = block.get("type")
            if role == "toolResult":
                if kind == "text":
                    events.append(("result", block.get("text", ""), msg.get("toolName"), ts))
            elif kind == "text":
                text = block.get("text", "")
                events.append((user_role(text) if role == "user" else "assistant" if role == "assistant" else "meta", text, None, ts))
            elif kind == "toolCall":
                args = block.get("arguments")
                events.append(("call", args if isinstance(args, str) else json.dumps(args), block.get("name"), ts))
    return Session(cwd, None, events)


def load(agent, sid, files):
    if agent == "claude":
        return claude_session(files)
    if agent == "codex":
        return codex_session(files[0])
    if agent == "pi":
        return pi_session(files[0])
    if agent == "opencode":
        return opencode_session(files[0], sid)
    return hermes_session(files[0], sid)


def called_skill(args):
    try:
        args = json.loads(args)
    except ValueError:
        return ""
    return args.get("skill") or args.get("name") or "" if isinstance(args, dict) else ""


class Matcher:
    """Per-event evidence that a session used or maintained one skill."""

    def __init__(self, skill, leads):
        word = rf"(?<![\w-]){re.escape(skill)}(?![\w-])"
        self.skill, self.leads = skill, leads
        self.trigger = re.compile(rf"(?<![\w/.$-])[$/]{re.escape(skill)}(?![\w-])")
        self.name = re.compile(word)
        self.skill_file = re.compile(rf"{word}/SKILL\.md")

    def signals(self, role, text, tool):
        found = set()
        if role == "user":
            text = REMINDER.sub("", text)
            if self.trigger.search(text):
                found.add("trigger")
            elif self.name.search(text):
                found.add("mention")
        if role == "call":
            if tool in SKILL_TOOLS and called_skill(text) == self.skill:
                found.add("skill-call")
            if self.skill_file.search(text) and (WRITE_TOOL.search(tool or "") or "*** Update File" in text):
                found.add("edit")
            if "retro.py" in text:
                found.add("retro")
        elif self.leads and any(l in squash(text) for l in self.leads):
            found.add("body")
        return found


def classify(matcher, events):
    signals, first_user = set(), None
    for role, text, tool, _ in events:
        signals |= matcher.signals(role, text, tool)
        if role == "user":
            text = REMINDER.sub("", text).strip()
            if not text.startswith("<command-name>/clear"):
                first_user = first_user or text[:300] or None
    explicit = signals & {"trigger", "skill-call"}
    if explicit or ("body" in signals and not signals & {"edit", "retro"}):
        kind = "use"
    elif signals & {"edit", "retro"}:
        kind = "maintenance"
    elif "mention" in signals:
        kind = "mention"
    else:
        return None
    by = "user" if "trigger" in signals else "self" if signals & {"body", "skill-call"} else "-"
    return {"kind": kind, "trigger": by, "signals": sorted(signals), "first_user": first_user}


def codex_subagent(path):
    """Codex subagent rollouts replay their parent's history, which has its own row."""
    with open(path) as f:
        try:
            return bool((json.loads(f.readline()).get("payload") or {}).get("parent_thread_id"))
        except ValueError:
            return False


def candidates(home):
    """Yield (agent, id, files) for every session store on this machine."""
    projects = home / ".claude/projects"
    for main in sorted(projects.glob("*/*.jsonl")):
        yield "claude", main.stem, [main, *sorted(main.parent.glob(f"{main.stem}/subagents/*.jsonl"))]
    seen = set()
    for f in sorted((home / ".codex").glob("sessions/**/*.jsonl")) + sorted((home / ".codex").glob("archived_sessions/*.jsonl")):
        if f.name not in seen and not codex_subagent(f):
            seen.add(f.name)
            yield "codex", f.stem, [f]
    for f in sorted((home / ".pi/agent/sessions").glob("**/*.jsonl")):
        yield "pi", f.stem, [f]


def hermes_dbs(home):
    dbs = [home / ".hermes/state.db", *sorted((home / ".hermes/profiles").glob("*/state.db"))]
    return [db for db in dbs if db.is_file() and ".pre-default" not in db.parent.name]


def find(skill, home, repo, since=None):
    home, repo = Path(home), Path(repo)
    leads, last_edit = fingerprints(skill, repo, home)
    matcher = Matcher(skill, leads)
    needles = [skill.encode()] + [l[:20].encode() for l in leads]
    found = []

    def keep(agent, sid, files, size=None):
        cwd, origin, events = load(agent, sid, files)
        verdict = classify(matcher, events)
        if not verdict:
            return
        start = next((e[3] for e in events if e[3]), None)
        era = "-"
        if last_edit and start:
            era = "post" if parse_time(start) >= parse_time(last_edit) else "pre"
        found.append({"agent": agent, "id": sid, "files": [str(f) for f in files], "start": start, "cwd": cwd,
                      "origin": origin, "era": era, "size": size or sum(len(e[1]) for e in events), **verdict})

    for agent, sid, files in candidates(home):
        if any(n in f.read_bytes() for f in files for n in needles):
            keep(agent, sid, files, sum(f.stat().st_size for f in files))
    for db in hermes_dbs(home):
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        pattern = f"%{skill}%"
        sids = [r[0] for r in con.execute("with recursive up(id, parent) as (select id, parent_session_id from sessions"
                                          " where id in (select session_id from messages where content like ? or tool_calls like ?)"
                                          " union select s.id, s.parent_session_id from sessions s join up on s.id = up.parent)"
                                          " select id from up where parent is null", (pattern, pattern))]
        con.close()
        for sid in sids:
            keep("hermes", sid, [db])
    opencode = home / ".local/share/opencode/opencode.db"
    if opencode.is_file():
        for sid in opencode_roots(opencode, skill):
            keep("opencode", sid, [opencode])
    found = [r for r in found if not since or (r["start"] or "") >= since]
    return sorted(found, key=lambda r: r["start"] or "")


def hermes_usage(skill, home):
    try:
        return json.loads((home / ".hermes/skills/.usage.json").read_text()).get(skill)
    except (OSError, ValueError):
        return None


def write_manifest(skill, found, path, repo, home):
    leads, last_edit = fingerprints(skill, Path(repo), Path(home))
    Path(path).write_text(json.dumps({"skill": skill, "leads": leads, "last_edit": last_edit, "sessions": found}, indent=1))


def clip(text, limit):
    return text if len(text) <= limit else f"{text[:limit]}...[+{len(text) - limit} chars]"


def transcript_name(record):
    return f"{(record['start'] or '')[:10]}-{record['agent']}-{record['id'][-8:]}.md"


def extract(record, out, matcher):
    """Condense one session: tool detail for a stretch after each skill signal, conversation elsewhere."""
    events = load(record["agent"], record["id"], record["files"]).events
    hits = [i for i, e in enumerate(events) if matcher.signals(*e[:3])]
    detail = {i for h in hits for i in range(h, h + DETAIL_AFTER + 1)}
    first, skipped = hits[0] if hits else 0, Counter()

    def flush(w):
        if skipped:
            w.write(f"\n--- CALLS {sum(skipped.values())}: {', '.join(f'{t} {n}' for t, n in skipped.most_common())}\n")
            skipped.clear()

    with open(out, "w") as w:
        w.write(f"# {record['agent']} {record['id']}\n\ncwd: {record['cwd']}  start: {record['start']}  "
                f"kind: {record['kind']}  trigger: {record['trigger']}  era: {record['era']}  origin: {record['origin']}  "
                f"signals: {', '.join(record['signals'])}\nsource: {' '.join(record['files'])}\n")
        for i, (role, text, tool, ts) in enumerate(events):
            stamp = (ts or "")[:19]
            if role in ("call", "result") and i not in detail:
                if role == "call":
                    skipped[tool or "?"] += 1
                continue
            flush(w)
            if role == "call":
                w.write(f"\n--- {stamp} CALL {tool}: {clip(text, LIMITS['call'])}\n")
            elif role == "result":
                w.write(f"--- OUT{f' ({tool})' if tool else ''}: {clip(text, LIMITS['result'])}\n")
            else:
                limit = LIMITS["before"] if i < first and role != "user" else LIMITS[role]
                w.write(f"\n### {stamp} {role.upper()}\n{clip(text, limit)}\n")
        flush(w)


def extract_all(manifest, outdir, kinds):
    data = json.loads(Path(manifest).read_text())
    matcher = Matcher(data["skill"], data["leads"])
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for r in data["sessions"]:
        if r["kind"] in kinds:
            path = outdir / transcript_name(r)
            extract(r, path, matcher)
            paths.append(path)
    return paths


def verify(manifest, reports):
    """Check each QUOTE line against its full session, whitespace-folded. Returns (count, failures)."""
    records = {transcript_name(r): r for r in json.loads(Path(manifest).read_text())["sessions"]}
    texts, count, failed = {}, 0, []
    for report in reports:
        for name, quote in QUOTE.findall(Path(report).read_text()):
            name, quote, count = Path(name).name, quote.strip().strip('"'), count + 1
            if name in records and name not in texts:
                r = records[name]
                texts[name] = squash("\n".join(e[1] for e in load(r["agent"], r["id"], r["files"]).events))
            if squash(quote) not in texts.get(name, ""):
                failed.append((str(report), name, quote))
    return count, failed


def table(manifest, reports, kinds=("use", "mention")):
    """One row per extracted session: its SESSION line fields, or None when no report has one."""
    lines = {Path(name).name: [f.strip() for f in rest.split(" | ")]
             for report in reports for name, rest in SESSION.findall(Path(report).read_text())}
    return [(transcript_name(r), lines.get(transcript_name(r)))
            for r in json.loads(Path(manifest).read_text())["sessions"] if r["kind"] in kinds]


def batches(paths, limit):
    groups, current, size = [], [], 0
    for path in sorted(paths, key=lambda p: -p.stat().st_size):
        n = path.stat().st_size
        if current and size + n > limit:
            groups.append(current)
            current, size = [], 0
        current.append(path)
        size += n
    return groups + [current] if current else groups


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("skill")
    f.add_argument("--repo", default=".", help="skills repo holding skills/<skill>/SKILL.md (default: cwd)")
    f.add_argument("--home", default=str(Path.home()))
    f.add_argument("--since", help="YYYY-MM-DD")
    f.add_argument("--manifest", help="write the found sessions as JSON for extract")
    e = sub.add_parser("extract")
    e.add_argument("manifest")
    e.add_argument("outdir")
    e.add_argument("--kinds", default="use,mention")
    e.add_argument("--batch-chars", type=int, default=350_000)
    v = sub.add_parser("verify")
    v.add_argument("manifest")
    v.add_argument("reports", nargs="+")
    t = sub.add_parser("table")
    t.add_argument("manifest")
    t.add_argument("reports", nargs="+")
    args = parser.parse_args()

    if args.cmd == "find":
        home = Path(args.home)
        found = find(args.skill, home, Path(args.repo), args.since)
        leads, last_edit = fingerprints(args.skill, Path(args.repo), home)
        print(f"fingerprints: {leads}\nlast edit: {last_edit}\nhermes dbs: {[str(d) for d in hermes_dbs(home)]}")
        print(f"hermes usage: {hermes_usage(args.skill, home)}\n")
        for r in found:
            print(f"{(r['start'] or '')[:16]}  {r['agent']:8} {r['kind']:11} {r['trigger']:4} {r['era']:4} "
                  f"{r['size'] // 1024:>6}K  {r['origin'] or '-'}  {r['cwd']}\n    {r['id']}  [{', '.join(r['signals'])}]  "
                  f"{squash(r['first_user'] or '')[:100]}")
        if args.manifest:
            write_manifest(args.skill, found, args.manifest, args.repo, home)
            print(f"\nwrote {len(found)} sessions to {args.manifest}")
    elif args.cmd == "verify":
        count, failed = verify(args.manifest, args.reports)
        for report, name, quote in failed:
            print(f"UNVERIFIED {report}: {name} | {quote}")
        print(f"{count - len(failed)}/{count} quotes verified")
        sys.exit(1 if failed else 0)
    elif args.cmd == "table":
        rows = table(args.manifest, args.reports)
        print("| session | verdict | trigger | scope | reaction |\n|---|---|---|---|---|")
        for name, fields in rows:
            print(f"| {name} | {' | '.join(fields) if fields else 'MISSING'} |")
        missing = sum(1 for _, fields in rows if not fields)
        print(f"\n{len(rows) - missing}/{len(rows)} sessions reported")
        sys.exit(1 if missing else 0)
    else:
        paths = extract_all(args.manifest, args.outdir, set(args.kinds.split(",")))
        for i, group in enumerate(batches(paths, args.batch_chars), 1):
            print(f"batch {i} ({sum(p.stat().st_size for p in group) // 1024}K): {' '.join(str(p) for p in group)}")


if __name__ == "__main__":
    main()
