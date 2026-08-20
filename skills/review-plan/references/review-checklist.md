# Review Checklist — Detailed Heuristics

Reference material for the review-plan skill. Load sections as needed during analysis.

---

## Implementation Plan Structure

Use these checks during the markdown structure gate.

### Required Top-level Sections

Flag a markdown implementation plan when any of these are missing:

- `## Plan spec` (declares the umbrella epic — see below)
- `## Purpose`
- `## Research inputs`
- `## Locked decisions`
- `## Scope`
- `## Cross-cutting constraints`
- `## Implementation slices`
- `## Suggested task order`
- `## Deliverables`
- `## Review checkpoint`

### Umbrella Epic (Plan spec)

Every implementation plan must declare a single umbrella epic that wraps the entire plan. This lets agents target the whole plan with one bead reference and prevents plan beads from scattering into the open backlog as loose siblings.

The `## Plan spec` section is a YAML block immediately after the H1, parallel to slice-level `Task spec`:

```yaml
plan_key: <snake_case_plan_key>     # required, stable across rewrites
plan_title: <human-readable title>  # optional, falls back to the H1
```

Findings:

- **CRITICAL** — `## Plan spec` missing entirely. Plan has no umbrella; extraction would produce loose top-level slices.
- **CRITICAL** — `plan_key` missing or not snake_case.
- **WARNING** — `plan_key` collides with a slice key in the same plan.

For JSON plans, the equivalent check is: exactly one parent-less item, and it must be `type: epic`. Multiple parent-less items → CRITICAL. Non-epic root → WARNING.

### Required Slice Shape

Inside `## Implementation slices`, each slice should have:

1. A numbered `###` heading
2. A short framing paragraph
3. `Key work`
4. `Acceptance`
5. `#### Task spec`

Flag slices that rely only on prose bullets with no `Task spec` as WARNING-level structural findings. They may be reviewable as prose, but they fail the extraction contract.

### Required Task-spec Fields

At the slice level, expect:

- `slice_key`
- `blockedBy`
- `beads`

At the leaf-bead level, expect:

- `key`
- `title`
- `type`
- `blockedBy`
- `files`
- `verification`
- `skills`
- `logging`
- `done_when`

Flag missing task-spec fields as:

- **CRITICAL** when they prevent dependency analysis or extraction (`key`, `blockedBy`, `files`)
- **WARNING** when they materially reduce agent reliability (`verification`, `skills`, `logging`, `done_when`)

### Ambiguous Wording

Flag these phrases when they appear inside `Task spec` blocks:

- `if needed`
- `or equivalent`
- `as warranted`
- `where practical`
- `etc.`
- `update as necessary`

Suggested fix: turn the ambiguity into an explicit decision, a separate follow-up task, or an open question in prose outside the task spec.

### Logging Expectations

When a leaf task changes a service operation, request boundary, or long-running background job:

- `logging` should be the **structured object form** (`operation`, `outcomes`, `append_fields`, `boundary`, optional `notes`) — not just `true`
- `skills` should include `/logging-best-practices`
- downstream JSON descriptions will carry a real `Logging:` section rendered from the object

Findings:

- **WARNING** — `logging: true` (placeholder) on a service-layer bead. Upgrade to the object form so the detail is durable across re-extractions.
- **WARNING** — object-form `logging` with only `success` / `failure` outcomes. Enumerate distinct outcomes including rejection paths.
- **WARNING** — `logging` is the object form but `skills` lacks `/logging-best-practices`.

---

## Codebase Checks

### File Existence Patterns

When a task description mentions files or modules, verify they exist (or that an upstream task creates them).

**TypeScript / JavaScript:**

- `src/` is the typical source root. Check `src/<module>/` for module dirs.
- Named exports: Grep for `export (function|const|class) <name>`.
- Route handlers: Grep for the HTTP method + path pattern (e.g., `router.post.*'/auth/signup'`).
- Database tables: Check migration files in `migrations/`, `drizzle/`, `prisma/schema.prisma`, or `supabase/migrations/`.

**Rust:**

- Module dirs match `src/<name>/mod.rs` or `src/<name>.rs`.
- Crate-level exports in `src/lib.rs`.
- Workspace members in root `Cargo.toml`.

**Go:**

- Package dirs under project root or `internal/`, `pkg/`, `cmd/`.
- Check `go.mod` for module path.

**Python:**

- Package dirs with `__init__.py` or `pyproject.toml` `[tool.setuptools.packages]`.
- Check `src/` or root-level package dirs.

**General:**

- Config files: `.env`, `config/`, settings files.
- Database: migration directories, schema files.
- API specs: `openapi.yaml`, `swagger.json`, GraphQL schema files.

### Collision Detection Heuristics

Build a map: `filepath → [task_keys]`. Flag collisions when:

1. **Same file, no dependency** — Two tasks both mention modifying `src/db/schema.ts` but neither blocks the other. Risk: merge conflicts, lost work.
2. **Same module, different files** — Two tasks modify different files in the same module dir (e.g., `src/auth/login.ts` and `src/auth/session.ts`). Lower risk but worth noting if no dep exists.
3. **Schema + migration** — One task modifies the schema definition, another creates a migration. These must be ordered.
4. **Config files** — `.env`, `docker-compose.yml`, `package.json` — these are frequent collision points. Flag if 2+ tasks modify them.
5. **Test files** — Less risky (additive), but flag if two tasks modify the same test file.

### Boundary Alignment

