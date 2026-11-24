"""Fetch the two free-licence hobby photos: personal/photos/hobby-1.jpg, hobby-2.jpg.

Usage: python tools/make_hobbies.py

Both images come from Wikimedia Commons under a free licence (CC0 / CC BY /
CC BY-SA). The photographer, licence and source page are written to
personal/CREDITS.md so the attribution travels with the demo.
"""
import html
import io
import json
import os
import re
import urllib.parse
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "personal", "photos")
CREDITS = os.path.join(ROOT, "personal", "CREDITS.md")

API = "https://commons.wikimedia.org/w/api.php"

# base name, search term, a word that must NOT appear in the title or the
# description (used to avoid photos of identifiable people)
PHOTOS = [
    ("hobby-1", "Sajek Valley landscape", ("portrait", "man", "woman", "girl", "boy", "people", "child")),
    ("hobby-2", "Dhaka street", ("portrait", "crowd", "people", "child", "woman", "man")),
]

SIZE = (900, 900)
UA = "hugo-personal-website/1.0 (demo template; +https://example.com)"


def api(params):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def strip_tags(value):
    return html.unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


# Words that mean the photo shows a person we could identify. Commons titles
# and descriptions are checked against these, so a photo of a crowd is
# rejected even when the title does not mention one.
PERSON_WORDS = (
    "portrait", "people", "person", "crowd", "child", "children", "woman",
    "women", "man", "men", "boy", "girl", "baby", "student", "worker",
    "vendor", "passenger", "pedestrian", "rickshaw puller", "family",
)


def search(term, exclude, limit=20):
    data = api(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": term,
            "gsrnamespace": 6,
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|size|mime",
            "iiurlwidth": 1200,
        }
    )
    pages = data.get("query", {}).get("pages", {})
    out = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        if info.get("mime") not in ("image/jpeg", "image/png"):
            continue
        meta = info.get("extmetadata", {})
        text = " ".join(
            [
                page.get("title", ""),
                strip_tags(meta.get("ImageDescription", {}).get("value")),
                strip_tags(meta.get("Categories", {}).get("value")),
                strip_tags(meta.get("ObjectName", {}).get("value")),
            ]
        ).lower()
        if any(word in text for word in PERSON_WORDS):
            continue
        if any(word in text for word in exclude):
            continue
        licence = strip_tags(meta.get("LicenseShortName", {}).get("value"))
        author = strip_tags(meta.get("Artist", {}).get("value"))
        if not licence or not author:
            continue
        out.append(
            {
                "title": page.get("title", ""),
                "thumb": info.get("thumburl"),
                "page": info.get("descriptionurl"),
                "licence": licence,
                "author": author,
                "width": info.get("width"),
                "height": info.get("height"),
            }
        )
    return out


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    picked = []
    for base, term, exclude in PHOTOS:
        candidates = search(term, exclude)
        if not candidates:
            raise SystemExit(f"no usable Commons image for {term!r}")
        # Prefer a landscape source big enough to crop from.
        chosen = None
        for c in candidates:
            if (c["width"] or 0) >= 1200 and (c["height"] or 0) >= 900:
                chosen = c
                break
        chosen = chosen or candidates[0]

        raw = fetch(chosen["thumb"])
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        side = min(im.size)
        left = (im.width - side) // 2
        top = (im.height - side) // 2
        im = im.crop((left, top, left + side, top + side)).resize(SIZE, Image.LANCZOS)
        out = os.path.join(OUTDIR, base + ".jpg")
        # Keep every demo file under 200 KB: drop the JPEG quality until it fits.
        quality = 82
        while True:
            im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
            size = os.path.getsize(out)
            if size <= 200_000 or quality <= 55:
                break
            quality -= 6
        chosen["file"] = base + ".jpg"
        picked.append(chosen)
        print(f"OK  {base}.jpg {size} bytes (q{quality})  <- {chosen['title']}")

    with open(CREDITS, "w", encoding="utf-8") as fh:
        fh.write("# Image credits\n\n")
        fh.write(
            "The demo images in this folder come from free sources. Replace a file with\n"
            "your own to make the site yours; the credits below only apply to the demo.\n\n"
        )
        for p in picked:
            fh.write(f"## `{p['file']}`\n\n")
            fh.write(f"- Title: {p['title']}\n")
            fh.write(f"- Photographer: {p['author']}\n")
            fh.write(f"- Licence: {p['licence']}\n")
            fh.write(f"- Source: {p['page']}\n\n")
    print(f"OK  {os.path.relpath(CREDITS, ROOT)}")


if __name__ == "__main__":
    main()
