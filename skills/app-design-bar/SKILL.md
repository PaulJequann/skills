---
name: app-design-bar
description: The shipping-quality bar for mobile app interfaces. Use when designing, building, polishing, or auditing screens in a mobile app, meaning React Native, Expo, SwiftUI, or UIKit code, or when mobbin-usage hands off a build. Covers platform fidelity, navigation semantics, anti-slop discipline, motion, state, and a recording-based verification loop that runs on Linux.
---

# App design bar

You are building screens that will sit next to the best-designed products in
the world, within seconds of the user opening them. This skill is the bar and
the method for clearing it. It stands on its own; the research step is sharper
with the Mobbin MCP through **mobbin-usage**.

Each law below is one line. A broken law is a **finding**, not a preference.
The reference named in each heading holds the detail, the platform mapping, and
the edge cases: load it when you build or audit that part of the screen, and
before you file a finding against it.

## Study before you draw

Your first move on any screen is research, not imagination. Shipping products
encode years of iteration.

1. Study 10 or more real screens of the type you are building, from
   different products, through **mobbin-usage**.
2. Extract the pattern, not the pixels: layout skeleton, hierarchy order,
   control choices, spacing rhythm, where the primary action sits, and how
   progress is communicated.
3. Take the proven skeleton and give it your product's voice. A wholesale copy
   of one screen is lazy and legally risky; ignoring every convention users
   know is worse.

## Native fidelity: [references/platform.md](references/platform.md)

The stack baseline, the SwiftUI and UIKit mapping, and the Android translation
live there too. Mobbin has no Android corpus, so an Android target always
loads it.

1. **Semantic colour, both themes, from day one.**
2. **Native controls over rebuilt ones**, per
   [references/native-controls.md](references/native-controls.md).
3. **One symbol family**: SF Symbols on iOS, Material Symbols on Android.
4. **The platform type ramp carries hierarchy**, one display size per screen,
   `fontVariant: ['tabular-nums']` for anything that counts.
5. **Continuous corners** on iOS.
6. **Shadow expresses elevation**, through `boxShadow`, one elevation system.
7. **One spacing rhythm**, 4 or 8, with `gap` over stacked margins.
8. **Safe areas are design surface**: the Dynamic Island, the home indicator,
   and on Android the edge-to-edge bars.
9. **Titles belong to the navigator.**
10. **Haptics are punctuation**: one per action, on the frame of the visual.
11. **Numbers formatted like a product**: 1.4M, 38k, $4.99.
12. **A ScrollView is the route's root** on any screen that can overflow.
13. **Targets meet the platform minimum**: 44 pt on iOS, 48 dp on Android.

## Navigation: [references/navigation.md](references/navigation.md)

Every transition answers three questions: how did the user get here, must they
be able to come back, and what does back do afterwards.

1. **Push goes deeper, replace moves on**: `router.push` versus
   `router.replace`. Back undoes navigation, never an event.
2. **Presentation is meaning**: modal for a task, sheet for an interruption,
   system controller for share and pickers.
3. **One-way doors leave the stack**: sign-in, finished onboarding, purchase,
   behind `Stack.Protected` and landed with `replace`. Back cannot re-enter
   them, and the user keeps their place.
4. **Back is blocked in exactly two cases**, through `usePreventRemove`: an
   irreversible request in flight, and unsaved work in a modal, after asking.
5. **Tabs are peers**, each with its own stack.
6. **Study the grammar**: note whether each step of a reference flow is a
   push, a modal, or a sheet.

## Anti-slop

AI-built interfaces share a look, and users file it under template within
seconds. Palette, materials, and layout come from the references you studied.
Each item is a default ban, lifted when the brand asks for it and you can say
why it fits. The **pre-flight** is the check: run these counts before
a flow reaches verification, and a failed count is a fix, not a judgement call.

| Count | Must be |
|---|---|
| Accent hues across the product | 1, spent on the primary action, active state, and progress |
| Grey families | 1, warm or cool |
| Corner radii outside the stated scale, such as "actions pills, cards 16, inputs 8" | 0 |
| Labels serving one intent, such as "Get started" and "Begin" | 1 |
| Emoji in chrome | 0; symbols are the icon set |
| Gradients, glass, glows, or confetti without a brand reason | 0 |
| Typefaces used for emphasis | 1; emphasis is weight or italic of the same family |
| Screens shipping only the success state | 0; skeletons, empty, and error states are designed |

