# Platform baseline and fidelity

The stack a mobile build assumes, how the laws land in SwiftUI and UIKit, the
native fidelity laws in full, and their Android translation.

## Stack baseline

Default stack assumptions for a mobile app. Override them when the project already
differs, and say so when you do.

- Expo with Expo Router, React Native, TypeScript.
- `react-native-reanimated` for motion, `react-native-gesture-handler` for
  gestures, and `@shopify/flash-list` (FlashList v2) for any list that can
  grow.
- `expo-image` for images, with SF Symbols through `source="sf:name"` on
  iOS. Use `expo-video` and `expo-audio`, never the deprecated `expo-av`.
- `react-native-safe-area-context` for insets. Never hard-code notch numbers.
- `process.env.EXPO_OS` over `Platform.OS` for platform checks, since it
  resolves at compile time.
- Server state in TanStack Query, client state in Zustand or Jotai, per
  [performance.md](performance.md).

For a native Swift project, the same laws land on these APIs:

| Law | SwiftUI |
|---|---|
| Semantic colour | `Color(.label)`, `Color(.secondarySystemBackground)`, and asset-catalog colours with dark variants |
| Symbols | `Image(systemName:)`, with `.symbolRenderingMode` and `.symbolEffect` |
| Continuous corners | `RoundedRectangle(cornerRadius:style: .continuous)` |
| Type ramp | `.font(.title)` and the other text styles, never fixed point sizes, and `.monospacedDigit()` for counts |
| Navigation | `NavigationStack` with `.navigationTitle` and path-based routing, `.sheet` with `.presentationDetents` |
| Motion | `.spring(duration:bounce:)` and `withAnimation`, with `@Environment(\.accessibilityReduceMotion)` |
| Haptics | `.sensoryFeedback` |
| Safe areas and scroll | The defaults are right. Reach for `.safeAreaInset` rather than hard-coded padding |

UIKit follows the same mapping through its own names, such as `UIColor.label`
and `UIImage(systemName:)`.

## Native fidelity laws

These details separate a native app from a web page in a wrapper. Violating one
is a finding, not a preference.

1. **Semantic colour, both themes, from day one.** Use system colour tokens
   through `Color` from `expo-router`, such as `Color.ios.label` and
   `Color.ios.secondarySystemBackground` on iOS, and Material dynamic colours
   on Android. Every screen renders correctly in light and
   dark before it counts as done. Resolve semantic colours to strings before
   handing them to an animated style.
2. **Native controls over rebuilt ones.** Switch, slider, segmented control,
   context menu, date picker: use the platform control or a faithful wrapper,
   per [native-controls.md](native-controls.md). A rebuilt toggle that animates 50 ms off the platform's timing reads as fake
   immediately.
3. **Symbols for iconography.** SF Symbols on iOS, Material Symbols on Android,
   through `expo-image` or `expo-symbols`. They inherit weight and optical size
   and respond to Dynamic Type. One icon family per screen.
4. **Typography carries the hierarchy.** Use the platform type ramp, one
   display size per screen, and tabular numerals,
   `fontVariant: ['tabular-nums']`, for anything that counts, times, or
   prices. `<Text selectable>` on data a user might want to copy.
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
    `contentInsetAdjustmentBehavior="automatic"`. Read size from
    `useWindowDimensions`, which tracks rotation and resizing, rather than
    `Dimensions.get()`.
13. **Targets meet the platform minimum**: 44 pt on iOS, 48 dp on Android,
    extending the hit area with `hitSlop` when the visual is smaller.

## On Android

Several laws above are written in iOS terms. On Android, the same intent lands
in different chrome, and research from Mobbin, which has no Android corpus,
has to be translated rather than copied.

- **Edge to edge.** Apps targeting Android 15 draw under the status and
  navigation bars whether they asked to or not. Pad content with the insets
  rather than assuming bars, and check the bottom action against the gesture
  bar the way you check the home indicator on iOS.
- **Predictive back.** Back is a gesture the user can preview and cancel. Let
  the system animation run, and intercept back only in the two cases the
  navigation laws allow. A custom back handler that ignores the preview reads
  as broken.
- **Press feedback is a ripple.** Use `android_ripple` on `Pressable` for rows,
  cards, and buttons rather than the iOS scale or opacity treatment.
- **Material chrome for Material jobs.** A top app bar rather than a large
  title, a snackbar rather than a toast or an alert for a transient outcome,
  and bottom sheets with a drag handle. Tabs sit in a navigation bar.
- **Dynamic colour is a choice, not a default.** Material You colours are
  available. Adopting them is a product decision; either way, both themes
  still ship.
- **Continuous corners do not exist.** `borderCurve` is ignored on Android, so
  judge the radius scale on its own there.
