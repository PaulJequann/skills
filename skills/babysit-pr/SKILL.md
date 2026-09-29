---
name: babysit-pr
description: Use when the user asks to babysit an existing GitHub PR through current-head CI and review, address routine CI or review findings, or continue after `file-pr` creates a ready PR whose automatic review may still be queued.
---

# Babysit PR

Own an existing pull request through CI and automated review. Work autonomously on routine, in-scope problems; report only after reaching a finish line or encountering a decision that genuinely needs the user.

## Interpret the request

1. Resolve the PR from an explicit URL or number, the current branch, or the immediately preceding `file-pr` result. If more than one PR is plausible, ask which one.
2. Treat “babysit this PR” as authorization to perform the routine work necessary to finish it:
   - investigate CI failures, conflicts, and review findings;
   - edit the scoped implementation and tests;
   - run appropriate verification;
   - commit and push remediation;
   - keep the PR title and body accurate;
   - reply to review findings with evidence;
   - resolve fully addressed automated-review threads; and
   - post the repository's review trigger, such as `@codex review`, for the
     one budgeted follow-up cycle. This holds even after `file-pr`, which
     requests reviews only when asked.
3. Do not stop merely because changes are uncommitted or unpushed. Those are normal intermediate states within this workflow.
4. Keep merge, deployment, branch deletion, and a third automated review cycle outside the default authority. Perform them only when the user explicitly asks; an authorized merge follows **Merge when authorized**.
5. Honor caller overrides such as CI-only monitoring, no rereview, a numeric review limit, a deadline, or “continue until every review is green.” Scope and safety boundaries still apply.

## Establish scope and review budget

Before changing code, recover the PR's intended outcome from the conversation, linked issue, title, body, diff, commits, and documented decisions. Treat explicit approvals, waivers, and intentional deletions as part of the specification; reviewers may not have that context.

Record:

- canonical base repository, PR number, base branch, and head branch;
- current remote head SHA and corresponding local commit;
- intended behavior and accepted exclusions;
- automatic-review trigger state, review cycles already requested or completed;
- the caller's loop policy.

A review cycle is the collection of configured automated-review feedback for
one head commit, not each comment or each reviewer. The budget never resets,
and memory of it does not survive compaction or a fresh invocation. Rebuild the
count from the PR itself: the heads that received a completed automated review,
and the explicit trigger comments already posted.

The default budget is:

1. the initial automated review cycle, whether automatic, already present, or explicitly requested; and
2. at most one additional automated review cycle after substantive remediation.

## Inspect authoritative PR state

Inspect the canonical base repository rather than trusting a fork or local remote name. Establish all of the following for the exact current head:

- draft or ready state, mergeability, and conflict state;
- required and optional checks, status contexts, Actions jobs, failure logs, and external check links;
- conversation comments and bot acknowledgements;
- formal reviews and inline review comments; and
- GraphQL review threads, including resolution, outdated state, and the commit each thread targets.

Do not treat an acknowledgement that a bot started work as a completed review. Count only reviews, comments, and reactions authored by the configured reviewer: your own thread replies create `COMMENTED` reviews on the current head. Do not treat “no checks found” as green. Green checks or reviews on an older head are evidence about that head, not the current one.

### Codex review state

When the configured reviewer is Codex, PR creation or `@codex review` starts two
reviews of the head: a security review and a code review. The code review is
the one the review loop waits for.

- The code review is complete for a head when the summary comment's
  `📝 Code Review` row shows it completed for that head, the bot submits a
  formal review, or it reacts 👍. The hidden JSON `status` and `headSha` in the
  summary comment track only the security review.
- A security-review usage-limit notice is neither a finding nor a completion.
  Ignore it and keep waiting for the code review. Its text:
  `You have reached your Codex usage limits for security reviews`.
- Completed is not clean. A cycle is clean only when the head has a 👍 or no
  new review threads; read that head's threads before calling it clean.
