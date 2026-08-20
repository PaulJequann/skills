---
name: capture-linear-issue
description: Capture consistent, evidence-backed issues in Linear while keeping issue history out of the repository. Use when the user asks to create, file, capture, or save an issue for later, including approval-gated vertical slices for clear oversized work, or when an agent discovers credible work outside the current task that may qualify for narrowly permitted autonomous capture.
---

# Capture Linear Issue

Create durable Linear issues without turning every observation into backlog
noise. Read [references/issue-template.md](references/issue-template.md) before
drafting an issue.

## Existing issue boundary

This skill creates new issues. Do not use it to refine, validate, or make an
existing issue implementation-ready.

When the work already has a Linear issue and the request is to establish its
behavior, scope, testing contract, or readiness, use
`investigate-linear-issue`. A user may explicitly ask to add evidence to an
existing duplicate; obtain the authority required by the duplicate workflow,
but do not treat that as capture.

## Resolve routing

1. Read applicable repository instructions.
2. Resolve the current repository from its Git remote.
3. Use the configured Linear team, normally `DEV`.
4. Find the exact `Repository/<Repository>` label in Linear.

Do not guess between teams or labels. Do not create routing configuration as a
side effect of capture. If routing is missing:

- for an explicitly requested capture, ask the user whether to run
  `setup-linear-workflow`;
- for an agent-discovered candidate, recommend capture and continue the
  original task without creating it.

## Decide authority

### Create without another confirmation

When the user explicitly asks to create or capture the issue, treat that request
as authorization to create one appropriately sized issue, or to propose a
vertical-slice breakdown when required. Search for duplicates before publishing.

### Permit narrow autonomous capture

Create an agent-discovered issue without prior approval only when every
condition holds:

- it is clearly outside the current task;
- it is a distinct defect or missing invariant, not a preference;
- concrete evidence supports the observation;
- it is useful even if the current branch changes;
- no likely duplicate exists;
- the body can be written without secrets, credentials, personal data, or
  other sensitive material;
- capture will not interrupt or redirect the current task; and
- repository routing is already configured.

Create it in `Backlog` with `Readiness/Needs investigation`, leave priority
unset, report the new identifier, and continue the original task.

### Ask before creating

Recommend an issue and wait when the concern:

- is architectural, subjective, or product-directional;
- changes security, privacy, permissions, retention, or trust boundaries;
- may be a major feature or broad refactor whose desired outcome or scope is
  not yet established;
- has incomplete or ambiguous evidence;
- substantially overlaps the current task; or
- requires choosing scope rather than recording an observed problem.

### Do not create

Only mention the observation in the task report when it is weak speculation,
minor cleanup, a generic improvement idea, already tracked, likely to disappear
after the current change, or too vague to investigate meaningfully.

## Assess work shape

For an explicitly requested capture whose behavior and scope are already clear,
decide whether the work has one independently verifiable outcome that fits in a
single fresh agent context window.

- If it does, capture one issue normally.
- If it does not, read and follow the shared
  [decomposition protocol](../linear-issue-workflow/references/decomposition.md)
  before creating anything.

## Search for duplicates

Search open issues in the configured team and repository label using the
problem's domain concepts, symptoms, and affected behavior rather than only the
proposed title.

If a likely duplicate exists:

- do not create another issue;
- return the candidate and explain the overlap; and
- ask before adding new evidence to the existing issue unless the user already
  requested that update.

## Draft the issue

Follow the issue template exactly, omitting only fields that are genuinely
inapplicable. Separate observed facts from hypotheses.

Include:

- reproducible evidence and relevant commands or errors;
- current file or component locations when they help reproduce the observation;
- the expected invariant or investigation question;
- repository, branch, revision, parent issue, and reporter when available; and
- explicit unknowns and scope boundaries.

Never paste secrets or sensitive payloads. Redact values and describe their
shape or effect instead.

Use a concise problem statement for the title. Do not put readiness, priority,
repository, or issue type prefixes in the title.

## Set issue properties

Unless the user specifies otherwise:

- Team: configured team
- Status: `Backlog`
- Repository: exact configured repository label
- Readiness:
  - `Needs investigation` for unverified or autonomous reports
  - `Needs decision` only when current evidence establishes the issue and the
    unresolved human decision is explicit
  - `Ready for implementation` only when the issue is already verified,
    behavior and scope are clear, acceptance criteria are testable, and no
    decision remains
- Priority: unset

Do not infer urgency from uncertainty. Do not create projects, cycles,
sub-issues, or relationships unless the user explicitly requests them.

## Create and verify

Create a single issue through Linear MCP. For an approved decomposition, follow
the shared [decomposition protocol](../linear-issue-workflow/references/decomposition.md).
Then re-read every created issue to verify its title, body, status, and labels.
If creation succeeds but a property update fails, report the partial result and
the exact missing property; do not create a replacement.

Return the issue identifier and link, its readiness, and whether the original
task continued. Never claim capture succeeded without a confirmed Linear issue.

## After verified capture: long-form artifacts

Keep the issue body focused on the problem, evidence, scope, and readiness.

When the user explicitly asks to preserve an implementation plan, spec, ADR,
investigation brief, or other long-form artifact, use `$linear-documents` to
publish it with the verified issue as its parent. Report the document URL with
the issue result.

Do not create a Linear document merely because an issue body is long. Never
create one during autonomous issue capture: a durable document is an additional
external write and requires explicit authorization.
