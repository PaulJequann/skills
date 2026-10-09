# Performance

Performance work starts with a measurement and ends with a measurement. A
change made without one is a guess, and guesses inside a render path usually
cost more than they save.

## Measure first

**Mobile.**

- The React profiler for render counts and commit durations.
- A native profiler trace for CPU hotspots and main-thread blocking.
- A release build on the slowest device you support. Development builds and
  simulators hide exactly the jank you are hunting.

**Web.**

- The browser performance panel for long tasks, layout shifts, and paint timing.
- A bundle analysis before any code-splitting decision, so you split the thing
  that is actually large.
- A throttled network profile, because the fast path you develop on is not the
  path your users have.

The number to record is not a feeling. Capture frame rate through the hero flow,
and the time to first meaningful paint for web, before you change anything.

## Jank

Jank is a frame that misses its budget. Three causes, in order of frequency.

1. **Work on the JS thread during a gesture.** A gesture must stay on the UI
   thread. See [motion.md](motion.md) for the discipline.
2. **Re-render storms.** A state change at the top of the tree re-renders
   everything below it. Fix the state shape before adding memoization, because
   memoizing a bad shape hides the problem instead of fixing it.
3. **Layout thrash.** Animating a layout property, or measuring inside a render,
   forces a reflow on every frame. Animate transform and opacity and measure
   once, ahead of time.

## Startup

- Defer work that is not needed for the first screen. A splash screen that
  covers a slow import is a symptom, not a fix.
- Load fonts and heavy assets in parallel with the first render rather than
  before it.
- On web, split the bundle by route so the first page ships only its own code.
- Check that the first screen has the data it needs before it renders, rather
  than rendering a skeleton and then replacing it, unless the skeleton is
  genuinely faster.

## Lists

- Virtualize every list that can grow, with stable keys. A key derived from the
  index defeats the reuse and reintroduces the cost.
- Give rows a fixed or predictable height where the design allows, because
  measurement per row is the expensive path.
- Recycle row components, and never attach an entering animation to a recycled
  row.

## Memory

- Remove listeners, subscriptions, and timers when a screen unmounts. A timer
  that outlives its screen keeps the whole tree alive.
- Hold image caches to a stated budget rather than letting them grow with
  scroll.
- Check for retained references after navigating away and back several times.
  A leak that survives ten navigations is a leak users will feel.

## The loop

1. Measure and record the number.
2. Change one thing.
3. Measure again with the same method on the same device.
4. Keep it if the number moved, revert it if it did not.

Do not batch optimizations, because a batch cannot tell you which change helped
and which one only added complexity.
