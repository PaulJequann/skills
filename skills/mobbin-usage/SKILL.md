---
name: mobbin-usage
description: Search Mobbin through its MCP server and turn real mobile and web screens into a design spec. Use when the Mobbin MCP is connected and the task involves researching UI patterns, walking a multi-step flow, improving or auditing an existing screen, comparing a screen one to one against references, or whenever a search_screens, search_flows or search_sections tool is available. Covers query craft, search modes, the required platform parameter, context-efficient contact sheets, citation, and the research playbooks.
---

# Mobbin usage

Mobbin holds more than 600,000 screens from shipping mobile and web products.
The MCP exposes three search tools and returns the screen images inline, so you
study real interfaces instead of describing them from metadata. This skill is
how you ask, and what to do with what comes back.

Pair it with **app-design-bar** for every build step. This skill decides
what to study, that one decides how to build.

## Ground rules

1. **Describe one screen per call.** The query field takes a single screen and
   the UI elements you would see. Two intents in one query returns the average
   of both.
2. **The platform parameter is required** on `search_screens` and
   `search_flows`, and takes `ios` or `web`. Keep the platform out of the query
   text, because the parameter already filters for it. `search_sections` has no
   platform parameter, since sections are website-only.
3. **Pick the mode by the query.** `search_screens` defaults to
   `mode: "deep"`, which reads intent and ranks noticeably better. `standard`
   matches the words you used and returns in about a third of the time. The
   rule of thumb is under "Modes" below.
4. **Credits are a real but modest cost.** Deep search spends 5 credits;
   standard search, `search_flows` and `search_sections` spend none. A paid
   plan's allowance covers dozens of deep searches a month, so spend them
   wherever they improve the research; quality comes before thrift.
5. **Look at the images, but not all at once.** The tool contract says to
   examine the returned images and forbids describing a screen from its
   metadata alone. A screen you never rendered is a screen you did not study.
   Render them through contact sheets, per "Context budget" below.
6. **Cite every screen you mention** as a markdown link to its `mobbin_url`.
   This is part of the tool contract, and it is what lets the user open and
   judge the screen themselves.
7. **Image URLs expire after 30 days.** Download what you study, since the
   files outlive the links. Re-run the search if a link has died, because the
   screen still exists.
8. **Respect the rate limit.** 60 requests per 60 seconds per user. On a 429,
   wait the `Retry-After` seconds, then back off exponentially.
9. **There is no Android corpus.** `platform` takes `ios` or `web` only. For an
   Android or cross-platform app, research with `ios` and translate what you
   pick through **app-design-bar**'s `references/platform.md`: a pattern carries
   over, its iOS chrome does not. Say in your notes that you did this.

## The three tools

| Tool | What it searches | Result list | Paging |
|---|---|---|---|
| `search_screens` | UI screens across mobile and web | `screens[]`: `id`, `image_url`, `mobbin_url`, `app_name`, `platform` | `exclude_screen_ids` |
| `search_flows` | Multi-step journeys, such as onboarding and checkout | `flows[]`: `id`, `name`, `actions[]`, `screen_count`, `mobbin_url`, `app_name`, `platform`, `screens[]` | `page`, `has_next_page` |
| `search_sections` | Website sections, such as pricing, about, and footer | `sections[]`: `id`, `image_url`, `mobbin_url`, `site_name` | `page`, `has_next_page` |

Every response echoes the `query`, carries the list above as structured
content, and appends the inline preview images after a JSON text block. The
exact payloads are in
[references/response-shapes.md](references/response-shapes.md).

| Parameter | Tools | Values | Notes |
|---|---|---|---|
| `query` | all | 1 to 500 characters | One screen, plain language |
| `platform` | screens, flows | `ios`, `web` | Required on both |
| `mode` | screens | `deep`, `standard`, `fast` | Defaults to `deep` and costs 5 credits. `fast` is a deprecated alias for `standard` |
| `limit` | screens, sections | 1 to 30 | Defaults to 20. The REST API allows 100; the MCP rejects anything above 30 |
| `limit` | flows | 1 to 10 | Defaults to 5 |
| `exclude_screen_ids` | screens | Up to 100 screen IDs | The only way to page screens. A repeated query returns the same IDs, so pass the ones you already have |
| `page` | flows, sections | 1-based | Continue while `has_next_page` is true |
| `image_format` | all | `webp`, `jpg` | Defaults to `webp`. Ask for `jpg` when the destination cannot read webp |
| `task_intent`, `output_destination`, `output_tool` | all | Free text, and `code`, `design_tool`, `doc`, `reference_library`, `chat`, `other` | Optional context about where the results are going. Safe to omit |

