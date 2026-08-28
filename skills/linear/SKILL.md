---
name: linear
description: Use whenever a task involves Linear issues, documents, planning, investigation, readiness, relationships, or completion. Route the request to the appropriate read or write workflow while keeping issue bodies current and comments as history.
---

# Linear

Handle Linear work through one entrypoint. Read repository instructions first,
resolve the current repository from its Git remote, and use its configured team
and exact `Repository/<Repository>` label. Use `setup-linear-workflow` when the
routing itself must be created or repaired.

## Canonical record

The issue body is the canonical current handoff. Keep it accurate, concise, and
usable without reconstructing truth from comments.

Comments are a dated activity log. After research or a material rewrite, add a
short sign-off stating what happened, when it happened, the resulting readiness,
and that the body was updated. Put durable findings, decisions, acceptance
criteria, test expectations, and exclusions in the body rather than repeating
them in the comment.

Linked documents hold long-form rationale, specs, ADRs, and runbooks. They may
support an issue body but do not replace the implementation contract needed by
the next agent.

## Route the request

- **Read or select work:** retrieve the named issue or document, summarize a
  requested queue, or select the next actionable issue. Read the body first,
  then labels and relationships. Read comments or linked documents when the
  task needs provenance, unresolved discussion, or supplementary detail.
- **Capture new work:** read
  [references/issue-body.md](references/issue-body.md) and follow **Capture**.
- **Investigate or refine an issue:** read
  [references/investigation.md](references/investigation.md) and follow
  **Investigate**.
- **Publish or update a document:** follow **Documents** below.
- **Decompose oversized work:** read
  [references/decomposition.md](references/decomposition.md) only after clear,
  confirmed work exceeds one fresh agent context window.
- **Record implementation progress or completion:** update the body first so it
  reflects the remaining work or completed result, add a short activity comment,
  update only the fields the request authorizes, and read the issue back.

## Write authority

An explicit request to create, update, publish, transition, or close a Linear
record authorizes that named mutation. A request to inspect, investigate,
review, summarize, or draft is read-only in Linear until the user approves the
proposed write.

New decomposition granularity and blocker edges always require explicit
approval before creating children or relationships. Closing, canceling,
marking duplicate, changing priority, assigning, or adding a project or cycle
also requires explicit authority.

For an agent-discovered issue, create without another confirmation only when it
is a distinct, evidenced defect outside the current task, remains useful if the
branch changes, has no likely duplicate, contains no sensitive data, and
routing is already configured. Create it as `Backlog` with
`Readiness/Needs investigation`, leave priority unset, report it, and continue
the original task. Otherwise recommend capture without writing.

## Capture

1. Search open issues in the configured team and repository by domain concepts,
   symptoms, and affected behavior.
2. If a likely duplicate exists, return it and explain the overlap. Add evidence
   only when that update is authorized.
3. Draft the body from the issue-body reference. Separate facts, hypotheses,
   unknowns, and decisions. Redact secrets and sensitive payloads.
4. Create one issue when the outcome is independently verifiable and fits one
   fresh agent context window. For larger clear work, propose decomposition and
   wait for approval.
5. Default to `Backlog`, the exact repository label, unset priority, and one
   readiness label matching the evidence.
6. Re-read every created record and verify its title, body, status, labels, and
   relationships. Report partial writes rather than creating replacements.

## Readiness

- `Needs investigation`: evidence, cause, behavior, scope, or testing path is
  materially uncertain. The body states the exact next evidence needed.
- `Needs decision`: the work is understood but a human product, architecture,
  security, privacy, compatibility, or scope decision remains. The body states
  the exact options and consequences.
- `Ready for implementation`: the body itself contains verified current and
  desired behavior, durable scope, independently testable acceptance criteria,
  relevant failure behavior, exclusions, and no unresolved decision.

Priority is independent from readiness. An oversized parent that indexes ready
children stays in `Backlog` with no readiness label and unset priority.

## Documents

Read a document only when the user names, links, or asks to find it. Resolve an
ID or slug directly, or search narrowly by title and metadata. When several
documents match, ask the user to choose. A read never edits, reparents, archives,
or subscribes.

Publish or update only when explicitly requested. Resolve exactly one parent:

- issue for ticket-specific plans, investigations, or decisions;
- project for a bounded initiative's shared material;
- team for cross-project ADRs, runbooks, or enduring context;
- initiative or cycle only when the artifact belongs there.

For a new document, search narrowly for a same-parent/title duplicate. For an
update, require the target ID, slug, or URL. Save the Markdown, then re-read and
verify the title, parent, content, and URL. Use issue attachments for binary
artifacts.

## Verification and report

After every write, re-read the affected records and verify all changed fields
and relationships. Never claim a write succeeded from the mutation response
alone.

Report the record identifiers and links, the outcome and readiness, what
changed, any approval still pending, and any partial or unverified result.
