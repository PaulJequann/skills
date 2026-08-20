---
name: code-review
description: Run a static, target-bounded, diff-grounded cross-model code or plan review through whichever review agent is available on this machine (Copilot, Grok Build, Gemini), producing one validated review package. Use when the user or applicable project instructions request a second-opinion review of working changes, commits, branches, named files, or implementation plans, including review-only, review-and-fix, and remediation-verification workflows.
allowed-tools: "Bash(git:*) Bash(which:*) Bash(command:*) Bash(br:*) Bash(~/.agents/skills/code-review/scripts/run-review.sh:*) Read Grep Edit AskUserQuestion"
metadata:
  supersedes: grok-review, gemini-review, code-review-archived
---

## Separate execution from policy

Own review execution: resolve the target, pick and constrain an agent, produce a
validated package, validate findings, and bound follow-up passes. Read applicable
`AGENTS.md` files and use their review emphasis and repository rules.

Leave governance to the caller and project instructions:

- when a second-opinion review is required;
- which severities block delivery;
- which tests, evidence, or approvals are required;
- whether an incomplete external review blocks delivery; and
- who may accept residual risk.

Do not invent those policies. Report an incomplete run as incomplete, not clean.
A completed result describes only the reviewed snapshot.

## Choose an agent

The review contract is identical across agents. The agent is a runtime detail,
so a machine missing one agent still gets a review from another.

```bash
RUNNER=~/.agents/skills/code-review/scripts/run-review.sh
"$RUNNER" --list
```

`--list` reports each adapter as available or unavailable with the reason.

| Situation | Selection |
|-----------|-----------|
| User named an agent | `--agent <id>` |
| Project instructions name an agent | that agent |
| Otherwise | omit `--agent` (defaults to `auto`) |

`auto` walks `grok-build copilot copilot-acp gemini` and takes the first
reachable one. Override the order with `REVIEW_AGENT_PREFERENCE`.

Requesting an unavailable agent fails rather than silently substituting another,
because "which model reviewed this" is part of the result. If the named agent is
missing, report that and ask whether to use an available one — do not swap
silently.

| Agent id | Backing | Notes |
|----------|---------|-------|
| `copilot` | `copilot` direct | Preferred where available: no acpx dependency, and the only path with a true tool-availability filter. |
| `grok-build` | `acpx` + `grok` | Grok Build speaks ACP only. |
| `gemini` | `acpx` + `gemini` | Runs in Gemini's read-only `plan` approval mode. **Unverified.** ACP mode needs `GEMINI_API_KEY`/`GOOGLE_API_KEY`; without it the CLI blocks on interactive OAuth and the run fails at startup. |
| `copilot-acp` | `acpx` + `copilot` | Same model as `copilot`, over ACP. Use only when a host needs every agent on one transport. |

## Choose a model

The Copilot adapters pin **`gpt-5.6-luna` at `max` reasoning effort**. Review is
a deliberate, low-volume, high-stakes task, so it does not inherit whatever the
interactive session happens to be set to. Every other agent uses its own
configured default.

Do not override this unless the user asks. When they do, model and reasoning
effort are **independent** knobs:

```bash
REVIEW_MODEL=gpt-5.6-sol REVIEW_EFFORT=medium "$RUNNER" --agent copilot
```

A request like "copilot with 5.6 sol medium" means `REVIEW_MODEL=gpt-5.6-sol`
plus `REVIEW_EFFORT=medium` — `gpt-5.6-sol-medium` is not a model name and the
run will fail. Effort levels are `none`, `minimal`, `low`, `medium`, `high`,
`xhigh`, `max`.

Model ids belong to the agent, not to this skill, and they change over time.
Read the current list rather than trusting one written down here:

| Agent | List models with |
|-------|------------------|
| `copilot`, `copilot-acp` | `copilot help config` (see the `model` key) |
| `gemini` | `gemini --help` |
| `grok-build` | `grok --help` |

An unknown model or effort fails the run and the runner prints the agent's own
rejection. It never silently falls back to another model, because "which model
reviewed this" is part of the result.

## Select a workflow

Infer one mode from the request and project instructions:

| Mode | Behavior |
|------|----------|
| Review only | Run one initial pass, validate, and present findings. Do not edit or run a remediation pass. |
| Review and fix | Run an initial pass, apply authorized validated fixes, run required local verification, then run at most one remediation pass by default. |
| Verify remediation | Review prior findings plus their remediation delta. Do not restart a broad audit. |

