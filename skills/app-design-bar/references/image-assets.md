# Image and illustration assets

Illustration is where a careful build most often falls apart, because assets
generated one at a time in different moods read as a patchwork. App-quality art
is generated, curated, and post-processed as one set.

## 1. One style system, decided before the first asset

Write it down once per app, keep it in the repository, and generate everything
against it:

- **Style family**, one of them: flat duotone, gradient mesh, 3D clay, paper
  collage, hand-drawn ink, photographic.
- **Palette**: three to five hexes from the design tokens, including the exact
  surface colour the assets will sit on.
- **Lighting and texture**, in the same words in every prompt, such as "soft
  top-left studio light, matte".
- **Subject grammar**: a mascot, abstract shapes, objects, or people, and if
  people, how they are rendered.

Every prompt is the style system plus a subject. That is what makes twelve
assets read as one commissioned set rather than twelve stock images.

## 2. Generate

Use the best image generation in the environment, such as an imagegen tool, the
Higgsfield MCP or CLI, or another current model.

- **Highest quality, largest size, then downscale.** Target at least twice the
  largest rendered size: an asset shown at 200 pt needs 1200 px or more for 3x.
  Upscaling invents detail that shows at 3x.
- **Three or four candidates per asset.** Pick one, and regenerate the rest of
  the set to match it if the winner drifted in style.
- **Sheets for icon sets and repeated elements**: one prompt, then slice, which
  guarantees shared lighting and palette.
- **Background**: the exact surface hex as a solid fill, or true transparency
  when the tool supports it.

## 3. Prompt pattern

```
[subject], [style family] illustration, [palette words + hexes],
[lighting], solid background #0F0F13, centered composition,
generous negative space, app illustration, no text, no watermark
```

- End every prompt with `no text`. Generated lettering is gibberish at any size
  and untranslatable.
- Empty states want a quiet subject, a resting object or a soft scene, with
  room around it.
- Success states imply motion through composition, such as a tilt or an arc.
- Onboarding heroes leave the third where the headline sits empty; say so in
  the prompt, as in "composition weighted to the bottom half".

## 4. Post-process

1. Inspect edges at 400 percent. A halo, a matte fringe, or JPEG blocking
   around the subject means regenerate or run a background-removal pass.
2. Trim to the content, with consistent padding.
3. Export 1x, 2x, and 3x PNG, or one high-resolution file that `expo-image`
   scales for full-bleed art. WebP for large photographic assets, and a
   responsive set with modern formats on web.
4. Keep each screen-level asset under 200 KB after compression.
5. Check both themes on the device. Art generated on a dark ground often halos
   on a light one, so ship theme twins or place the asset on a
   theme-invariant surface.
6. Name files by role, not by sequence.

## Icons

Interface actions use the platform symbol set, which inherits weight and
responds to text size. Generate icons only for concepts the set lacks, as one
family in one sheet, and keep generated icons off screens that also show system
symbols.

## App icon

Generate at 1024 by 1024, with no transparency and square corners, since the OS
applies the mask. Test it at 60 px; a concept that dies small gets simplified.
Store screenshots and marketing art follow the in-app style.

## Quality gate

Put every asset on one board, in both themes, at the size it will appear, then
check each in place. Reject an asset when any of these holds:

- Its style drifts from the set: lighting, palette, or line weight.
- A halo or fringe shows at 400 percent.
- It carries baked-in text or a watermark.
- The composition fights the layout: the subject is cropped by a safe area, or
  the focal point sits under a button.
- It is soft beside the crisp type next to it, a sign of the wrong density.
- It reads as clip art, the model's default style with no art direction.
