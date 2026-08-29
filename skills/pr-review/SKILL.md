---
name: pr-review
description: >
  Fetch and analyze automated/bot review comments on a GitHub PR (GitHub Copilot,
  ChatGPT Codex, or any reviewer). Use when the user types "/pr-review" or asks to
  "review PR feedback", "check PR comments", or "look at what Copilot/Codex said".
  Accepts an optional PR number; defaults to the current branch's open PR.
  Presents findings with AskUserQuestion to decide per-item. Does NOT commit or push.
---

# PR Review Skill

Fetch bot/reviewer comments on a GitHub PR, validate each finding against actual
code, present a triage table, then walk through each item interactively.

## Invocation

```
/pr-review [PR number]
```

- No argument → detect the open PR for the current branch
- With number → review that specific PR (e.g. `/pr-review 42`)

---

## Workflow

### Step 1 — Resolve PR number

If the user provided a number, use it directly.

Otherwise detect it:
```bash
gh pr view --json number --jq '.number' 2>/dev/null
```

If that fails (not on a branch with an open PR), try:
```bash
gh pr list --state open --head "$(git branch --show-current)" --json number --jq '.[0].number'
```

If no PR is found, tell the user and stop.

### Step 2 — Fetch repo info

Get the `owner/repo` slug needed for API calls:
```bash
gh repo view --json nameWithOwner --jq '.nameWithOwner'
```

### Step 3 — Fetch all review comments

Run both of these in parallel — they capture different comment types:

**A. Top-level PR comments** (issue-style comments, where bots often post summaries):
```bash
gh api repos/{owner}/{repo}/issues/{pr}/comments --paginate
```

**B. Inline review comments** (line-level diff comments — where Codex/Copilot post per-finding):
```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments --paginate
```

**C. Formal reviews** (review bodies with APPROVE/REQUEST_CHANGES):
```bash
gh api repos/{owner}/{repo}/pulls/{pr}/reviews --paginate
```

Parse all three. Key fields to extract from each comment:
- `user.login` — the reviewer (e.g. `chatgpt-codex-connector[bot]`, `github-copilot[bot]`, human)
- `body` — the comment text (may contain markdown, badge tags like `P1`, `P2`)
- `path` — file path (inline comments only)
- `line` / `original_line` — line number (inline comments only)
- `created_at` — timestamp

**Important:** Bot reviews (Codex, Copilot) often nest multiple findings inside a single
top-level comment as markdown. Parse the body text for individual finding blocks —
look for patterns like:
- `**P1**`, `**P2**`, badge image tags (`![P1 Badge]`)
- Numbered lists of findings
- Bold headings per finding

### Step 4 — Filter and deduplicate

- Keep only comments from the PR's reviewers/bots that contain actual findings
- Skip: merge notifications, CI status posts, "LGTM" approvals, empty bodies, bot quota/usage-limit notices (e.g. `You have reached your Codex usage limits for security reviews`)
- If the same finding appears in both the top-level summary and as an inline comment,
  keep the inline version (has file/line context)

### Step 5 — Validate each finding against current code

For each finding that references a file and/or line:

1. Read the referenced file with the Read tool
2. Check whether the described issue actually exists in the current code
   (the branch may have already fixed it since the review was posted)
3. Mark each finding as:
   - **Valid** — issue exists in current code
   - **Already fixed** — code no longer has the problem
   - **False positive** — finding misunderstands the code
   - **Needs investigation** — can't determine without deeper context

Only present **Valid** and **Needs investigation** findings to the user.
Silently drop already-fixed and clear false positives (mention the count at the end).

### Step 6 — Present findings table

Show a summary before asking about individual items:

```
## PR #N Review — <N> findings from <reviewer list>

| # | Priority | Reviewer | File | Finding summary |
|---|----------|----------|------|-----------------|
| 1 | P2       | codex    | src/foo.tsx:42 | Cmd+R not wired as keydown handler |
| 2 | P2       | codex    | src/bar.tsx:15 | Modal not triggered on navigate |
```

If there are no valid findings after validation, say so and stop.

**Priority mapping** (extract from badge/label if present, otherwise infer from severity language):
- P0 / CRITICAL → 🔴
- P1 / HIGH → 🟠
- P2 / MEDIUM → 🟡
- P3 / LOW → 🔵
- Unlabelled → infer from language ("regression", "bug" → P2; "suggestion" → P3)

### Step 7 — Triage interactively

For each valid finding (P0/P1 first, then P2, then P3), use **AskUserQuestion** to ask:

```
Finding #N (P2 — codex): <short description>

File: src/foo.tsx:42
Detail: <full finding body, trimmed to key point>
```

Options:
- **Fix now** — implement the fix immediately in this session
- **Skip** — not worth fixing / disagree with the finding
- **Create bead** — track for later (`br create`)

Group related findings into a single question when they are in the same file and
clearly linked (e.g. two issues in the same function).

### Step 8 — Implement chosen fixes

For each "Fix now":
1. Read the file if not already read
2. Implement the minimal fix — don't refactor surrounding code
3. Run `bun run verify` (or project equivalent) after all fixes are applied
4. Report what was changed (file + description), but **do not commit or push**

For each "Create bead":
```bash
br create --title "<finding summary>" --type bug --priority <2|3> \
  --description "From PR #N review by <reviewer>: <finding body>"
```

### Step 9 — Summary

After processing all findings, print:

```
## Done

Fixed N findings, skipped M, created K beads.

Changed files (not yet committed):
- src/foo.tsx
- src/bar.tsx

Run `bun run verify` to confirm, then commit and push when ready.
```

---

## Notes

- **Validate before presenting.** Don't surface findings the code already handles.
- **Bot reviews are noisy.** Codex/Copilot often comment on pre-existing code from earlier
  commits in the PR. Always check which commit the comment was posted on vs. current HEAD.
- **Nested findings.** Codex typically posts one top-level comment with a collapsible
  summary, then individual inline comments per finding. The inline comments have the real
  detail — prioritise those.
- **No gh CLI?** If `gh` is not installed or not authenticated, tell the user and stop.
- **Pagination.** Use `--paginate` on all API calls to catch PRs with many comments.
- **Private repos.** `gh api` handles auth automatically via the gh CLI token.