## Query craft

Search quality is the whole job, and the rules are narrow:

- Name the elements you would see and how they relate. "Checkout page with a
  promo code field and an Apple Pay button" beats "checkout flow".
- Describe one screen. Split two intents into two calls.
- Skip negations. "Without ads" pulls ads into the results.
- Skip vague style words in standard mode. "Modern" and "clean" match
  nothing; name the treatment instead, such as "dark dashboard with a hero
  number and weekly bars". Deep mode scores intent, so mood words can work
  there.
- Skip disconnected keyword lists. Prose describes a screen, keywords describe
  a bag of words.
- Name an app to filter to it. "Spotify now-playing screen" returns only
  Spotify screens. A screen ID in the query matches nothing.
- Keep the platform out of the query text.

## Modes

Measured on the same four queries in both modes, deep was the better search
every time, and the gap tracks how much the query depends on meaning rather
than words:

| Query kind | Example | Standard | Deep |
|---|---|---|---|
| Named elements | "Checkout screen with a promo code field and an Apple Pay button" | Good, with a few near misses | Good, slightly tighter |
| Behaviour or intent | "Onboarding step the user can skip and finish later" | About a third on target | Nearly all on target |
| Mood and treatment | "Calm dark stats dashboard where one number dominates" | Mixed | Nearly all on target |
| Strategy | "Pricing page that steers users toward the middle tier" | About half | Nearly all |

Deep took 9 to 14 seconds against about 3 for standard.

So the choice is about fit, not price:

- **Deep** for any query that describes behaviour, intent, mood, or strategy,
  and for the searches whose results will shape the design.
- **Standard** for fast, wide sweeps across many phrasings, for paging through
  more of a result set you already judged relevant, and for app-filtered
  lookups such as "Spotify now-playing screen", where the words already carry
  the query.

Credits are counted per successful call, so three deep searches cost 15, and a
search that returns nothing or fails costs nothing. Mobbin has no balance tool,
and no response reports credits. Deep search on the website and through the
MCP share one allowance: 300 a month on Pro, 600 per member on Team and
Enterprise. A grace period starting 5 October 2026, expected to run about six
months, keeps deep search working past the allowance while Mobbin calibrates
enforcement.

## Context budget

Research quality depends on the context you have left when you start judging,
not on how many screens you saw. Each search returns up to 30 preview images,
each one costs context, and hosts cap the images a conversation may carry. In
one trial, four calls put 112 previews into context, and the host then
replaced the earliest with `[media removed: request limit]` before the agent
had written notes on them, so that research was lost. Splitting searches
across more calls does not help, because the cap is on the conversation.

The loop, one query at a time:

1. **Search and return rows, not images.** Through a gateway, return a compact
   row per result and emit nothing:

   ```ts
   const r = await tools.mobbin_mcp.<owner>.<connection>.search_screens({
     query, platform: "ios", mode: "deep", limit: 12 });
   if (!r.ok) return r.error;
   return JSON.stringify(r.data.structuredContent.screens.map(s =>
     [s.app_name, s.id, s.image_url.split("/").pop()]));
   ```

2. **Sheet it.** Pipe those rows into the bundled script, which downloads
   every screen at full resolution and tiles them into one numbered image:

   ```bash
   python3 <skill-dir>/scripts/sheet.py research/<topic>/q1 <<'EOF'
   [["Grok Bot","051333f5-6f99-4de9-81eb-425bc71c1b78","LbyD9dq5"], ...]
   EOF
   ```

   It writes `sheet.png`, the full-resolution files as `NN-<app>-<id>.webp`,
   and `manifest.tsv`. Twelve phone screens make one image of about 1600 by
   1200 pixels, readable enough to triage. Pass `--web` for landscape tiles.
   It needs Pillow with webp support.
3. **Read the sheet, then write notes before the next search.** Per screen
   worth keeping: number, app, `mobbin_url`, one line on what it shows and why
   it matters. Mark the rest off target in one line. Notes written while the
   image is in view survive; notes written from memory three searches later do
   not.
