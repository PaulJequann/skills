#!/usr/bin/env python3
"""Tests for retro.py."""

import importlib.util
import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path


def load_retro_module():
    script_path = os.path.join(os.path.dirname(__file__), "retro.py")
    spec = importlib.util.spec_from_file_location("retro", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


retro = load_retro_module()

TS = "2026-09-01T10:00:00.000Z"
SKILL_V1 = """---
name: demo
description: Audit demos. Use when demoing.
---

# Demo

Audit demos by the defect they would detect.
"""
SKILL_V2 = """---
name: demo
description: Audit demos. Use when demoing.
---

# Demo

Judge each demo by the defect it catches, not by
coverage or passing status.

## Steps
"""
BODY = SKILL_V2.split("---\n", 2)[2]
LISTING = "- demo: Audit demos. Use when demoing. (file: /h/.agents/skills/demo/SKILL.md)"


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records))


def codex_meta():
    return {"timestamp": TS, "type": "session_meta", "payload": {"id": "c1", "cwd": "/work", "originator": "codex_exec"}}


def codex_msg(role, text):
    kind = "output_text" if role == "assistant" else "input_text"
    return {"timestamp": TS, "type": "response_item",
            "payload": {"type": "message", "role": role, "content": [{"type": kind, "text": text}]}}


def codex_call(name, args, output):
    return [
        {"timestamp": TS, "type": "response_item",
         "payload": {"type": "function_call", "name": name, "arguments": json.dumps(args)}},
        {"timestamp": TS, "type": "response_item",
         "payload": {"type": "function_call_output", "output": output}},
    ]


def claude_rec(role, content, **extra):
    return {"type": role, "timestamp": TS, "cwd": "/work", "message": {"role": role, "content": content}, **extra}


class RetroTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.repo = Path(self.tmp.name) / "repo"
        skill = self.repo / "skills" / "demo" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(SKILL_V2)

    def tearDown(self):
        self.tmp.cleanup()

    def find(self):
        return retro.find("demo", home=self.home, repo=self.repo)

    def only(self):
        found = self.find()
        self.assertEqual(len(found), 1, found)
        return found[0]

    def codex(self, name, records):
        write_jsonl(self.home / ".codex/sessions/2026/09/01" / name, [codex_meta(), codex_msg("developer", LISTING)] + records)

    def claude(self, uuid, records, project="-work"):
        write_jsonl(self.home / ".claude/projects" / project / f"{uuid}.jsonl", records)

    def hermes_db(self, path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(path)
        db.execute("create table sessions (id text primary key, started_at real, cwd text, title text, source text)")
        db.execute("create table messages (id integer primary key, session_id text, role text, content text,"
                   " tool_call_id text, tool_calls text, tool_name text, timestamp real)")
        db.execute("insert into sessions values ('h1', 1788000000, '/work', 't', 'bytes')")
        db.executemany("insert into messages (session_id, role, content, tool_calls, tool_name, timestamp)"
                       " values ('h1', ?, ?, ?, ?, 1788000000)", rows)
        db.commit()
        db.close()

    def test_codex_listing_and_injected_instructions_are_not_a_use(self):
        self.codex("rollout-a.jsonl", [
            codex_msg("user", "# AGENTS.md instructions\n\nRun $demo after every change."),
            codex_msg("user", "fix the build"),
            codex_msg("assistant", "done"),
        ])
        self.assertEqual(self.find(), [])

    def test_codex_dollar_trigger_with_injected_body_is_user_triggered_use(self):
        self.codex("rollout-a.jsonl", [
            codex_msg("user", "$demo on your work"),
            codex_msg("user", f"<skill>\n<name>demo</name>\n{BODY}</skill>"),
        ])
        hit = self.only()
        self.assertEqual((hit["agent"], hit["kind"], hit["trigger"], hit["origin"]), ("codex", "use", "user", "codex_exec"))
        self.assertEqual(hit["first_user"], "$demo on your work")

    def test_codex_self_read_of_skill_file_is_self_triggered_use(self):
        self.codex("rollout-a.jsonl", [codex_msg("user", "review the tests")]
                   + codex_call("exec_command", {"cmd": "cat ~/.agents/skills/demo/SKILL.md"}, SKILL_V2))
        hit = self.only()
        self.assertEqual((hit["kind"], hit["trigger"]), ("use", "self"))

    def test_claude_skill_tool_is_self_triggered_use(self):
        self.claude("s1", [
            claude_rec("user", "check my tests"),
            claude_rec("assistant", [{"type": "tool_use", "id": "t", "name": "Skill", "input": {"skill": "demo"}}]),
            claude_rec("user", [{"type": "tool_result", "tool_use_id": "t", "content": "Launching skill: demo"}]),
            claude_rec("user", [{"type": "text", "text": f"Base directory for this skill: /h/demo\n\n{BODY}"}], isMeta=True),
        ])
        hit = self.only()
        self.assertEqual((hit["agent"], hit["kind"], hit["trigger"]), ("claude", "use", "self"))
        self.assertEqual(hit["first_user"], "check my tests")

    def test_claude_slash_command_is_user_triggered_use(self):
        self.claude("s1", [
            claude_rec("user", "<command-name>/demo</command-name>\n<command-args>the diff</command-args>"),
            claude_rec("user", [{"type": "text", "text": BODY}], isMeta=True),
        ])
        self.assertEqual(self.only()["trigger"], "user")

    def test_claude_listing_in_system_reminder_is_not_a_use(self):
        self.claude("s1", [claude_rec("user", f"<system-reminder>\n{LISTING}\n</system-reminder>\nfix the build")])
        self.assertEqual(self.find(), [])

    def test_subagent_report_and_other_skill_args_are_not_triggers(self):
        self.claude("s1", [
            claude_rec("user", "tidy the docs"),
            claude_rec("assistant", [{"type": "tool_use", "id": "t", "name": "Skill",
                                      "input": {"skill": "writing-for-agents", "args": "review skills/demo/SKILL.md"}}]),
            claude_rec("user", "<task-notification>\nThe user ran $demo on the diff.\n</task-notification>"),
        ])
        self.assertEqual(self.find(), [])

    def test_skill_path_in_user_text_is_a_mention_not_a_trigger(self):
        self.claude("s1", [claude_rec("user", "what does ~/.agents/skills/demo/SKILL.md cover?")])
        hit = self.only()
        self.assertEqual((hit["kind"], hit["trigger"]), ("mention", "-"))

    def test_claude_subagent_use_folds_into_parent_session(self):
        self.claude("s1", [claude_rec("user", "audit everything")])
        write_jsonl(self.home / ".claude/projects/-work/s1/subagents/agent-x.jsonl",
                    [claude_rec("user", [{"type": "text", "text": BODY}], isMeta=True, isSidechain=True)])
        hit = self.only()
        self.assertEqual((hit["id"], hit["kind"]), ("s1", "use"))
        self.assertEqual(len(hit["files"]), 2)

    def test_edit_of_skill_file_marks_maintenance(self):
        self.claude("s1", [
            claude_rec("user", "improve the demo skill"),
            claude_rec("assistant", [{"type": "tool_use", "id": "t", "name": "Edit",
                                      "input": {"file_path": "/repo/skills/demo/SKILL.md", "old_string": "a", "new_string": "b"}}]),
        ])
        self.assertEqual(self.only()["kind"], "maintenance")

    def test_hermes_skill_view_is_use_and_backup_profiles_are_skipped(self):
        rows = [
            ("user", "look at the tests", None, None),
            ("assistant", "", json.dumps([{"function": {"name": "skill_view", "arguments": '{"name":"demo"}'}}]), None),
            ("tool", json.dumps({"success": True, "name": "demo", "content": SKILL_V2}), None, "skill_view"),
        ]
        self.hermes_db(self.home / ".hermes/state.db", rows)
        self.hermes_db(self.home / ".hermes/profiles/bytes.pre-default.1/state.db", rows)
        hit = self.only()
        self.assertEqual((hit["agent"], hit["kind"], hit["trigger"], hit["cwd"], hit["origin"]),
                         ("hermes", "use", "self", "/work", "bytes"))

    def test_opencode_skill_tool_in_child_session_folds_into_root(self):
        db_path = self.home / ".local/share/opencode/opencode.db"
        db_path.parent.mkdir(parents=True)
        db = sqlite3.connect(db_path)
        db.execute("create table session (id text primary key, parent_id text, directory text, time_created integer)")
        db.execute("create table message (id text primary key, session_id text, time_created integer, data text)")
        db.execute("create table part (id text primary key, message_id text, session_id text, time_created integer, data text)")
        db.executemany("insert into session values (?, ?, '/work', 1788000000000)", [("root", None), ("child", "root")])
        db.executemany("insert into message values (?, ?, 1788000000000, ?)", [
            ("m1", "root", json.dumps({"role": "user"})),
            ("m2", "child", json.dumps({"role": "user"})),
            ("m3", "child", json.dumps({"role": "assistant"})),
        ])
        db.executemany("insert into part values (?, ?, ?, ?, ?)", [
            ("p1", "m1", "root", 1788000000000, json.dumps({"type": "text", "text": "check my tests"})),
            ("p2", "m2", "child", 1788000001000, json.dumps({"type": "text", "text": "$demo the suite"})),
            ("p3", "m3", "child", 1788000002000, json.dumps({"type": "tool", "tool": "skill", "state": {
                "input": {"name": "demo"}, "output": f"<skill_content name=\"demo\">{BODY}"}})),
        ])
        db.commit()
        db.close()
        hit = self.only()
        self.assertEqual((hit["agent"], hit["id"], hit["kind"], hit["trigger"]), ("opencode", "root", "use", "self"))
        self.assertIn("skill-call", hit["signals"])

    def test_pi_inventory_listing_is_not_a_use(self):
        write_jsonl(self.home / ".pi/agent/sessions/--work--/2026_x.jsonl", [
            {"type": "session", "id": "p1", "timestamp": TS, "cwd": "/work"},
            {"type": "message", "message": {"role": "user", "content": [{"type": "text", "text": "list my skills"}]}},
            {"type": "message", "message": {"role": "toolResult", "toolName": "bash",
                                            "content": [{"type": "text", "text": "demo\nother-skill"}]}},
        ])
        self.assertEqual(self.find(), [])

    def test_old_version_lead_matches_and_use_is_dated_against_last_edit(self):
        git = ["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        skill = self.repo / "skills/demo/SKILL.md"
        subprocess.run(git[:3] + ["init", "-q"], check=True)
        skill.write_text(SKILL_V1)
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["commit", "-qm", "v1"], check=True, env={**os.environ, "GIT_COMMITTER_DATE": "2026-08-01T00:00:00Z"})
        skill.write_text(SKILL_V2)
        subprocess.run(git + ["commit", "-qam", "v2"], check=True, env={**os.environ, "GIT_COMMITTER_DATE": "2026-09-15T00:00:00Z"})
        self.claude("s1", [
            claude_rec("user", "go"),
            claude_rec("user", [{"type": "text", "text": SKILL_V1.split("---\n", 2)[2]}], isMeta=True),
        ])
        hit = self.only()
        self.assertEqual((hit["kind"], hit["era"]), ("use", "pre"))

    def test_extract_keeps_every_session_and_details_only_near_the_use(self):
        noise = codex_call("exec_command", {"cmd": "make lint"}, "lint output " * 50)
        self.codex("rollout-2026-09-01T10-00-00-aaaa.jsonl", [codex_msg("user", "early work")] + noise * 20
                   + [codex_msg("user", "$demo on your work"), codex_msg("user", f"<skill>\n{BODY}</skill>")]
                   + noise + [codex_msg("user", "that verdict was wrong")])
        self.codex("rollout-2026-09-01T11-00-00-bbbb.jsonl", [codex_msg("user", "$demo please")])
        manifest = Path(self.tmp.name) / "manifest.json"
        retro.write_manifest("demo", self.find(), manifest, repo=self.repo, home=self.home)
        out = Path(self.tmp.name) / "tx"
        paths = retro.extract_all(manifest, out, kinds={"use"})
        self.assertEqual(len(paths), 2)
        text = max(paths, key=lambda p: p.stat().st_size).read_text()
        self.assertIn("that verdict was wrong", text)
        self.assertEqual(text.count("--- OUT"), 1)
        self.assertEqual(text.count("CALL exec_command"), 21)

    def test_verify_rejects_quotes_missing_from_the_session(self):
        self.codex("rollout-a.jsonl", [codex_msg("user", "$demo on your work"),
                                       codex_msg("user", "that verdict\n  was wrong")])
        manifest = Path(self.tmp.name) / "manifest.json"
        retro.write_manifest("demo", self.find(), manifest, repo=self.repo, home=self.home)
        name = retro.transcript_name(self.only())
        report = Path(self.tmp.name) / "report.md"
        report.write_text(f"QUOTE {name} | that verdict   was wrong\n"
                          f'QUOTE tx/{name} | "$demo on your work"\n'
                          f"QUOTE {name} | the user loved it\n"
                          f"QUOTE 2026-01-01-codex-deadbeef.md | that verdict was wrong\n")
        count, failed = retro.verify(manifest, [report])
        self.assertEqual(count, 4)
        self.assertEqual([q for _, _, q in failed], ["the user loved it", "that verdict was wrong"])


if __name__ == "__main__":
    unittest.main()
