---
name: skeptical-test-audit
description: Skeptically audit automated tests by the regression each one catches. Use when reviewing tests for a change, or when pruning a suite that feels bloated, ceremonial, or overtested.
---

# Skeptical Test Audit

Judge each test by the defect it catches, not by coverage, passing status, or assertion count. The burden of proof is on keeping: a test must earn Keep, the harsher verdict wins a tie, and tests written in this session get no benefit of the doubt.

## 1. Gather evidence

1. Read the acceptance criteria, the production diff, and every test in scope: the change's added or changed tests, or the suite the user names, plus changed shared fixtures, fakes, and helpers.
2. Trace the production behavior and nearby existing tests until you can say whether each test's named behavior actually reaches its assertion.
3. When a test claims to guard a specific protection, such as a recheck, lock, cancellation mask, filter, or cleanup, mutate it: remove the protection in a scratch copy or stash, confirm the test fails, then restore and verify the restore. Every "would fail" claim rests on a failure you observed.

## 2. Judge each test

Done when every test in scope, counted as one test function or case, has a row:

| Test | Contract proved | Fails only if | Verdict | Evidence and recommendation |
| --- | --- | --- | --- | --- |

- **Test**: the verbatim test name.
- **Fails only if**: `<incorrect implementation>` → `<harmful result>` for `<caller or user>`, naming a defect that no sibling or existing test also catches.
- **Verdict**: the bare word.

Verdicts:

- **Keep**: earned a unique Fails-only-if, asserts the right observable outcome, and needs no edit, not even a cosmetic one.
- **Improve**: worthwhile behavior with a weak oracle, unrepresentative fixture, brittle boundary, misleading name, unnecessary coupling, or incomplete failure case. Give the smallest repair to the existing test.
- **Merge**: its defect is caught by siblings. Name the surviving test or table-driven replacement and confirm it covers every merged input case.
- **Remove**: catches no plausible defect; see What to flag. State the evidence, naming the surviving test for a duplicate. Tests the diff already deletes are "Remove (already applied)".

## 3. Find gaps

List each new branch, toggle, filter, and acceptance criterion in the production change, including how it combines with existing logic such as indexing, pagination, or ordering. Map each to the test that proves it; the unmapped ones are gaps.

## 4. Apply changes

Only when the user asks you to prune, fix, or apply; otherwise leave every test untouched.

1. Finish the verdict table first.
2. Edit only audited tests: apply Remove and Merge, make the stated repair for each Improve, and strip fixture fields and fake hooks nothing uses.
3. Assert against real output: run the code and copy the actual message or value. Report any loosened assertion as a weakening.
4. Mark applied verdicts, such as "Merge (applied)".

## 5. Summarize

Deliver the table and this summary in your reply: counts for Keep, Improve, Merge, and Remove, the before/after test count, then:

- the highest-risk gap;
- the smallest changes that make the suite trustworthy, strengthening or merging existing tests, with a new test proposed only for the highest-risk gap;
- any removal awaiting user approval.

## What to flag

- **Tautologies and echoes**: tests that restate construction, property values, or the fake's own behavior, and coverage-only tests.
- **Change detectors**: tests that read source, config, or template text and assert substrings, or restate declared literals. They fail on every intentional edit and on no defect; frequent co-change with the file under test is supporting evidence.
- **Removed-behavior guards**: tests or assertions whose only job is proving a deleted feature stays deleted. They fail only when someone deliberately reintroduces the feature, and are edited along with that design change. When a feature is removed, delete its assertions and fixture fields outright. An absence check earns Keep only when the absence is a security, privacy, cost, or compatibility contract, such as a secret never logged or a retired endpoint that keeps rejecting calls.
- **Bug-fix regression tests** earn Keep only by covering a behavior gap the other tests leave. A bug that shipped is strong evidence of such a gap; reproducing a bug found during implementation is not.
- **Fixtures** must be realistic and minimal. Cite the producing code before calling a state realistic or impossible; a fixture production cannot produce makes the test Improve even when another test covers the real shape. Every field serves the test's contract. An integration test's fixture must force the production decision under test.
- **Fakes** that add suspension points, failure modes, or timing the real adapter cannot produce.
- **Implementation coupling**: assertions on private state or incidental details a behavior-preserving refactor would break. Mock-call assertions earn Keep only when the absence, presence, order, or payload of an external interaction is a security, cost, audit, delivery, or compatibility contract.
- **Contract level**: prefer the narrowest stable contract; a domain function is valid when it is the stable contract.
- **Specialized tests**: endpoint/framework smoke tests and visual snapshots earn Keep only by naming and proving the integration, compatibility, or visual contract that justifies their maintenance.
- **Smells**: fixed sleeps, uncontrolled clocks, broad snapshots, vague names, assertion roulette, and multi-behavior tests. A multi-step test proving one real workflow counts as one behavior.
