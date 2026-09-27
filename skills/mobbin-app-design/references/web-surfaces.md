# Web surfaces

Marketing pages, pricing, and product sites have their own conventions, and
Mobbin covers them. `search_sections` searches website sections, so study real
pricing pages and footers rather than inventing them.

## What to research with which tool

| Surface | Reach for |
|---|---|
| Hero, feature, social proof, FAQ sections | `search_sections` |
| Pricing and plan comparison | `search_sections` |
| Footer and sitemap | `search_sections` |
| A full page, to see how sections are ordered | `search_screens` with `platform: "web"` |
| An in-product web app screen, such as a dashboard | `search_screens` with `platform: "web"` |

Run the vocabulary sweep on standard mode first, because section names are
conventional words that match well. Spend a deep search only when the question
is about intent, such as "pricing page that de-emphasises the middle tier".

## Section order

Most pages follow an order that exists because it works. Deviate with a reason.

1. Hero: what the product is, for whom, and the single next action.
2. Proof: logos, numbers, or a named customer, early enough to pre-empt doubt.
3. Features: grouped by what the user gets, not by how it is built.
4. Pricing, when the product sells directly, after the value is established.
5. Objections: FAQ, security, integration, or migration.
6. Footer: sitemap, legal, and the secondary paths.

Pull three or four pricing sections before designing one. Compare where the
recommended tier sits, whether an annual toggle exists and which side it
defaults to, how the anchor price is framed, and what happens to the layout when
a tier is missing.

## Fidelity on the web

The native fidelity laws do not transfer. These do.

- **Semantic HTML carries behaviour.** A `button` element brings focus, the
  Enter and Space keys, and the right role. A `div` with a click handler brings
  none of them, and you will not remember to add all three.
- **Focus is a design surface.** Every interactive element needs a visible focus
  state that is not the browser default suppressed. Tab through the finished
  page and confirm the order matches the reading order.
- **Hover states need partners.** For every hover rule, write the focus and
  active rule beside it.
- **Text stays text.** Selectable, searchable, translatable. A headline rendered
  into an image fails all three.
- **Images reserve their space.** Set width and height, or an aspect ratio, so
  the page does not shift while it loads.
- **The viewport is not fixed.** Test at 375 px and at 1440 px, and at 200
  percent text zoom. Clipping at any of the three is a defect.

## Performance on the web

The user's perception is dominated by what happens in the first second.

- Ship the content the user came for first, and defer the rest. A hero image
  that blocks the headline is a mistake.
- Size and format images for where they are displayed. A 4000 px source in a
  400 px slot wastes the slowest part of the connection.
- Load fonts in a way that does not hide text, and subset them to the characters
  you use.
- Measure with the browser's performance panel before optimizing anything, and
  measure again after. Optimization without a measurement is a guess.

## Accessibility floor

Not a separate project. These are part of done.

- Every image has alternative text, and decorative images have empty alt.
- Every form field has a label, and every error is announced rather than only
  coloured.
- Colour is never the only signal for state. Pair it with text, an icon, or a
  shape.
- The page works with the keyboard alone, including any modal, which must trap
  focus while open and return it to the trigger when closed.
- The document has one `h1`, and headings nest without skipping levels.

## Definition of done, per web surface

- [ ] Studied three or more real sections of the same type before designing
- [ ] Section set and order chosen deliberately, with a reason for any deviation
      from the conventional order
- [ ] Narrow and wide viewport, and 200 percent text zoom, all verified by
      looking
- [ ] Keyboard-only pass through the whole page, focus always visible
- [ ] Reduced motion and dark mode both honoured
- [ ] Contrast passes on every text and control surface
- [ ] Images reserve their space, so nothing shifts while loading
- [ ] Reload and deep link both land the user where they expect
