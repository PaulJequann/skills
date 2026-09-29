---
name: skill-retro
description: Run a retro on a skill from the sessions where local coding agents (Claude Code, Codex, Hermes, Pi, OpenCode) used it, and improve it from the evidence. Use when asked how a skill performs in practice, or to improve a skill from its session history.
---

# Skill retro

Improve a skill from what happened when agents ran it: the calls they made,
the output they gave, and how the user reacted. The retro ends with an edit
only where the evidence bar holds: a problem seen in two or more sessions, or
one severe failure the user had to correct.

Transcripts hold private session data. Write every harvest file to your
scratchpad or a temp directory, never into the skills repo.

## 1. Scope

Name the skill, the skills repo that authors it, and the user's question: a
general retro, or a specific worry such as "it feels ceremonial". Read the
current `SKILL.md` and `git log` of it, so you know which versions ran.

## 2. Harvest

From the skills repo:

```bash
python3 <skill-dir>/scripts/retro.py find <skill> --manifest <scratch>/manifest.json [--since YYYY-MM-DD]
```

It scans every Claude Code project, the OpenCode database, Codex live and
archived sessions, Hermes state databases (backup profiles skipped), and Pi
sessions. Subagent sessions fold into their root session. It matches on the
lead sentence of every committed version of the skill body, so listings of
installed skills never count.

Each row carries:

- **kind**:
  - `use`: an explicit invocation, or the body loaded.
  - `maintenance`: edited the skill, or ran a retro on it.
  - `mention`: the user named it, but nothing loaded.
- **trigger**: `user` or `self`.
- **era**: `pre` or `post` the skill's last commit.
- **origin**: the entry point the session came through, such as `cli`,
  `codex_exec`, or Hermes `bytes`.

Hermes `.usage.json` counts print as a cross-check.

Done when you have read every row and can say which ones are real uses. A
body-only `self` row can be a read for reference, such as an agent reviewing
the skills repo; its first user message usually shows it. The harvest covers
this machine only; name the machines it missed if the user runs agents
elsewhere.

## 3. Extract

```bash
python3 <skill-dir>/scripts/retro.py extract <scratch>/manifest.json <scratch>/tx
```

This writes one condensed transcript per `use` or `mention` session and prints
batches of about 200K characters; raise `--batch-chars` when the batches
outnumber the analysts you want to run. Each transcript keeps the whole
conversation, with tool calls and outputs in a window after each skill signal
and a one-line count of the calls elsewhere.

## 4. Analyse

Dispatch one subagent per batch, in parallel, all in one message. Give each:

- the path of [references/analyst-brief.md](references/analyst-brief.md), to
  read first;
- its transcript paths;
- the skill's `SKILL.md` path and the repo path;
- the user's question from step 1;
- its report path, `<scratch>/reports/batch-<n>.md`.

Pass paths rather than paraphrases, so every analyst reads the same text.
When every report is written, check the quotes:

```bash
python3 <skill-dir>/scripts/retro.py verify <scratch>/manifest.json <scratch>/reports/*.md
```

Done when verify passes, or you have dropped every claim that rests on an
`UNVERIFIED` quote.

## 5. Synthesize

Build one table across all analyst reports: session, verdict, trigger, scope,
and the user's reaction. Then group the suggestions into **themes**.

- A theme meets the evidence bar with support from two or more sessions, or
  from one session where the user had to correct a severe failure.
- A theme seen only in `pre` sessions may already be fixed. Check the current
  text before you count it.
- A theme's cause tags decide its edit, by the analyst brief's **Suggested
  changes** rule. **Harness** problems stay out of the skill; list them for
  the user.
- Everything else is a one-off: report it, but leave the skill alone.

Done when every suggestion sits in a theme or in the one-offs.

Report to the user: the usage picture, meaning who triggers the skill, how
often, and where; each theme with its supporting sessions and a verbatim quote;
the proposed edits; the harness problems; and the one-offs. Wait for their
go-ahead before editing.

## 6. Edit and ship

1. Make the approved edits to the authored `SKILL.md` in the repo.
2. Review the whole skill with **writing-for-agents**, and apply what it finds.
3. Show the user the diff.
4. Commit only the skill's own paths, and only when the user says to. Other
   sessions may have uncommitted work in the same repo.
5. Push when the user says to, then sync the installed copies, for example with
   `dotfiles skills sync`. The sync pulls from the remote, so it has no effect
   before the push.
