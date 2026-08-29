---
name: create-verification-skill
description: Create and prove a project-local Agent Skill for driving an application or library through its public user interfaces. Use only when the user explicitly asks to create a verification, control, or app-driving skill for a repository.
license: MIT. Derived from Cursor pstack; see LICENSE.txt
---

# Create a verification skill

Create one project-local skill named `verify-<app>` that an unfamiliar coding
agent can execute without client-specific instructions.

## Establish the contract

Inspect source, configuration, and current documentation before asking the
user. Resolve:

- the application and user-facing interfaces in scope;
- the real local build or start path, including readiness, authentication, and
  seed state;
- existing drivers such as browser tests, PTY helpers, debug protocols, CLI
  wrappers, or request scripts;
- observable proof for each interface; and
- isolation controls for ports, data directories, profiles, devices, and
  accounts.

Prefer an existing driver that exercises a production interface. Introduce a
helper only when it makes the user path repeatable without exposing an internal
shortcut.

Reach a working baseline when the environment permits it. Diagnose a failed
build or launch before writing commands around it. Product-code repair requires
separate authorization. An environment, device, entitlement, or credential
block may still yield a source-backed draft, but the final report must name
every instruction that could not be run.

## Keep one portable copy

Use `.agents/skills/verify-<app>/` as the authored directory unless the
repository already has a documented canonical skill location. When an active
client cannot discover that directory, use its supported installer or add a
relative discovery symlink when the repository's operating systems support
symlinks. Keep one authored copy and add discovery entries only for clients the
project uses.

Use standard Agent Skills frontmatter. Keep coding-client extensions optional.
The skill body must not require slash commands, a named coding-agent product,
proprietary tool-call syntax, or delegation.

Prefer repo-owned shell commands for driving the app. When a UI has no portable
driver, describe each operation by capability and stable handle, such as
"click the button named Save," and state the observable result. The executing
client maps that operation to its browser, desktop, mobile, or terminal tool.
Coordinates and tab order are last-resort handles and must include the state
that makes them stable.

## Write the generated skill

Give `verify-<app>/SKILL.md` a description that names the app, the interfaces it
drives, and the verification requests that should activate it. Write from the
repository root unless a command explicitly changes the working directory.
Include these contracts:

### Launch

Give the exact build or start command, readiness signal, and teardown. Create a
unique run identity and record every owned PID, session, container, profile,
port, scratch path, and evidence path. A short-lived CLI or TUI usually uses one
build followed by a fresh isolated terminal or PTY session for each drive.

### Doctor

Provide one read-only entry point that decides whether the target is worth
driving. It should return success only when the relevant application identity,
revision, process, endpoint, profile, data directory, and authentication match
the current run. An unowned or mismatched target is a failure. The diagnostic
must say which fact is wrong.

### Drive

Give literal repo-owned commands where they exist. Otherwise pair tool-neutral
user actions with stable handles and expected results. Prefer accessible names,
stable test IDs, prompts, routes, flags, and public request shapes. Cover every
entry point claimed by the feature map.

### Evidence

Name the artifact directory and the minimum proof for each interface. Capture
the action and resulting state. When a drive creates a durable side effect,
confirm it through a safe second view. State when visual proof, a structured
snapshot, a transcript, response data, logs, or an exit code is required. Test
modes and dry-runs need observed boundaries, not trust in their names. Use a
substitute only at an existing production boundary, and state which external
behavior remains unproved.

### Cleanup

Use the ownership record to stop and remove only resources created by the run.
Preserve evidence. Include cleanup after failed attempts. Cleanup must be safe
to run again.

### Helpers

Document every helper's invocation and dependencies. Mark executable files
executable. Keep helpers independent of the coding-agent client.

## Seed the feature map

Read [`references/feature-map.md`](references/feature-map.md), then create
`verify-<app>/features/README.md` and one file per selected user feature. Start
with the highest-value coherent features, usually three to five. A smaller app
may need fewer. Prefer an honest small map over invented quota-filling entries.

The map is the maintained verification source. Each feature records the
behavior, every supported user entry point, exact driving recipe, observable
proof, and traps that could invalidate a run. Keep implementation details out
unless an agent needs one to drive or observe the public behavior.

## Calibrate the proof

For each selected feature, record one safe negative control: a deliberately
wrong precondition, target, action, or expected result that the recipe must
reject. Name the exact check that should fail and how to restore the baseline.
The control must not edit product code, damage shared state, or trigger an
external side effect. If no safe control exists, explain why and mark that
feature's proof as uncalibrated.

Run the tracer feature's negative control before its correct path. The tracer
is proved only when the control fails at the named check and the restored path
passes. A control that unexpectedly passes exposes a proof gap, even when the
feature itself appears to work.

## Validate the result

First validate the package and discovery:

1. Run an Agent Skills validator when available.
2. Resolve every discovery alias to the authored directory.
3. Confirm each active client can discover the same skill without duplicated
   source.

Then run one tracer feature end to end:

1. Launch and run doctor.
2. Run its negative control and confirm rejection at the named check.
3. Restore the baseline and run doctor again.
4. Drive the feature through a real user entry point.
5. Capture its required evidence.
6. Clean up, including after failed iterations.
7. Confirm the evidence remains and every owned resource is gone.

Report `ready` only when package discovery, the tracer's negative control, and
its restored correct path pass. Report `draft` when the skill is source-backed
but a required validation step remains unproved. A draft report names the
attempted step, observed failure, and unmet prerequisite.

Commit, publish, or open a pull request only when the request authorizes it.
