---
name: mobbin-usage
description: Search Mobbin through its MCP server and turn real mobile and web screens into a design spec. Use when the Mobbin MCP is connected and the task involves researching UI patterns, studying onboarding, paywall, checkout, pricing or footer screens, walking a multi-step flow, improving an existing screen, or whenever a search_screens, search_flows or search_sections tool is available. Covers query craft, search mode and credit cost, the required platform parameter, image handling, citation rules, and the research playbooks.
---

# Mobbin usage

Mobbin holds more than 600,000 screens from shipping mobile and web products.
The MCP exposes three search tools and returns the screen images inline, so you
study real interfaces instead of describing them from metadata. This skill is
how you ask, and what to do with what comes back.

Pair it with **mobbin-app-design** for every build step. This skill decides
what to study, that one decides how to build.

## Ground rules

1. **Describe one screen per call.** The query field takes a single screen and
   the UI elements you would see. Two intents in one query returns the average
   of both.
2. **The platform parameter is required** and takes `ios` or `web`. Keep the
   platform out of the query text, because the parameter already filters for it.
3. **Standard search first.** `search_screens` defaults to `mode: "deep"`,
   which spends 5 credits. `standard` returns in low latency and spends
   nothing. Reach for deep when the query is genuinely nuanced, not by default.
4. **Budget blind.** Mobbin's MCP has no balance tool, so you cannot check the
   allowance mid-task. The plans ship 300 credits a month on Pro and 600 per
   member on Team and Enterprise, and only deep search spends them. Every
   standard call, `search_flows` and `search_sections` cost nothing.
5. **Look at the images.** The tool contract says to examine the returned
   images and forbids describing a screen from its metadata alone. A screen you
   never rendered is a screen you did not study.
6. **Cite every screen you mention** as a markdown link to its `mobbin_url`.
   This is part of the tool contract, and it is what lets the user open and
   judge the screen themselves.
7. **Image URLs expire after 30 days.** Each result carries a low-resolution
   preview sized for you to read plus a high-resolution `image_url` for
   export. Read the preview, download from `image_url` when the user wants the
   file. Re-run the search if a link has died, because the screen still exists.
8. **Respect the rate limit.** 60 requests per 60 seconds per user. On a 429,
   wait the `Retry-After` seconds, then back off exponentially.

## The three tools

| Tool | What it searches | What it returns |
|---|---|---|
| `search_screens` | UI screens across mobile and web | Matching screens with inline images, app name, platform, and a `mobbin_url` |
| `search_flows` | Multi-step journeys, such as onboarding and checkout | Flow metadata with evenly-spaced preview images and per-screen previews |
| `search_sections` | Website sections, such as pricing, about, and footer | Section images with metadata |

Parameters confirmed against Mobbin's API reference for screens:

| Parameter | Values | Notes |
|---|---|---|
| `query` | 1 to 500 characters | One screen, plain language |
| `platform` | `ios`, `web` | Required |
| `mode` | `deep`, `standard`, `fast` | Defaults to `deep` and costs 5 credits. `fast` is a deprecated alias for `standard` |
| `limit` | 1 to 100 | Defaults to 20 |
| `image_quality` | `optimized`, `high` | Defaults to `optimized`, which is sized for an agent to read |
| `exclude_screen_ids` | Up to 100 screen IDs | Use it to page past results you already have |

`search_flows` and `search_sections` take a natural-language query with no
documented mode parameter, so they do not spend credits.

## Query craft

Search quality is the whole job, and the rules are narrow:

- Name the elements you would see and how they relate. "Checkout page with a
  promo code field and an Apple Pay button" beats "checkout flow".
- Describe one screen. Split two intents into two calls.
- Skip negations. "Without ads" pulls ads into the results.
- Skip vague style words. "Modern" and "clean" match nothing; name the
  treatment instead, such as "dark dashboard with a hero number and weekly
  bars".
- Skip disconnected keyword lists. Prose describes a screen, keywords describe
  a bag of words.
- Name an app to filter to it. "Spotify now-playing screen" searches that app.
- Keep the platform out of the query text.

## Modes and credits

| Call | Credits |
|---|---|
| `search_screens` with `mode: "standard"` | 0 |
| `search_screens` with `mode: "deep"` | 5 per successful search |
| `search_flows` | 0 |
| `search_sections` | 0 |

Credits are counted per call, not per message, so one request that fires three
deep searches costs 15. A search that returns no results, or that fails on
Mobbin's side, costs nothing. Repeating a search counts as a new search.

Since there is no balance tool, the discipline lives in the mode choice. Sweep
broadly with `standard`, then spend a deep search on the one question that
keyword matching cannot answer, such as "onboarding screens where users can
skip steps but still finish setup later".

Mobbin is rolling out credit enforcement with a grace period that started on
5 October 2026. Until it ends, deep search keeps working past the allowance.
Assume the limit is real and treat the grace period as time to calibrate.

## Images and citation

Every result carries two images. The preview is low resolution and exists for
you to read. The `image_url` is high resolution and is what you download when
the user wants a file, a Figma paste, or a document insert. Read the preview,
export from `image_url`.

Cite as you report. Any screen you name in a response gets a markdown link to
its `mobbin_url`, so the user can open the source rather than trust your
summary of it.

In hosts that support the MCP Apps specification, meaning ChatGPT, Claude
Desktop and Web, and the Codex App, the server also renders an interactive
gallery of the results. Do not promise a gallery in a host that cannot render
one. The images in the tool result are the thing you can always rely on.

## Playbooks

| Scenario | Reference |
|---|---|
| Build an app or a site from scratch | [references/build-from-scratch.md](references/build-from-scratch.md) |
| Make an existing screen better | [references/improve-a-screen.md](references/improve-a-screen.md) |
| Flow and section research, and the general study method | [references/research-methods.md](references/research-methods.md) |

Both build playbooks finish in the verification loop from
**mobbin-app-design**. Research that never reaches a verified screen is
decoration.

## Local research board

Mobbin image URLs last 30 days, but your notes last longer. Save what you
study:

```
research/
  <category>/
    apps.md          # the shortlist, with the query that found each one
    screens/         # downloaded images, named by app and screen
    notes.md         # per-screen observations, with the mobbin_url
    patterns.md      # cross-product synthesis
```

Record the query beside each screen. When a result is weak, the query is
usually the cause, and a note of the query that produced it is what makes the
next pass better.

## What is unverified

This skill was written from Mobbin's published documentation and tool
descriptions before a live MCP session. Confirm these on the first real run and
correct the skill:

- The exact field names in an MCP response. The published REST example returns
  `screens[]` with `id`, `image_url`, `image.url`, `image.url_expires_at`,
  `image.width`, `image.height`, `mobbin_url`, `app_name`, and `platform`. The
  MCP payload may differ.
- Whether a result set carries a pagination cursor. Only `limit` and
  `exclude_screen_ids` are documented, so do not assume a cursor exists, and
  page with `exclude_screen_ids` if it does not.
- The shape of a `search_flows` result, including whether each flow carries an
  id and per-screen ids.
- Whether `search_sections` accepts `platform`, and what its payload carries.
- Whether the MCP exposes any filter beyond the query, such as app or screen
  type.

Once connected, run each tool once, save the payloads under `references/`, and
replace this section with the observed shapes.
