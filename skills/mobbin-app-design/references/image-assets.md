# Image and illustration assets

Illustration is where a careful build most often falls apart, because assets
generated one at a time in different moods read as a patchwork.

## One style system, decided before the first asset

Write the style down as a sentence, then generate everything against it:

> Flat duotone illustration, deep teal and warm sand, no gradients, geometric
> shapes with a 4 px stroke, no faces in detail.

Every asset follows it. Same palette, same lighting, same level of detail, same
background treatment. A set that mixes a 3D clay object with a line drawing
looks assembled even when both are well made.

## Pipeline

1. **Write the style sentence** and keep it in the repository, so the next
   person generates assets that match.
2. **Generate at the highest quality the model offers**, then downscale to the
   densities you need. Never upscale, because upscaling invents detail that was
   not there and shows at 3x.
3. **Prompt for a flat or transparent background** matched to your surface
   colour. A white halo or a wrong-colour matte around a transparent asset is
   an automatic redo, and it is the most common defect.
4. **Export at each density** the platform uses: 1x, 2x, and 3x for mobile, and
   a responsive set with modern formats for web.
5. **Name by role, not by sequence**, so replacing one asset later does not
   require reading every file.

## Prompt patterns

- Name the style, the palette by role, and the subject. "Flat duotone
  illustration of an empty inbox, deep teal and warm sand, geometric, no text"
  gives the model enough constraints to be consistent.
- State what to leave out. Text is the most common failure, because generated
  lettering is usually wrong and a user notices immediately.
- Ask for the composition you need. Empty-state art wants a centred subject with
  room around it. A hero wants space where the headline will sit.
- Generate three and pick one rather than iterating on a single asset forever.
  Variety comes cheap, and one of three usually reads better than the fourth
  revision of the first.

## Icons

Use the platform symbol set first. Generate icons only for concepts the set does
not cover, and generate them as a family in one pass so the stroke weight and
optical size stay consistent. Mixing generated icons with system symbols on one
screen is visible, and it is the reason a screen looks slightly off in a way
that is hard to name.

## Where assets fail

- **Inconsistent lighting.** One asset lit from the top left and another from
  the bottom right.
- **Wrong background.** A colour that matched the old surface colour, left over
  after a theme change.
- **Wrong density.** A 1x asset stretched into a 3x slot, visible as softness
  against crisp type beside it.
- **Text in the image.** Illegible at small sizes and untranslatable at any
  size.
- **A generated icon set used for chrome.** Actions in the interface should use
  the platform's symbols so they inherit weight and respond to text size.

## Checking the set

Put every asset on one screen and look at them together, in both themes, at the
size they will actually appear. Inconsistency that is invisible one asset at a
time is obvious in a grid. Then check each one in place, because an asset that
works on a neutral board can still be wrong against a themed surface.
