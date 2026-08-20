---
name: file-pr
description: Use when the user asks to file a GitHub PR for clearly scoped work.
---

# File a Pull Request

Complete the clearly scoped publication work, then present the branch as a
decision a reviewer can understand. Optimize the title and body for why the
change should merge, not for recounting commits.

## Interpret the request

- Treat a request to file a PR as authorization to complete its normal
  prerequisites: identify the session's work, run required final verification,
  prepare a feature branch when needed, stage only the in-scope changes, commit
  them, push the branch, and create one PR.
- Use the conversation, repository state, plans, issues, and current diff to
  determine what belongs. Do not ask the user to reconfirm work that is already
  clear from the session.
- Do not stop merely because changes are uncommitted, the branch is unpushed, or
  no feature branch exists yet. Those are expected parts of filing the PR.
- Pause when there is genuine consequential ambiguity: unrelated or overlapping
  user changes cannot be separated safely, the intended scope or base is
  unclear, required verification fails materially, credentials are missing, or
  publication would require a destructive or materially different action.
- Do not infer authorization to request reviews, add labels, post comments,
  resolve review threads, merge, or delete branches. Perform those stages only
  when the user asks for them.
- If another GitHub publishing workflow defaults to a draft, let this skill's
  ready-state and end-to-end filing rules own the operation while retaining its
  repository and safe-staging safeguards.

## Prepare the publishable branch

1. Read applicable repository instructions and PR templates.
2. Inspect the conversation, status, staged and unstaged diffs, untracked files,
   recent commits, and verification already performed. Separate the intended
   work from unrelated user changes; never sweep unrelated paths into the PR.
3. Run the repository-required or proportionate final verification for
   publication when it has not already been completed on the final diff.
4. Resolve the canonical repository and base. If the work is on the default
   branch, create an appropriately named feature branch unless repository
   instructions or an explicit user request require another approach.
5. Stage only the identified in-scope paths and commit them with a message that
   represents the change. Preserve valid existing commits rather than rewriting
   history merely for neatness.
6. Fetch the base when needed, resolve the exact head and current SHA, and push
   the branch with upstream tracking. Do not force-push unless the session
   explicitly authorizes history rewriting or it is an already-authorized
   remediation workflow using a safe lease.
7. Inspect the complete base-to-head diff, changed-file list, and commit list.
   Do not derive the PR from only the first or latest commit message.
8. Check for an existing open PR with the same repository, base, and head. Reuse
   and report it instead of creating a duplicate; do not edit unrelated PR
   metadata unless that action is authorized.
9. If one concise title cannot truthfully cover the diff, flag likely mixed or
   accidental scope before filing rather than hiding it behind a vague title.

## Write an outcome-oriented title

- State the primary capability, benefit, protection, or behavior delivered by
  merging the complete diff.
- Prefer plain language and the project's domain vocabulary.
- Keep the title concise, usually no more than about 70 characters.
- Omit Conventional Commit prefixes and scopes such as `feat(mobile):`,
  `fix(auth):`, `refactor(web):`, and `chore(tooling):`.
- Avoid leading with an implementation mechanism such as a library, database,
  file move, or refactor unless that mechanism is itself the reviewed outcome.
- Do not lead with an issue number, implementation stage, or internal plan
  checkpoint.

### Title examples

Bad: `feat(mobile): add core password authentication`

Good: `Enable secure mobile sign-in and session restoration`

Bad: `refactor(web): relocate app into workspace`

Good: `Make room for mobile without disrupting the web app`

Bad: `feat(records): add structured operational Review Records`

Good: `Make failed reviews easier to diagnose`

Bad: `fix(auth): stabilize Turnstile across form rerenders`

Good: `Keep CAPTCHA verification stable while users type`

Bad: `chore(tooling): remove web relocation hazards`

Good: `Protect the web app during workspace migration`

## Write a reviewer-oriented body

Use these sections when they carry information; omit empty or ceremonial
sections and keep small PRs small.

- `Why`: In one to three sentences, explain the current problem and the benefit
  or protection delivered by merging.
- `What changed`: Summarize behavioral or architectural outcomes in a few
  bullets. Include implementation detail only when it helps review.
- `Review guide`: Identify the riskiest seams, important invariants, and where
  reviewer attention is most valuable.
- `Verification`: Give exact commands and meaningful outcomes. Include manual,
  hosted, device, migration, or performance evidence when relevant. State gaps
  honestly; never turn unavailable or unreported evidence into a pass.
- `Scope`: State important non-goals or deferred work when they prevent an
  incorrect review assumption.
- `Risks and tradeoffs`: Record relevant compatibility concerns, rollout risks,
  or narrow accepted waivers with their evidence and invalidation conditions.
- `Tracking`: Add issue-closing syntax only when closing that issue on merge is
  intended and supported by the delivered scope.

Do not use the body as a session transcript, commit inventory, or agent process
log. Omit model identifiers, review IDs, authorization timestamps, and internal
ceremony unless a specific fact materially affects the code review. Link to
durable detailed evidence instead of duplicating it.

## Create the PR

- Create exactly one PR with an explicit base and head.
- Create a ready PR by default. Set `draft: false` or pass the tool's explicit
  ready equivalent even when omitting a draft flag would currently behave the
  same way.
- Create a draft only when the user explicitly says `draft`.
- Do not infer draft state from incomplete verification, open follow-up work, or
  agent confidence. Disclose those facts in the body while preserving the
  requested ready default.
- Supply the body through a file or standard input to preserve Markdown and
  avoid shell interpolation problems.
- If creation returns an ambiguous result, inspect GitHub read-only before
  retrying. Never blindly create a second PR.
- Do not request a bot or human review merely because the PR is ready; readiness
  allows configured automations to run. Request a review only when asked.
- When this is followed by `babysit-pr`, hand off immediately after the ready
  PR readback. Treat an empty post-creation readback as automatic-review
  pending; `babysit-pr` owns monitoring and its initial-review gate determines
  whether an explicit fallback trigger is warranted.

## Verify the published result

Read the PR back from GitHub and confirm:

- the URL and PR number;
- the exact base and head branches;
- the expected current head SHA;
- the final title and body;
- `isDraft: false`, unless the user explicitly requested a draft.

If authorized work changes the diff before the filing task is complete,
reconcile the title and body against the final head before reporting completion.
Report the URL, ready or draft state, base/head, and any verification gaps. Do
not imply that checks passed when GitHub reports no checks, and do not continue
into review monitoring or merge unless the user requested those stages.
