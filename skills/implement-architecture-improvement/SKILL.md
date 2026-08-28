---
name: implement-architecture-improvement
description: Implement one ready architecture improvement and deliver its PR.
---

# Implement an architecture improvement

Select one unblocked architecture issue with
`Readiness/Ready for implementation`, implement its authoritative brief in an
isolated workspace, file one ready pull request, and babysit current-head CI and
automated review. Never merge or deploy.

Invoking this skill authorizes normal work required for one implementation:
selecting the issue, creating an isolated branch or worktree, editing code and
tests, committing, pushing, filing one ready PR, performing bounded routine
review remediation, correcting the selected issue's readiness when current
evidence makes implementation unsafe, and linking the verified PR from Linear.
It does not authorize merge, deployment, branch deletion, issue closure,
unapproved child issues, or unrelated cleanup.

Finish in exactly one state:

- `Ready for human approval`: the PR is stable at an exact head with current
  CI and review state reported.
- `Existing PR babysat`: the selected issue already had a PR and no duplicate
  implementation was created.
- `Returned to investigation`: current evidence invalidated readiness before
  implementation began.
- `Needs decision`: implementation exposed a decision outside the authoritative
  brief and no speculative choice was made.
- `No work`: no eligible ready architecture issue exists.
- `Blocked`: access, isolation, verification, or publication prevented safe
  delivery.

## 1. Select one ready issue

Use a named issue when provided. Otherwise:

1. Resolve the current repository from its Git remote and exact Linear
   repository label.
2. Find open issues with `Readiness/Ready for implementation` whose bodies
   contain an `Architecture candidate report` link and a complete current
   implementation contract.
3. Exclude blocked issues, parent index issues, and issues waiting on a human
   decision.
4. Prefer explicit priority, then the oldest unblocked issue. When approved
   child issues exist, select the first unblocked ready child rather than its
   parent.

Read the canonical body first, then relationships, linked documents, the
Stashbox report, and readiness history. Read comments when provenance or
unresolved discussion matters. Find an existing branch or open PR linked to the
issue before creating anything. If one exists, skip implementation and proceed
directly to PR babysitting.

Complete this step with one eligible issue and no duplicate implementation, or
finish with `No work`.

## 2. Revalidate the implementation contract

Read applicable repository instructions, domain documents, ADRs, PR templates,
current Git status, default branch, and remote state. Treat the Linear issue
body as the scope contract. Comments and earlier reports provide history and
rationale but cannot silently expand it.

Verify against the current default-branch head:

- desired behavior and acceptance criteria still apply;
- the stated module owns the behavior;
- callers and dependencies still match the prepared design;
- no newer ADR or change invalidates the seam;
- blockers are complete; and
- every required behavior has a practical verification path.

If drift invalidates readiness, make no product edits. Load and follow the
investigation mode of `linear`, persist the exact next evidence under
`Readiness/Needs investigation`, and finish with `Returned to investigation`.
If a product, architecture, security, privacy, compatibility, or scope decision
remains, persist `Readiness/Needs decision` and finish without implementation.

Complete this step only when the issue remains independently implementable on
the current base.

## 3. Establish isolation and scope

Never edit a shared or dirty checkout. Use the current workspace only when it
is an isolated worktree dedicated to this issue and its existing state is fully
accounted for. Otherwise create a dedicated worktree and feature branch from
the current canonical base using Paseo worktree isolation when available or a
safe Git worktree when it is not.

Name the branch with the Linear identifier and a concise outcome slug. Record
the base SHA. Keep credentials outside the repository and inherit only the
normal repository-approved secret mechanism.

Write the implementation plan in the agent's working context, not in the
repository. Map each acceptance criterion to the module interface, caller
migration, and verification evidence. Keep one coherent outcome and exclude
adjacent cleanup.

Complete this step with a clean isolated workspace, exact base SHA, scoped
branch, and every acceptance criterion mapped.

## 4. Implement the deepening

