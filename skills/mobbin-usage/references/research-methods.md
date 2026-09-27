# Research methods

Mobbin is a search surface, not a catalog you walk. You cannot open an app and
page through its screens in journey order, so every study is built from queries
you compose. That makes the question you are answering the only thing keeping
the work honest.

## Pick the tool from the question

| The question sounds like | Reach for |
|---|---|
| "What does a good X screen look like?" | `search_screens` |
| "How do winners structure X end to end?" | `search_flows` |
| "How should this marketing page section work?" | `search_sections` |

A flow is not a screen and a section is not an app screen. "How long is
onboarding, and what does each step earn" is a flows question that
`search_screens` answers badly, because screens arrive without their order.

## Study discipline

- **Name the question before you search.** Every pass answers something your
  task needs, such as "what does a winning paywall carry" or "where does the
  paywall sit in a trial app". Knowing the question is what turns a gallery
  into a spec.
- **Write the query from the answer you want.** Mobbin matches on the elements
  you name. If you cannot name the elements, you do not yet know what you are
  looking for, and the search will show you that quickly.
- **Run standard before deep.** Standard is free and fast, so it is the right
  first probe. Deep spends 5 credits and interprets intent, which is worth it
  only for a query with no good keywords, such as "onboarding where the user
  can skip but finish setup later".
- **Cross-product before within-product.** One screen tells you one team's
  taste. Five screens from five teams tell you the convention. When winners
  diverge, that is a real choice. When they converge, that is a convention you
  break on purpose or not at all.
- **Render every image.** A result you did not look at is not evidence. The
  tool contract asks for this directly, and metadata alone cannot tell you
  where the primary action sits or how the hierarchy reads.
- **Log the query beside the result.** A weak result is usually a weak query.
  The note is what makes the second pass better than the first.
- **Stop at saturation.** The question is answered when new screens stop
  changing your spec. Until then, keep querying, and vary the phrasing, because
  a reworded query surfaces a different set.

## Flow research

Flows are where retention and conversion live, and they are the hardest thing
to study through a search tool. Work within that limit:

1. Search the journey by name and shape, such as "onboarding with a progress
   bar and a skip link" or "checkout with guest option and Apple Pay".
2. Take what comes back as a sample, not a transcript. The previews are spaced
   evenly across the flow, so the steps between them are real and invisible to
   you.
3. Read the spacing as a signal. A flow whose previews jump from account
   creation straight to a paywall is short. One with many previews carries
   decisions in between.
4. Follow the `mobbin_url` when the user needs the complete journey. The
   canonical Mobbin page carries the whole thing, and the MCP tool does not.
5. Say so when you are inferring. A flow studied from three previews supports
   "this style of onboarding is common", not "this app's step four asks for
   notification permission".

High-value journeys to study in almost any category: onboarding length and
what each step earns, paywall placement and trial framing, the first five
seconds after launch, and the category's signature flow.

## Section research

`search_sections` covers websites, which is the half of Mobbin that mobile-only
libraries do not have. Use it for marketing and product sites:

- Pricing pages, including tier structure, anchoring, and where the annual
  toggle sits.
- Footers, including what earns a link and how the sitemap is grouped.
- About and company narrative pages.
- Hero and feature sections, when the question is how a claim gets made.

The same discipline applies. Name the elements you would see, and study several
products before treating anything as a convention. When you are building a
marketing surface, `search_sections` is the primary tool and `search_screens`
is the secondary one.

## Working from the user's own references

Users often arrive with a Mobbin screen already open. Ask for its
`mobbin_url`, which is the canonical link, or for the app and screen name, and
search from that. Studying the screen they chose is faster than guessing at the
one they meant, and it anchors the whole pass to their taste.
