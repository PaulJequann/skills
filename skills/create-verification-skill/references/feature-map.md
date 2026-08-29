# Feature map format

The feature map tells an unfamiliar agent what user behavior exists, how to
reach it, how to drive it, and what proves it worked. Keep commands and handles
literal. Record product behavior, not implementation structure.

## Index contract

`features/README.md` contains:

1. Baseline preconditions for launch, seed state, authentication, and isolation.
2. Driving conventions shared by every feature.
3. Evidence rules, the artifact location, and its retention or ignore policy.
4. An index with one link and scope sentence per feature file.

The index and its sibling feature files must match exactly. State whether a
recipe starts from baseline or carries state from another recipe.

## Feature file contract

Start with an H1 title and one paragraph describing user-visible behavior. Then
use these H2 sections in order.

### `Sub-features`

List short stable IDs, one per distinct behavior. IDs make evidence and run
reports traceable without turning prose into test cases.

### `How to get to it (user POV)`

List every supported user entry point, such as a menu action, shortcut, CLI
command, route, request, or library call. Omit internal setters and test-only
backdoors.

### `Driving it with <driver>`

Begin with `Preconditions:`. Then use labeled bullets. Each bullet contains:

1. the user action;
2. a literal repo-owned command or a tool-neutral operation with a stable
   handle;
3. the observable result; and
4. the evidence to retain when that action needs separate proof.

After the positive recipe, add `Negative control:` with one safe counterexample.
Name the deliberately wrong condition or action, the exact check that must
reject it, and the steps that restore the baseline. The control must be safe to
run locally and must not rely on editing product code.

For example:

```markdown
- **Save the note.** Click the button named `Save note`. A status named
  `Note saved` appears and the editor heading reads `Release checklist`.
- **Confirm persistence.** Return to `All notes` and open `Release checklist`.
  The editor shows the saved title and body. Retain an accessibility snapshot
  at `artifacts/create-note/reopened.txt`.
```

Use exact commands when the repository owns a driver:

```markdown
- **CLI entry.** Run `control-notes cli -- notes create --title "CLI note"
  --body "Created from terminal" --format json`. Exit code `0` and stdout
  contain the new note ID and title. Retain the command, stdout, stderr, and
  exit code at `artifacts/create-note/cli-create.txt`.
```

### `Gotchas`

Record conditions that could waste a run or invalidate its proof, such as focus
rules, eventual consistency, destructive defaults, shared state, or misleading
success messages. Include the recovery when it is not obvious.

## Proof rules

- Capture the action and result, not only a final screen.
- Use structured or accessibility state for semantic UI behavior. Add a
  screenshot when appearance or visual identity matters.
- Record command, stdout, stderr, and exit code for terminal behavior.
- Confirm durable mutation through a safe second view when one exists.
- Retain the negative control's operation, rejection point, and result beside
  the positive evidence when calibration runs.
- Keep evidence after cleanup and label it with the feature ID and entry point.
- Report an unreachable path with the attempted operation and missing
  prerequisite. Never substitute proof from another entry point.
