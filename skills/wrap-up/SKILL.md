---
name: wrap-up
description: End-of-session memory capture running project-level and global reflection in sequence. Use when ending a session, saying "wrap up", or "end session".
---

# wrap-up

End-of-session memory capture. Runs project-level and global reflection in sequence.

**Use when:** Session is ending and there may be learnings worth capturing.

---

## Trigger

User says `/wrap-up`, "wrap up", or "end of session".

---

## Process

### Step 1: Detect project context
Check if the current directory has a `brain/` directory or `.agents/skills/reflect/SKILL.md`.

### Step 2: Project-level reflect (if applicable)
If a project-level reflect skill exists:
- Read and follow `.agents/skills/reflect/SKILL.md`
- Execute its full process (scan for technical learnings, route to brain/)
- If no technical learnings found, say so and move on

If no brainmaxxing installation, skip this step.

### Step 3: Global reflect
Read and follow `~/.claude/skills/reflect-global/SKILL.md`:
- Execute its full process (scan for behavioral corrections, route to CLAUDE.md/rules/)
- If no behavioral signals found, say so

### Step 4: Combined summary
```
## wrap-up summary
- Project reflect: [findings captured / no findings / skipped (no brain/)]
- Global reflect: [findings captured / no findings]
```
