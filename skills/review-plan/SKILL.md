---
name: review-plan
description: >
  Review implementation plans and beads-batch JSON for structure compliance,
  codebase alignment, dependency correctness, collision risks, and task
  granularity. Use when the user types "/review-plan", asks to "review the
  plan", "check the JSON", "audit the plan structure", or "validate against
  the codebase". Accepts JSON plan files and markdown implementation plans,
  especially plans with per-slice Task spec blocks, and emits or updates a
  repo-local lockfile in `.beads/plan-locks/` for reviewed markdown plans.
---

# Review Plan

Structured review of implementation plans or beads-batch JSON files. Gathers findings, then walks the user through them one-at-a-time to drive each to a decision before any edits land on disk.

The core principle: **findings are not done until the user has answered for them.** Don't dump a report and stop. Don't silently mutate the plan. Walk the tree.

For markdown plans that pass review, also produce or update a repo-local lockfile using `scripts/plan-lock.py`. The lockfile is the machine-oriented, provenance-stamped artifact that later review passes and `/beads-batch` consume.

---

## Target Resolution

Determine what to review based on the argument:

1. **JSON file given** — Use it directly. Confirm it exists.
2. **Markdown file given** — Use it directly.
   - If it contains per-slice `Task spec` blocks, treat those blocks as the canonical task surface.
   - If it does not, parse headings/tasks as a fallback and record a structure finding.
3. **No argument** — Glob for `.beads/plans/*.json`.
   - Exactly one found → use it.
   - Multiple found → list them and ask the user to pick (see §Asking Questions).
   - None found → tell the user no plan files found, ask for a path.

Set `$TARGET` and `$TARGET_TYPE` (json | markdown) for subsequent phases.

---

## Phase 1 — Gather Context

Run these in parallel:

1. **Read the plan** — Read `$TARGET` completely. Parse all items/tasks.
   - JSON: extract `items[]` with keys, titles, parents, deps, descriptions, types.
   - Markdown with `Task spec`: extract the required top-level sections, slice headings, slice prose, and every `Task spec` bead.
   - Markdown without `Task spec`: extract task headings, descriptions, file references, and dependency mentions as fallback material only.
2. **Run validation** (JSON only) — `python3 ~/.agents/skills/beads-batch/scripts/beads-batch.py validate $TARGET` — capture stdout/stderr.
3. **Read project structure** — `ls` top-level dirs, read `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` (whichever exists) to understand module boundaries.

Collect all leaf tasks:
- JSON: non-epic items, or items with no children.
- Markdown with `Task spec`: every bead under every slice.
- Markdown without `Task spec`: inferred task-like headings only, with a structure warning that the plan is not yet extraction-ready.

---

## Phase 1.5 — Structure Gate

Run this phase **before** codebase cross-reference. A markdown plan that does not meet the house structure can still be reviewed, but its structure gaps must be reported explicitly instead of being silently worked around.

For markdown plans:

1. **Check required top-level sections** using `references/review-checklist.md`:
   - `Plan spec` (declares the umbrella epic — `plan_key` / `plan_title`)
   - `Purpose`
   - `Research inputs`
   - `Locked decisions`
   - `Scope`
   - `Cross-cutting constraints`
   - `Implementation slices`
   - `Suggested task order`
   - `Deliverables`
   - `Review checkpoint`

   Missing `## Plan spec` is a CRITICAL structural finding — the plan has no umbrella epic, which means imported beads will scatter into the open backlog instead of clustering under one queryable root. Fix before extraction.

2. **Check slice shape**:
   - Every implementation slice has a numbered `###` heading
   - Every slice has framing prose
   - Every slice has `Key work`
   - Every slice has `Acceptance`
   - Every slice has `#### Task spec`

3. **Check `Task spec` completeness**:
   - slice-level: `slice_key`, `blockedBy`, `beads`
   - leaf-bead level: `key`, `title`, `type`, `blockedBy`, `files`, `verification`, `skills`, `logging`, `done_when`
   - dependency keys refer to real keys inside the same plan
   - skill names begin with `/`
   - `logging` is explicit on every bead

