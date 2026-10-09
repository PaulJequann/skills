# Verification loop and device matrix

A screen is finished when it survives this checklist while running, not when it
compiles. Budget as many iterations as it takes. The goal is "I cannot find a
flaw", not "looks fine".

## Loop mechanics

Linux is the default host. It runs the Android emulator and every browser, so
those are the local loop. iOS needs Apple hardware, covered at the end.

**Android emulator.**

1. Boot an AVD with `emulator -avd <name>`, then launch the app with
   `npx expo run:android`, or `npx expo start` and press `a`.
2. Screenshot with `adb exec-out screencap -p > s.png`, or with whatever device
   tool you have. Open the screenshot and study it. Do not trust your memory of
   what you wrote.
3. Interact. Tap every control, type overlong text, background and foreground
   the app, and rotate when the app claims to support it. Hardware back is
   `adb shell input keyevent KEYCODE_BACK`.
4. For motion, record the entire flow, not just the hero transition:
   `adb shell screenrecord --bit-rate 8000000 /sdcard/m.mp4`, stop it with
   Ctrl-C, then `adb pull /sdcard/m.mp4`. A recording stops itself at three
   minutes, so split a long flow. Read it as frames, per
   [motion.md](motion.md).
5. Force every condition from the shell rather than through the settings UI:

| Condition | Command |
|---|---|
| Dark mode | `adb shell cmd uimode night yes`, and `no` to return |
| Large text | `adb shell settings put system font_scale 2.0`, and `1.0` to return |
| Reduced motion | `adb shell settings put global transition_animation_scale 0` and the same for `animator_duration_scale`, then force-stop and relaunch: Reanimated reads the setting at launch |
| Deep link | `adb shell am start -W -a android.intent.action.VIEW -d "<scheme>://<path>"` |
| Offline | `adb shell svc wifi disable` and `adb shell svc data disable` |

Some of these restart the app. Android recreates the activity for any
configuration change missing from `android:configChanges` in the merged
`AndroidManifest.xml`; Expo lists `uiMode` but leaves out `fontScale`, so a
font scale change relaunches the app on its initial route. Toggle one
condition at a time: set it, return to the screen under test by deep link,
confirm it is the start state you meant, screenshot, then reset before the
next. The deep link opens a fresh instance, which is right for layout checks.
Whether the in-progress state survived the restart is a separate state check,
and a lost draft there is a real finding.

Rule these out before filing anything: the dev-client tools button (a floating
gear from `expo-dev-client`), the emulator's stylus handwriting toolbar over
focused fields, and hardware back, which navigates when no keyboard is up.

For a first-run flow, start from a clean profile: `adb shell pm clear
<package>`, or a dedicated AVD that never signed in. A device with a session
skips steps and redirects differently.

When the device tool cannot read the screen, for example when `uiautomator
dump` fails, fall back to `adb exec-out screencap -p` for pixels and
`adb shell input tap <x> <y>` in physical pixels, from `adb shell wm size`.

**Web.**

1. Load the page in a real Chromium or Firefox at the narrow and wide
   breakpoints, and at 200 percent text zoom.
2. Screenshot each state and study it the same way.
3. Drive the keyboard: tab through the whole page, and confirm the focus order
   matches the reading order and that focus is always visible.
4. For motion, record the interaction, such as with Playwright's `recordVideo`
   or a DevTools screencast, and read it as frames. Browser performance panels
   hide jank that a recording shows.
5. Reload mid-flow, and open the deep link directly. The state should survive.

**iOS.**

The iOS Simulator and every SwiftUI or UIKit build need macOS and Xcode. From
Linux, reach iOS one of these ways, and say which one you used:

- An Expo development build or Expo Go on a physical iPhone over the network.
  Record with the phone's screen recorder and transfer the file.
- A remote Mac, such as a spare machine over SSH or a hosted Mac runner, driving
  `xcrun simctl io booted screenshot s.png` and
  `xcrun simctl io booted recordVideo m.mov`.
- Cloud builds for installation on a device, when neither of the above is
  available.

When iOS is a target and none of these is reachable, verify everything else on
Android and web, and report the iOS-only checks as unverified: the Dynamic
Island, the home indicator, and iOS back-swipe behaviour. Do not claim them.

## The full-motion pass

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

Read the recording as frames, one contact sheet per transition, using the
method in [motion.md](motion.md). Hunt for:

- Dropped or stuttered frames against the frame rate you claimed.
- One-frame flashes: unstyled first paint, a wrong-theme frame mid-transition,
  or a colour that briefly renders the wrong token.
- Layout jumps, double-render pops, springs that clip or overshoot into
  content, and elements that reflow after appearing.

The recording plays as one piece, smooth end to end, with no visual glitch. One
bad frame means the flow is not done.

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
| A current Pixel AVD | The local primary target on Linux. Material behaviour, the back gesture, font metrics |
| A small-screen AVD, around 360 dp wide | Layout compression and reachability |
| A current iPhone Pro, with the Dynamic Island | The design target when the product ships on iOS. Reached through a device or a remote Mac |
| A real browser at 375 px | Mobile web is half the traffic |
| A real browser at 1440 px or wider | Layout that only breaks when it stretches |
| A tablet, only if the product claims support | Otherwise letterbox explicitly and say so |

Run the full checklist on the Pixel AVD, and on the iPhone whenever you can
reach one. On the others, verify layout, safe areas, and the hero flow.
