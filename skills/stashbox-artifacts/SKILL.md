---
name: stashbox-artifacts
description: Publish or revise a standalone HTML or Markdown deliverable in Stashbox and return its stable viewer link. Use for an artifact the user asks to create, update, present, or deliver; exclude ordinary repository documentation and source-file edits unless the user requests link delivery.
---

# Stashbox Artifacts

Treat the stable viewer link as the handoff for a standalone HTML or Markdown
deliverable. A published artifact is one evolving stash: revisions preserve its
history while its viewer URL stays fixed.

## Deliver an artifact

1. Finish and inspect the local `.html`, `.htm`, `.md`, or `.markdown` file.
   HTML must be self-contained because Stashbox does not bundle sibling assets.
2. Honor an explicit local-only or no-upload instruction by returning the local
   path and stopping.
3. Run `scripts/upload.sh <path> [viewer-url]` from this skill:
   - An explicit viewer URL or a `<!-- Stashbox: viewer-url -->` marker in the
     file publishes a revision to that stash.
   - An unmarked file without a viewer URL creates a stash.
4. Lead the response with the stable viewer URL. State whether Stashbox created
   the stash, published a revision, or found it already current. Include the
   local path only as useful secondary information.

Delivery is complete only when the script returns successfully with a viewer
URL and reports the publish result. On failure, preserve the local file and
report the error and local path; the artifact remains undelivered.

For an artifact that should keep the same link across future edits, place its
stable URL near the top after the first publish:

```html
<!-- Stashbox: https://stashbox.local.bysliek.com/example-id -->
```

Publish the marker as the next revision. Later runs then discover the stash
without requiring the URL in the prompt.

## Boundaries

- Conditional updates use the stash's current ETag. Treat a conflict as a
  reconciliation stop: inspect the latest source or history before retrying.
- A fresh stash requires an unmarked file and no explicit viewer URL. Preserve
  an existing stable link unless the user requests a separate artifact.
- Stashbox uses trusted-network isolation and requires no bearer token or other
  credential.
- Keep deletion controls private. Delete an uploaded artifact only when the
  user explicitly requests deletion and supplies or authorizes resolving its
  deletion endpoint.
- Markdown renders with raw HTML disabled.
