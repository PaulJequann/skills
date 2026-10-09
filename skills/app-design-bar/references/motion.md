# Motion

Motion is a design decision, not a decoration pass. Decide whether something
should animate before deciding how. Code samples use Reanimated 4 with
`react-native-gesture-handler` and `react-native-worklets`.

## Decide first

Run the frequency gate. Something the user meets a hundred times a day gets the
platform default and nothing else. Tens of times a day gets under 150 ms and
near imperceptible. Occasional surfaces such as sheets and modals get standard
motion. Delight is reserved for rare, first-time moments.

Then name the purpose in one word: feedback, continuity, state change, avoiding
a jarring cut, explanation, or delight. If no word fits, delete the animation.
Passing the gate with no code is a good outcome, and it is the outcome most
often.

Then pick the family. Mixing them up is the most common tell of non-native
motion: a sheet that closes on a fixed 300 ms timing after a fling feels dead,
and a button that springs for 800 ms on tap feels like a toy.

| Family | Driver | Curve | Examples |
|---|---|---|---|
| **Responsive**: the user is touching it | Gesture position and velocity | Spring, seeded with the gesture velocity | Sheet drag, swipe to dismiss, pull to refresh, card pan |
| **Narrative**: the system started it | Time | Timing with a strong ease-out, 150 to 350 ms | Screen entrances, fades, reveals, toasts |

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

One vocabulary per product, defined once and imported everywhere. The
designer form, where duration is perceptual:

```ts
const SNAP = { duration: 400, dampingRatio: 1 };   // settle, no oscillation
const SHEET = { duration: 300, dampingRatio: 0.8 }; // one soft overshoot

offset.set(withSpring(dest, { ...SNAP, velocity: e.velocityY }));
```

Bounce only when the gesture carried momentum, because bounce on a
programmatic transition reads as a bug.

## Timing

Everything that is not gesture-driven is timing, under 300 ms, with a strong
ease-out: `Easing.bezier(0.23, 1, 0.32, 1)`. Built-in curves are too weak to
read as intentional. Entrances ease out.

| Moment | Duration | Treatment |
|---|---|---|
| Press feedback on a button or card | 100 to 150 ms | Scale to 0.97, on press-in |
| Press feedback on a list row | 100 to 150 ms | Background highlight, never scale |
| Bar button | 100 to 150 ms | Opacity |
| Toast or banner | 200 to 300 ms | Slide plus fade |
| Modal or sheet | 300 to 400 ms | Spring or a strong ease-out |

Exits run about 0.7 times the entrance duration, and they leave the way they
came in. Enter from
scale 0.95 with a fade, never from scale 0, because growing from nothing reads
as a pop. Menus grow from their trigger, with centred modals exempt.

## The thread rule

A gesture stays on the UI thread from touch to settle.

```ts
const pan = Gesture.Pan()
  .onChange((e) => { offset.set(offset.get() + e.changeY); })
  .onEnd((e) => {
    const dismiss = offset.get() > H * 0.3 || e.velocityY > 800;
    offset.set(withSpring(dismiss ? H : 0, { ...SNAP, velocity: e.velocityY }));
    if (dismiss) scheduleOnRN(onClose);
  });
```

- Work in worklets with shared values, reading with `.get()` and writing with
  `.set()`, never during render. React state stays out of `onChange`.
- Cross to the JS thread once, at gesture end, with `scheduleOnRN` from
  `react-native-worklets`. It replaces the deprecated `runOnJS`.
- Thresholds combine distance or velocity, so a fast flick from 10 px away
  dismisses.
- A new gesture mid-spring grabs the current animated value, not the
  destination.
- Animate `transform` and `opacity` only. Layout properties force a reflow on
  every frame.
- One `useAnimatedStyle` per animated node, and no allocation in a worklet's
  hot path: no `.map` and no object spread per frame.
- Entering animations belong on fresh mounts. A recycled list row is being
  reused under a new key, so it gets none.
- A collapsing header keeps a fixed height and translates its content inside a
  clip.
- Track the keyboard with `react-native-keyboard-controller`, which follows the
  real keyboard frame by frame, rather than a listener plus a guessed duration.

When a transition stutters, profile before guessing, per
[performance.md](performance.md). The usual causes are a heavy render
committed mid-animation and an image decoding on the UI thread.

## Layout animation

Use layout animation sparingly and with a stated purpose. Sorting a list,
expanding a row, and revealing a section can justify it. Re-laying out on every
keystroke cannot.

```tsx
<Animated.View
  entering={FadeInDown.duration(220).springify().damping(30)}
  exiting={FadeOut.duration(150)}
  layout={LinearTransition.springify().damping(30)}
/>
```

Prefer a single `layout` transition on the container over transitions scattered
across children, since scattered transitions fight each other and produce the
shimmy users notice without being able to name. Stagger list entrances by
index with `delay(index * 40)`, capped at about eight items; past that, the
list enters as a block.

**Continuity without shared elements.** Keep the tapped thumbnail's position
stable while the detail screen fades in over it, measuring it with `measure()`
in a worklet. Match the corner radius and aspect ratio of the origin card and
the destination hero so the eye reads them as one object.

## Scroll-linked effects

```ts
const y = useScrollOffset(scrollRef);
const headerStyle = useAnimatedStyle(() => ({
  opacity: interpolate(y.get(), [0, 64], [0, 1], Extrapolation.CLAMP),
  transform: [{ translateY: interpolate(y.get(), [-100, 0], [-50, 0], Extrapolation.CLAMP) }],
}));
```

Native behaviours worth reproducing exactly:

- The large title collapses into the navigation bar over roughly the first
  52 pt of scroll.
- Content scrolling under a translucent bar gets a fade or blur mask, not a
  hard clip.
- A hero image stretches on overscroll, by interpolating negative offsets into
  scale.

## Reduced motion

Respect the setting on every platform. Spatial motion collapses to a cross-fade.
The platform's own transitions stay as the platform defines them, because the
user has already told the system what they want.

Read the animation library's default before adding a gate or filing a finding.
In Reanimated 4, layout animations and `withTiming` and `withSpring` all follow
the system setting unless given a `reduceMotion` config, and they jump to the
final value. The cross-fade that replaces spatial motion is still yours to
build:

```tsx
const reduceMotion = useReducedMotion();
<Animated.View entering={reduceMotion ? FadeIn.duration(150) : SlideInDown.springify()} />
```

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

You cannot watch a video, so turn the recording into frames and read those.
Note the timestamps where each transition starts, then pull a contact sheet of
one transition, 30 frames on one image:

```
ffmpeg -ss 1.2 -t 0.5 -i m.mov -vf "fps=60,scale=240:-1,tile=6x5" -frames:v 1 sheet.png
```

Read the sheet left to right for the shape of the motion: where it starts, how
it eases, and whether it settles. When a cell looks wrong, extract that window
at full resolution with `-vf fps=60 frames/%03d.png` and read the frames around
it. For a whole-flow pass, sample at `fps=4` first to find the transitions,
then sheet each one. Judging feel at full speed is the user's job; ask them to
watch the recording when feel is the open question.

In the frames, look for a pop at the start or end, a double-render flash where the element
paints twice, a spring that clips or overshoots into other content, elements
that reflow after they appear, and any single frame painted in the wrong theme
or the wrong colour token.

Measure the frame rate rather than trusting the feel. The bar is a sustained
frame rate through every transition of the hero flow, measured on a release
build on the slowest device you support. Development builds and simulators hide
the jank you are hunting.
