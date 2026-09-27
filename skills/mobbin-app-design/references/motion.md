# Motion

Motion is a design decision, not a decoration pass. Decide whether something
should animate before deciding how.

## Decide first

Run the frequency gate. Something the user meets a hundred times a day gets the
platform default and nothing else. Tens of times a day gets under 150 ms and
near imperceptible. Occasional surfaces such as sheets and modals get standard
motion. Delight is reserved for rare, first-time moments.

Then name the purpose in one word: feedback, continuity, state change, avoiding
a jarring cut, explanation, or delight. If no word fits, delete the animation.
Passing the gate with no code is a good outcome, and it is the outcome most
often.

## Springs

If a finger was involved, it is a spring.

- Capture the live value on grab, so the animation starts from where the element
  actually is rather than from a guessed origin.
- Hand the release velocity into the spring. A spring that ignores the flick
  feels dead.
- Project the target from momentum, so a fast flick commits to the next state
  rather than snapping back.
- Rubber-band past boundaries rather than hard-clamping.
- Stay grabbable mid-flight. A user who catches a moving element should be able
  to steer it.

One vocabulary per product, stated once and reused everywhere. A common pair is
`{ duration: 400, dampingRatio: 1 }` to settle and `{ duration: 300,
dampingRatio: 0.8 }` for a sheet. Bounce only when the gesture carried momentum,
because bounce on a programmatic transition reads as a bug.

## Timing

Everything that is not gesture-driven is timing, under 300 ms, with a strong
ease-out. Built-in curves are too weak to read as intentional. Never ease in on
an entrance.

| Moment | Duration | Treatment |
|---|---|---|
| Press feedback on a button or card | 100 to 150 ms | Scale to 0.97, on press-in |
| Press feedback on a list row | 100 to 150 ms | Background highlight, never scale |
| Bar button | 100 to 150 ms | Opacity |
| Toast or banner | 200 to 300 ms | Slide plus fade |
| Modal or sheet | 300 to 400 ms | Spring or a strong ease-out |

Exits are faster than entrances, and they leave the way they came in. Enter from
scale 0.95 with a fade, never from scale 0, because growing from nothing reads
as a pop. Menus grow from their trigger, with centred modals exempt.

## The thread rule

A gesture must never hop the JS thread.

- Work in worklets with shared values, reading with `.get()` and writing with
  `.set()`.
- Animate `transform` and `opacity` only. Layout properties force a reflow on
  every frame.
- Cross back to the JS thread only at gesture end.
- Never use an entering animation on a recycled list row, because the row is not
  entering, it is being reused under a new key.
- Never animate a header's height. Translate the content inside a fixed clip
  instead.
- Track the keyboard with the platform keyboard library, never with a listener
  plus a guessed duration.

## Layout animation

Use layout animation sparingly and with a stated purpose. Sorting a list,
expanding a row, and revealing a section can justify it. Re-laying out on every
keystroke cannot.

Prefer a single `layout` transition on the container over transitions scattered
across children, since scattered transitions fight each other and produce the
shimmy users notice without being able to name.

## Reduced motion

Respect the setting on every platform. Spatial motion collapses to a cross-fade.
The platform's own transitions stay as the platform defines them, because the
user has already told the system what they want.

## On web

The same decisions apply with different primitives.

- CSS transitions for anything with a defined start and end state. They run off
  the main thread for `transform` and `opacity`, and they are what the browser
  is best at.
- The Web Animations API when you need to control playback, such as pausing or
  reversing mid-flight.
- A spring library when the motion is gesture-driven, matching the physical
  behaviour your references show.
- Animate `transform` and `opacity` rather than `top`, `left`, `width`, or
  `margin`, which trigger layout on every frame.
- Honour `prefers-reduced-motion` in CSS rather than in script, so the
  preference applies before the page becomes interactive.
- Never animate something the user is reading. On a marketing page this most
  often means the pricing table.

## Verifying motion

Record the flow and watch it twice. Once at full speed to judge how it feels,
once scrubbing frame by frame to find what the eye missed at speed.

Look for a pop at the start or end, a double-render flash where the element
paints twice, a spring that clips or overshoots into other content, elements
that reflow after they appear, and any single frame painted in the wrong theme
or the wrong colour token.

Measure the frame rate rather than trusting the feel. The bar is a sustained
frame rate through every transition of the hero flow, measured on a release
build on the slowest device you support. Development builds and simulators hide
the jank you are hunting.