Count distinct modules a task touches. Module = top-level directory under `src/` (or equivalent).

- **1 module**: Good. Focused task.
- **2 modules**: Acceptable if they're closely related (e.g., `api` + `db`).
- **3+ modules**: Flag as WARNING — likely too broad. Suggest splitting by module boundary.

Exception: tasks that are explicitly cross-cutting (e.g., "add logging to all endpoints") can span many modules intentionally. Check if the task description acknowledges this.

---

## Dependency Analysis

### Common Implicit Dependency Patterns

These patterns indicate task A should block task B even if no dep is declared:

| A creates | B uses | Signal |
| --- | --- | --- |
| Type/interface definition | Import of that type | Grep for `type <Name>` or `interface <Name>` in A's files, import in B's |
| Database migration | Query against new table/column | Migration file in A, query referencing table in B |
| Config/env variable | `process.env.VAR` or equivalent | `.env` addition in A, env read in B |
| API endpoint | Fetch/call to that endpoint | Route definition in A, HTTP call in B |
| Package dependency | Import from that package | `package.json` change in A, import in B |
| Shared utility function | Call to that function | Function definition in A, call in B |

### Over-serialization Detection

A dependency is over-serialized when:

- Task A blocks task B
- A and B mention NO overlapping files or modules
- A and B create/use NO overlapping types, tables, or configs
- Removing the dep wouldn't cause any ordering issue

Flag as NOTE with suggestion to remove the dep for parallel execution.

### Critical Path Analysis

1. Build the directed acyclic graph from `blockedBy` relationships.
2. Find the longest path (most edges) — this is the critical path.
3. Report: chain length, task keys in order, total estimated effort along the chain.
4. Flag bottleneck tasks: any task where removing it would reduce the critical path length by 2+.

---

## Granularity Thresholds

### Too Big (WARNING)

Flag a leaf task if ANY of these apply:

- Description mentions 5+ distinct files
- Description is over 500 words
- Task title contains "and" joining two distinct concepts (e.g., "Create schema and write migrations and seed data")
- Task spans 3+ modules (see Boundary Alignment above)

Suggested fix: split along natural boundaries (file groups, module boundaries, or the "and" in the title).

### Too Small (NOTE)

Flag a leaf task if ALL of these apply:

- Description is under 20 words or absent
- Task is purely mechanical (rename, update import path, change a constant)
- An adjacent sibling task touches the same file

Suggested fix: fold into the adjacent task.

### Missing Tasks

Check against these common gaps:

- **Auth plans**: login but no logout, no session expiry, no password validation rules
- **API plans**: endpoints but no error handling strategy, no rate limiting, no auth middleware
- **Database plans**: schema but no migrations, no seed data, no indexes
- **Frontend plans**: components but no loading states, no error states, no responsive design
- **Testing**: implementation tasks but no corresponding test tasks
- **Config/setup**: feature code but no env vars, no config files, no deployment changes

### Description Quality

Good descriptions include:

- Specific file paths or module names
- What will be created, modified, or deleted
- Acceptance criteria or expected behavior
- Dependencies on external systems or APIs
- Verification surface when the task is part of a structured implementation-plan workflow

Flag descriptions that are:

- Empty or just the title restated
- Vague ("implement the feature", "set up the thing")
- Missing file/module references (for non-epic items)
- Missing verification or completion criteria when the surrounding plan uses `Task spec`

### Code-shape Alignment

Flag as WARNING when a task spec or description:

- introduces a new helper, manager, service, shared type, or DTO "for reuse" without naming multiple real consumers or a volatile external boundary
- widens a shared interface when the behavior could stay in an implementation module
- spreads one behavior across generic catch-all surfaces such as `utils`, `helpers`, `common`, `manager`, or `misc` without an established repo pattern
- adds a new layer of indirection with no clear coupling, volatility, or boundary-isolation reason

Fix: keep the interface narrow, extend an existing cohesive module, and keep orchestration thin unless multiple callers genuinely need the shared seam.

### Verification Posture

Flag as WARNING when a task spec or description:

- creates a new dedicated test file without showing why an existing proof surface is insufficient
- uses one test file per sibling bead in the same implementation module
- proposes unit tests for pure wiring, registration, copy, styling, or schema-only work where a smoke check or existing suite would be enough

Fix: reuse the cheapest existing executable proof surface that would fail if the bead were wrong.

---

## Skill Heuristics

When a leaf task lacks a `skills` field, use content patterns to suggest likely skills.
Project-specific routing (e.g., AGENTS.md §1) takes precedence when available.

### Pattern Matching

| Pattern (case-insensitive) | Suggested Skill | Confidence |
| --- | --- | --- |
| migration, schema, table, column, index, RLS, policy, SQL, query, database | /supabase-postgres-best-practices | high |
| UI, UX, component, layout, responsive, accessibility, design, frontend, CSS, tailwind | /frontend-design | high |
| test, spec, TDD, coverage, assertion, fixture | /tdd | medium |
| log, logging, observability, trace, metric, wide event | /logging-best-practices | medium |

### Rules

1. Match patterns against title + description. Flag as NOTE:
   `[NOTE] [key] Leaf task may benefit from: /skill-name (matched: "term"). Add "skills": ["/skill-name"].`
2. Multiple matches → suggest all.
3. Skip epics — skills are only for leaf tasks.
4. **high** confidence: always flag. **medium**: flag only if 2+ terms match or title matches directly.
