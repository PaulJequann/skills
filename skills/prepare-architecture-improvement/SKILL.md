---
name: prepare-architecture-improvement
description: Prepare one architecture candidate for implementation readiness.
---

# Prepare an architecture improvement

Take one architecture candidate from `Needs investigation` to a verified
readiness outcome. Revalidate its Stashbox report against the current code,
resolve the module and interface design far enough to implement safely, and
persist one authoritative Linear investigation result without editing code.

Invoking this skill authorizes selection of one issue and immediate persistence
of one result that does not introduce a new vertical-slice decomposition. It
does not preapprove unknown child issues, blocker relationships, issue closure,
implementation, a pull request, or deployment.

Finish in exactly one state:

- `Ready`: Linear contains a verified authoritative implementation brief and
  `Readiness/Ready for implementation`.
- `Needs decision`: a precise product, architecture, security, privacy, or scope
  decision blocks implementation and Linear records that result.
- `Needs investigation`: the evidence remains insufficient and Linear records
  the next evidence needed.
- `Approval required`: a new vertical-slice decomposition is proposed but was
  not persisted because its granularity and blockers need human approval.
- `Disposition required`: the candidate is duplicate, fixed, invalid, or
  superseded, but the issue was not closed or canceled.
- `No work`: no eligible architecture candidate exists.
- `Blocked`: repository, Stashbox, or Linear access prevents preparation.

## 1. Select one issue

Use a named issue when provided. Otherwise:

1. Resolve the current repository from its Git remote and exact Linear
   repository label.
2. Find open issues with `Readiness/Needs investigation` whose body contains an
   `Architecture candidate report` Stashbox link.
3. Exclude issues blocked on an explicit human decision, missing access, or an
   approved dependency.
4. Prefer explicit priority, then the oldest actionable issue.

Read the complete issue, comments, labels, relationships, linked documents,
and current status. Confirm its repository label matches the current remote.
Stop on a mismatch rather than investigating the wrong codebase.

Complete this step when one eligible issue is selected and its complete Linear
state is known, or finish with `No work`.

## 2. Recover the discovery evidence

Open the exact Stashbox viewer URL from the issue. Read the candidate report,
including its recorded branch and revision, current and proposed ownership,
caller and test evidence, architecture backtest, counterargument, ADRs, and
open questions.

Treat the report and issue as claims, not proof. Record any disagreement
between them and any missing artifact. A missing or unreadable report is
`Blocked`; do not reconstruct it from a summary and pretend the original
evidence was reviewed.

Complete this step when every material claim in the issue can be traced to the
report or is explicitly marked unsupported.

## 3. Revalidate against the current repository

Keep the repository read-only. Read applicable repository instructions,
`CONTEXT.md` files, ADRs, design documents, current Git status, and the exact
current revision.

Inspect the current implementation, every relevant caller, the highest
practical behavior path, and the tests that cross the current interface. Check
changes since the report revision. Preserve dirty work and exclude uncommitted
changes from the accepted baseline unless the issue explicitly owns them.

Confirm or falsify:

- the observed ownership split and leaked caller knowledge;
- the deletion-test result;
- the historical change-compression claim;
- the expected locality and leverage;
- the proposed test surface;
- dependency and adapter assumptions; and
- continued compatibility with current ADRs and domain language.

Run read-only diagnostics or focused tests when they materially reduce
uncertainty. Leave diagnostic artifacts untracked or remove them before
reporting. Do not edit product code, create a feature branch, or prototype the
implementation.

Complete this step when the candidate is confirmed, falsified, or reduced to
specific unresolved evidence.

## 4. Resolve the architecture contract

For a confirmed candidate, compare at least two materially different interface
or seam placements. Do not compare cosmetic variations. For each alternative,
state:

- behavior and decisions owned by the module;
- everything callers must know;
- dependencies and justified adapters;
- failure and cancellation behavior;
- migration impact on current callers;
- the stable interface through which tests observe behavior; and
- what remains deliberately outside the module.

Choose a preferred direction only when current evidence settles the tradeoff.
Prefer a small interface that absorbs real behavior, preserves domain
ownership, and concentrates verification. Do not add a seam with one real
adapter, preserve a shallow compatibility interface without a stated need, or
move complexity from the implementation into configuration and ordering rules.

Record an exact human decision instead of choosing when alternatives change
product behavior, trust, security, privacy, compatibility, data ownership, or
scope materially.

Complete this step when the preferred architecture contract is evidence-backed
or the remaining decision and its options are explicit.

## 5. Determine readiness and work shape

Load and follow the investigation mode of `linear`, including its canonical
body and readiness rules.

Mark the issue ready only when the current and desired behavior, module
ownership, interface contract, edge and failure behavior, migration scope,
acceptance criteria, exclusions, and test-evidence matrix are all independently
verifiable and no decision remains.

Keep one implementation issue only when it has one coherent outcome that fits
in a single fresh agent context window. When the work needs new vertical slices
or expand-contract batches, follow the decomposition protocol only through the
proposal stage. Finish with `Approval required`; invocation of this skill does
not approve the unknown granularity or blocker graph.

Use `Needs decision` for a non-decomposition decision, `Needs investigation`
for missing evidence, and `Disposition required` for duplicate, fixed, invalid,
or superseded work. Do not close, cancel, or mark an issue duplicate.

Complete this step with exactly one readiness or disposition outcome.

## 6. Persist the result

For `Ready`, `Needs decision`, or `Needs investigation`, rewrite the issue body
as the canonical current handoff, replace the readiness label with the selected
outcome, and add one concise dated investigation sign-off comment. A ready body
must include durable acceptance criteria and the test-evidence matrix. Evidence
may name current paths and revisions; the implementation contract must not
depend on line numbers or a file-by-file edit recipe.

For `Disposition required`, update the body with the verified finding, add the
sign-off comment, and set `Readiness/Needs decision` so disposal remains a human
action.

For `Approval required`, return the complete draft investigation result and
numbered decomposition proposal without changing Linear. Do not publish a
partial comment, readiness transition, child issue, or relationship before the
user approves the granularity and blocker edges.

Re-read every changed Linear record. Verify the canonical body, sign-off
comment, readiness label, issue identity, and unchanged status, priority,
assignee, project, cycle, and relationships.

Complete this step only when the intended Linear result is verified or the
approval-gated proposal is complete and nothing was written.

## 7. Report

Return:

- issue identifier and URL;
- terminal state and confidence;
- current revision and report revision;
- confirmed or falsified architecture finding;
- preferred interface direction or exact decision required;
- persisted readiness transition or approval-gated decomposition;
- next evidence or human action, if any;
- whether Linear changed; and
- confirmation that no product code changed.
