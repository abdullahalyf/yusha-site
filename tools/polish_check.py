"""Polish pass: build the site against hostile profile data and look for
layout breakage.

Every case below is a variant of personal/profile.yaml that a real site
owner could plausibly ship. For each case the script builds the site,
serves it, loads every page in Chrome at mobile and desktop widths and
reports:

  * horizontal overflow (document scrollWidth > viewport width)
  * elements that stick out past the right edge of the document
  * images with a missing or empty alt attribute
  * more than one <h1> on a page
  * a section that renders with no visible content at all

Usage:
    python tools/polish_check.py             # every case
    python tools/polish_check.py long-name   # only cases matching a name
    STYLE=orchid python tools/polish_check.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shoot import Cdp, free_port, start_chrome, wait_for_devtools  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUGO = os.environ.get("HUGO_BIN", "hugo")
PROFILE = os.path.join(ROOT, "personal", "profile.yaml")
BACKUP = PROFILE + ".polishbak"
PUBLIC = os.path.join(ROOT, "public-polish")

PAGES = ["/", "/about/", "/projects/", "/contact/"]
WIDTHS = [("mobile", 375, 780), ("desktop", 1280, 900)]

BASE = open(PROFILE, encoding="utf-8").read()


def _section(text):
    """Return the part of profile.yaml from `text:` up to the next top-level key."""
    start = BASE.index(text)
    rest = BASE[start + len(text):]
    end = len(rest)
    for i, line in enumerate(rest.split("\n")):
        if i > 0 and line and not line[0].isspace() and not line.startswith("#"):
            end = rest.index("\n" + line)
            break
    return BASE[start:end + len(text)]


def _replace_block(text, source):
    """Swap the top-level `text:` block of profile.yaml for `source`."""
    start = BASE.index(text)
    rest = BASE[start + len(text):]
    end = len(rest)
    for i, line in enumerate(rest.split("\n")):
        if i > 0 and line and not line[0].isspace() and not line.startswith("#"):
            end = rest.index("\n" + line)
            break
    return BASE[:start] + source + rest[end:]


LONG_NAME = (
    BASE.replace('name: "Tanvir Rahman"', 'name: "Mohammad Abdullah Al Mamun Chowdhury"')
    .replace('short_name: "Tanvir"', 'short_name: "Abdullah"')
    .replace(
        'photo_alt: "Portrait of Tanvir Rahman"',
        'photo_alt: "Portrait of Mohammad Abdullah Al Mamun Chowdhury"',
    )
)

LONG_PROJECT = BASE
for old, new in [
    (
        "Campus Lost & Found",
        "An Interdepartmental Campus Lost, Found and Redistribution Services "
        "Platform With Real-Time Notifications",
    ),
    (
        "Bus Time Bot",
        "A Public Transit Schedule Aggregator And Departure Notification Bot "
        "For University Shuttle Services",
    ),
    (
        "Shop Ledger",
        "A Lightweight Point Of Sale And Stock Ledger Application For Small "
        "Family Retail Hardware Outlets",
    ),
    (
        "Study Deck",
        "A Spaced Repetition Flashcard Platform With Adaptive Scheduling And "
        "Collaborative Deck Authoring",
    ),
]:
    LONG_PROJECT = LONG_PROJECT.replace(f'title: "{old}"', f'title: "{new}"')

ZERO_PROJECTS = _replace_block(
    "projects:",
    'projects: []\n',
)

ONE_PROJECT = _replace_block(
    "projects:",
    "projects:\n"
    '  - title: "Campus Lost & Found"\n'
    '    summary: "A web app where students post and claim lost items on campus."\n'
    '    tech: ["Laravel", "MySQL"]\n'
    '    live: "https://example.com"\n'
    '    code: ""\n'
    "    featured: true\n",
)

SEVEN_PROJECTS = _replace_block(
    "projects:",
    "projects:\n"
    + "".join(
        f'  - title: "Project Number {i}"\n'
        f'    summary: "Summary for project {i}. It does one thing well and '
        f'that thing is useful to somebody."\n'
        f'    tech: ["Laravel", "MySQL"]\n'
        f'    live: ""\n'
        f'    code: ""\n'
        f"    featured: {str(i <= 2).lower()}\n"
        for i in range(1, 8)
    ),
)

LONG_BIO = _replace_block(
    "bio:",
    "bio: |\n"
    "  I'm a Computer Science student who likes turning messy real-world "
    "problems into simple software. Most of my work is small web apps for "
    "people I know: shops, clubs and classmates, and this paragraph exists to "
    "be deliberately long so that the layout has to cope with a wall of text "
    "that never ends and simply keeps going for a very long time without any "
    "relief at all.\n"
    "\n"
    "  I started with a lost-and-found board for my campus because things kept "
    "disappearing between the canteen and the library. It turned into a Laravel "
    "app with 300 students on it, and after that I stopped looking for big "
    "ideas and started looking for small problems that already have an "
    "audience, which is a lesson I keep relearning every time somebody asks me "
    "what I am building next and I answer with the truth, which is usually "
    "that I am building nothing at all until a small problem walks up and "
    "introduces itself.\n"
    "\n"
    "  Outside class I work with our programming club, take part in the "
    "university's contest once a year, and write about what I break along the "
    "way. I want to work as a backend engineer after graduation, ideally on a "
    "team where shipping is more important than pitching, and where the person "
    "next to me will tell me when my migrations are wrong instead of waiting "
    "until the production incident review.\n",
)

NO_PHONE = BASE.replace('phone: "+880 1712-345678"', 'phone: ""')

# The second project has no photo: personal/photos/project-2.* is removed
# from the mount for this case.
NO_IMAGE_PROJECT = _replace_block(
    "projects:",
    "projects:\n"
    '  - title: "Campus Lost & Found"\n'
    '    summary: "A web app where students post and claim lost items on campus."\n'
    '    tech: ["Laravel"]\n'
    '    live: "https://example.com"\n'
    '    code: ""\n'
    "    featured: true\n"
    '  - title: "A Project With No Screenshot At All"\n'
    '    summary: "This project deliberately has no photo, so the card has to work without one."\n'
    '    tech: ["Python"]\n'
    '    live: ""\n'
    '    code: ""\n'
    "    featured: true\n",
)

# The gallery section hides itself when there is no `gallery:` list and no
# images in personal/photos/gallery/. The folder is hidden for this case.
EMPTY_GALLERY = _replace_block("gallery:", "gallery: []\n")

# A gallery with images but no list: the images are still shown, in name
# order, and simply have no captions.
NO_GALLERY_LIST = _replace_block("gallery:", "gallery: []\n")

# The achievements stay, but none of them has a certificate image.
ACHIEVEMENTS_NO_IMAGES = BASE

# `highlight_academics: true` puts the results first in the facts row, and
# with fewer than two projects the home page leads with the achievements.
ACADEMICS_HIGHLIGHT = (
    BASE.replace("highlight_academics: false", "highlight_academics: true")
    .replace(
        "academics: []",
        'academics: ["CGPA 3.70 / 4.00", "SSC GPA 5.00", "HSC GPA 5.00"]',
    )
)

CASES = {
    "long-name": LONG_NAME,
    "long-project-titles": LONG_PROJECT,
    "zero-projects": ZERO_PROJECTS,
    "one-project": ONE_PROJECT,
    "seven-projects": SEVEN_PROJECTS,
    "long-bio": LONG_BIO,
    "no-phone": NO_PHONE,
    "project-no-image": NO_IMAGE_PROJECT,
    "empty-gallery": EMPTY_GALLERY,
    "no-gallery-list": NO_GALLERY_LIST,
    "achievements-no-images": ACHIEVEMENTS_NO_IMAGES,
    "academics-highlight": ACADEMICS_HIGHLIGHT,
}

# Files that a case hides, so the "no image" case really has no image.
HIDE_FILES = {
    "project-no-image": ["project-2.jpg", "project-2.jpeg", "project-2.png",
                         "project-2.webp"],
    "achievements-no-images": ["award-1.jpg", "award-1.jpeg", "award-1.png",
                               "award-1.webp", "award-2.jpg", "award-2.jpeg",
                               "award-2.png", "award-2.webp", "award-3.jpg",
                               "award-3.jpeg", "award-3.png", "award-3.webp"],
}

# Whole folders a case hides, so the section really has nothing in it.
HIDE_DIRS = {
    "empty-gallery": ["gallery"],
}

AUDIT_JS = r"""
(() => {
  const vw = document.documentElement.clientWidth;
  const out = {overflow: false, offenders: [], alt: [], h1: 0, empty: [],
               docWidth: document.documentElement.scrollWidth, vw: vw};
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (r.right > vw + 1) {
      const cs = getComputedStyle(el);
      if (cs.position === 'fixed') continue;
      out.offenders.push({
        tag: el.tagName.toLowerCase(),
        cls: String(el.className.baseVal !== undefined
              ? el.className.baseVal : (el.className || '')).slice(0, 60),
        right: Math.round(r.right),
        text: (el.textContent || '').trim().slice(0, 40)
      });
    }
  }
  out.offenders = out.offenders.slice(0, 6);
  for (const img of document.querySelectorAll('img')) {
    const hasAlt = img.hasAttribute('alt');
    const empty = hasAlt && !img.getAttribute('alt').trim();
    // An empty alt is correct for a decorative image, which is one that sits
    // inside an aria-hidden container and repeats information that is already
    // in the text next to it.
    const decorative = !!(img.closest('[aria-hidden="true"]'));
    if (!hasAlt || (empty && !decorative)) {
      out.alt.push(img.getAttribute('src') || '(no src)');
    }
  }
  out.h1 = document.querySelectorAll('h1').length;
  for (const sec of document.querySelectorAll('main section')) {
    if (sec.textContent.trim().length === 0) out.empty.push(sec.className || sec.id);
  }
  out.overflow = out.docWidth > vw + 1;
  return out;
})()
"""


def wait_for_server(port, timeout=40):
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def build(style):
    env = dict(os.environ)
    env["HUGO_PARAMS_STYLE"] = style
    res = subprocess.run(
        [HUGO, "--gc", "--minify", "--panicOnWarning", "--destination", PUBLIC],
        cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if res.returncode != 0:
        print(res.stdout.decode("utf-8", "replace"))
        raise subprocess.CalledProcessError(res.returncode, res.args)


def serve(port):
    env = dict(os.environ)
    proc = subprocess.Popen(
        [HUGO, "server", "--port", str(port), "--bind", "127.0.0.1",
         "--renderToMemory", "--disableFastRender"],
        cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if not wait_for_server(port):
        proc.terminate()
        raise RuntimeError("hugo server did not start")
    return proc


def audit_all(cdp, session, base, style):
    """Load every page at every width and run the audit."""
    problems = []
    cdp.call("Page.enable", {}, session)
    for label, w, h in WIDTHS:
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": w, "height": h, "deviceScaleFactor": 1,
             "mobile": label == "mobile", "screenWidth": w, "screenHeight": h},
            session,
        )
        for path in PAGES:
            cdp.call("Page.navigate", {"url": base + path}, session)
            time.sleep(0.7)
            res = cdp.call(
                "Runtime.evaluate",
                {"expression": AUDIT_JS, "returnByValue": True},
                session,
            )
            out = res.get("result", {}).get("value")
            if out is None:
                problems.append(f"{style} {label} {path}: audit returned nothing")
                continue
            if out["overflow"]:
                problems.append(
                    f"{style} {label} {path}: horizontal overflow "
                    f"(doc {out['docWidth']} > vw {out['vw']})"
                )
            for o in out["offenders"]:
                problems.append(
                    f"{style} {label} {path}: <{o['tag']} class=\"{o['cls']}\"> "
                    f"right={o['right']} (vw {out['vw']})"
                )
            for a in out["alt"]:
                problems.append(f"{style} {label} {path}: image without alt: {a}")
            if out["h1"] != 1:
                problems.append(f"{style} {label} {path}: {out['h1']} <h1> elements")
            for e in out["empty"]:
                problems.append(f"{style} {label} {path}: empty section {e!r}")
    return problems


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    style = os.environ.get("STYLE", "harbor")
    cases = {k: v for k, v in CASES.items() if not only or only in k}
    if not cases:
        print(f"no case matches {only!r}")
        return 1

    shutil.copyfile(PROFILE, BACKUP)
    photos = os.path.join(ROOT, "personal", "photos")
    stash = tempfile.mkdtemp(prefix="polish-photos-")
    all_problems = []
    try:
        for name, content in cases.items():
            with open(PROFILE, "w", encoding="utf-8") as fh:
                fh.write(content)
            # Hide the files this case needs gone, and put them back after.
            hidden = []
            for fname in HIDE_FILES.get(name, []):
                src = os.path.join(photos, fname)
                if os.path.exists(src):
                    dst = os.path.join(stash, fname)
                    shutil.move(src, dst)
                    hidden.append((dst, src))
            # A whole folder can be hidden too, so a section really has
            # nothing in it.
            for dname in HIDE_DIRS.get(name, []):
                src = os.path.join(photos, dname)
                if os.path.isdir(src):
                    dst = os.path.join(stash, dname)
                    shutil.move(src, dst)
                    hidden.append((dst, src))
            print(f"\n=== {name} (style={style}) ===", flush=True)
            try:
                build(style)
                print("  build: OK", flush=True)

                port = free_port()
                proc = serve(port)
                cport = free_port()
                cprofile = tempfile.mkdtemp(prefix="polish-profile-")
                chrome = start_chrome(cport, cprofile)
                try:
                    ws = wait_for_devtools(cport)
                    cdp = Cdp(ws)
                    cdp.connect()
                    tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
                    session = cdp.call(
                        "Target.attachToTarget", {"targetId": tid, "flatten": True}
                    )["sessionId"]
                    problems = audit_all(cdp, session, f"http://127.0.0.1:{port}", style)
                finally:
                    chrome.terminate()
                    try:
                        chrome.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        chrome.kill()
                    shutil.rmtree(cprofile, ignore_errors=True)
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill()

                if problems:
                    for p in problems:
                        print(f"  FAIL {p}")
                    all_problems.extend(problems)
                else:
                    print("  OK   no layout problems found")
            finally:
                for dst, src in hidden:
                    shutil.move(dst, src)
    finally:
        shutil.copyfile(BACKUP, PROFILE)
        os.remove(BACKUP)
        shutil.rmtree(PUBLIC, ignore_errors=True)
        shutil.rmtree(stash, ignore_errors=True)

    print(f"\n{'=' * 60}")
    if all_problems:
        print(f"{len(all_problems)} problem(s) found")
        return 1
    print("All polish cases clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