Editing authority comes from the calling task, not from this skill.

## Resolve one target

Stop on an empty diff. Ask the user to narrow a diff larger than 8,000 lines
instead of increasing the turn budget.

| Intent | Command |
|--------|---------|
| Last N commits | `git diff HEAD~N..HEAD` |
| Commit range | `git diff <from>..<to>` |
| Single commit | `git show <sha>` |
| Staged | `git diff --staged` |
| Unstaged / working | `git diff` |
| Bead ID | Diff of commits mentioning that bead ID |
| Branch | `git diff main...<branch>` |
| `.md` with plan signals (`## Phase`, `### Migration`, etc.) | Plan mode — read file, no git |
| File paths | Read files directly |
| Default | `--staged` if staged, else `git diff` |

For a git target, also compute the changed-file list with the matching
`--name-only` form. Use `git show --name-only --pretty=format: <sha>` for a
single commit. Treat the list as navigation help, never as a read allowlist.

## Build a target-bounded review

Scan the target for implicated risks and append only matching priority notes.
These improve an active review; they never decide whether the skill must run.

| Signals | Priority note |
|---------|---------------|
| Authentication, authorization, policy, tenant isolation, session, or middleware | Prioritize trust boundaries, privilege escalation, privacy, and access-control correctness. |
| Migration, schema, DDL, serialization, or durable state | Prioritize compatibility, data preservation, constraints, indexes, and rollback safety. |
| HTTP clients, APIs, retries, webhooks, or external services | Prioritize idempotency, retry/backoff, rate limits, failure handling, and timeouts. |
| Locks, queues, workers, async coordination, or caches | Prioritize races, deadlocks, duplicate work, stale state, and ordering. |
| UI components or interaction handlers | Prioritize accessibility, state transitions, error states, and responsive behavior. |
| Tests or fixtures | Prioritize determinism, false-greens, assertion quality, and missing regression coverage. |

Use repository reads to verify callers, contracts, tests, and assumptions. Do
not expand into an audit of unrelated pre-existing code.

Build one stdin stream in this order:

1. Common instructions
2. Matching priority notes
3. Mode-specific instructions
4. Target description and changed-file starting points
5. Diff payload, named paths, or plan path

Use this common block:

```text
Act as a senior reviewer. Be terse. Skip praise.

Constraints (hard):
- Use only repository-scoped file read/search tools. Do not use shell, terminal,
  git, web, write, edit, delete, or move tools.
- Treat the supplied diff, files, or plan as the review subject. Use surrounding
  repository files only to verify callers, contracts, tests, and assumptions.
- Read applicable AGENTS.md instructions. Treat violations as actionable even
  when the implementation plan requested the conflicting change.
- Do not run tests, typechecks, builds, or other empirical checks.

Review for material regressions in correctness, security, privacy, data
integrity, concurrency, failure handling, performance, public contracts,
operability, test validity, and repository-rule compliance.

Evidence rules:
- Report a pre-existing defect only when this target newly relies on it, exposes
  it, or claims to enforce the affected invariant.
- Identify a concrete failing path or violated invariant for every finding.
- Verify candidates against relevant callers, tests, and surrounding code.
- For a test gap, explain the false-green or regression the current tests miss.
- Consolidate duplicate symptoms under their root cause.
- Drop speculative, low-confidence, purely stylistic, optional-hardening,
  unrelated-debt, and safely deferrable candidates.

Output rules:
- Work silently. Do not narrate tool use, investigation, retractions, or
  non-findings.
- Return exactly one review block and no text before or after it.
- Return at most eight highest-risk findings that could justify changing or
  delaying this target. Omit LOW findings.
- Group affected files under one root cause instead of repeating symptoms.
- Keep each field to one or two sentences. Avoid code blocks unless essential.
- Report only findings you judge to have medium or high confidence.
- A clean result means no finding meets this prompt's materiality threshold; it
  does not assert that no improvement is possible.

For a clean review:
BEGIN_REVIEW
status: clean
summary: No actionable findings.
END_REVIEW

For findings:
BEGIN_REVIEW
status: findings

1. HIGH | correctness | path/to/file.ts:123
Failure: Concrete supported scenario that fails.
Evidence: Why the target permits the failure.
Fix: Smallest safe correction.
Test: Regression that fails before the correction.
END_REVIEW
```

