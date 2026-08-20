---
name: linear-documents
description: "Use for a Linear document: retrieve a named document as task context, or explicitly publish or update a durable Markdown artifact."
---

# Linear Documents

Use Linear documents as durable, long-form task context without turning the
repository into an unbounded planning archive. Treat reads and writes as
separate authority modes.

## Read a document

Read only when the user names, links, or asks to find a specific document.

1. Extract the document ID or slug from a Linear URL. If the URL has no usable
   token, use `list_documents` with a narrow title query and metadata fields
   first.
2. If several documents plausibly match, show the candidates and ask which one
   to use. Do not guess from a title alone.
3. Retrieve the resolved document with `get_document`.
4. Use only the sections relevant to the task. State the document URL and
   parent in the result, and distinguish its claims from independently verified
   repository or runtime evidence.

Never edit, reparent, archive, or subscribe to a document while reading it.
Do not sweep the workspace or preload document bodies into task context.

## Publish or update a document

Write only when the user explicitly asks to publish, save, or update a Linear
document. Drafting Markdown is not permission to create an external record.

1. Preserve the supplied Markdown unless the user asks to transform it. Read
   [references/document-template.md](references/document-template.md) only
   when drafting a new document or the user requests a template.
2. Resolve exactly one parent. Require the user to specify it if it is not
   clear:
   - `issue` for an implementation plan, investigation, or decision tied to one
     issue;
   - `project` for a bounded initiative's spec or shared execution material;
   - `team` for a cross-project ADR, runbook, or enduring shared context;
   - `initiative` or `cycle` only when the artifact truly belongs there.
   When publishing an artifact tied to a newly captured issue, use that issue
   as the document parent.
3. For an update, require the target document ID, slug, or URL. For a new
   document, search narrowly for a likely same-parent/title duplicate; ask
   before replacing or duplicating a plausible existing document.
4. Call `save_document` with the title, content, and exactly one parent (or
   `id` for an existing document).
5. Re-read the resulting document and verify its title, parent, content, and
   URL before reporting success.

Use a Linear document for long-form Markdown. Use issue attachments for binary
artifacts that accompany an existing issue.

## Return

For a read, report the selected document title, URL, parent, and the relevant
answer. For a publish, report the same fields plus whether the result was
created or updated. Never claim success without the readback.
