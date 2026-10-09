#!/usr/bin/env python3
"""Download Mobbin results and tile them into one numbered contact sheet.

Reads a JSON array on stdin. Each row is [app, id, image] or an object with
app/app_name/site_name, id/screen_id, and image_url. `image` may be a full
image_url, the short code after /api/mcp/short/, or a local file such as a
screenshot of your own screen, which puts it on the same sheet for a side by
side comparison.

    python3 sheet.py research/onboarding/q3 < rows.json

Writes <dir>/NN-<app>-<id8>.<ext> at full resolution, <dir>/manifest.tsv, and
<dir>/sheet.png (sheet-2.png and so on past --per-sheet). Prints the sheet
paths. Needs Pillow with webp support.
"""
import argparse
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SHORT = "https://mobbin.com/api/mcp/short/"


def rows_from(data):
    for i, r in enumerate(data, 1):
        if isinstance(r, (list, tuple)):
            app, sid, img = (list(r) + [None, None, None])[:3]
        else:
            app = r.get("app") or r.get("app_name") or r.get("site_name") or "?"
            sid = r.get("id") or r.get("screen_id") or ""
            img = r.get("image_url") or r.get("image") or r.get("code")
        img = str(img)
        if Path(img).expanduser().is_file():
            url = Path(img).expanduser()
        else:
            url = img if img.startswith("http") else SHORT + img
        yield {"n": i, "app": str(app), "id": str(sid), "url": url}


def fetch(row, out):
    slug = re.sub(r"[^a-z0-9]+", "-", row["app"].lower()).strip("-") or "screen"
    if isinstance(row["url"], Path):
        path = out / f"{row['n']:02d}-{slug}{row['url'].suffix}"
        path.write_bytes(row["url"].read_bytes())
        row["file"] = path
        return row
    req = urllib.request.Request(row["url"], headers={"User-Agent": "mobbin-sheet"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read()
        ctype = resp.headers.get("content-type", "")
    ext = "jpg" if "jpeg" in ctype else "png" if "png" in ctype else "webp"
    stem = "-".join(filter(None, (f"{row['n']:02d}", slug, row["id"][:8])))
    path = out / f"{stem}.{ext}"
    path.write_bytes(body)
    row["file"] = path
    return row


def font(size):
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def tile(rows, cols, width, height, dest):
    pad, label_h = 8, 26
    grid_rows = -(-len(rows) // cols)
    sheet = Image.new(
        "RGB",
        (cols * (width + pad) + pad, grid_rows * (height + label_h + pad) + pad),
        "white",
    )
    draw = ImageDraw.Draw(sheet)
    badge, label = font(22), font(15)
    for k, row in enumerate(rows):
        x = pad + (k % cols) * (width + pad)
        y = pad + (k // cols) * (height + label_h + pad)
        img = Image.open(row["file"]).convert("RGB")
        img.thumbnail((width, height), Image.LANCZOS)
        sheet.paste(img, (x + (width - img.width) // 2, y))
        draw.rectangle((x, y, x + 34, y + 28), fill="black")
        draw.text((x + 5, y + 2), str(row["n"]), fill="white", font=badge)
        draw.text((x, y + height + 4), row["app"][:28], fill="black", font=label)
    sheet.save(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--per-sheet", type=int, default=12)
    ap.add_argument("--width", type=int, default=260, help="tile width in px")
    ap.add_argument("--height", type=int, default=560, help="tile height in px")
    ap.add_argument("--web", action="store_true", help="landscape tiles for web screens")
    args = ap.parse_args()
    if args.web:
        args.cols, args.width, args.height = 3, 520, 340

    rows = list(rows_from(json.load(sys.stdin)))
    args.out.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(8) as pool:
        rows = list(pool.map(lambda r: fetch(r, args.out), rows))

    with open(args.out / "manifest.tsv", "w") as f:
        for r in rows:
            f.write(f"{r['n']}\t{r['app']}\t{r['id']}\t{r['file'].name}\n")

    for s in range(0, len(rows), args.per_sheet):
        chunk = rows[s : s + args.per_sheet]
        name = "sheet.png" if s == 0 else f"sheet-{s // args.per_sheet + 1}.png"
        tile(chunk, args.cols, args.width, args.height, args.out / name)
        print(args.out / name)
    print(f"{len(rows)} images, legend in {args.out / 'manifest.tsv'}")


if __name__ == "__main__":
    main()