4. **Check wording quality**:
   - Flag ambiguous phrases such as `if needed`, `or equivalent`, `as warranted`, `where practical`, or `etc.` when they appear inside `Task spec`.
   - Flag beads that introduce a new helper, manager, service, shared type, or DTO "for reuse" without evidence of multiple real consumers or a volatile boundary.
   - Flag `verification` entries that create a new dedicated test file when an existing module-level proof surface appears sufficient.

For JSON plans:

1. Validate the JSON structure normally.
2. Also check workflow expectations:
   - leaf items should have `skills`
   - descriptions should be concrete enough for an implementing agent
   - service-layer work should not hide missing logging expectations
3. **Umbrella epic**: exactly one parent-less item, and it must be `type: epic`. Multiple roots → CRITICAL finding (the plan has no umbrella, beads will scatter into the backlog). Single non-epic root → WARNING (promote to epic).

Structure findings are actionable findings like any other. Do not defer them to the final summary.

---

## Phase 2 — Codebase Cross-Reference (MANDATORY — do not skip)

**This phase is the core of the review.** Reading the plan against itself is not a review — it only catches internal inconsistencies. A plan that is internally coherent but factually wrong about the codebase will send an implementing agent down a broken path. You MUST open the referenced source files and verify every load-bearing claim before reporting findings.

**Never trust a plan's claims about the codebase.** Every file path, line number, function name, schema shape, type signature, SQL column, and "X already exists / doesn't exist" assertion in the plan is a hypothesis until you've opened the file and confirmed it. Pattern-matching on the plan's confidence is a boundary violation.

For each leaf task:

- **Markdown with `Task spec`** — use the bead's `files`, `verification`, `blockedBy`, `skills`, `logging`, and `done_when` as the primary review surface. Use prose for rationale and context, not as the canonical task definition.
- **Markdown without `Task spec`** — use the inferred headings only as fallback, and keep the missing-structure finding alive through the walkthrough.

1. **Verify load-bearing claims from source.** For every claim the plan makes about existing code, open the referenced file and confirm:
   - Function / class / type / constant exists at the claimed location
   - Shape/signature matches what the plan describes (fields, params, return type)
   - Line numbers are accurate (minor drift OK, note it; wrong function is not OK)
   - SQL table columns referenced actually exist on the referenced table (not a sibling table)
   - "X doesn't exist yet" / "no consumers" / "orphan" claims verified by Grep, not assumed
   - Claimed import paths resolve
   - Proposed refactor targets (e.g., `Map<string, X>` → `Map<string, Y>`) are at the cited location with the cited shape

2. **Check downstream type impact.** If a task adds a field to an interface, grep for every other interface/type that returns or consumes that shape. A plan that adds a field to interface A but forgets that the field also has to be added to interface B (because function C returns B and gets merged into A) is a type error waiting to happen — flag it.

3. **File existence & boundary.** Glob/Grep for files, modules, tables, endpoints mentioned. Flag if referenced code doesn't exist AND no upstream task creates it. Flag tasks spanning 3+ unrelated modules as potentially too broad.

4. **Collision detection.** Build a map of file/module → [tasks that mention it]. Flag files appearing in 2+ tasks with no dependency between them.

**Report verification coverage in the final summary.** The summary MUST include a "what checked out" block listing the specific claims you verified against source, not just a list of findings. If you couldn't verify a claim (file too big, unclear reference), say so explicitly — do not silently skip.

**Red flag — if you're about to report findings without having opened any source files, stop and re-enter Phase 2.** You haven't done the review yet.

---

## Phase 3 — Dependency Analysis

1. **Implicit ordering** — For each task, identify types/tables/configs it creates vs. uses. If task A creates something task B uses but no dep exists, flag it.
   - For markdown plans with `Task spec`, use `blockedBy` as the declared graph and compare it against file/type reality.