For an initial plan review, append:

```text
Plan threshold:
- Report only decisions that make the next implementation stage unsafe,
  unexecutable, internally contradictory, or likely to require irreversible
  rework.
- Missing implementation detail is not a finding when it can be decided safely
  during implementation.
```

Use the plan section instead of `path/to/file.ts:123` and `Validation` instead
of `Test`.

## Use progressive follow-ups

Never repeat the initial broad prompt after fixes. A remediation pass must
include:

- the prior complete review block;
- the local disposition of each finding;
- the remediation diff since the reviewed snapshot; and
- only the surrounding paths needed to verify those fixes.

Append:

```text
Remediation review:
- Verify whether each previously validated finding is resolved.
- Report a new finding only when the remediation introduced a concrete
  CRITICAL or HIGH regression.
- Do not reopen unchanged areas, repeat resolved findings, broaden the audit,
  or add hardening and wishlist items.
- Return clean when the listed blockers are resolved and the remediation adds
  no CRITICAL or HIGH regression.
```

Use the wrapper's normal per-run budget for remediation. Bound cost through the
finite pass count and narrow prompt, not a shorter timeout or turn limit.

Run a remediation pass on the **same agent** as the initial pass. Switching
agents mid-sequence invalidates the "previously reported" framing, because the
new agent never made those findings. Deliberately re-running the initial pass on
a second agent for extra coverage is a separate initial pass, not a follow-up —
present the two results separately rather than merging them into one verdict.

## Bound convergence

Absent an explicit finite user or project budget:

1. Run at most one initial pass.
2. Run at most one remediation pass.
3. Consider a third completed pass only for exceptional blocker verification.
4. Never run a fourth pass automatically.

A project may set a different finite budget. Do not interpret phrases such as
"until clean" as permission for an unbounded loop.

After pass two, validate and, when authorized, repair any remaining CRITICAL or
HIGH blocker. If another pass could verify that repair, prefer asking whether
to run a final scoped pass when the host supports non-blocking input with a
timeout. Use a short timeout (about 90 seconds) and default to stopping. Do not
block unattended or cloud workflows.

On timeout, unavailable input, or an unattended run, proceed autonomously only
when all are true:

- a locally validated CRITICAL or HIGH finding remains;
- code changed specifically to resolve that finding;
- the finding describes concrete correctness, security, data-loss, privacy, or
  public-contract failure;
- repository reads and deterministic verification cannot establish closure;
- no unresolved product decision or new authority is required; and
- the next prompt can target only that finding and remediation.

Otherwise stop and report the residual finding or risk. Use the wrapper's normal
per-run budget for a third pass and append:

```text
Final blocker verification:
Verify only the listed unresolved blocker and its remediation. Report whether
the concrete failure remains or whether this remediation introduced a CRITICAL
or HIGH regression. Do not reopen unrelated code or identify additional
improvements.
```

Allow at most one transport retry across the review session, only when the
failure is plausibly transient or the retry changes its diagnosed condition.
Do not retry the same deterministic transport or validation failure. A retry
does not turn an incomplete attempt into a completed review.

## Run the review

Pipe the complete prompt into the runner:

```bash
RUNNER=~/.agents/skills/code-review/scripts/run-review.sh
CHANGED="$("${NAME_ONLY_CMD[@]}")"

{
  printf '%s\n' "$REVIEW_HEADER"
  printf '\nTarget: %s\n' "$TARGET_DESCRIPTION"
  printf 'Changed files (starting points, not an allowlist):\n%s\n' "$CHANGED"
  printf '\n--- DIFF ---\n'
  "${DIFF_CMD[@]}"
} | "$RUNNER" --agent "$AGENT"
```

Omit `--agent` to auto-select. For named files or a plan, omit the diff marker
and list the repo-relative paths after the target description.

The runner:

- resolves the agent and refuses to substitute a different one;
- grants only repository read/search tools;
- captures the agent's JSON event stream outside the caller context;
- reconstructs assistant text and extracts the last complete review block;
- normalizes known equivalent clean and finding layouts before validation;
- rejects malformed, missing, contradictory, or oversized packages;
- accepts a complete validated package even if the agent exits non-zero
  afterward; and
