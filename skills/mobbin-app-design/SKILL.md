---
name: mobbin-app-design
description: Build screens that hold up next to real shipping products, for mobile and for web. Use when designing or implementing any interface, including screens, flows, onboarding, paywalls, checkout, marketing pages, pricing sections, tab bars, sheets, settings, and empty states, or when polishing motion, navigation, typography, dark mode, accessibility, or perceived performance. Enforces platform fidelity, semantic colour, native controls, navigation semantics, purposeful motion, a recording-based verification loop, and an anti-slop discipline. Pairs with the Mobbin MCP for reference research.
---

# Mobbin app design

You are building screens that will sit next to the best-designed products in
the world, within seconds of the user opening them. This skill is the bar and
the method for clearing it.

It stands on its own. The research step is sharper with the Mobbin MCP
connected, and the build laws hold with or without it.

## The prime directive: study before you draw

Never design a screen from imagination when you can study how shipping
products solved the same screen. Those products encode years of iteration and
A/B testing. Your first move on any screen is research:

1. Pull real references for the category and the screen type you are building.
   **mobbin-usage** carries the exact playbooks. Study twenty or more screens
   before writing interface code.
2. Extract the pattern, not the pixels: the layout skeleton, the hierarchy
   order, the control choices, the spacing rhythm, where the primary action
   sits, what earns an illustration, and how progress is communicated.
3. Copying one product's screen wholesale is lazy and legally risky. Ignoring
   every convention users already know is worse. Take the proven skeleton, then
   give it your product's voice.

## Platform baseline

Default stack assumptions for mobile. Override them when the project already
differs, and say so when you do.

- Expo with Expo Router, React Native, TypeScript.
- `react-native-reanimated` for motion, `react-native-gesture-handler` for
  gestures, and a virtualized list for anything that can grow.
- `expo-image` for images, with SF Symbols available through `sf:` sources on
  iOS. Use `expo-video` and `expo-audio`, never the deprecated `expo-av`.
- `react-native-safe-area-context` for insets. Never hard-code notch numbers.
- `process.env.EXPO_OS` for compile-time platform checks.

Default stack assumptions for web. Match the project when it already has one.

- Semantic HTML first, because it carries focus order, labels, and roles for
  free. A div with a click handler is a defect, not a style choice.
- The framework the project already uses for routing. Do not introduce a
  second router to build one page.
- Real CSS for layout. Flexbox and grid, with logical properties so
  internationalization does not need a rewrite.
- Design tokens as custom properties, so a theme change is one edit rather than
  a find-and-replace.

## Native fidelity laws

These details separate a native app from a web page in a wrapper. Violating one
is a finding, not a preference.

1. **Semantic colour, both themes, from day one.** Use system colour tokens
   such as `Color.ios.label` and `Color.ios.secondarySystemBackground` on iOS,
   and dynamic colours on Android. Every screen renders correctly in light and
   dark before it counts as done. Resolve semantic colours to strings before
   handing them to an animated style.
2. **Native controls over rebuilt ones.** Switch, slider, segmented control,
   context menu, date picker: use the platform control or a faithful wrapper. A
   rebuilt toggle that animates 50 ms off the platform's timing reads as fake
   immediately.
3. **Symbols for iconography.** SF Symbols on iOS, Material Symbols on Android,
   through `expo-image` or `expo-symbols`. They inherit weight and optical size
   and respond to Dynamic Type. Do not mix three icon families on one screen.
4. **Typography carries the hierarchy.** Use the platform type ramp, one
   display size per screen, and tabular numerals for anything that counts,
   times, or prices. Make text selectable when a user might want to copy it.
5. **Continuous corners.** `borderCurve: 'continuous'` on every rounded
   rectangle. Squircle corners are the cheapest native-feeling win available.
6. **Shadow through the CSS `boxShadow` property**, not the legacy `shadow*`
   and `elevation` props. Shadows express elevation, not decoration. One
   elevation system per app.
7. **One spacing rhythm.** Pick 4 or 8 and never leave it. Prefer flexbox `gap`
   over stacked margins. ScrollView padding belongs in
   `contentContainerStyle`, never on the ScrollView itself.
8. **Safe areas and the Dynamic Island are part of the design.** Verify with
   content scrolled under the island, does the fade or blur treatment hold, and
   with the home indicator, does the bottom action clear it. Check landscape
   when the app supports it.
9. **Navigation titles belong to the navigator.** Use the stack's native title
   and its large-title collapse behaviour rather than a hand-rolled header.
10. **Haptics are punctuation.** A selection tick when a value crosses a
    threshold, a light impact when something settles, a notification for an
    outcome. On the same frame as the visual, one per user action, never the
    only feedback, never on scroll, never in a loop.
