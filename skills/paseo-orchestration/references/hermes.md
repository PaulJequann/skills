# Hermes integration

Load this reference when Hermes is the orchestrator.

## Discover the real connection

1. Inspect the current tool catalog for Paseo operations. Use deferred tool
   discovery only when the runtime actually offers those tools. A skill naming
   `list_profiles` does not make that tool available.
2. Prefer supported agent-scoped Paseo tools when available. Otherwise inspect
   `paseo --help` and the relevant subcommand help through the terminal tool.
   Verify the target daemon and the supported way to discover profiles and
   materialize all selected settings. Do not invent a profile flag or silently
   discard settings that the CLI cannot express.
3. Establish whether the connection carries the real parent agent identity and
   workspace. Verify callback or wait support before asynchronous dispatch.
   CLI launch acceptance alone proves neither parentage nor callback delivery.
4. If configuration is needed, load `hermes-agent` and its relevant reference,
   then check the current official docs. Keep changes in the authorized Hermes
   profile. Do not copy credential-bearing configuration into briefs or records.

Hermes MCP documentation:
https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp

## Route delegation deliberately

Apply the main skill's worker-request routing rule before using native
`delegate_task`, even for quick subtasks. Native delegation does not inherit
Paseo profile settings. Read its schema for current tool access, nesting, and
lifetime limits when the selected route permits it.

If Paseo is blocked, distinguish an absent tool connection from an unavailable
daemon or unsupported operation. Report the actual failure. For requested
workers, obtain authorization for a native fallback and verify that it preserves
the task's duration, access, isolation, and visibility requirements. Never
describe native children as Paseo agents.

## Installation and activation

Author shared changes in the `pauljequann/skills` checkout, not the installed
`~/.agents/skills` tree or a duplicate under `~/.hermes/skills`. Publish the
source before installing through `dotfiles skills add`. The dotfiles command
also publishes desired inventory; verify both local installation and remote
inventory, including pending operations.

Hermes must discover the shared skill directory in the intended profile.
Confirm discovery in a fresh session. Do not assume this running session's
catalog refreshes after installing a skill.

If fresh-session evaluation shows missed activation, add a short routing rule
through the supported, source-managed global instruction mechanism after
checking its scope. Suggested wording:

> Load `paseo-orchestration` when workers are requested, even for quick tasks,
> or before delegating substantial work. Discover live Paseo profiles before
> choosing worker launch settings. Otherwise perform straightforward tasks directly.

Keep the playbook in the shared skill. A home-level AGENTS.md is not a portable
global instruction mechanism. Do not alter other Hermes profiles or general
identity files as an installation shortcut.
