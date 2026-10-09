# Playbook: audit a flow or screen

The user wants to know how good an existing flow or screen is and what to
change, without a rebuild. The deliverable is a report whose every claim can be
checked, either in a screenshot of the product as it is or in a Mobbin
reference beside it.

## 1. Capture before you read code

Run the product and capture every step in order, before opening the source.
The screenshots are what users see, and they keep the audit from turning into
a code review. Use the loop in **app-design-bar**'s verification reference.

- For a first-run flow, use a clean install or a fresh emulator profile. A
  signed-in device skips steps and redirects differently.
- Stop before the first step with real side effects, such as creating an
  account on a production service or charging a card. Read that step and
  everything after it from code, and list it under "not attempted".
- Save captures as `audit/NN-<step>.png`, in flow order, with
  `adb exec-out screencap -p`. Device captures cost more context than the
  research does: a full-resolution phone capture is about as costly as a whole
  Mobbin sheet, and device tools that return a screenshot after every tap add
  one per interaction. Review captures as a sheet, the same way as research:
  `sheet.py audit/review` with rows like `["03 look", "", "audit/03-look.png"]`.
  Open a single capture at full resolution only for detail you will cite.

Then read only the code you need to explain what you saw: the route layout, the
state model, and each screen's component. A capture tells you what; the code
tells you why and where.

## 2. Map the flow

A table, one row per step: route or screen, what it asks for, the primary
action, the escapes, and any progress indicator. List the branches under it:
errors, empty and loading states, and what back does from each step.

## 3. Find deficits

Write each deficit as a checkable statement, and mark it **V** if you saw it on
the device or **C** if you inferred it from code. Cover both kinds:

- **Behaviour.** Dead ends, lost state, a back that goes somewhere surprising,
  validation that allows nonsense through, a progress indicator that lies.
- **Craft.** Hierarchy, the type ramp against the design system, spacing
  rhythm, colour roles and what the accent is spent on, icon consistency,
  empty bands, platform fidelity. Check these against the project's design
  system document, if it has one, as well as against **app-design-bar**.

Before you file a deficit, rule out your test setup as the cause. Change one
thing at a time, and after anything that restarts the app, such as an Android
font scale change, return to the step and confirm the start state before you
test the next thing.

Before you file a motion or accessibility deficit, read the library's default
in `node_modules`. **app-design-bar**'s `references/motion.md` notes what Reanimated 4
already does under reduced motion.

## 4. Research

Run `search_flows` first for the journey as a whole, then `search_screens` for
the steps with the worst deficits, one query per step. Follow the context
budget in the skill: rows, sheet, notes, next query.

Aim for three to five strong references per step you will recommend changes
to, not an even spread across every step. Log every query as the skill's
research board describes.

## 5. Compare one to one

For each step you will make recommendations about, put the capture beside its
best references on one sheet, with `--cols` set to one more than the number of
references:

```bash
python3 <skill-dir>/scripts/sheet.py audit/compare-look --cols 3 --width 380 --height 820 <<'EOF'
[["Ours: Look", "", "audit/04-look.png"],
 ["Grok Bot", "051333f5-6f99-4de9-81eb-425bc71c1b78", "LbyD9dq5"],
 ["Too Good To Go", "660bc32b-0316-47ce-9ddc-ef1ec9dac482", "Io9UaBAB"]]
EOF
```

Read the sheet, then write what the references do that yours does not, and
what yours already does. This is where recommendations stop being generic: a
side by side often shows the gap is smaller, or different, from what the code
suggested, and it catches recommendations for something the screen already
has.

## 6. Report

1. The flow map.
2. Deficits, ranked by severity, each marked V or C, with the capture it shows
   in. Beneath them, what you ruled out as test setup and what the project
   documents as an accepted limitation, so a reviewer can tell both from
   regressions.
3. The research log and the references kept, each with its `mobbin_url` and
   one line on why.
4. Recommendations, each tied to a deficit and to at least one reference, and
   each stated as what a screenshot must show afterwards.
5. What was verified on the device, what was inferred from code, and what was
   not attempted and why.

Keep the one-to-one sheets beside the report, because they are the fastest way
for the user to judge a recommendation.
