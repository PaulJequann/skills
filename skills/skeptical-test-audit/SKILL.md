---
name: skeptical-test-audit
description: Review added or changed automated tests for whether they catch concrete realistic regressions. Use when a user asks to audit, evaluate, prune, review, or improve tests for a task, issue, branch, pull request, or diff. Inspect the production change and existing coverage, then report Keep, Improve, or Remove for every test without editing tests unless asked.
---

# Skeptical Test Audit

Audit tests by the defect they would detect, not by coverage, passing status, or the number of assertions.

## Gather evidence first

1. Read the task or issue acceptance criteria, the production diff, and all added or changed tests.
2. Inspect the relevant production behavior and nearby existing tests. Establish whether the named behavior actually reaches the asserted result; do not trust test names.
3. Check fixtures against production constraints such as dates, authorization, precedence, serialization, retries, and real adapter semantics.
4. Do not modify, delete, quarantine, or add tests during a review unless the user explicitly asks for changes.

## Judge each test

For every changed test, report:

| Test | Behavior / contract proved | Plausible defect caught | Verdict | Evidence and recommendation |
| --- | --- | --- | --- | --- |

Use these verdicts:

- **Keep** — fails for a concrete, plausible regression and asserts the right observable outcome.
- **Improve** — targets a worthwhile behavior but has a weak oracle, unrepresentative fixture, brittle boundary, misleading name, unnecessary coupling, or incomplete failure case. Give the smallest specific repair.
- **Remove** — high-confidence tautology, duplicate, construction/property echo, framework/config wiring check without an application contract, fake-owned test, or coverage-only test. State the existing evidence that makes it safe to remove.

For a retained test, explicitly finish this statement:

> It would fail if `<incorrect implementation>` caused `<harmful result>` for `<caller or user>`.

## Defaults and exceptions

- Prefer outcomes through the narrowest stable contract. A public user API is often right, but direct domain-function tests are valid when that function is the stable contract.
- Flag assertions of private state or incidental implementation details when a refactor could preserve behavior but break the test.
- Flag mock-call assertions that merely mirror internal wiring. Keep them when the absence, presence, order, or payload of an external interaction is a security, cost, audit, delivery, or compatibility contract.
- Flag fixed sleeps, uncontrolled clocks, broad snapshots, vague names, assertion roulette, and multi-behavior tests. Do not condemn a multi-step test that proves one real workflow.
- Treat endpoint/framework smoke coverage and visual snapshots as specialized tests. Keep only when they name and prove the integration, compatibility, or visual contract that justifies their maintenance cost.
- Do not equate a green integration test with coverage of its claimed behavior. Validate that its fixture forces the production decision under test.

## Finish with a decision summary

Report counts for Keep, Improve, and Remove, then list:

- the highest-risk unproven behavior;
- the smallest changes that would make the suite trustworthy;
- any proposed removal that needs user approval before deletion.

Do not recommend new dependencies or broad coverage targets merely to score the suite. Suggest focused mutation or fault-injection experiments only when they would resolve a specific uncertainty about a critical behavior.
