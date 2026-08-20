---
name: investigate-linear-issue
description: Investigate a Linear issue against the current codebase, document evidence, assess whether confirmed work needs approval-gated vertical slices, and update its readiness without implementing the fix. Use when the user says to investigate, verify, confirm, reproduce, or take a look at a Linear issue, asks for issues needing investigation, or asks an agent to select and investigate one such issue.
---

# Investigate Linear Issue

Treat investigation as diagnosis and issue preparation, not implementation.
Read [references/investigation-report.md](references/investigation-report.md)
before posting findings.

## Resolve the target

For a named issue:

1. Read its complete body, comments, labels, relationships, linked or child
   Linear documents, and current status.
2. Resolve its repository label and compare it with the current Git remote.
3. Stop and report the mismatch rather than investigating the wrong repository.

When the user asks for a queue summary, list matching issues without changing
them. When the user asks to select and investigate one:

1. Filter open issues by the current repository and
   `Readiness/Needs investigation`.
2. Exclude issues blocked on explicit human decisions or missing access.
3. Prefer explicit Linear priority, then the oldest actionable issue.
4. State the selected identifier and proceed; the request already authorizes
   choosing one.

Do not silently broaden a named investigation to adjacent issues.

## Approval boundary

An investigation request authorizes diagnosis and a draft report, not Linear
writes. By default, keep the investigation read-only in Linear while working.
Present the complete proposed investigation result in the conversation,
including the proposed readiness transition and any proposed decomposition, and
ask the user to approve or revise it.

Only after explicit approval may you post the drafted comment, change the
readiness label, publish child issues, or create relationships. “Investigate
and update Linear,” “persist the findings,” or equivalent explicit instruction
authorizes immediate persistence for a non-decomposition result; still report
exactly what was written. It does not approve a newly proposed vertical
decomposition: the granularity and blocking edges always need explicit approval
before any related Linear write.

## Establish the claim

Use the issue as the starting report, not as proof.

1. Inspect applicable repository instructions and relevant current code.
2. Search by domain concept for an existing implementation, duplicate issue,
   or already-fixed behavior.
3. Reproduce or falsify the report at the highest practical interface.
4. Trace the responsible code path or boundary.
5. Inspect history only when it materially helps explain the behavior.
6. Run focused diagnostic commands or tests as needed.
7. For behavior that depends on an external provider, verify the provider's
   current official documentation before declaring a testing path unavailable
   or requiring a hosted environment. Record the provider-backed path and its
   limits separately from application-owned fakes.
8. Record what was tried, the actual result, and remaining uncertainty.

Label unbenchmarked performance explanations and otherwise unverified causes as
plausible, not proven.

Do not edit product code, implement a fix, create a feature branch, or refactor
while investigating. Diagnostic artifacts must remain untracked or be removed
before reporting.

## Assess implementation shape

When the claim is confirmed and the desired behavior is sufficiently understood,
assess whether its implementation has one independently verifiable outcome that
fits in a single fresh agent context window. This assessment may already have
been completed during capture; retain and validate that earlier conclusion
rather than repeating it mechanically.

An established enhancement or accepted architecture decision may satisfy this
condition even when there is no reproducible defect. It still needs clear
current and desired behavior, decisions, scope, and independently verifiable
acceptance criteria.

- If it fits, continue with the ordinary readiness assessment.
- If it does not fit, read and follow the shared
  [decomposition protocol](../linear-issue-workflow/references/decomposition.md)
  before marking the issue `Ready for implementation`.

## Choose one readiness outcome

### Ready for implementation

Propose `Readiness/Ready for implementation` only when all are true:

- the claim is confirmed or the desired enhancement is established;
- current and desired behavior are clear;
- relevant edge cases and failure behavior are understood;
- acceptance criteria are independently verifiable;
- scope boundaries are explicit; and
- no product, architecture, security, privacy, or scope decision remains.

For behaviorally significant work, the brief also includes a test-evidence
matrix. Map each important behavior to its public interface, test level,
allowed test double (if any), focused harness or command, and expected
evidence. Do not use a private state-machine test as the primary proof when
the behavior is owned by a higher-level interface.

Draft an authoritative implementation brief with the investigation result.

### Needs decision

Propose `Readiness/Needs decision` when the issue is sufficiently understood but
a human decision blocks implementation. State one or more exact decisions,
their material options, and the consequence of each. Do not choose for the
user. Approval of a proposed vertical-slice breakdown is one such decision.

### Needs investigation

Propose retaining or applying `Readiness/Needs investigation` when the claim cannot be
reproduced, evidence is insufficient, the likely cause remains materially
uncertain, or more access or data is needed. State the next evidence that would
resolve the uncertainty.

### Duplicate, already fixed, or invalid

Draft the evidence and identify the likely duplicate or existing behavior. Ask
before closing, canceling, or otherwise disposing of the issue unless the user
explicitly granted that authority.

## Write durable findings

Use the investigation report template. Present its complete draft in the
conversation before posting it unless immediate persistence was explicitly
authorized.

Keep evidence precise, including current paths and commands when useful.
However, make the authoritative implementation brief durable:

- describe behavioral contracts and stable interfaces;
- avoid line numbers;
- avoid prescribing file-by-file edits;
- avoid depending on the current directory structure; and
- state independently testable acceptance criteria and explicit exclusions.

The newest comment headed `## Authoritative implementation brief` is the
implementation contract. Earlier issue text and discussion remain context.

When the user explicitly requests a long-form design, ADR, or testing rationale,
use `$linear-documents` after posting the authoritative comment. The document
is supplementary context: link it from the brief, but keep the durable behavior,
acceptance criteria, and test-evidence matrix in the comment so a fresh
implementer has one executable contract.

## Persist approved findings

Unless the user requested a read-only investigation or explicitly authorized
immediate persistence for a result without a new decomposition:

1. Present the complete investigation-result draft, proposed readiness, and—if
   applicable—numbered vertical-slice proposal in the conversation.
2. Ask for approval to persist the result and, where applicable, approve or
   revise the slice granularity and blocking edges.
3. Stop without changing Linear until the user responds.

After approval, or when the user explicitly authorized immediate persistence
for a result without a new decomposition:

1. Post the accepted investigation result as one concise comment.
2. Replace the readiness label with the accepted outcome.
3. If an approved decomposition exists, follow the shared decomposition
   protocol to publish the parent, children, and relationships in the same
   approved batch.
4. Re-read the issue and every created record to verify the comment, label,
   titles, bodies, and relationships.

Do not change status, priority, assignee, project, cycle, or close the issue.
Do not mark it `In Progress`; investigation readiness is represented by the
readiness label.

If Linear MCP is unavailable, return the completed report and clearly state
that it was not persisted. Never claim the issue was updated without
verification.

## Report

Return:

- issue identifier;
- outcome and confidence;
- concise root cause or verified finding;
- proposed or persisted readiness transition;
- unresolved decision or next evidence, if any; and
- whether Linear was changed or approval is pending;
- confirmation that no implementation was performed.