2. **Over-serialization** — Tasks with a dep between them but no shared files/types. Could run in parallel. Flag.
3. **Critical path** — Walk the dependency graph to find the longest chain. Flag if any single task is a bottleneck blocking 3+ downstream tasks.

---

## Phase 4 — Granularity & Completeness

Apply thresholds from `references/review-checklist.md` §Granularity:

1. **Too big** — Leaf tasks referencing 5+ files or descriptions over 500 words.
2. **Too small** — Purely mechanical tasks that could fold into an adjacent task.
3. **Missing tasks** — Obvious steps not covered by the plan's stated goals.
4. **Description quality** — Tasks without descriptions, or descriptions lacking file/module references.
5. **Skill annotations** — Leaf tasks without a `skills` field. Suggest likely skills from `references/review-checklist.md` §Skill Heuristics.

For markdown plans with `Task spec`, treat `files`, `verification`, and `done_when` as part of description quality and completeness, not optional extras.
Also treat code-shape guidance as reviewable scope: flag plans that widen public interfaces, spread one behavior across generic catch-all modules, or introduce indirection without a clear coupling or volatility reason.

---

## Phase 5 — Classify Findings

Split everything Phases 2–4 produced into two buckets:

### Actionable findings
Anything with a concrete fix the user can accept, modify, or reject. These enter the walkthrough.

Each actionable finding must carry:
- **id** — `[#N]` for reference
- **severity** — CRITICAL / WARNING / NOTE
- **task keys + file paths** affected
- **proposed fix** — concrete, not vague
- **confidence** — `high` (mechanical, edit-distance typo, missing dep clearly implied) or `judgment` (anything requiring taste)

High-confidence fixes are still presented for approval — they just get pre-filled as the recommended option. **No silent auto-fixes.**

### Stats-only findings
Pure-info items with no action: counts, ratios, longest chain, "N/N tasks have skills." These never enter the walkthrough. They render in the stats block at the end.

---

## Phase 6 — Walkthrough

This is where the skill earns its keep. Drive every actionable finding to a decision.

### Mode selection

- **Interactive (default)** — walk the user through findings.
- **Batch** — emit the full report and stop. Use this when running inside a sub-agent, non-TTY context, or when the orchestrating agent cannot relay user answers. Detect by: no human-question tool available, or explicit `--batch` argument.

### Walk order

1. CRITICAL findings, one-at-a-time.
2. WARNING findings, one-at-a-time.
3. NOTE findings, batched into a single multi-select question (or two if more than ~8 NOTEs).

Within each severity, order by impact (most blocking first).

### Per-finding question shape

For each CRITICAL/WARNING finding, ask the user a single question with these four options. The recommended option depends on confidence:
- **high confidence** → "Apply fix" is the recommended/first option
- **judgment** → no recommendation; user must choose

```
[#N] <severity>: <one-line summary>

Affected: <task keys, file paths>
Proposed fix: <concrete change>
Why: <one-line rationale>

Options:
  fix      — apply the proposed fix as written
  modify   — describe a different fix; agent applies what you say
  skip     — leave as-is, no change
  explain  — agent expands on reasoning, then re-asks
```

If the user picks `explain`, give the deeper rationale (what breaks, what code you checked, edge cases) and re-ask the same finding. Don't loop on `explain` more than twice — after the second explain, force a fix/modify/skip choice.

If the user picks `modify`, capture their instruction verbatim, restate it as a concrete diff plan in one sentence, and treat it as accepted.

### Checkpoints

After every 5 findings (across all severities combined), pause and ask:
- **continue** — keep walking
- **batch-apply rest with recommendations** — accept all remaining recommended fixes, skip judgment-required findings
- **stop** — abandon remaining findings, apply only what's already been decided

### Conflict handling

The walkthrough accumulates an in-memory patch. It does not touch `$TARGET` until Phase 7.

