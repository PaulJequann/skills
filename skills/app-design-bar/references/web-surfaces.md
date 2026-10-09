# Web surfaces

Any screen that runs in a browser: in-product web apps, marketing pages,
pricing, and product sites. They have their own conventions, and Mobbin covers
them. `search_sections` searches website sections, so study real
pricing pages and footers rather than inventing them.

## Stack baseline

Match the project when it already has one.

- Semantic HTML first, because it carries focus order, labels, and roles for
  free. A div with a click handler is a defect, not a style choice.
- The framework the project already uses for routing. Do not introduce a
  second router to build one page.
- Real CSS for layout. Flexbox and grid, with logical properties so
  internationalization does not need a rewrite.
- Design tokens as custom properties, so a theme change is one edit rather than
  a find-and-replace.

## What to research with which tool

| Surface | Reach for |
|---|---|
| Hero, feature, social proof, FAQ sections | `search_sections` |
| Pricing and plan comparison | `search_sections` |
| Footer and sitemap | `search_sections` |
| A full page, to see how sections are ordered | `search_screens` with `platform: "web"` |
| An in-product web app screen, such as a dashboard | `search_screens` with `platform: "web"` |

Section names are conventional words that match well, so `search_sections`
and standard-mode screen searches handle the sweep. When the question is about
strategy rather than parts, such as "pricing page that steers users toward the
middle tier", run a deep `search_screens` with `platform: "web"`, which ranks
that kind of question far better.

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
  percent text zoom. Content reflows at all three rather than clipping.
- **The user's rendering choices win.** Honour `prefers-reduced-motion`,
  `prefers-color-scheme`, and the user's base font size, and leave zoom on.
- **One breakpoint system, stated.** Define the breakpoints once and name them.
  Ad-hoc media queries at arbitrary widths read as assembled.
- **Targets stay reachable.** Interactive targets are at least 24 by 24 CSS
  pixels with spacing, and primary actions are larger. Mobile web gets the
  mobile target rule.

## Routing and state

1. **URL is state.** Anything a user would share, bookmark, or reload into goes
   in the URL: filters, search terms, pagination, the open tab. A reload that
   loses the user's place is a defect.
2. **Links are links.** Navigation uses anchors with real hrefs so that
   middle-click, copy link, and open in new tab work. A router call on a
   click handler alone breaks all three.
3. **Back and forward both work.** The browser's one control is not decoration,
   and intercepting it to run a modal close is a finding unless the URL
   changed.
4. **Loading is a state, not a spinner.** Reserve the layout, then fill it.
   A full-page spinner for a partial update throws away the page the user was
   reading.
5. **Errors reach the user, loudly or not at all.** A failed action either
   surfaces an inline message the user can act on, or retries in the
   background. Silent failure is the worst option and the most common.

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
