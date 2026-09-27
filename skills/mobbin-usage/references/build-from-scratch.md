# Playbook: build from scratch

The user says "build me a habit tracker" or "build me a landing page for this".
This is the full loop. It ends with a verified build, not a scaffold.

Decide the target surfaces first, because that decision drives every query.
A mobile app means `platform: "ios"` with `search_screens` and `search_flows`.
A website or marketing page means `platform: "web"` with `search_screens` and
`search_sections`. A product with both means two research passes, since the
conventions do not transfer.

## Phase 1: frame the screen list

Turn the request into a list of screens or sections in journey order, before
searching anything. "Habit tracker" becomes welcome, onboarding, permission
request, home with today's habits, habit detail, streak history, paywall,
settings, empty state. A landing page becomes hero, social proof, features,
pricing, FAQ, footer.

The list is the research plan. Everything after this step is answering a
question about one line of it.

## Phase 2: establish the convention

For each screen on the list, run a standard search and study the results:

```
search_screens(query="<screen type, with the elements you expect>",
               platform="ios", mode="standard", limit=20)
```

Budget roughly five to ten screens per type, from different products. Render
every image. As you go, build `research/<category>/notes.md` with the
`mobbin_url` and the query beside each screen.

You are extracting the convention, so track:

- The layout skeleton. Where does the eye land first, and what sits below it?
- What each screen treats as its one job.
- Control choices. Segmented control against tabs, sheet against pushed screen.
- The spacing and radius rhythm, in relative terms if you cannot measure it.
- Where the primary action sits, and how it is distinguished.
- What gets an illustration, and what gets plain text.

Write the cross-product summary into `patterns.md`: what every product does
(table stakes), what only the best do (the edge), and what all of them do badly
(the opening).

## Phase 3: go deep on the decisive questions

Standard search matches words. When the question is about intent rather than
vocabulary, spend the 5 credits:

```
search_screens(query="onboarding where the user can skip a step but finish setup later",
               platform="ios", mode="deep")
```

Deep is worth it for a question like "how do winners handle a user who abandons
the paywall and comes back", where no single element name finds the answer.
Keep it to the two or three questions that decide your design. Budget check: a
handful of deep searches per task is normal; twenty is a problem, and there is
no balance tool to warn you.

For journeys, switch tools rather than modes:

```
search_flows(query="onboarding for a fitness app, with a goal question and a trial paywall")
search_sections(query="pricing page with three tiers and an annual toggle")   # web
```

## Phase 4: write the spec

From `patterns.md`, write the spec the build will follow. It has four parts:

1. **Screen list**, in journey order, one line each, with its job.
2. **Per screen**, the skeleton you adopted and the reference that proves it.
3. **Navigation and routing map.** For every screen, what it is and what back
   does from it, including the one-way doors. The rules come from
   `mobbin-app-design`; the evidence comes from the flows you studied.
4. **The opening.** The thing all the winners do badly, which is where your
   product earns its place.

Every line should be checkable against a screenshot. If a line cannot be
checked, it is a mood, not a spec.

Get user sign-off when they are present. Otherwise state the choices and
proceed.

## Phase 5: build

For every screen, in journey order:

1. Re-open your notes and the downloaded references for that screen type.
   For gaps, run another standard search, and a deep one only if the gap is
   about intent.
2. Implement following **mobbin-app-design** end to end: platform fidelity,
   native controls, motion with the platform's own curves, and boring state.
3. Fill asset gaps with the best image model available at high quality, one
   style system for the whole product, per that skill's asset reference.
4. Run the verification loop until you cannot find a defect. Screenshots for
   layout, a screen recording for motion, both themes, both platforms the
   product claims.

## Phase 6: the bar

Walk the finished product three times as a new user:

- **Happy path.** Every screen in order, nothing skipped.
- **Skeptic path.** Skip everything skippable. Does the product still work, and
  does it still make sense?
- **Abuse path.** Bad input, no network, interrupt mid-flow, and every back
  path, especially immediately after sign-in, onboarding, a purchase, and a
  finished session, where back must not re-enter the old state.

Compare each screen against the best reference you studied. A screen of yours
that is worse than the best equivalent you found goes back into the loop. The
build is not done until every screen survives that comparison.
