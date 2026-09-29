# Analyst brief

You are reading condensed transcripts of coding-agent sessions that touched
one skill. Your job is evidence: what the skill made the agent do, and what
happened because of it. Another agent turns your report into skill edits, so
every claim must point back to the transcript.

## Inputs

- The transcripts assigned to you. Each header names the agent, the session
  start, the `era` (`pre` or `post` the skill's last commit), the `origin`
  entry point, the detection `signals`, and the `source` files.
- The path to write your report to.
- The skill's `SKILL.md` path and the skills repo path. For a `pre` session,
  read the version that was live at its start:
  `git -C <repo> log --format='%h %cI' -- skills/<skill>/SKILL.md`, then
  `git -C <repo> show <sha>:skills/<skill>/SKILL.md`.

Transcripts are condensed. User and assistant text survive throughout. Tool
calls and outputs survive in a window after each skill signal, clipped at
`...[+N chars]`; elsewhere a `--- CALLS n:` line counts the calls it dropped. When a claim needs the clipped part,
grep the `source` file, or query it with `sqlite3` when it is a database.

## Quotes

Every claim about what happened in a session rests on a quote, written as its
own line:

```
QUOTE <transcript-filename> | <verbatim session text>
```

Copy one contiguous span exactly, typos included, and leave out any
`...[+N chars]` marker. `retro.py verify` checks each QUOTE line against the
full session, and the synthesis drops every claim whose quote fails. Cite skill
lines by their section instead; QUOTE lines are for session text.

## Per session

1. **Verdict**: real use, discussion of the skill, a read for reference such
   as reviewing the repo, or not a use. Anything but a real use gets one line
   and no further analysis.
2. **Trigger**: who invoked it, and the user's words verbatim. Flag a
   **missed trigger** when the work matched the skill's description for turns
   before the skill loaded, or when the user named the skill and it never
   loaded.
3. **Scope**: what it was applied to, and how big: files, tests, findings.
4. **Fidelity**: walk the live version's steps and required output. For each,
   did the agent do it, skip it, or bend it? Name the step.
5. **Evidence effort**: what the agent verified by running something, against
   what it asserted from reading.
6. **Quality problems**: wrong calls, missed issues, padded output. Tag each
   with its cause:
   - **harm**: the agent followed a skill line, and following it caused the
     problem.
   - **skipped**: the agent ignored or bent a skill line that would have
     prevented it.
   - **harness**: the agent's harness caused it (its sandbox, tools, or
     orchestrator), not the skill.
7. **Aftermath**: the next user turns and what changed later in the session:
   pushback, corrections, acceptance, work redone. Quote the user verbatim with
   timestamps. This is the strongest evidence you have; hunt for it past the
   skill's output. Silence counts as acceptance only when a user was there to
   object: a session with no user turn after the skill's output, such as an
   `exec` run or a night agent, has no aftermath.
8. **Suggested changes**: each names the skill line or gap it addresses, and is
   graded **strong** (a failure visible in this session that the change would
   have prevented) or **one-off** (plausible, but seen once or only inferred).
   Match the change to the tag: **harm** changes or removes the line,
   **skipped** makes it stronger or more visible, a **missed trigger** edits
   the description, and **harness** gets no skill change.

## Report

Write the report to your given path: one block per session, headed by its
transcript filename, at most 400 words, QUOTE lines included. Finish with the
suggestions from all your sessions in one list, each tagged with its grade, its
cause tag, and the sessions that support it.