- prints one compact usage line to stderr when the agent reports usage.

Do not call `copilot`, `acpx`, or `gemini` directly unless debugging an adapter.
The runner defaults every pass to ten turns and 600 seconds. Override only
through the environment variables below when the target demonstrably needs more
room. Do not shorten later passes merely because their prompts are narrower.

| Variable | Default | Purpose |
|----------|---------|---------|
| `REVIEW_AGENT` | `auto` | Same as `--agent`. |
| `REVIEW_AGENT_PREFERENCE` | `grok-build copilot copilot-acp gemini` | Auto-selection order. |
| `REVIEW_MODEL` | `gpt-5.6-luna` on Copilot adapters, else agent default | Override the model. |
| `REVIEW_EFFORT` | `max` on Copilot adapters | Reasoning effort (`none`…`max`). |
| `REVIEW_MAX_TURNS` | `10` | Agent turn cap (ACP adapters). |
| `REVIEW_TIMEOUT_SECONDS` | `600` | Cooperative timeout for ACP adapters, and the base for the watchdog below. |
| `REVIEW_TIMEOUT_GRACE_SECONDS` | `60` | Headroom before the watchdog fires. |
| `REVIEW_MAX_OUTPUT_BYTES` | `24576` | Review package size ceiling. |
| `REVIEW_DEBUG_DIR` | unset | Also preserve prompt and raw event stream. |

No agent can hang the caller indefinitely. ACP adapters pass a cooperative
`--timeout` to acpx; on top of that the runner runs every adapter under a
watchdog at `REVIEW_TIMEOUT_SECONDS + REVIEW_TIMEOUT_GRACE_SECONDS` (660s by
default) and terminates the agent's whole process tree if it overruns. The grace
window exists so a cooperative timeout fires first and yields a real diagnosis
rather than a bare kill. A watchdog kill is reported as incomplete, never clean.

When invoking the runner through a host shell or task tool, set the host timeout
at least 120 seconds above that combined limit (about 780s at defaults). Never
use equal timeouts: the host must leave enough time for the agent to exit and
for the runner to parse, preserve diagnostics, and report usage. Treat these
limits as stuck-run guards; use the finite pass budget to control review cost.

The command finishes when the runner exits; its JSON event file is an internal
transport detail and must not be printed or loaded into the agent context.

On failure the runner preserves compact diagnostics in a temporary directory and
prints its path. Set `REVIEW_DEBUG_DIR` only for deeper diagnosis.

## Validate and return

Treat any non-zero runner exit as incomplete, never clean. Report its compact
diagnostic and let applicable project policy determine the delivery consequence.
An agent that answers in prose instead of the review block is incomplete, not a
pass — the runner enforces this, so do not work around it by reading the
agent's raw text.

For a completed package:

1. Verify cited code and relevant callers before accepting each finding.
2. Spot-check every HIGH/CRITICAL finding especially carefully.
3. Classify each as valid now, valid later, false positive, or needing context.
4. Apply edits only in review-and-fix mode with existing authority.
5. Run only the local verification required by the caller or project.
6. Follow the bounded progressive workflow above instead of chasing a clean
   result.

Present `| # | Severity | Category | File | Finding | Valid? |`, followed by
fixes, deferred risks, incomplete-run status, and compact usage when relevant.
Name the agent that produced the review. Ask one grouped question only when
authorization or material product intent is unclear; otherwise preserve
autonomous progress.

## Add an agent

Create `scripts/agents/<id>.sh` defining `ADAPTER_DECODER`, `ADAPTER_SUMMARY`,
`adapter_available`, `adapter_missing_reason`, and `adapter_run`. Nothing else
changes; `--list` and `--agent <id>` pick it up automatically.

Constrain the agent at the **availability** layer — the flags that decide which
tools the model can see — not only at the permission layer. Permission denial is
a backstop, not a sandbox: an agent that can still see a shell tool may choose
it, get denied, and abort the turn with no output instead of falling back to
reading files. Copilot uses `--available-tools`; Gemini uses
`--approval-mode plan`. When an ACP agent has no such lever of its own, launch
it through acpx's `--agent` escape hatch so its native flags still apply.

Reuse an existing decoder when the transport matches. Add one to
`parse-review.mjs` only for a genuinely new wire format, and note where that
transport reports usage — it is not uniform even among ACP agents.