11. **Format numbers like a product.** 1.4M, 38k, $4.99. Trim trailing zeros.
    Localize dates.
12. **Root scroll behaviour.** Any screen that can overflow wraps its content
    in a ScrollView as the first component in the route, with
    `contentInsetAdjustmentBehavior="automatic"`. Use `useWindowDimensions`,
    never `Dimensions.get()`.

## Web fidelity laws

The web has its own fidelity bar, and it is not the mobile one with a wider
viewport.

1. **Semantic elements and a real focus order.** Buttons are `button`, links are
   `a` with an href, headings nest without skipping. Keyboard users traverse
   the screen in the order the design reads.
2. **No focus suppression.** Never remove a focus ring without replacing it
   with something at least as visible. A focus style that only matches a
   browser default is a finding.
3. **Hover is not the only affordance.** Every hover state has a focus and an
   active counterpart, because touch and keyboard never hover.
4. **Respect the user's rendering choices.** Honour `prefers-reduced-motion`,
   `prefers-color-scheme`, and the user's base font size. Never disable zoom.
5. **Layout survives the container.** Test the narrow viewport, the wide
   viewport, and a 200 percent text zoom. Content reflows rather than clips.
6. **Text is real text.** Selectable, searchable, and copyable. Text rendered
   into an image is a defect unless it is a logo.
7. **One breakpoint system, stated.** Define the breakpoints once and name them.
   Ad-hoc media queries scattered at arbitrary widths read as assembled.
8. **Targets stay reachable.** Interactive targets are at least 24 by 24 CSS
   pixels with spacing, and the primary actions are larger. Mobile web is
   half the traffic and gets the mobile target rule.

## Navigation laws

Navigation is the part a screenshot cannot show, and users feel it within ten
seconds. Every transition answers three questions: how did the user get here,
must they be able to come back, and what does back do afterwards.

1. **Push goes deeper, replace moves on.** Push when the user will want to
   return. Replace or redirect when returning would land in a state the world
   has moved past. Back undoes navigation, never an event.
2. **Presentation is meaning.** A self-contained task with steps is a modal with
   its own stack and its own Cancel and Done. A short interruption such as a
   picker or a filter is a sheet with detents and drag-to-dismiss. Immersive
   content is a full-screen modal with an explicit close. Something floating
   over a still-visible screen is a transparent overlay. Destructive
   confirmation is an action sheet. Item actions are a native context menu.
   Sharing, browsing, and photo picking use the system controller, never a
   rebuilt route. A sheet that grows a second step was a modal all along. If a
   link could reach it, it is a route, not local state.
3. **One-way doors leave the stack.** Sign-in on an app that requires it,
   completed onboarding including the skip path, a purchase, and a finished
   session. Guard them so that back cannot re-enter the old state. Android back
   from home exits the app rather than showing the login screen, and a paid
   paywall never reopens. Keep the user's place at the same time. Sign-in
   demanded by one action is a modal over the screen that action was taken on,
   and a paywall opened from a feature dismisses back onto that feature,
   unlocked.
4. **Block back in exactly two cases.** An irreversible request in flight, for
   seconds, with visible progress, and unsaved work in a modal, after asking.
   Transient in-screen state such as selection mode or an expanded search
   consumes the first back, and the second back leaves. Anything else that
   traps back, such as a funnel or a rating prompt, is a defect. The edge swipe
   works everywhere else.
5. **Tabs are peers.** No slide between tabs, each tab keeps its own stack, and
   re-tapping the active tab pops that tab to its root. Full-attention screens
   such as a composer, a player, or a checkout live above the tabs in the root
   stack. Deep links land with a real stack underneath. A cold start resolves
   session state before choosing a screen, so no login flashes before home.
6. **Study the grammar, not just the pixels.** While studying a winning flow,
   note what each step is, whether a push, a modal, or a sheet, and match that
   consistency.

## Web routing and state laws

1. **URL is state.** Anything a user would share, bookmark, or reload into goes
   in the URL: filters, search terms, pagination, the open tab. A reload that
   loses the user's place is a defect.
2. **Links are links.** Navigation uses anchors with real hrefs so that
   middle-click, copy link, and open in new tab work. A router call on a
   click handler alone breaks all three.
3. **Back and forward both work.** The browser's one control is not decoration,
   and intercepting it to run a modal close is a finding unless the URL
   changed.
4. **Loading is a state, not a spinner.** Reserve the layout, then fill it.
   A full-page spinner for a partial update throws away the page the user was
   reading.
5. **Errors reach the user, loudly or not at all.** A failed action either
   surfaces an inline message the user can act on, or retries in the
   background. Silent failure is the worst option and the most common.

## Anti-slop laws

AI-built interfaces share a look, and users file it under template within
seconds. Each of these is a default ban. Any of them is permitted when the
brand asks for it and you can say why it fits this product.

