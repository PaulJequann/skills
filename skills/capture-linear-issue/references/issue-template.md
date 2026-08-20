# Engineering Issue Template

Use this structure for every captured issue.

```markdown
## Summary

A concise statement of the problem or desired outcome.

## Current behavior or observation

State what currently happens or what was observed. Separate verified behavior
from hypotheses.

## Desired behavior or investigation question

State what should happen instead. For an unconfirmed report, state the invariant
or concrete question the investigation must answer.

## Evidence

Provide reproduction results, commands, errors, logs, affected interfaces, or
current code locations. Redact secrets and sensitive data.

## Impact

State who or what is affected and why the issue is worth retaining.

## Open questions

- Unknown or unverified point
- Decision that may be required

## Scope boundaries

- Adjacent behavior this issue does not currently include

## Discovery context

- Discovered during:
- Repository:
- Branch or revision:
- Reported by: user / agent
```

For a ready issue, add concrete, independently verifiable acceptance criteria
after `Desired behavior or investigation question`. Do not invent criteria for
an unverified report merely to make it appear ready.
