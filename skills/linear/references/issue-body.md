# Linear issue body

The body is the canonical current handoff. Use only the sections the issue
needs, but keep enough context for a fresh agent to act without reading the
comment history.

```markdown
## Summary

A concise statement of the problem or desired outcome.

## Verified current behavior

What currently happens. Separate verified facts from remaining hypotheses.

## Desired behavior or investigation question

The durable outcome, or the exact question that further research must answer.

## Evidence

Reproduction results, commands, errors, relevant interfaces, revisions, or
linked artifacts. Redact sensitive values.

## Implementation contract

For ready work, describe the stable behavioral contract, important failure and
edge behavior, and interfaces through which the result is observed.

## Acceptance criteria

- [ ] Independently verifiable behavioral criterion
- [ ] Failure-path or regression criterion

## Test evidence

For behaviorally significant work, map each required behavior to its public
interface, test level, allowed external-I/O double, focused command or harness,
and expected observable evidence.

## Scope boundaries

- Adjacent behavior excluded from this issue

## Decisions or remaining unknowns

- Exact decision, uncertainty, or next evidence required

## Research provenance

- Last verified:
- Repository and revision:
- Linked document or artifact:
```

For a new unverified report, retain discovery context such as branch, revision,
and reporter when useful. For an investigated issue, rewrite misleading or
obsolete material instead of appending contradictions. Preserve historical
detail only when it still helps reproduce or understand the current work.
