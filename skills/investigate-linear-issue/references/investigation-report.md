# Investigation Report

Draft one of these forms in the conversation. Post it as a Linear comment only
after the user approves persistence, unless the user explicitly authorized an
immediate Linear update.

## Standard investigation result

```markdown
## Investigation result

**Outcome:** Confirmed / Not reproduced / Needs decision / Duplicate /
Already fixed / Invalid
**Confidence:** High / Medium / Low

### Findings

State what was verified, falsified, or remains uncertain. Separate evidence from
inference.

### Root cause or controlling behavior

State the proven root cause. If it is not proven, name the leading explanation
as plausible and explain what would confirm it.

### Validation performed

- Command, reproduction, inspection, or test and its actual result

### Next evidence or decision

- Exact evidence still needed, or exact human decision blocking progress
```

## Ready outcome

When and only when the issue is ready, append this section to the same comment:

```markdown
## Authoritative implementation brief

### Summary

State the behavior that must change.

### Current behavior

Describe the verified status quo.

### Desired behavior

Describe the durable behavioral contract, including relevant error and edge
cases.

### Key interfaces

- Stable type, command, API, configuration shape, or user-facing boundary

### Acceptance criteria

- [ ] Independently verifiable behavioral criterion
- [ ] Regression or failure-path criterion
- [ ] Required validation at the highest practical interface

### Test-evidence matrix

For behaviorally significant work, map each required behavior to one
unambiguous proof path. Test doubles may replace only the named external I/O;
they must not reproduce the lifecycle or policy being verified.

| Behavior | Public interface and test level | Allowed double | Focused harness or command | Expected evidence |
| --- | --- | --- | --- | --- |
| Example failure behavior | Route, command, or API boundary / integration | Provider transport only | Exact focused command | Observable safe result |

### Out of scope

- Adjacent behavior that must not be included
```

Paths and line numbers may appear in investigation evidence. Do not use them as
the implementation contract. The newest authoritative implementation brief
supersedes older briefs while prior discussion remains historical context. A
user-requested child document may preserve rationale or extended test guidance,
but it is supplementary; link it from this comment rather than making it the
only implementation contract.