- Match the bot under both logins: `chatgpt-codex-connector` in GraphQL and
  `chatgpt-codex-connector[bot]` in REST.

After every push, re-read the remote head SHA and reset monitoring to that exact head.

## Triage CI and conflicts

Classify a failing or missing check before acting:

- **PR-caused failure:** fix it, verify it, commit, and push.
- **Small adjacent blocker:** apply the smallest safe correction when it is necessary to validate or ship the PR, and disclose the scope addition.
- **Broader unrelated defect:** do not absorb it into the PR. Capture it through the configured issue workflow when it is concrete, worthwhile, non-duplicative, and nonblocking; otherwise surface it in the handoff.
- **Infrastructure or flaky failure:** gather evidence, then rerun once on an unchanged head when a rerun can distinguish flake from defect. Do not repeatedly rerun a deterministic failure.
- **Expected skipped or neutral result:** verify why it is expected and explain it; do not misreport it as green.
- **Missing expected automation:** verify triggers, paths, permissions, draft state, and workflow configuration instead of waiting indefinitely.

Resolve routine mechanical base conflicts and revalidate the result. If the normal repository workflow requires rebasing, use `--force-with-lease`, never an unconditional force push. Escalate semantic conflicts that require a product or ownership decision.

## Validate review findings independently

Treat every review comment as a hypothesis. Inspect the current code, tests, diff, repository conventions, and documented intent before accepting it. Severity labels and confident wording are not proof.

Classify each finding:

| Classification | Action |
| --- | --- |
| Valid and in scope | Fix, test, commit, push, reply with evidence, then resolve the automated thread. |
| Already fixed or stale | Verify against the current head, explain the evidence, and resolve the automated thread. |
| False positive or conflicts with an approved decision | Explain the governing context and evidence; update the PR body if that context was missing; resolve the automated thread. |
| Valid, out of scope, and nonblocking | Keep it out of the PR. Duplicate-check and capture a focused issue when worthwhile, then link it in the reply or handoff. |
| Valid, out of scope, and release-blocking or high impact | Stop and bring the decision to the user with impact, evidence, and a recommendation. Do not call the PR ready. |
| Unclear or decision-heavy | Investigate as far as possible, then ask the user only for the unresolved decision. |

Do not grow the PR merely to make every reviewer suggestion disappear. Do not create backlog noise from speculative or trivial comments.

Human-authored feedback deserves extra care. Address routine requested fixes, but do not dismiss a human review or automatically ping a human reviewer unless the repository's established workflow calls for it.

## Remediate a cycle

1. Wait for the configured checks and reviewers for the current head to reach a terminal state.
2. Gather all actionable failures and findings for that head before editing. Batch related remediation rather than pushing once per comment.
3. Make the smallest coherent in-scope change.
4. Run targeted regression checks and the repository's required final verification.
5. Stage only intended files, create a clear commit, and push it. Preserve repository history conventions; do not rewrite shared history without necessity.
6. Reconcile the PR title and body when remediation changes the outcome, scope, verification, or accepted limitations.
7. Reply inside each finding's review thread with the disposition and concrete evidence, such as the fixing commit, test result, governing decision, or follow-up issue. A PR-level summary comment does not count as a reply.
8. Resolve each automated review thread by its ID, after replying to it, and only once its finding is fixed, disproved, stale, or deliberately deferred with a durable disposition.
9. Read the new remote head and begin current-head CI monitoring again.

While checks or reviews are pending, keep monitoring instead of handing the waiting work back to the user. Post an update when state changes, such as a review starting, findings arriving, or a push landing, not once per poll.

## Gate the initial review

Run this gate once for the initial cycle, before posting an explicit review
trigger or acting on initial review findings. It is complete when the initial
review is terminal for the current head, or the documented fallback trigger is
visible or acknowledged for that head.

1. Confirm whether the ready PR has configured automatic review automation. If
   it does, set `initial_review = pending` for the current head. An empty
   post-creation readback remains `pending`.