1. **No default styling from the model's own taste.** Purple and indigo
   gradient actions with a glow, glassmorphism on every card, mesh-gradient
   heroes, confetti for minor events, sparkles in headings. Your palette,
   materials, and layout come from the references you studied, not from the
   first thing you reach for unprompted.
2. **One accent, locked.** Pick one accent colour and it is the accent on every
   screen. No blue action on one screen and teal on the next, and no new hue
   appearing on screen seven. Neutrals carry the product. The accent is spent
   where the value is, on the primary action, the active state, and progress.
3. **One grey family.** Warm greys or cool greys, never both in one product.
4. **Shape lock.** One corner-radius scale, stated as a rule, such as actions
   are pills, cards 16, inputs 8, and never violated. Mixed radii without a
   stated rule read as assembled from parts.
5. **No emoji as iconography.** Icons are the platform symbol set. Emoji appear
   when the product's voice is genuinely playful, sparingly, in content, and
   never in chrome.
6. **One label per intent.** "Get started", "Start now", and "Begin" are one
   intent. Pick one phrasing and use it everywhere.
7. **Emphasis stays in the family.** Emphasize with weight or italic of the same
   typeface. A serif word injected into a sans headline for interest is
   amateur.
8. **Ship full state cycles.** Success-only is the default failure mode.
   Skeletons match the final layout's shape, empty states are composed and say
   how to fill them, and errors are inline and specific.
9. **The pre-flight is mechanical.** Before a flow reaches verification, count
   distinct accent hues, which must be 1. Count distinct corner radii, which
   must all come from the stated scale. Count emoji in chrome, which must be 0.
   Count gradients without a brand reason, which must be 0. Count labels
   serving one intent, which must be 1. A failed count is a fix, not a
   judgement call.

## Motion laws

Motion is the highest-leverage polish and the easiest thing to overdo. Decide
in this order.

- **The frequency gate comes first.** Something met a hundred times a day, such
  as a tab switch, the keyboard, scroll, or back, gets the platform default and
  nothing else. Something used tens of times a day, such as a press or a row
  select, gets motion under 150 ms and near imperceptible. Sheets, modals, and
  toasts get standard motion. Delight is reserved for rare, first-time moments.
  Passing this gate with zero lines of code is a success. When unsure, delete
  the animation.
- **Name the purpose in one word.** Feedback, continuity, state change,
  avoiding a jarring cut, explanation, or delight. If no word fits, do not build
  it. Data the user is reading never moves for style.
- **If a finger was involved, it is a spring.** Start from the live value
  captured on grab, hand the release velocity into the spring, project the
  target from momentum so a flick commits, rubber-band past boundaries, and stay
  grabbable mid-flight. One vocabulary per product, for example
  `{ duration: 400, dampingRatio: 1 }` to settle and `{ 300, 0.8 }` for sheets.
  Bounce only when the gesture carried momentum.
- **Everything else is timing under 300 ms with a strong ease-out.** Built-in
  curves are too weak. Never ease in on an entrance. Press feedback lands on
  press-in, at 100 to 150 ms: scale to 0.97 on buttons and cards, a background
  highlight rather than scale on list rows, opacity on bar buttons. Exits are
  faster than entrances and leave the way they came in. Enter from scale 0.95
  with a fade, never from scale 0. Menus grow from their trigger, with centred
  modals exempt.
- **A gesture never hops the JS thread.** Worklets and shared values, transform
  and opacity only, no entering animation on recycled list rows, never animate
  a header's height, and track the keyboard with the platform keyboard library
  rather than a listener plus a guessed duration.
- **Respect reduced motion.** Your spatial motion collapses to cross-fades and
  the platform's own transitions stay the platform's.
- **The bar is a measured frame rate through the hero flow on a release build
  on the slowest device you support.** Development builds hide exactly the jank
  you are hunting. See [references/performance.md](references/performance.md).

## State architecture

Screens that feel good have boring state.

- **Server state** lives in a query library that handles caching, retries, and
  optimistic updates. Never a fetch inside an effect.
- **Client state** lives in a small store. A broad application context causes
  the re-render cascades that make an interface feel heavy.
- **Ephemeral state**, such as open, focused, or scrolled, stays local to the
  component that owns it.
- **Optimistic by default.** Taps reflect instantly, reconcile in the
  background, and roll back loudly on failure.
- **Uncontrolled inputs** for high-frequency typing surfaces. A controlled
  input on every keystroke is a top cause of typing jank.
- **Persist small client state** in the fastest available store when latency
  starts to show.

## Perceived performance

- Skeletons only for content whose shape you know. Otherwise reveal
  progressively. Never a full-screen spinner for a partial update.
