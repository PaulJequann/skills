# Linear investigation

Investigation diagnoses and prepares the issue. It does not implement the fix.

## Resolve and establish the claim

1. Read the issue body, labels, status, repository label, and relationships.
   Read comments and linked documents for relevant provenance or unresolved
   discussion.
2. Match the repository label to the current Git remote. Stop on a mismatch.
3. Treat the issue as a report, not proof. Search current code and existing
   issues, reproduce or falsify at the highest practical interface, trace the
   controlling boundary, and run focused diagnostics.
4. Use current first-party sources for external-provider behavior. Separate
   repository evidence, provider evidence, and inference.
5. Record what was tried, the actual result, and remaining uncertainty. Keep
   diagnostic artifacts untracked or remove them before reporting.

When selecting from a queue, filter open issues by the current repository and
`Readiness/Needs investigation`, exclude work blocked on decisions or access,
then prefer explicit priority and the oldest actionable issue.

## Choose the outcome

- **Ready for implementation:** the body can state verified behavior, the
  durable implementation contract, acceptance criteria, test evidence, scope,
  failure behavior, and exclusions with no decision remaining.
- **Needs decision:** state each exact decision, its material options, and the
  consequence of each.
- **Needs investigation:** state the exact evidence or access that would resolve
  the remaining uncertainty.
- **Duplicate, already fixed, invalid, or superseded:** state the evidence and
  proposed disposition. Disposal remains a separately authorized action.

Assess whether confirmed implementation work fits one fresh agent context
window. Read the decomposition reference and propose slices only when it does
not.

## Draft before writing

Present the proposed outcome, readiness, and complete replacement body in the
conversation. For decomposition, also present the numbered children and blocker
edges. An investigation request remains read-only until the user approves this
write, unless the request explicitly included updating Linear.

## Persist approved findings

1. Replace or revise the issue body so it is the best current handoff. Correct
   disproved claims, remove useless context, preserve useful evidence, and make
   the next action explicit.
2. Replace the readiness label with the accepted outcome. Preserve status,
   priority, assignee, project, cycle, and closure unless separately authorized.
3. Publish any approved children and relationships through the decomposition
   workflow.
4. Add one concise sign-off comment:

   ```markdown
   Investigation completed on YYYY-MM-DD.

   Outcome: <outcome>
   Readiness: <old> -> <new>

   The issue body was updated with the verified findings and current handoff.
   Research performed by: <actor>
   ```

   Add a link or one-line material note when useful. Do not duplicate the body.
5. Re-read the issue, comment, labels, and relationships. Verify the canonical
   body and every authorized change.

If Linear is unavailable, return the completed proposed body and state that it
was not persisted. Confirm that no product implementation was performed.