If a user decision on finding `#K` would invalidate or contradict an earlier accepted fix from finding `#J` (J<K):
1. Drop `#J` from the in-memory patch.
2. Insert a new synthetic finding immediately after `#K`: "Your answer to #K conflicts with the earlier fix for #J. Pick which wins."
3. Walk that synthetic finding through the same fix/modify/skip/explain prompt.

### NOTE batching

Present all NOTEs in one multi-select question: "Which of these NOTE-level fixes should I apply?" with each NOTE as an option. User selects any subset. No per-NOTE explain loop — NOTEs are low-stakes by definition.

---

## Phase 7 — Apply

Once the walkthrough completes (naturally or via checkpoint stop):

1. Build the final edit set from the in-memory patch.
2. Apply to `$TARGET` in a single Edit pass. Never touch other project files.
3. Re-run `beads-batch validate` if `$TARGET_TYPE` is JSON. If validation now fails, surface the failure and ask whether to revert or fix-forward.
4. Print the summary:

```
## Plan Review: <filename>

### Applied (N)
[#1] <one-line>
[#3] <one-line>
...

### Skipped (M)
[#2] <one-line> — user skipped
[#5] <one-line> — user skipped after explain

### Stats
- N leaf tasks, M epics
- Longest dependency chain: X tasks (key1 -> key2 -> ...)
- N collision risks detected
- N/N tasks have file-specific descriptions
- N/N leaf tasks have skill annotations
```

5. **For reviewed markdown plans, build or update the repo-local lockfile.**
   - Default path: `.beads/plan-locks/<plan-stem>.lock.json`
   - Command:
     - `python3 scripts/plan-lock.py build $TARGET --reviewer review-plan`
   - If the lockfile already exists, this appends a new review pass while preserving prior passes.
   - If the default path would collide with a lockfile for a different source plan, require an explicit `-o` override instead of overwriting.
   - Include the lockfile path in the final summary.

---

## Asking Questions (cross-agent)

This skill runs under multiple agents. Use whichever question-asking mechanism your harness provides. The shape of every question is the same: a clear question, 2–4 labeled options, recommended option first when applicable.

**Per-agent tool mapping:**

| Agent           | Tool to use                                          |
|-----------------|------------------------------------------------------|
| Claude Code     | `AskUserQuestion` (set `multiSelect: true` for NOTE batch) |
| GitHub Copilot  | `ask_user`                                           |
| Codex CLI       | `ask_user` / built-in interactive prompt             |
| Generic / other | Emit a numbered block, wait for reply (see below)    |

**Generic fallback format** (when no structured tool exists):

```
QUESTION [#N]: <question text>
  [a] <option label> — <one-line description>      (recommended)
  [b] <option label> — <one-line description>
  [c] <option label> — <one-line description>
  [d] <option label> — <one-line description>

Reply with the letter of your choice (e.g. "a"), or "a: <notes>" to add context.
```

For batched NOTE questions, the user may reply with multiple letters: `a c d`.

If running in batch mode (no user available), skip the walkthrough entirely, write the full findings report (Phase 5 classification + stats block) to stdout, and exit without modifying `$TARGET`.

---

## Constraints

- Never edit `$TARGET` during Phases 1–6. All edits happen in Phase 7.
- Edits normally touch only `$TARGET`. Exception: for reviewed markdown plans, this skill may also create or update the repo-local `.beads/plan-locks/*.lock.json` companion artifact.
- If `$TARGET_TYPE` is markdown with `Task spec`, do **not** skip structural findings about keys, deps, skills, logging, or verification. Those are first-class review targets.
- If `$TARGET_TYPE` is markdown without `Task spec`, fall back to prose review but keep the missing-structure finding alive through the walkthrough.
- Do not commit changes. Ever. The user commits.
- Load `references/review-checklist.md` only when you need detail on specific heuristics — don't load it upfront.
- The walkthrough is the skill. If you find yourself emitting a report and stopping, you've failed the contract — re-enter Phase 6.
- Codebase verification is non-negotiable. If you emit findings without having opened source files to verify the plan's claims, you've failed the contract — re-enter Phase 2. "The plan is internally consistent" is not a review.