4. **Open finalists at full resolution, one file at a time**, and only the
   ones whose detail you need to cite, such as a control, spacing, or copy.

For `search_screens`, a `limit` of 12 is a good default: one sheet, enough
breadth. Go to 20 or 30 when a sweep is on target, which becomes two or three
sheets. `search_flows` caps at 10.

For flows, return metadata first: `name`, `app_name`, `actions`,
`screen_count`, `mobbin_url`, and `screens[]` in `position` order. Choose
flows from that, then sheet each chosen flow on its own, so the whole journey
reads left to right in one image. A row per flow screen:

```ts
f.screens.sort((a, b) => a.position - b.position).map(x =>
  [`${f.app_name} ${x.position}/${f.screen_count}`, x.screen_id,
   x.image_url.split("/").pop()])
```

Cite a flow screen as the flow's `mobbin_url` plus its position. The inline flow previews are only a sample anyway.

With a direct MCP connection the previews arrive inline whether you want them
or not. Keep `limit` to what you will judge, write notes after every call, and
download from `image_url` for anything you need to look at again.

Load this skill's references and **app-design-bar**'s references when a step
needs them, not all up front. They are long, and reading them first spends the
context the research needs.

## Images and citation

The `image_url` is a `mobbin.com/api/mcp/short/` link that redirects to
Mobbin's image CDN and needs no authentication, so a plain `curl -L` saves it
at full resolution, typically 1180 by 2676 for a phone screen and webp by
default. The inline previews are about 300 pixels wide. For flows, each
preview is preceded by a text label such as `Flow 0: screen 3/5`, and a flow
gets a sample of its screens, typically the first, a middle one, and the last.

A flow's `screens[]` lists every screen in the flow with its own `image_url`
and `position`, not only the previewed ones. Sheet those rather than guessing
what sits between two previews.

Cite as you report. Any screen you name in a response gets a markdown link to
its `mobbin_url`, so the user can open the source rather than trust your
summary of it. Screens link to `mobbin.com/screens/<id>`, flows to
`mobbin.com/flows/<id>`, and sections to `mobbin.com/sites/sections/<id>`.

In hosts that support the MCP Apps specification, meaning ChatGPT, Claude
Desktop and Web, and the Codex App, the server also renders an interactive
gallery of the results. Elsewhere, rely on the images and the rows.

### Through a tool gateway

When Mobbin is reached through a gateway that runs code against connected
tools, rather than as a direct MCP connection, the result is a plain object.
Its `content` array holds the preview blocks and `structuredContent` holds the
lists. Return compact rows from `structuredContent` as above. Emit a preview
block only when you need one specific image and cannot run the script, and
never return base64.

## Playbooks

| Scenario | Reference |
|---|---|
| Build an app or a site from scratch | [references/build-from-scratch.md](references/build-from-scratch.md) |
| Make an existing screen better | [references/improve-a-screen.md](references/improve-a-screen.md) |
| Audit a flow or screen without building, and compare it one to one | [references/audit-a-flow.md](references/audit-a-flow.md) |
| Flow and section research, and the general study method | [references/research-methods.md](references/research-methods.md) |

The build playbooks finish in the verification loop from
**app-design-bar**. Research that never reaches a verified screen is
decoration. An audit finishes in recommendations the user can check in a
screenshot.

For any multi-step subject, such as onboarding, checkout, or account
creation, run `search_flows` before `search_screens`. It costs no credits,
shows how the steps chain, and tells you which single screens deserve a
detailed search.

When a search comes back off target, rephrase it or switch it to deep mode,
and keep at the topic until it has references: a screen without references
is a screen you cannot argue about.

## Local research board

Mobbin image URLs last 30 days, but your notes last longer. Save what you
study:

```
research/
  <category>/
    log.md           # one row per query, see below
    q1/, q2/ ...     # sheet.py output: sheet.png, full-size files, manifest.tsv
    notes.md         # per-screen observations, with the mobbin_url
    patterns.md      # cross-product synthesis
```

`log.md` has one row per call: number, tool, mode, query, results returned,
results on target, and the numbers you kept. When a result is weak, the query
is usually the cause, and the log is what makes the next pass better.
