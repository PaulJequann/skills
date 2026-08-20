# Linear Issue Decomposition Protocol

Read this protocol only when an explicit capture or completed investigation
shows that clear implementation work exceeds one fresh agent context window.

## Model

A **parent** groups the slices that jointly deliver one outcome. It is an index
of the outcome and scope, not a second implementation ticket. Each **child**
owns one narrow, complete, independently demoable or verifiable behavior.

**Parent-child** and **blocking** express different facts. Make both native
Linear relationships when the tracker supports them:

- Parent-child: this slice belongs to the outcome.
- Blocking: this slice cannot begin until another slice completes.

Do not use a parent-child relationship as a substitute for a blocker, or vice
versa. If native relationships are unavailable, record the equivalent parent
and blocker identifiers in the child body.

## Decide whether to decompose

Keep one issue when it has one independently verifiable outcome that fits in a
single fresh agent context window.

Otherwise, propose vertical slices. Do not divide work by technical layer. Put
necessary prefactoring first and give each slice only blockers that genuinely
gate it.

Do not decompose unverified reports, unresolved decisions, or autonomous
agent-discovered captures. Do not force a wide mechanical refactor into vertical
slices; use expand-contract: additive expansion, independently safe migration
batches, then a final contract step.

## Propose and obtain approval

Present a numbered breakdown. For every child, show:

- **Title**
- **Blocked by**
- **What it delivers** — the end-to-end behavior, not a layer-by-layer task
- **Acceptance criteria**

Ask the user to approve the granularity and blocking edges, or to merge, split,
or revise the proposal. Present the complete proposal in the conversation and
do not create a parent, children, relationships, investigation comment, or
readiness transition until approval.

For a breakdown discovered during investigation, include the proposed
`Needs decision` transition and the draft investigation result in the
conversation. Approval of the breakdown is the exact blocking decision. After
approval, persist the accepted investigation result and publish the approved
breakdown as one verified batch.

## Publish an approved breakdown

1. Search for duplicates using the overall outcome and each proposed child.
2. Resolve the parent:
   - **Existing investigated issue:** retain it as the native parent.
   - **Direct capture:** create a concise umbrella parent after approval. State
     the outcome and scope boundaries, but do not duplicate the children’s
     implementation detail.
3. Create every child as a native child of that parent. Child readiness must
   reflect its actual implementation readiness.
4. Wire blocking edges in a second pass, after every child has an identifier.
5. Keep the parent out of the agent-ready queue: use `Backlog`, no readiness
   label, and unset priority. For an existing investigated parent, ensure it
   has no readiness label once the approved children are published.
6. Re-read the parent and every child. Verify titles, bodies, status, labels,
   parent-child relationships, and blocking edges.

Return the parent and every child identifier and link, each child’s readiness
and blockers, and whether the original task continued. Never claim publication
succeeded without verified Linear records.
