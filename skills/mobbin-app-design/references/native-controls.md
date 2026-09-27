# Native controls

A rebuilt control is the fastest way to make an app read as a web page. Use the
platform control, or a wrapper faithful enough that a user cannot tell.

## The rule

Before building any control, ask what the platform already ships. The answer is
almost always something. A custom control is justified when the platform has
nothing close, or when the brand genuinely needs a different shape and you can
say why.

## Common controls

| Need | iOS | Android |
|---|---|---|
| Boolean toggle | `Switch` | `Switch` |
| Single choice from 2 to 4 | Segmented control | Segmented button or chips |
| Single choice from 5 or more | Wheel picker in a sheet | Radio list or exposed dropdown |
| Date or time | Platform picker | Platform picker |
| Item actions | Native context menu | Overflow menu |
| Short choice list | Action sheet | Bottom sheet |
| Destructive confirmation | Action sheet with a destructive role | Alert dialog |
| Share, browse, pick a photo | System controller | System intent |

A segmented control is for two to four options. Past four, switch to a picker or
a list, because the labels start truncating and the control stops being legible.

## Sheets and modals

Choose by what the surface is, not by how it looks:

- **Detent sheet** for a short set of choices, a filter panel, or a share
  target. Support drag to dismiss, and resize detents when the content changes.
- **Full-height modal** for a task with steps, with its own Cancel and Done at
  the top.
- **Alert or action sheet** for confirmation, especially destructive
  confirmation, where the platform owns the semantics and the user already
  knows the pattern.
- **Transparent overlay** for something that floats over a screen the user can
  still see: a confirmation card, a lightbox, a coach mark.

A sheet that grows a second step was a modal from the start. Convert it rather
than stacking detents.

## Menus

Use the native context menu for actions on an item, reached by long press on
iOS and by a long press or overflow on Android. Menus grow from the point that
invoked them, and dismiss on outside tap. Never build a menu as an absolutely
positioned list that ignores where it came from.

## Pickers and input

- Reach for the platform picker for dates, times, and constrained values.
  Rebuild it only when the product needs a range the platform cannot express.
- Set the correct keyboard type on every text field. A numeric field that opens
  an alphabetic keyboard is a defect.
- Use uncontrolled inputs for high-frequency typing, and read the value on
  submit or on blur.
- Never fight the keyboard. Track it with the platform keyboard library rather
  than a listener with a guessed duration.

## Haptics

Haptics accompany a visual change, on the same frame, one per user action.

| Moment | Feedback |
|---|---|
| A value crosses a step or snaps to a detent | Selection |
| Something settles into place | Light impact |
| A heavier commitment, such as a long-press drop | Medium impact |
| Success or failure of an action the user waited for | Notification |

Never fire haptics on scroll, in a loop, or as the only feedback for something.
If the user cannot see it, a buzz does not make it clear.

## Icons

Use SF Symbols on iOS and Material Symbols on Android, through `expo-image`
with an `sf:` source or through `expo-symbols`. They inherit weight and optical
size from the surrounding type, which is why they stay consistent when the user
changes their text size.

Do not mix icon families on one screen. A set drawn from two libraries reads as
assembled even when each icon is fine on its own.

## Checking your work

The test is a side-by-side recording against the same control in a shipping
app. Open one reference on one device and your build on another, and watch both
at the same time. If your control settles on a different curve, or its tap
target is smaller, or its label truncates where the reference's does not, it is
not finished.
