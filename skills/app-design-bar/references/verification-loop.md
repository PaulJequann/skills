# Verification loop and device matrix

A screen is finished when it survives this checklist while running, not when it
compiles. Budget as many iterations as it takes. The goal is "I cannot find a
flaw", not "looks fine".

## Loop mechanics

**Mobile.**

1. Launch on the iOS Simulator first, then the Android emulator. Use
   `npx expo start` and press `i` or `a`, or your development build.
2. Screenshot with `xcrun simctl io booted screenshot s.png`, or with whatever
   device tool you have. Open the screenshot and study it. Do not trust your
   memory of what you wrote.
3. Interact. Tap every control, type overlong text, background and foreground
   the app, and rotate when the app claims to support it.
4. For motion, record the entire flow with
   `xcrun simctl io booted recordVideo m.mov`, not just the hero transition.

**Web.**

1. Load the page in a real browser at the narrow and wide breakpoints, and at
   200 percent text zoom.
2. Screenshot each state and study it the same way.
3. Drive the keyboard: tab through the whole page, and confirm the focus order
   matches the reading order and that focus is always visible.
4. For motion, record the interaction, then scrub it. Browser performance
   panels hide jank that a recording shows.
5. Reload mid-flow, and open the deep link directly. The state should survive.

## Per-screen checklist

**Layout**

- [ ] Nothing clipped by the Dynamic Island or status bar, and scrolled content
      passes under it with the intended treatment rather than a hard edge
- [ ] The bottom action clears the home indicator
- [ ] Optical alignment checked at 2x zoom, including icons against text
      baselines and whether centred things actually look centred
- [ ] Spacing comes from the stated rhythm, with no stray 13 in an 8 system
- [ ] Long text wraps or truncates by design, not by accident
- [ ] Empty, loading, and error states each verified by forcing them
- [ ] On web, layout holds at the narrow viewport, the wide viewport, and 200
      percent text zoom

**Theme and type**

- [ ] Dark and light mode both screenshotted and inspected
- [ ] Large text sizes produce no overlap and no clipped labels
- [ ] Secondary text stays readable in both themes
- [ ] Contrast meets the platform minimum on every text and control surface

**Motion**

Evaluated on the full-flow recording, never on stills.

- [ ] Entrances play once, correctly, on first mount, and not again when
      navigating back
- [ ] A gesture follows the finger one to one, releases with velocity, and
      settles cleanly when cancelled mid-gesture
- [ ] Scrubbing frame by frame shows no pop at animation start or end, no
      double-render flash, and no one-frame white or wrong-theme frame
- [ ] Every modal and sheet cycle recorded: present, drag, dismiss, cancel
- [ ] The keyboard appearing and dismissing recorded, with the layout moving
      with it and the focused input staying visible
- [ ] Sustained frame rate through every transition, measured rather than
      eyeballed
- [ ] Reduced motion enabled turns spatial animation into fades

**Interaction**

- [ ] Every target meets the platform minimum size
- [ ] Press, hover, focus, and active states all exist for anything interactive
- [ ] Haptics fire where a platform control would fire them, and never twice
- [ ] The keyboard appears with the right type, does not cover the focused
      input, and dismisses sensibly
- [ ] The back gesture works everywhere it should, on every platform
- [ ] Rapid double taps do not navigate or submit twice
- [ ] On web, every interactive element is reachable and operable by keyboard
      alone

**State**

- [ ] Backgrounding mid-flow and returning preserves state
- [ ] Killing and relaunching restores what should persist and resets what
      should not
- [ ] Offline behaviour is deliberate: actions queue, or they fail loudly. They
      never fail silently
- [ ] On web, reloading preserves anything the user would expect to survive

## Device matrix

| Profile | Why it earns a slot |
|---|---|
| Latest iPhone Pro, with the Dynamic Island | Primary mobile design target |
| A small iPhone, no island | Layout compression and reachability |
| Latest Pixel | Material behaviour, back gesture, font metrics |
| A real browser at 375 px | Mobile web is half the traffic |
| A real browser at 1440 px or wider | Layout that only breaks when it stretches |
| A tablet or iPad, only if the product claims support | Otherwise letterbox explicitly and say so |

Run the full checklist on the primary target. On the others, verify layout,
safe areas, and the hero flow.
