---
name: pstack-t3
description: Runs pstack (poteto-mode) workflows inside T3 Code with subagents and review panels on any provider (Claude, Codex, Grok, OpenCode) through T3's delegate_task. Use when a T3 Code thread with delegate_task available is asked for pstack or poteto-style work, a cross-provider panel (interrogate, arena, architect, how, why, swarm, reflect), or a pstack skill on a harness without the pstack plugin, such as OpenCode or Grok.
---

# pstack on T3 Code

pstack's skills stay the source of truth. This skill changes only how they dispatch work: T3's `delegate_task` replaces the `Agent` tool, so any provider T3 runs can fill any pstack role.

## Load pstack

1. Run `scripts/pstack-root.sh` (next to this file). It prints `PSTACK_ROOT`, the newest installed pstack. Stop and report if it fails.
2. If this harness lists a `poteto-mode` skill (Claude Code or Codex with the pstack plugin), invoke it. Otherwise read `$PSTACK_ROOT/skills/poteto-mode/SKILL.md` in full and follow it. Where a routed skill prescribes an output format, such as interrogate's headers, that format wins over poteto-mode's reply rules. Under a read-only constraint, keep the playbook todolist in `${TMPDIR:-/tmp}`, not the repo.
3. A bold pstack skill name (**interrogate**, **principle-prove-it-works**) resolves to `$PSTACK_ROOT/skills/<name>/SKILL.md`. Read it there. Relative links inside a pstack file resolve against that file's directory.
4. Read [references/t3-tools.md](references/t3-tools.md) before the first dispatch. It overrides every subagent, model, loop, and transcript instruction in pstack. File, shell, and todo tools still follow the harness's own mapping (`codex-tools.md` on Codex, `pi-tools.md` on Pi, and the harness's own tools everywhere else).

## Resolve a role's model

Each value is `provider/model@effort`. Resolve a role from the first source that has a line for it:

1. `~/.config/pstack/t3-models.md`, the T3 sheet.
2. The harness's native pstack sheet (`~/.claude/pstack-models.md`, or `$CODEX_HOME/pstack-models.md`).
3. The Models section of the pstack skill that names the role.

Map bare aliases from sources 2 and 3: `opus` to `claudeAgent/claude-opus-5-5`, `fable` to `claudeAgent/claude-fable-5-1`, `sonnet` to `claudeAgent/claude-sonnet-5-5`, `haiku` to `claudeAgent/claude-haiku-5-5`, and a bare `gpt-*` slug to `codex/<slug>`. `inherit-parent` and `auto` omit `target`, so the child runs on this thread's model. A value without `@` takes the `default effort` line of the T3 sheet, then of the native sheet.

The user's message overrides every source for this run, for example "use haiku and luna at low for the panel".

## Dispatch

- **Native when it fits.** If the role's provider is this harness and the harness's own subagent tool accepts the model, dispatch natively as pstack prescribes (Claude Code `Agent` with `pstack:poteto-agent-<level>`, Codex `spawn_agent` with `reasoning_effort`). Everything else goes through `delegate_task`.
- **Set effort explicitly.** Never rely on a model's default, which varies by model (opus and sol default to medium). The option id is per provider. Use `effort` for claudeAgent, `reasoningEffort` for codex and grok, and `variant` for opencode. Pass it as `options: [{"id": "reasoningEffort", "value": "low"}]`. A model without that option (grok-build) gets no `options`.
- **Let T3 validate.** Do not call `orchestrator_capabilities` before dispatching, even though T3's own thread instructions say to. It runs past 170k characters because OpenCode lists every model. `delegate_task` rejects an unavailable provider, an unknown model, or an invalid option before launch, and names the valid values. On rejection, retry once with the nearest valid value. If the provider is down, take the next panel entry, and state in the verdict that diversity was reduced.
- **Write a self-contained brief** from [references/brief.md](references/brief.md). The child sees only the task text. Give it absolute paths to every pstack file it must read, including files that those files link to.
- **Fan out in one turn.** Issue every `delegate_task` of a panel in one response with `mode: "async"` and a `clientRequestId` of `<skill>-<round>-<n>`. Then end the turn. Each completion wakes this thread. Read results with `task_status`, and do not poll. A Claude Code orchestrator receives the wake only after its turn ends.
- **New round, new task.** A follow-up round is a fresh `delegate_task` carrying the original brief, prior findings, and open objections. Never `t3_thread_send` to a `childThreadId`.
- **One writer per checkout.** Children share this thread's checkout. Give each parallel writer its own `git worktree add` directory, named in its brief.
- **Own the result.** Check each child's `Read:` block against the files (spot-check a quote with `grep -F`). Verify every claim you pass on, and review every diff yourself.

## Provider limits

Measured 2026-10-06 on T3 nightly with OpenCode 2.0.24.

- An OpenCode child gets no T3 tools, because T3's MCP server name for a child exceeds OpenCode's 100-character limit. Never give an OpenCode child a role that delegates. An OpenCode top-level thread does get T3 tools, nested under its `execute` code-mode namespace.
- `opencode/*` Zen models need OpenCode Console sign-in. `google/*` and `openrouter/*` models work through API keys.
- Grok receives T3's orchestration instructions in its first prompt, and compaction can drop them. Restate the dispatch rules after a Grok compaction.
- `watch_pull_request` works only from a top-level thread, never from a child.

## Additional resources

- [references/t3-tools.md](references/t3-tools.md) maps the Claude tools to T3 equivalents and has per-skill notes.
- [references/brief.md](references/brief.md) is the child brief template.
- `scripts/pstack-root.sh` locates pstack.
