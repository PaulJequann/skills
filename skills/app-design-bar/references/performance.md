# Performance

Performance work starts with a measurement and ends with a measurement. A
change made without one is a guess, and guesses inside a render path usually
cost more than they save.

## Measure first

**Mobile.**

- The React profiler for render counts and commit durations.
- A native profiler trace for CPU hotspots and main-thread blocking.
- Cold-start markers from `react-native-performance`. Measure cold starts
  only.
- A release build on the slowest device you support. Development builds and
  simulators hide exactly the jank you are hunting.
- On Android, frame timing from the shell. Run
  `adb shell dumpsys gfxinfo <package> reset`, drive the flow, then read
  `adb shell dumpsys gfxinfo <package>` for the janky-frame percentage and the
  90th and 99th percentile frame times. That is the number to record. Read
  `Janky frames`, not the legacy line. On an emulator the absolute numbers are
  poor even for the system's own apps, so use them only to compare before and
  after on the same AVD, and take the pass or fail number from a device.

**Web.**

- The browser performance panel for long tasks, layout shifts, and paint timing.
- A bundle analysis before any code-splitting decision, so you split the thing
  that is actually large.
- A throttled network profile, because the fast path you develop on is not the
  path your users have.

The number to record is not a feeling. Capture it for the exact interaction
that feels bad, before you change anything, and hold it to a budget:

| Metric | Budget |
|---|---|
| Transition and gesture frame rate | 60 fps, no dropped frames in the hero flow |
| Cold-start time to interactive, mid-tier device | Under 2 s |
| Keystroke to echo | Under 50 ms |
| List fling | No blank cells at fling speed |
| Initial JS bundle | Watch the trend; investigate any jump over 10 percent |
| Web | Time to first meaningful paint, on a throttled profile |

A claim of improvement carries its before and after numbers: 45 to 60 fps,
3.2 s to 1.8 s.

## Perceived performance

- Skeletons only for content whose shape you know. Otherwise reveal
  progressively, and keep the page the user was reading while a part of it
  updates.
- Preload the next screen's data on press-in, not on navigation complete.
- Size image sources correctly, recycle them in lists, and reserve their space
  with a placeholder, such as an `expo-image` thumbhash or blurhash, so nothing
  jumps when they load.

## Jank

Jank is a frame that misses its budget. Three causes, in order of frequency.

1. **Work on the JS thread during a gesture.** A single `runOnJS` or
   `scheduleOnRN` in `onChange` is enough to ruin it. See
   [motion.md](motion.md) for the discipline. A heavy destination screen
   committed mid-transition stalls even UI-thread animation, so defer its
   expensive work until the transition ends, through the navigator's
   `transitionEnd` event or `requestIdleCallback`. `InteractionManager` is
   deprecated.
2. **Re-render storms.** A state change at the top of the tree re-renders
   everything below it. The classic causes are a broad context or store read by
   leaves, inline object and array props into memoized children, and parent
   state that belongs local. Fix the state shape first:
   - Server state in TanStack Query or the project's equivalent, which owns
     caching, retries, and optimistic updates, rather than `useEffect` with
     `fetch`.
   - Client state in an atomic store, Zustand selectors or Jotai atoms, so a
     change re-renders only its consumers.
   - Small persisted client state in MMKV rather than AsyncStorage, once
     latency shows.
   - Typing surfaces uncontrolled: `defaultValue` with `onChangeText` writing
     to a ref or store, committed on submit or debounce.
   - `useDeferredValue` for expensive derived UI, such as filter results,
     behind a fast-changing input.

   Memoization comes last, and only with profiler evidence of wasted renders.
   `useMemo`, `useCallback`, and `React.memo` over a bad shape hide the problem.
   The React Compiler replaces most manual memoization once cascades show up
   in the profiler; check it for bailouts, because a bailed-out hot component
   silently loses the win.
3. **Layout thrash.** Animating a layout property, or measuring inside a render,
   forces a reflow on every frame. Animate transform and opacity and measure
   once, ahead of time.

## Startup

- Defer work that is not needed for the first screen. A splash screen that
  covers a slow import is a symptom, not a fix.
- Load fonts and heavy assets in parallel with the first render rather than
  before it.
- Keep native navigation through `react-native-screens`.
- Inspect the bundle when it grows: `npx react-native bundle --platform ios
  --dev false --bundle-output out.js --sourcemap-output out.map`, then
  `source-map-explorer out.js out.map`. Barrel imports such as
  `import { x } from '@/components'` are the classic silent bloat; import
  from the source file.
- On web, split the bundle by route so the first page ships only its own code.
- Check that the first screen has the data it needs before it renders, rather
  than rendering a skeleton and then replacing it, unless the skeleton is
  genuinely faster.

## Lists

- Virtualize every list that can grow with FlashList, with stable keys. A
  growable list on a ScrollView is the most common single cause of React
  Native jank. A key derived from the
  index defeats the reuse and reintroduces the cost.
- Give rows a fixed or predictable height where the design allows, because
  measurement per row is the expensive path.
- Recycle row components. Give `expo-image` rows a `recyclingKey`, keep
  `renderItem` free of inline closures over large parent scopes, and leave
  entering animations off recycled rows.

## Memory

- The symptom is memory that grows while navigating back and forth. Take heap
  snapshots and hunt JS leaks before blaming native.
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

One change per measurement: a batch cannot tell you which change helped and
which one only added complexity.
