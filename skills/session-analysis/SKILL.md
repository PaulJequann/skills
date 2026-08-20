---
name: session-analysis
description: Audits Claude Code hook system effectiveness and proposes concrete improvements. Use when the user types "/session-analysis" or asks to analyze hooks, audit hook effectiveness, review what hooks did this session, evaluate signal vs noise in hooks, or improve the Claude Code hook setup. Reads ~/.claude/settings.json and all hook files, cross-references them against actual tool usage in the current session, evaluates each hook's signal quality, and presents a ranked improvement plan with interactive per-suggestion options (implement now / add context / skip).
---

# Session Analysis Workflow

## Step 1 — Read the hook configuration

Read these files in parallel:
- `~/.claude/settings.json` — which hooks are registered, their matchers and timeouts
- Every `.ts` file in `~/.claude/hooks/` — what each hook actually does

## Step 2 — Reconstruct session tool usage

From the current conversation context, identify:
- Which tools were called (Read, Grep, Edit, Write, Bash, Task, Glob) and roughly how often
- Whether any tool calls were denied or modified by hooks (look for `system-reminder` blocks showing hook output injected as `additionalContext` or `permissionDecisionReason`)
- The session's dominant activity type: code editing, codebase exploration, planning/CLI, mixed

## Step 3 — Cross-reference hooks vs actual tool usage

For each registered hook in `settings.json`, determine whether it fired this session based on whether its matcher tool was called. A hook "had effect" if it produced non-empty output (additionalContext, deny decision with content, or updatedInput).

## Step 4 — Evaluate each hook on four axes

For every hook (whether it fired or not):

1. **Signal quality** — Was the injected context useful? Did it contain info not already available from the file content, native tool output, or CLAUDE.md?
2. **False positive rate** — Did it fire on cases that added noise rather than signal? (e.g., dead code detection catching test helpers, extract injection on small files already being fully read)
3. **Redundancy** — Does a native Claude Code feature (LSP plugin, file content, CLAUDE.md preload, built-in tool behavior) already cover what this hook provides?
4. **Project/language fit** — Are the hook's internal patterns appropriate for the actual codebase language? (e.g., `def funcName` search patterns are Python-only and fail silently on TypeScript projects)

## Step 5 — Generate ranked improvement plan

Produce improvements ordered by impact (most impactful first). Each improvement must be:
- **Specific**: name the exact file and the change (add a size gate, change `deny` to `additionalContext`, add exclude pattern, etc.)
- **Scoped**: one clear change per improvement
- **Justified**: one sentence explaining the observed problem

Format each as:
```
[#] <hook-filename> — <one-line problem statement>
Fix: <exactly what to change and why>
Effort: low | medium | high
```

## Step 6 — Present improvements interactively

Walk through improvements in rank order. For each one:

1. State the problem and fix clearly
2. Use `AskUserQuestion` with these options:
   - **Implement now** — make the change immediately, then move to next improvement
   - **Add context** — incorporate user's feedback and re-present this improvement
   - **Skip** — move on

Make the change before presenting the next improvement when "Implement now" is chosen. After all improvements are processed, give a one-line summary of what changed.

## Evaluation heuristics

**Good hook characteristics:**
- Fires rarely due to scoped matchers + internal early-exit conditions
- Injects context not already in the file or native tool output
- Language/project-aware (reads `detectLanguage()` and branches appropriately)
- Fails silently with `{}` on all error paths — never blocks tool execution

**Problem patterns to flag:**
- Hook fires on broad tool (Read, Edit) with no internal size/type filter → latency tax with low yield
- `deny` decision substituting hook results for actual tool output → stale index becomes invisible incorrect result
- Language-specific patterns (`def X`, `class X`) hardcoded for one language in a multi-language or wrong-language project
- Hook active for file types where it provides zero value (e.g., diagnostics hook configured for Python only but runs and returns `{}` on every TypeScript edit)
- Session-start hook firing every resume with high-noise output (hundreds of results, mostly false positives)
- Duplicates LSP plugin functionality when `enabledPlugins` shows LSP is active
