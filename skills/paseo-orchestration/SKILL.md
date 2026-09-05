---
name: paseo-orchestration
description: Use for substantial research, workers, or fleet delegation.
---

# Paseo orchestration

Own the result while Paseo runs delegated agents. Choose work worth separating,
launch from live profiles, and carry returned work through verification.

## When to use

Load before choosing a delegation mechanism for substantial research,
independent implementation tasks, long-running work, cross-machine execution,
or a second opinion on a consequential decision. The user need not mention
Paseo. Perform a small lookup, mechanical command, or tightly coupled edit
directly when delegation adds no useful independence.

Prefer Paseo for durable, profile-driven, user-visible delegation. Native
subagents are suitable for short disposable subtasks without those needs, or a
disclosed fallback when Paseo is unavailable. An explicit request for Paseo
retains priority; report a blocker rather than silently switching systems.

## Prerequisites

Load the existing `paseo` skill for current operations and profile mapping.
For Hermes parents, also read [Hermes integration](references/hermes.md).
For connectivity, product behavior, or version uncertainty, load `paseo-help`.
Treat application skills as the command reference, not this policy as an API cache.

## Procedure

### 1. Choose the delegation shape

Identify the outcome and dependencies before launching:

- Research: a bounded question with sources, uncertainties, and a recommendation.
- Worker: an independently testable change with exclusive write ownership.
- Advisor: a judgment without transferring implementation ownership; load
  `paseo-advisor`.
- Committee: contrasting analysis when stuck or facing a consequential design
  uncertainty; load `paseo-committee`. Preserve unresolved dissent rather than
  treating agreement as proof. Bound follow-up exchanges before launching.
- Handoff: transfer the task with its current state; load `paseo-handoff` and
  preserve its return-without-waiting behavior.

Delegate only tasks with a clear deliverable and useful independence. Keep the
critical dependent work with the parent until prerequisites are available.

### 2. Discover profiles and placement

Call `list_profiles` and read every profile's notes. Honor a named profile;
otherwise match notes to the work, then materialize its settings exactly as the
`paseo` skill specifies. Discover available providers and models when no profile
fits, and disclose that fallback. Verify reasoning options rather than assuming
that labels such as high or maximum are interchangeable across providers.

A profile is launch configuration, not a persistent identity or a saved task
prompt. Put responsibilities and acceptance criteria in the briefing. Record
the selected profile name and effective settings in the task record, but
rediscover profiles for subsequent launches rather than caching model choices.

Select the daemon separately from the model. Establish the target machine,
repository path, starting revision, required tools and access, and workspace.
Remote paths belong to the remote daemon. A unified UI does not imply a shared
filesystem, transferable workspace IDs, or cross-daemon parentage.

Read-only agents may share a workspace when they need the same snapshot.
Independent writers normally get separate worktrees. Account for dirty work:
record the intended snapshot and explicitly transfer necessary changes rather
than assuming a worktree or another machine has them. Never overwrite user work.
For cross-machine results, agree on a retrievable artifact or authorized Git
transfer before launch. Do not push branches merely to move data without scope
for that publication.

Finish this step with a justified profile, a verified target, and nonconflicting
ownership for each task.

### 3. Brief and launch

Use [the worker briefing](templates/worker-brief.md). Supply context a fresh
agent can actually access, required skills, exact scope, acceptance criteria,
and evidence to return. Analysis-only work explicitly prohibits file edits.
Workers inherit the user's authorization boundaries, not broader authority.

Set a task-wide concurrency budget and remaining delegation depth in every
brief. Unless the user specifies otherwise, start with at most two simultaneous
children and no grandchildren. Raise or subdivide that allocation only when
independent work justifies it; a child may spawn only within an explicitly
allocated share, not a fresh copy of the parent's entire budget. Specify a
bounded retry or review budget and escalation condition. Use a monetary cap
only when the runtime can enforce or reliably observe it.

Create isolated workspaces before their writers. Preserve parentage and enable
finish notifications as documented. Record daemon identity, agent ID,
workspace ID, revision, task owner, deliverable, and status. Use a durable task
record for work that must survive the parent's session. Record accepted launch
IDs immediately; reconcile uncertain launches before retrying to prevent
creating duplicate agents. Never manufacture parent identity or detach a child
through an undocumented operation.

### 4. Manage asynchronously

Continue useful independent work after launch. With verified completion
notifications, let notifications drive follow-ups rather than status polling.
A notification that a child errored or needs permission is not task completion.
Respect provider reasoning time; silence alone is not a reason to interrupt.

On failure, inspect the specific error and existing artifacts. Recover within
the assigned scope and retry budget, or escalate with the blocker. Reuse the
existing agent for follow-ups when its context remains useful. Before replacing
a writer, ensure the prior writer has stopped and recover its output. Do not
restart a daemon that may host active work as a routine recovery step.

Use a supported wait or event mechanism if callbacks are unavailable. Establish
that mechanism before dispatch; a background CLI launch alone does not prove
the parent will receive a completion message. For a normal delegated task,
continue through verification rather than ending with launch IDs as the result.

### 5. Verify and integrate

Read the actual returned artifact or diff. Treat the child's summary as a claim,
not evidence. Check scope, starting revision, test commands and outcomes, and
remaining risks. Re-run relevant checks in the integration environment; inspect
cross-machine evidence on the machine that produced it. Verify external writes
by reading back their exact targets.

Integrate independent changes in dependency order through the agreed Git
workflow, preserving unrelated work. Resolve overlap and run combined tests;
separate green branches do not prove the combined result works. For research,
check the cited sources and distinguish observation from recommendation.

Close only when every acceptance criterion has evidence or an explicit blocker.
Report the result, verification, and remaining work concisely. Keep useful
advisors available for an ongoing topic; archive completed resources only after
recovering artifacts and confirming the user's intended retention. An owned
worktree can disappear on workspace archival, so archival is not harmless cleanup.

## Pitfalls

- A cheaper model that needs repeated repair may cost more overall. Choose by
  task fit and observed outcomes, not price or reasoning labels alone.
- Profile discovery and tool access must work on the selected daemon. Local
  availability does not prove remote availability.
- A worker cannot expand permission, publication scope, or delegation budget.
- Human input is needed for genuinely unresolved intent or authorization, not
  as a deliberate gate for machine-verifiable steps already authorized.

## Verification

For each run, account for every launched child and every requested deliverable.
Check that the recorded settings, target, ownership, returned artifacts, and
integration evidence match the briefing. Separate lifecycle completion from
successful task completion.

When installing or changing this skill, use the scenarios in
[behavioral verification](references/verification.md). Structural validation
proves packaging only; fresh-session traces prove orchestration behavior.
