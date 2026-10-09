# Response shapes

Observed from live calls on 27 September 2026, trimmed to two results each.
IDs and short links are real but the `image_url` values expire after 30 days.

Every tool returns an MCP result with two parts:

- `content`: a JSON text block with the same list as `structuredContent` (each
  entry also carries a zero-based `index`), followed by the inline preview
  images as `image/webp` blocks, or `image/jpeg` with `image_format: "jpg"`.
- `structuredContent`: the lists below. Prefer it over parsing the text block.

No response carries credit usage, a balance, an expiry timestamp, or image
dimensions.

## search_screens

```json
{
  "query": "Paywall with a yearly and monthly plan toggle and a free trial button",
  "screens": [
    {
      "id": "355c903b-4580-4f82-bd8f-0c46195fa434",
      "image_url": "https://mobbin.com/api/mcp/short/KTztSzqj",
      "mobbin_url": "https://mobbin.com/screens/355c903b-4580-4f82-bd8f-0c46195fa434",
      "app_name": "Jomo",
      "platform": "ios"
    }
  ]
}
```

One inline preview per screen, in result order. There is no `page` or
`has_next_page`. To get the next batch, repeat the query with
`exclude_screen_ids` set to every `id` you already have; a live test returned
zero overlap. The same query in the same mode returned the same IDs in the same
order, so a repeat without exclusions only spends another call.

Deep mode returns this exact shape.

## search_flows

```json
{
  "query": "Onboarding that asks for notification permission",
  "page": 1,
  "has_next_page": true,
  "flows": [
    {
      "id": "aaf55efd-d945-4196-8e05-e65a1553c571",
      "name": "Onboarding",
      "actions": ["Onboarding", "Turning On/Off"],
      "mobbin_url": "https://mobbin.com/flows/aaf55efd-d945-4196-8e05-e65a1553c571",
      "app_name": "Google",
      "platform": "ios",
      "screen_count": 5,
      "screens": [
        { "screen_id": "7ed5797f-33f4-4a55-8a11-f96f82e88bc9", "image_url": "https://mobbin.com/api/mcp/short/RUdBX0jL", "position": 1 },
        { "screen_id": "28e1c4b5-f377-47c5-ae14-b5f4e4b1e37a", "image_url": "https://mobbin.com/api/mcp/short/h904r6MI", "position": 2 }
      ]
    }
  ]
}
```

`screens[]` holds every screen in the flow, `screen_count` of them, ordered by
`position`. The inline previews are a sample: a three-screen flow previewed all
three, a five-screen flow previewed positions 1, 3 and 5. Each preview is
preceded by a text block such as `Flow 1: screen 3/5`, which names the flow by
its zero-based index and the screen by its position.

Default `limit` is 5 and the maximum is 10. Five flows produced 19 previews.

## search_sections

```json
{
  "query": "Pricing section with three tiers and a monthly annual toggle",
  "page": 1,
  "has_next_page": true,
  "sections": [
    {
      "id": "f66ba39e-9d4f-4336-955d-8721fef92d47",
      "image_url": "https://mobbin.com/api/mcp/short/csIZqC8T",
      "mobbin_url": "https://mobbin.com/sites/sections/f66ba39e-9d4f-4336-955d-8721fef92d47",
      "site_name": "Oku"
    }
  ]
}
```

The name field is `site_name`, not `app_name`, and there is no `platform`
field. The tool's schema has no `platform` parameter; passing one is accepted
and ignored.

## Image links

`image_url` is a short link that answers `302` with `cache-control: no-store`
and redirects to a signed `bytescale.mobbin.com` URL. It needs no auth header,
so `curl -sSL -o <file> <image_url>` saves the full-resolution image. A phone
screen came back at 1180 by 2676 pixels, against roughly 300 pixels wide for
the inline preview.

## Validation errors

Out-of-range arguments fail with MCP error `-32602` and a message naming the
field and bound, for example `Too big: expected number to be <=30` for
`limit: 100` on `search_screens`.