2. Inspect current-head checks, Actions/jobs, comments, review metadata, and
   configured trigger evidence, such as 👀 reactions or a `📝 Code Review` row
   in progress. Transition to `terminal` only when the code review completes,
   read for Codex by **Codex review state**.
3. If the automation path is absent, or is present but failed to launch after
   that bounded diagnostic wait, verify that no equivalent request is pending.
   Only then use the repository-established explicit trigger and record the
   fallback reason. Transition to `fallback` when that trigger is visible or
   acknowledged.
4. Treat every automated reviewer or trigger targeting the same head as part of
   the initial cycle. If a manual trigger overlaps a pending automatic review,
   merge both result sets into that one cycle.

## Apply the bounded review loop

Use this default state machine:

1. Run the initial-review gate. Its completion criterion is `terminal` or
   `fallback` for the current head.
2. Gather and classify all initial-cycle findings, then batch-remediate them.
   This step is complete when every actionable finding is fixed, disproved,
   stale, or durably deferred and no actionable thread lacks a disposition.
3. Request at most one additional automated review only after the initial cycle
   reaches a terminal state and substantive remediation makes another pass
   useful. An initial clean review, false positives resolved by evidence, or a
   narrow CI-only correction may leave the follow-up cycle unused. The step is
   complete when the follow-up request is either intentionally unused or
   visible for the new head. Before posting the trigger, confirm from the PR
   that the follow-up cycle is unused.
4. See a requested follow-up review through to terminal, even when the PR
   already looks ready. Validate and batch-remediate its findings, then push
   and finish current-head CI. This step is complete when CI is terminal and
   every follow-up finding has a disposition.
5. Hand the stable PR to the user for human approval, or merge it under
   **Merge when authorized**, without starting a third automated review under
   the default policy. The workflow is complete when the handoff names the
   exact head, CI state, cycle history, and next human action.

Use the repository's configured reviewer and trigger; do not silently
substitute another reviewer. If feedback arrives for a stale head, validate
whether it still applies to the current head before acting.

An explicit caller policy replaces the default numeric limit. For example, “until all reviews are green” authorizes further useful cycles, while “CI only” authorizes none. Even under an unlimited loop, stop for genuine product decisions, release-blocking out-of-scope discoveries, unsafe history changes, unavailable credentials, or a repeated non-progressing loop.

## Reach the finish line

Before handing off, audit the exact remote head:

- local, pushed, and PR head commits agree;
- the PR is conflict-free;
- current-head required CI is green, or the absence of checks is explicitly investigated and reported;
- expected skipped or neutral checks are explained;
- no known actionable automated-review thread is left without a disposition;
- review findings have been fixed, disproved, or durably deferred;
- out-of-scope findings kept out of the PR are listed or linked as issues;
- the title and body still describe the actual change and verification;
- the review budget and any intentionally unre-reviewed final head are explicit; and
- any remaining human approval or decision is named precisely.

Finish with the PR link, exact head, CI state, review-cycle history, each finding with its fix or disposition in one line, deferred issues, and the single next human action. A count such as "3 findings fixed" does not replace the list. The handoff is owed in full even when merge is authorized or other work is in flight.

## Merge when authorized

When the user authorized merging, such as "merge when ready", finish the audit
and handoff first. Then compare the audited head with the last head a completed
automated review saw. The follow-up cycle usually finds something, so an
unreviewed final head is the normal case.

- **Only remediation since the last review**, meaning fixes for review findings
  or CI: merge with `gh pr merge <number> --match-head-commit <audited head>`,
  using the repository's merge method. Delete the branch when the user asked.
  Then fast-forward the local base branch; if it has diverged, such as holding
  the pre-squash commits, say so and ask before resetting it.
- **New behavior or scope since the last review**, such as work the user added
  mid-babysit: stop before merging. Name the unreviewed change by files and
  lines, and ask whether to merge it or review it first.

Either way, the final message states that the merged head was not re-reviewed
when that is true.