## Motion: [references/motion.md](references/motion.md)

1. **The frequency gate comes first.** A hundred times a day gets the platform
   default; tens of times gets under 150 ms; delight is for rare, first-time
   moments. Passing the gate with no code is a success.
2. **Name the purpose in one word**, or delete the animation.
3. **A finger means a spring**, seeded with the release velocity.
4. **Everything else is timing under 300 ms with a strong ease-out**,
   `Easing.bezier(0.23, 1, 0.32, 1)`.
5. **Gestures stay on the UI thread**: worklets, transform and opacity only,
   and `scheduleOnRN` once at gesture end.
6. **Reduced motion collapses spatial motion to cross-fades.** Read the
   library's default before gating.
7. **The bar is a measured frame rate** through the hero flow, on a release
   build, on the slowest supported device, per
   [references/performance.md](references/performance.md).

## State and performance

- **Server state** in TanStack Query, which owns caching and retries, **client
  state** in Zustand or Jotai, **ephemeral state** local to its component.
- **Optimistic by default**: taps reflect instantly, reconcile in the
  background, roll back loudly on failure.
- **Uncontrolled inputs** on high-frequency typing surfaces.
- **Virtualize every list that can grow** with FlashList, with stable keys.
- **Measure before and after**, per
  [references/performance.md](references/performance.md).
- **One visual language for illustration**, per
  [references/image-assets.md](references/image-assets.md).

## Verification loop: [references/verification-loop.md](references/verification-loop.md)

A screen exists once you have seen it running.

1. Launch it: the Android emulator locally, an iPhone or a remote Mac for iOS,
   a real browser for web.
2. Screenshot and look: alignment, optical centring, spacing rhythm, long
   content, both themes, large text.
3. Run the **full-motion pass**. Screenshots prove layout and nothing about
   motion.
4. Fix, relaunch, re-verify, until you cannot find a flaw at full zoom on a
   running device.

Once the flow stabilizes and a device-driving tool is available, script the
happy path so later changes re-verify for free.

## Definition of done, per screen

- [ ] 10 or more real references studied, and the adopted pattern named
- [ ] Navigation answered: what back does on every shipped platform, and a
      one-way door that back cannot re-enter
- [ ] Every law above checked, and the pre-flight counts pass
- [ ] Light and dark mode both seen running
- [ ] Safe areas verified on mobile; narrow, wide, and 200 percent zoom on web
- [ ] Long content, empty, loading, and error states designed
- [ ] The whole flow recorded and scrubbed, with no glitch or wrong-colour frame
- [ ] Reduced motion and large text verified on every platform
- [ ] Targets meet the platform minimum, and contrast passes in both themes
- [ ] Assets from one style family, crisp at the densities used
- [ ] Lists virtualized, input smooth, re-renders profiled

## References

| File | Load when |
|---|---|
| [references/platform.md](references/platform.md) | Starting a build, a SwiftUI or UIKit project, any Android target, or filing a fidelity finding |
| [references/navigation.md](references/navigation.md) | Adding a route, modal, sheet, tab, or one-way door, or auditing what back does |
| [references/native-controls.md](references/native-controls.md) | Choosing and wiring controls, menus, pickers, sheets, haptics, and icons |
| [references/motion.md](references/motion.md) | Any animation, gesture, or transition, or a reduced-motion finding |
| [references/verification-loop.md](references/verification-loop.md) | Running the app to verify or audit it: commands, the full-motion pass, the checklist |
| [references/web-surfaces.md](references/web-surfaces.md) | Any browser surface: stack, fidelity, routing, and state laws, plus marketing and pricing pages |
| [references/performance.md](references/performance.md) | Jank, slow startup, perceived speed, large bundles, and memory growth |
| [references/image-assets.md](references/image-assets.md) | Generating illustrations, icons, and hero art |

Adapted from Appllama's
[appllama-app-design-skill](https://github.com/Appllama/appllama-skills/tree/main/skills/appllama-app-design-skill),
MIT licensed.
