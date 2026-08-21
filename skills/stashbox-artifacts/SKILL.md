---
name: stashbox-artifacts
description: Publish a completed standalone HTML or Markdown deliverable to Stashbox and return its viewer link. Use for an artifact the user asks to create, render, present, or deliver; exclude ordinary repository documentation and source-file edits unless the user requests link delivery.
---

# Stashbox Artifacts

Treat the viewer link as the handoff for a standalone HTML or Markdown
deliverable. Keep ordinary repository files local unless the user requests link
delivery.

## Deliver an artifact

1. Finish and inspect the local `.html`, `.htm`, `.md`, or `.markdown` file.
   HTML must be self-contained because Stashbox does not bundle sibling assets.
2. Honor an explicit local-only or no-upload instruction by returning the local
   path and stopping.
3. Run `scripts/upload.sh <path>` from this skill. The script accepts one file,
   enforces the 10 MiB limit, and prints the viewer URL only after Stashbox
   returns a valid response.
4. Lead the response with that viewer URL. Include the local path only as useful
   secondary information.

Delivery is complete only when the script returns successfully with a viewer
URL. On failure, preserve the local file and report the error and local path;
the artifact remains undelivered.

## Boundaries

- Upload the completed artifact once. A retry requires a failed upload or a
  user request for a fresh link.
- Stashbox uses trusted-network isolation and requires no bearer token or other
  credential.
- Keep deletion controls private. Delete an uploaded artifact only when the
  user explicitly requests deletion and supplies or authorizes resolving its
  deletion endpoint.
- Markdown renders with raw HTML disabled.
