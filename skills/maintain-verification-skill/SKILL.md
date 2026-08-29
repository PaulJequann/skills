---
name: maintain-verification-skill
description: Audit and repair a project-local verification skill against current source, portability requirements, and live application behavior. Use only when the user explicitly asks to maintain, refresh, or audit an existing verification skill.
license: MIT. Derived from Cursor pstack; see LICENSE.txt
---

# Maintain a verification skill

Check a project's verification skill against current source and real user
behavior.

## Scope and outcomes

Edit only the authored verification skill and existing discovery entries that
point to it. This includes its `SKILL.md`, feature map, and owned helpers.
Product code stays read-only.

Report exactly one outcome:

- `clean`: structure, portability, source coverage, and live coverage all pass;
  no correction is worth keeping.
- `changed`: corrections were made and each correction has relevant proof.
- `blocked`: required coverage or proof could not finish safely. Name the
  blocker and every incomplete path.

Publication is separate. When authorized, publish the corrections as one
change set and at most one pull request.

## Locate one authored skill

Search project-local skill directories for a skill with launch and drive
instructions plus a feature map. Include `.agents/skills/` and client-specific
directories already present in the repository. Resolve symlinks so discovery
entries do not appear as separate skills.

Ask the user to choose only when several authored verification skills remain.
If none exists, report that the repository needs the creation workflow.

## Audit structure and portability

Read the map index and enumerate its sibling feature files. Correct missing,
extra, duplicate, and dead entries.

Check that:

- the authored directory has valid Agent Skills frontmatter;
- discovery entries resolve to that one copy;
- instructions use repo-owned commands or tool-neutral actions instead of a
  coding client's tool-call syntax;
- client-specific metadata is optional;
- helper dependencies, invocation, and executable permissions are documented;
  and
- each feature recipe names a safe negative control, its expected rejection
  point, and baseline restoration.

Treat a failed discovery or portability check as drift. Prove any correction
with the relevant validator or active client before finishing.

## Reconcile every mapped feature

For each feature file, trace current behavior from source and record:

- user entry points and stable handles;
- likely drift with file citations, or `none`; and
- one concise live recipe with its expected evidence.

Independent workers may inspect separate features concurrently when the coding
client supports them. Keep those tasks read-only. When delegation is
unavailable, inspect the features directly. The same coverage is required.

Check recent user-facing changes for features missing from the map. Add one
only with a concrete source path and a distinct user behavior. Every indexed
feature needs source evidence and a live recipe before the live pass.

## Plan feature-level live coverage

The feature is the coverage unit, not every sentence in its file. Exercise one
representative recipe per feature. Also exercise an entry point separately when
it uses a different protocol, adapter, permission boundary, or user-visible
result. Do not create terminal work merely to replay equivalent bullets.

Combine recipes into as few application states as practical. Follow the target
skill's launch model: one isolated long-lived instance for a server or UI, or a
fresh isolated session for each short-lived CLI or TUI drive.

## Run the live pass

Exercise every planned recipe while preserving three invariants:

- Run doctor before the first drive, for each fresh session, and after
  surprising behavior. Reset or relaunch when doctor cannot see a wedged UI
  state.
- Check that evidence remains after cleanup.
- Remove owned residue as soon as a drive no longer needs it. Keep a shared
  instance alive only until its final planned drive.

If doctor fails because its own instructions drifted, correct it, restart only
what changed, and retry once. Then report `blocked` if it still fails.

Use `verified-unreachable` only with the attempted route and exact missing
prerequisite, such as authentication, entitlement, operating system, device,
or external state. Add an omitted prerequisite to the map. Unreachable does
not count as verified behavior.

## Triage and prove corrections

- Description, route, handle, prerequisite, or expected-result mismatch is map
  drift. Correct it.
- Working behavior that the documented driver cannot exercise is a driver gap.
  Correct the owned helper or instructions.
- Behavior that current source or product documentation says should work, but
  which fails through the real user path, is a product defect. Record the
  failure and leave product code and intended map behavior unchanged.

Re-drive every correction that changes how a feature is reached, exercised, or
observed. Recheck discovery after portability changes. Finish teardown after
all rechecks and confirm evidence remains.

When doctor, a driver, an expected result, or evidence logic changes, run the
affected negative control before the corrected path. The correction is not
proved if the control passes unexpectedly or fails somewhere other than its
named rejection point. Restore the baseline, run doctor, and then re-drive the
correct path. Do not rerun controls for unchanged proof unless source drift or
live behavior calls their sensitivity into question.

Keep scratch run notes with source coverage, live coverage, unreachable paths,
drift, product defects, corrections, and outcome. Do not commit the notes.

## Finish

For `changed`, reread every changed file and pair each correction with proof.
For `clean` or `blocked`, do not create a branch or pull request solely for the
run. Report structure, portability, source coverage, and live coverage
separately so one cannot mask a gap in another.
