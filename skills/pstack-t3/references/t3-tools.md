# T3 dispatch mapping for pstack

pstack skills are written in Claude Code tool language. Under T3 Code, the harness tool map still governs files, shell, and todos. This file governs everything that spawns, waits on, schedules, or reads other agents. Where it disagrees with `codex-tools.md` or another runtime map, this file wins.

## Tool actions

| pstack / Claude action | Under T3 |
|---|---|
| `Agent` / `Task` for a role whose model is outside this harness | `delegate_task` with `target: {providerInstanceId, model, options}` (see SKILL.md Dispatch) |
| N parallel `Agent` calls in one message | N `delegate_task` calls in one response, `mode: "async"`, then end the turn |
| `run_in_background: true` | `mode: "async"`, the default |
| Wait for a subagent result | End the turn. The completion wakes this thread. Read it with `task_status`. Use `mode: "wait"` only when this turn cannot continue without the result. |
| `readonly: true`, or "the prompt forbids file writes" | State read-only scope in the brief. T3 has no read-only flag. |
| `subagent_type: "general-purpose"` | Panel brief (references/brief.md) |
| `subagent_type: "pstack:poteto-agent"` | Agent brief (references/brief.md) |
| `pstack:effort-<level>`, `pstack:poteto-agent-<level>`, `reasoning_effort` | `target.options` with the provider's effort option id |
| `subagent_type: "pstack:comment-sicko"` | Agent brief that reads `$PSTACK_ROOT/skills/poteto-mode/references/agents/comment-sicko.md` in full instead of poteto-mode |
| Resume or steer a running subagent (`SendMessage`) | A fresh `delegate_task` with the consolidated scope. Cancel the old one first. |
| Stop a subagent | `task_cancel`, then confirm with `task_status` that `workState` is no longer `working`. A task with `hasPendingChildRuns` still has live nested work. |
| `isolation: "worktree"` | The child runs `git worktree add <dir> -b <branch>` and works only there. Name the dir in its brief. Only if the user asked for separate threads, use `t3_thread_launch` with `workspaceStrategy` instead, since launched threads do not wake this one. |
| `loop` skill, `/loop`, a watcher subagent | Time-based: `schedule_task`. PR events: `watch_pull_request` from a top-level thread. Within one session: end the turn and let completions wake you. |
| `AskUserQuestion` | The harness's question tool if it has one, otherwise plain text |
| `Skill` tool, `/command` | Read `$PSTACK_ROOT/skills/<name>/SKILL.md` |
| Transcripts under `~/.claude/projects/` | `t3_thread_search` to find a thread, `t3_thread_read` to read it. This covers every provider's history. |
| Image generation (teach) | `html_preview` then `html_render` for diagrams |
| List MCP servers (why) | The tools this harness exposes to the session. Children on another provider see that provider's MCP config, not yours. |

## Per-skill notes

| Skill | Under T3 |
|---|---|
| `interrogate` | One `delegate_task` per `interrogate reviewers` entry. Fill `references/reviewer-prompt.md` yourself. For `{RUBRIC_CONTENTS}` and `{CODE_QUALITY_CONTENTS}`, list `rubric.md` and `code-quality-review.md` by absolute path in the brief's read list instead of pasting them. Fill `{DIFF_OR_FILES}` with the diff, or with absolute file paths when the review names files rather than a branch. The Agreement Map now compares providers, so name provider and model per reviewer. |
| `arena` | Runners and the cross-judge are `delegate_task` calls. Writing runners each get their own worktree dir. The judge reads the candidates' worktree paths. |
| `architect` | The runner prompt says "read the architect skill". List `$PSTACK_ROOT/skills/architect/SKILL.md`, `references/runner-prompt.md`, `references/rationale-template.md`, and `references/design-red-flags.md` as absolute paths in each brief. |
| `how` | Explorers and the explainer use the panel brief. The prompts name Glob, Grep, and Read. Children use their own search tools. |
| `why` | Investigators get `investigator-prompt.md`, plus the one `sources/<source>.md` playbook and `epistemics.md`, as absolute paths. The synthesizer prompt says to read `references/epistemics.md`. Give it the absolute path. pstack's warning about readonly mode stripping MCP is Cursor-specific. Ignore it. |
| `swarm` | One `delegate_task` per worker on the `swarm workers` model. Workers that write each get a worktree dir or an output dir of their own. |
| `reflect` | Skip `find-transcript.mjs`. Read this thread with `t3_thread_read`. Write a digest of it to a temp file and pass that path to each reviewer. The reviewer templates look for Claude `Read` and `Agent` calls. On another harness, tell them the equivalent tool names. |
| `recall`, `show-me-your-work`, `eval`, session-pickup | `t3_thread_search` and `t3_thread_read` replace the transcript directory. Eval candidates can run on different providers. |
| `babysit` and the Babysit and Shipping playbooks | `watch_pull_request` replaces the `watch-pr` watcher and `loop` from a top-level thread. From a child, run `watch-pr` through the shell. |
| `orchestrate`, `autopilot-*`, `multi-phase-plan` | Keep the `orch` store, outside the repo, at `~/.local/state/pstack/orchestrate/<slug>/` (pass `--store`). Workers are `delegate_task` children owned by T3, so the playbook line "after a restart, in-flight subagents are dead" may not hold. Check `task_status` before re-dispatching. |
| `no-comments` | See the comment-sicko row above. |
| `setup-pstack` | It does not know T3 values and drops unknown role lines. Edit `~/.config/pstack/t3-models.md` by hand instead. |
| `create-verification-skill`, `automate-me` | Write the generated skill to `.agents/skills/` so every harness finds it. |