- Virtualize every list that can grow, with stable keys.
- Preload the next screen's data on press-in, not on navigation complete.
- Size image sources correctly, recycle them in lists, and reserve their space
  with a placeholder so nothing jumps when they load.
- Measure, optimize, and re-measure. Blind memoization is not optimization. The
  method lives in [references/performance.md](references/performance.md).

## Image and illustration assets

When a screen calls for illustration, empty-state art, or imagery beyond the
symbol set:

- Generate assets with the best image model available to you at the highest
  quality it offers, then downscale to the densities you need. Never upscale.
- One visual language per product. Pick a style, such as flat duotone, 3D clay,
  or hand-drawn, and generate every asset in that style, palette, and lighting.
  A mixed-style set reads as template output.
- Prompt for transparent or flat backgrounds matched to your surface colour.
  Composite artifacts such as white halos or wrong-colour mattes are an
  automatic redo.
- Full pipeline and prompt patterns:
  [references/image-assets.md](references/image-assets.md).

## The verification loop

A screen does not exist until you have seen it running. The loop:

1. Implement, then launch it: the simulator or emulator for mobile, the
   browser's device mode and a real browser for web.
2. Screenshot and actually look. Alignment, optical centring, spacing rhythm,
   truncation with long content, both themes, and large text sizes.
3. Run the full-motion pass below. Screenshots prove layout and prove nothing
   about motion.
4. Fix, relaunch, and re-verify. Repeat until you cannot find a defect, then run
   [references/verification-loop.md](references/verification-loop.md) once more.

Do not declare a screen finished from reading the code. Do not stop at "looks
fine". Stop at "I cannot find a flaw at full zoom".

If a device-driving tool is available, script the happy path once the flow
stabilizes so later changes re-verify for free. Verify on a real device or a
real browser before you claim a platform works, because a simulator and a
browser are not the same thing as the hardware.

### The full-motion pass

Evaluate every flow as moving pictures, never as stills. Record the entire flow
end to end and exercise all of it:

- Every transition, push, pop, tab switch, and route change.
- Every back path: the chevron, the edge swipe, the Android hardware back, and
  the browser back button. After each one-way door, attempt a back that must
  fail to re-enter the old state.
- Every modal and sheet: present, drag, dismiss, and cancel mid-drag.
- The keyboard in both directions. Does the layout move with it, is the focused
  input visible, does anything jump when it dismisses?
- Every interaction: press states, gesture follow-through, interrupted
  gestures, rapid taps, and scroll flings at both extremes.
- A reload on web, and a deep link straight into the middle of the flow.

Watch the recording twice: once at full speed for feel, once scrubbing frame by
frame. Hunt for:

- Dropped or stuttered frames against the frame rate you claimed.
- One-frame flashes: unstyled first paint, a wrong-theme frame mid-transition,
  or a colour that briefly renders the wrong token.
- Layout jumps, double-render pops, springs that clip or overshoot into
  content, and elements that reflow after appearing.

The recording plays as one piece, smooth end to end, with no visual glitch. One
bad frame means the flow is not done.

## Definition of done, per screen

- [ ] Studied ten or more real references for this screen type, and can name the
      pattern adopted
- [ ] Navigation answered: what this screen is, what back does from it on every
      platform the product ships, and behind a one-way door, that back cannot
      re-enter the old state
- [ ] Light and dark mode both verified by looking at them
- [ ] Safe areas, the Dynamic Island, and the home indicator verified on mobile
- [ ] Narrow and wide viewport, plus 200 percent text zoom, verified on web
- [ ] Long content, empty, loading, and error states designed rather than
      defaulted
- [ ] Motion: the whole flow recorded and scrubbed, entrances, presses,
      transitions, modals, and keyboard all native in feel, with no glitch frame
      and no wrong-colour frame
- [ ] Reduced motion respected on every platform
- [ ] Large text sizes do not break the layout, and text is selectable where it
      helps
- [ ] Every interactive target meets the platform minimum, and contrast passes
      in both themes
- [ ] Assets come from one style family, are crisp at the densities used, and
      have no compositing halo
- [ ] Lists are virtualized where they can grow, input is not janky, and no
      re-render storms exist, all profiled rather than assumed

## References

| File | Load when |
|---|---|
| [references/verification-loop.md](references/verification-loop.md) | Final verification checklist and device matrix |
| [references/native-controls.md](references/native-controls.md) | Choosing and wiring platform controls, menus, pickers, and sheets |
| [references/motion.md](references/motion.md) | Gesture, transition, spring, and layout animation work |
| [references/web-surfaces.md](references/web-surfaces.md) | Marketing pages, pricing, and other web-specific surfaces |
| [references/performance.md](references/performance.md) | Jank, slow startup, large bundles, and memory growth |
| [references/image-assets.md](references/image-assets.md) | Generating illustrations, icons, and hero art |
