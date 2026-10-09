# Native controls

A rebuilt control is the fastest way to make an app read as a web page. Use the
platform control, or a wrapper faithful enough that a user cannot tell.

## The rule

Before building any control, ask what the platform already ships. The answer is
almost always something. A custom control is justified when the platform has
nothing close, or when the brand genuinely needs a different shape and you can
say why. Then match the platform's numbers, per
[When you rebuild a control](#when-you-rebuild-a-control).

## Common controls

| Need | iOS | Android | Package |
|---|---|---|---|
| Boolean toggle | Switch | Material switch | `Switch` from `react-native`, native on both |
| Single choice from 2 to 4 | Segmented control | Segmented buttons or chips | `@react-native-segmented-control/segmented-control` |
| Single choice from 5 or more | Wheel picker in a sheet | Radio list or exposed dropdown | A picker in a sheet, or a list |
| Value in a range | Slider | Material slider | `@react-native-community/slider` |
| Date or time | Wheel or inline calendar | Material pickers | `@react-native-community/datetimepicker`, with `display="inline"` for an iOS calendar |
| Item actions | Context menu | Popup or overflow menu | `zeego`, native menus on both |
| Short choice list or destructive confirmation | Action sheet | Bottom sheet or alert dialog | `@expo/react-native-action-sheet`, which wraps `ActionSheetIOS` |
| Sheet content | Detent sheet | Bottom sheet | Expo Router `formSheet`, or `@gorhom/bottom-sheet` |
| Search | Search in the navigation bar | Search view | Expo Router `headerSearchBarOptions` |
| Pull to refresh | Refresh control | Swipe refresh | `RefreshControl` on the scroll view or list |
| In-app browser | Safari view controller | Custom tabs | `expo-web-browser` |
| Share, pick a photo | System controller | System intent | `expo-sharing`, `expo-image-picker` |
| Haptics | Feedback generators | Vibrator | `expo-haptics` |

A segmented control is for two to four options. Past four, switch to a picker or
a list, because the labels start truncating and the control stops being legible.

## Sheets

Which surface a task gets (modal, sheet, full-screen, overlay) is a navigation
decision, made per [navigation.md](navigation.md). Wiring a sheet well:

- Detents come from the content, through `enableDynamicSizing`, or from the
  platform set of medium and large. Arbitrary percentages read as arbitrary.
- The sheet's drag hands off to inner scroll through the library's
  `BottomSheetScrollView` or `BottomSheetFlashList`, not a plain ScrollView.
- The backdrop fades with the sheet's position, by interpolating
  `animatedIndex`, dims to about 40 percent black, and dismisses on tap.
- Set `keyboardBlurBehavior="restore"` and test with the keyboard up. Most
  sheet bugs in the wild are keyboard interactions.

## Menus

Item actions live in a native context menu anchored to the item, reached by
long press on iOS and by long press or an overflow button on Android. It grows
from the point that invoked it and dismisses on outside tap.

```tsx
<ContextMenu.Root>
  <ContextMenu.Trigger>{card}</ContextMenu.Trigger>
  <ContextMenu.Content>
    <ContextMenu.Item key="share" onSelect={share}>
      <ContextMenu.ItemTitle>Share</ContextMenu.ItemTitle>
      <ContextMenu.ItemIcon ios={{ name: 'square.and.arrow.up' }} />
    </ContextMenu.Item>
    <ContextMenu.Item key="delete" destructive onSelect={confirmDelete}>
      <ContextMenu.ItemTitle>Delete</ContextMenu.ItemTitle>
      <ContextMenu.ItemIcon ios={{ name: 'trash' }} />
    </ContextMenu.Item>
  </ContextMenu.Content>
</ContextMenu.Root>
```

A destructive item carries the `destructive` role and leads to a confirm step,
an action sheet, before anything is deleted.

## Forms and input

- Labels sit above fields. A placeholder is an example, not a label.
- Every input sets `keyboardType`, `autoComplete`, and `textContentType`, which
  choose the keyboard and enable autofill. One-time codes use
  `textContentType="oneTimeCode"`.
- Chain the return key: `returnKeyType="next"` focuses the next field, and the
  last field submits.
- Validate on blur or submit. An error appears beneath its field in the
  platform's error colour and stays until the value is fixed.
- Reach for the platform picker for dates, times, and constrained values.
  Rebuild it only when the product needs a range the platform cannot express.
- High-frequency typing uses uncontrolled inputs, read on submit or blur, per
  [performance.md](performance.md).
- Keyboard avoidance uses `react-native-keyboard-controller`, tested with the
  keyboard up on both platforms.

## Haptics

Haptics accompany a visual change, on the same frame, one per user action,
through `expo-haptics`.

| Moment | Feedback |
|---|---|
| A value crosses a step or snaps to a detent | `Haptics.selectionAsync()` |
| Something settles into place | `Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)` |
| A heavier commitment, such as a long-press drop | `Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)` |
| Success or failure of an action the user waited for | `Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)`, or `Error` |

Scrolling, loops, and state the user cannot see get no haptic. A buzz supports
a visible change; it never stands in for one.

## Icons

Use SF Symbols on iOS and Material Symbols on Android, through `expo-image`
with `source="sf:name"` or through `expo-symbols`. They inherit weight and
optical size from the surrounding type, which is why they stay consistent when
the user changes their text size. The active tab uses the filled variant.

One icon family per screen. A set drawn from two libraries reads as assembled
even when each icon is fine on its own.

## When you rebuild a control

Match the platform's numbers, not your instincts:

- An iOS-style switch: the thumb travels about 22 pt in about 0.2 s, with a
  slight squish.
- Pressed states: opacity 0.4 for plain-text buttons, scale 0.97 with a slight
  darken for filled buttons, springing back on release. Android rows and
  buttons use a ripple.
- Selection cells: the checkmark enters with a short fade and scale, and the
  row flashes the selection colour for about 150 ms.
- The haptic the real control would emit.

## Checking your work

The test is a side-by-side recording against the same control in a shipping
app. Open one reference on one device and your build on another, and watch both
at the same time. If your control settles on a different curve, or its tap
target is smaller, or its label truncates where the reference's does not, it is
not finished.
