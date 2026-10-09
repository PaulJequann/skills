# Child brief template

Fill one brief per child. Every path is absolute. Pick the kind that matches what the pstack skill prescribes.

## Panel kind

Use this for a role that pstack dispatches as `general-purpose`: interrogate reviewers, arena runners and judges, architect runners, how, why, reflect, and swarm workers. Paste the skill's prompt template, filled in, as the Task.

```
You are a <role> in a pstack <skill> run. This brief is your whole task. Do not invoke poteto-mode or any session-start mandate, and do not spawn or delegate subagents.

Read these files in full before working, and cite only files you read:
- <$PSTACK_ROOT/skills/...>
- <repo files in scope>

Begin your reply with a "Read:" block. Give one line per file above, quoting the first non-heading line after its H1 verbatim, or its first line when it has no H1.

Scope: read-only. Do not create, edit, or delete files, and do not run commands that change state.
<or: You own only <paths> in the worktree <dir>. Touch nothing else. Do not commit.>

Task:
<filled pstack prompt template>

Output:
<format the skill expects back>
```

## Agent kind

Use this where pstack prescribes `pstack:poteto-agent`: playbook code delegates and ad-hoc helpers.

```
You are a pstack delegate for <playbook step>. Read <$PSTACK_ROOT>/skills/poteto-mode/SKILL.md in full first, and follow it for this task. Read the principle skills it names for this kind of work under <$PSTACK_ROOT>/skills/. Where it names a Claude Code tool, use your harness's equivalent. Do not delegate further unless this brief says to.

Begin your reply with a "Read:" block. Give one line per pstack file you read, quoting the first non-heading line after its H1 verbatim, or its first line when it has no H1.

Scope: you own only <paths> in <checkout or worktree dir>. Do not commit or push.

Task:
<goal, data shape, acceptance check>

Output:
<what changed, the verification you ran with its output, open questions>
```