Implement the authoritative contract as if the intended ownership had been a
foundational assumption. Put behavior and invariants behind the prepared
interface, preserve domain language, and keep dependencies at justified seams.

Migrate all in-scope callers in the same change. Delete replaced shallow
interfaces and obsolete tests rather than preserving compatibility layers that
the brief does not require. Keep internal seams private. Require two justified
adapters before retaining an adapter seam.

At each meaningful checkpoint, inspect the full diff and callers. Stop for
`Needs decision` when implementation reveals a material contract choice. Do
not choose a broader redesign merely because it looks attractive while editing.

Complete this step when every scoped caller uses the prepared interface, old
paths are removed where authorized, and the diff contains no unrelated work.

## 5. Design and run verification

Immediately before adding or changing automated tests, load and follow
`purposeful-test-design`. Record its test-intent ledger in the run output. Add
only tests that detect a named harmful behavioral regression.

Test through the deepened module's interface. Replace obsolete shallow-module
tests once the new interface-level evidence exists. Use real local substitutes
for persistence or filesystem behavior, an in-memory adapter for owned remote
seams, and mocks only for true external providers.

Run, in order:

1. focused tests for the changed behavior and failure paths;
2. static, type, lint, or architecture checks relevant to the changed seam;
3. repository-required final verification; and
4. any acceptance command named in the authoritative brief.

Classify every failure. Fix in-scope regressions, distinguish confirmed
baseline or infrastructure failures, and stop when a required acceptance
criterion cannot be proven. Do not turn unavailable evidence into a pass.

Complete this step when every acceptance criterion has exact evidence and all
material verification gaps are resolved or explicitly blocking delivery.

## 6. Audit the final change

Re-read the authoritative brief, repository instructions, changed files,
base-to-head diff, caller search, and test-intent ledger. Confirm:

- every acceptance criterion is satisfied;
- the interface is smaller in caller knowledge, not only in line count;
- the historical change-compression claim still holds for the implemented
  shape;
- no compatibility shim or speculative abstraction escaped the scope;
- removed interfaces have no remaining callers or configuration references;
- working-tree changes all belong to the selected issue; and
- verification ran on the final diff.

Complete this step only when the final diff is one reviewable architecture
outcome.

## 7. File the PR

Load and follow `file-pr`. Create one ready PR from the isolated branch. The PR
must link the Linear issue and Stashbox architecture report, explain the change
in module, interface, locality, and testability terms, identify the riskiest
seams, list exact verification, and state important exclusions.

After GitHub readback verifies the PR, post one concise Linear comment with the
PR URL and exact head SHA, then set the issue status to `In Progress`. Preserve
its `Readiness/Ready for implementation` label. Re-read the issue and verify the
comment, status, and unchanged scope metadata.

If an existing PR was found, do not create another or rewrite its metadata
unless routine remediation changes its outcome or verification.

Complete this step when one verified ready PR exists and Linear points to its
exact head.

## 8. Babysit the PR

Load and follow `babysit-pr` immediately after filing or resolving the existing
PR. Use its default bounded review budget, configured reviewer, exact-head CI
checks, review-thread inspection, and routine remediation rules.

Keep changes inside the authoritative brief. Do not create additional Linear
issues during this workflow; report valid out-of-scope findings in the final
handoff. Stop for semantic conflicts, decision-heavy review findings,
release-blocking out-of-scope defects, unavailable credentials, or a repeated
non-progressing loop.

Do not merge, deploy, delete the branch, or mark the Linear issue done. A final
head may be intentionally unre-reviewed after the allowed remediation cycle;
state that explicitly.

Complete this step only at the babysitting finish line or a genuine decision
or access blocker.

## 9. Report

Return:

- Linear issue identifier and URL;
- PR URL, base, branch, and exact head SHA;
- terminal state;
- implemented module and interface outcome;
- acceptance and verification evidence;
- CI and review-cycle state for the exact head;
- remediation and remaining findings;
- any intentionally unre-reviewed final head;
- workspace and branch cleanup still pending; and
- the single next human action.
