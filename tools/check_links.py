"""Check every internal link in the built site.

Usage: python tools/check_links.py [public_dir]

Walks every HTML file under public/, extracts href/src values that point
inside the site, and checks that the target exists on disk. Fragments are
checked too: a link to /about/#education has to find an element with
id="education" on that page.

Exits non-zero when a link is broken, so it can be used as a build gate.
"""
import io
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urldefrag, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Attributes that carry a URL, per element.
URL_ATTRS = {
    "a": ("href",),
    "link": ("href",),
    "img": ("src",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "iframe": ("src",),
    "video": ("src", "poster"),
    "audio": ("src",),
}


class Collector(HTMLParser):
    """Pull every URL and every id out of an HTML file."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs and attrs["id"]:
            self.ids.add(attrs["id"])
        for attr in URL_ATTRS.get(tag, ()):
            value = attrs.get(attr)
            if not value:
                continue
            if attr == "srcset":
                for part in value.split(","):
                    url = part.strip().split(" ")[0]
                    if url:
                        self.urls.append(url)
            else:
                self.urls.append(value)


def parse(path):
    parser = Collector()
    parser.feed(io.open(path, encoding="utf-8", errors="replace").read())
    return parser


def main():
    public = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "public"))
    if not os.path.isdir(public):
        print(f"no build output at {public}")
        return 1

    # Every file on disk, relative to public/.
    on_disk = set()
    for root, _dirs, files in os.walk(public):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), public).replace("\\", "/")
            on_disk.add(rel)

    # Parse every page once so fragments can be looked up.
    ids_by_page = {}
    pages = [f for f in on_disk if f.endswith(".html")]
    for rel in pages:
        ids_by_page[rel] = parse(os.path.join(public, rel)).ids

    broken = []
    checked = 0
    for rel in pages:
        parser = parse(os.path.join(public, rel))
        for url in parser.urls:
            if url.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:")):
                continue
            path_part, fragment = urldefrag(url)
            if not path_part:
                # A link to "#something" on the same page.
                target_page = rel
            elif path_part.startswith("/"):
                target_page = path_part.lstrip("/")
            else:
                target_page = os.path.normpath(
                    os.path.join(os.path.dirname(rel), path_part)
                ).replace("\\", "/")
            checked += 1

            # A directory URL means its index.html.
            candidates = [target_page]
            if target_page.endswith("/"):
                candidates.append(target_page + "index.html")
            if target_page == "":
                candidates.append("index.html")

            found = next((c for c in candidates if c in on_disk), None)
            if found is None:
                broken.append((rel, url, "target does not exist"))
                continue

            if fragment:
                page_ids = ids_by_page.get(found)
                if page_ids is None:
                    # The target is not an HTML page, so it has no ids.
                    broken.append((rel, url, "fragment target is not an HTML page"))
                elif fragment not in page_ids:
                    broken.append((rel, url, f"no element with id={fragment!r}"))

    print(f"checked {checked} internal links across {len(pages)} pages")
    if broken:
        print(f"\n{len(broken)} broken link(s):")
        for page, url, why in broken:
            print(f"  {page}  ->  {url}   ({why})")
        return 1
    print("no broken internal links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
