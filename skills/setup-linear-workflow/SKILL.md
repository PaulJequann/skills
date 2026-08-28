---
name: setup-linear-workflow
description: Configure or verify the minimal Linear workflow used by the global Linear skill. Use only when the user explicitly asks to set up Linear, onboard a repository, repair its Linear routing, or inspect whether the workflow is configured correctly.
---

# Setup Linear Workflow

Configure the smallest workflow needed for agent-assisted issue capture and
investigation. Keep durable issue data in Linear and only stable routing policy
in repositories.

## Inspect before proposing changes

1. Read applicable `AGENTS.md` and `CLAUDE.md` instructions.
2. Determine the current repository from `git remote -v`; do not infer it from
   the directory name when a remote is available.
3. Inspect the Linear MCP tools actually available. Do not assume every Linear
   workspace setting is exposed through MCP.
4. Inspect existing teams, workflow statuses, labels, label groups, and
   templates using supported read operations.
5. If Linear MCP is unavailable or unauthenticated, stop before changing the
   repository. Verify the current client's supported connection or
   authentication flow before giving instructions; do not invent a command.

## Propose the minimal configuration

Prefer an appropriate existing team. Otherwise propose one development team:

- Name: `Development`
- Identifier: `DEV`
- Workflow: keep Linear's existing default statuses unchanged

Configure or verify these label groups:

```text
Repository (workspace-level)
└── <one label for each onboarded repository>

Readiness (team-level)
├── Needs investigation
├── Needs decision
└── Ready for implementation
```

Use these meanings:

- `Needs investigation`: the report is not sufficiently verified or scoped.
- `Needs decision`: the issue is understood but a human product, architecture,
  security, privacy, or scope decision blocks implementation.
- `Ready for implementation`: the claim is verified, desired behavior and
  acceptance criteria are clear, and no unresolved decision blocks work.

Only one label from each group may be present. Keep priority independent from
readiness. Do not create projects, cycles, initiatives, custom statuses,
estimates, triage rules, category labels, sample issues, or automations.

Optionally propose one team template named `Engineering issue` with these
sections:

```markdown
## Summary
## Current behavior or observation
## Desired behavior or investigation question
## Evidence
## Impact
## Open questions
## Scope boundaries
## Discovery context
```

Do not make the template mandatory.

## Require approval

Present:

1. What already exists.
2. Exact proposed Linear changes.
3. Exact repository-file change, if any.
4. Which changes the current MCP tools support.
5. Which changes require manual Linear UI work.

Do not mutate Linear or repository files until the user approves this plan.
Explicitly invoking this setup skill authorizes inspection, not unreviewed
configuration changes.

## Apply supported changes

After approval:

1. Apply only supported, approved Linear changes.
2. For unsupported operations, give precise UI navigation steps instead of
   calling undocumented APIs.
3. Re-read the resulting Linear configuration and verify every applied change.
4. Never create an issue merely to test setup.

Treat reruns as reconciliation: reuse matching objects and do not create
duplicates.

## Onboard the repository

Derive the repository label from its canonical remote repository name, using a
clear display form such as `Repository/Kashbot`. Reuse an existing matching
label. Do not create aliases for alternate Git remote URL formats.

Propose this stable block for the repository's existing agent instruction file:

```markdown
## Linear issue tracking

Issues are tracked in Linear under team `DEV`.

- Repository label: `Repository/<Repository>`
- Use the global `linear` skill for Linear issues, documents, and workflow operations.
- Do not create repository-local backlogs, task databases, or issue caches.
- Do not implement issues marked `Readiness/Needs investigation` unless the
  user explicitly overrides the workflow.
```

Update the existing `AGENTS.md` or `CLAUDE.md` according to repository
convention. If neither exists, ask which file to create. Update an existing
Linear section in place and preserve surrounding user content. Do not add
`docs/agents`, tracker configuration files, or cached Linear state.

## Report

Return:

- team name and identifier;
- repository label;
- readiness labels;
- template status;
- repository instruction status;
- manual actions still required; and
- anything that could not be verified.
