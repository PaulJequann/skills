---
name: purposeful-test-design
description: Plan purposeful automated tests. Use only when the user explicitly asks to design tests or assess whether tests are needed, or immediately before you add or revise automated tests. Do not use merely because an implementation task or slice may include tests. Output a test-intent ledger before writing tests.
---

# Purposeful Test Design

Add a test only when it can detect a plausible harmful defect in behavior.
Do not add a test to increase coverage or test count.

Do not invoke this skill for ordinary implementation planning. An implementation
agent may decide whether tests are needed as part of its normal work. Invoke
this skill only when it needs a deliberate test-design decision or is about to
write or change automated tests.

## Procedure

1. State the behavior that a caller or user can observe.
2. Name one plausible incorrect implementation.
3. Name the harmful result and the affected caller or user.
4. Select the narrowest stable boundary that can detect the defect.

Use these boundaries:

- Pure function or domain service for a deterministic domain rule
- Real adapter for persistence, serialization, permission, or provider behavior
- Public API or browser workflow for behavior across multiple layers

Use the same contract that a real caller uses when possible.

## Configuration rule

Use a configuration file as test input only when its value changes a public
runtime behavior. Assert that behavior, not the configuration itself.

Do not test that a configuration file contains, saves, remembers, defaults, or
serializes a setting. Do not make a test pass by reading the configuration file
or inspecting its JSON/YAML shape.

For invalid configuration, rely on normal build or startup validation. Add a
test for rejection only when validation behavior or its fail-safe outcome is
the changed public contract.

## Removal rule

Verify each requested removal in the current change.
Do not add a test that only keeps a removed artifact absent.
Test the behavior of the replacement.

Add a negative repository-policy check only when the user explicitly requests an ongoing constraint.
The check must detect a named harmful result at a stable boundary.
Otherwise, recommend `No new test`.
Put proof of the removal in the acceptance checks, not in a test.

## Decision

Recommend `Test` only when you can complete this sentence:

> This test fails if `<incorrect implementation>` causes `<harmful result>` for `<caller or user>`.

Recommend `No new test` when:

- The compiler makes a mechanical edit safe.
- You cannot name a harmful result.
- The claim only states that an artifact was removed.
- The claim only states that configuration was stored or has a particular shape.

## Test rules

- Assert an observable result, state change, error, durable side effect, or event.
- Make the fixture depend on the target rule.
- Keep one behavior in each test.
- Assert a mock interaction only when the interaction is a contract.
- Use a snapshot only for an explicit visual, compatibility, or assembly contract.

## Output

Output this table before you write tests:

| Behavior | Plausible defect | Boundary | Observable result | Decision |
| --- | --- | --- | --- | --- |

Use only `Test` or `No new test` in the Decision column.
Then give the smallest test set.
Give one-time checks under `Acceptance checks`.
If the user requests implementation, implement the requested production change.
Write only the tests marked `Test`.
Run the focused test set.
