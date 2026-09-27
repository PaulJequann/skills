# Playbook: make an existing screen better

The user has a screen, either as code, a screenshot, or a running app, and wants
it better. Better means measurably closer to the best equivalent screens
shipping today, verified by looking at it, not by reading the diff.

## 1. Diagnose before searching

Run the screen and study it against the definition of done in
`mobbin-app-design`. Name the three worst deficits precisely, as checkable
statements:

- "No hierarchy. Three text rows at the same weight and size."
- "Dead motion. The sheet appears with no transition."
- "Rebuilt segmented control, so it animates differently from the platform's."
- "Only the success state exists. No empty, loading, or error state."

The research pass answers these deficits. Without them you are collecting
inspiration, which is not the job.

## 2. Two sweeps

Run both, because they surface different screens.

**The vocabulary sweep.** Standard mode, several phrasings, one screen per
query:

```
search_screens(query="workout summary with a hero duration and a stats grid",
               platform="ios", mode="standard", limit=20)
search_screens(query="streak statistics screen with weekly bars",
               platform="ios", mode="standard", limit=20)
```

Rewording matters. "Streak statistics" and "weekly progress with bars" return
overlapping but not identical sets, and the second phrasing often reaches
products the first missed.

**The intent sweep.** One or two deep searches, spent on what vocabulary cannot
find:

```
search_screens(query="calm dark stats dashboard where one number dominates and everything else is quiet",
               platform="ios", mode="deep")
```

Style words work here and only here. "Calm" and "quiet" are useless in standard
mode because they match no element, and useful in deep mode because the
pipeline scores intent. That is what the 5 credits buy.

Save everything into `research/<category>/`, with the query recorded beside
each screen. Aim for 30 or more across both sweeps, then pick the 5 to 8 that
actually bear on your deficits and write down why each one earns its place.

For a website or marketing surface, run the vocabulary sweep with
`platform: "web"` and add `search_sections` for the section you are fixing.

## 3. Extract the target

From the picks, write the target as a spec, not a mood board:

- Layout skeleton and the hierarchy order down the screen.
- Control choices, named.
- Type ramp and where each level appears.
- Spacing rhythm, and the radius rule.
- Colour roles, including what the accent is spent on.
- The motion moments, named, with what each one is for.

Every line should be checkable in a screenshot of the rebuilt screen. If a line
cannot be checked, cut it.

## 4. Rebuild and iterate

1. Implement against the spec using **mobbin-app-design**.
2. Generate asset gaps with the best image model available, one style system
   across the whole set.
3. Screenshot, compare side by side with your top references, fix, repeat.
   Record the motion and watch it twice, once at speed and once frame by frame.
   Check both themes, large type sizes, and reduced motion.
4. Stop when the honest side-by-side reads at least as good as the best
   reference. Not "better than before", which is a low bar. If it does not
   read as good, name the gap and go around again.

## 5. When the screen is part of a flow

Screens live in journeys, and a screen that is fine alone can wreck the step
after it. Once the screen passes, walk one step before and one step after in
the running app, and check the entrance transition, the exit, and the state
carried across.

If the screen is a sheet, a modal, or a step behind a one-way door, verify the
presentation matches what it actually is. Use `search_flows` to see how winners
chain the surrounding steps, and remember that flow previews are a sample, so
follow the `mobbin_url` when the chaining is what you need to see.

Finally, ask what back does from this screen, on each platform the product
ships. It is the part no screenshot shows and every user finds in ten seconds.
