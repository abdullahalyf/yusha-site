"""Draw the blog illustrations: personal/blog/*.jpg

Usage: python tools/make_blog_covers.py

One flat illustration per demo post, drawn as SVG and rasterised by Chrome.
Each is a simple scene in the same palette as the site's accent colour, so
the blog looks like it has real covers without borrowing anyone's photos.

Each post gets two files:
  <name>.jpg        1200x630  wide cover, used as the post cover image
  <name>-body.jpg   1200x750  inline illustration, used inside the post text
"""
import base64
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shoot import Cdp, free_port, start_chrome, wait_for_devtools  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "personal", "blog")

WIDTH = 1200
HEIGHT = 630

INK = "#142033"
ACCENT = "#0E7490"
LIGHT = "#5CC8DD"
PAPER = "#F6F8FB"
CARD = "#FFFFFF"
LINE = "#DCE3EC"
MUTED = "#8FA0B6"

# --- Cover 1: a Laravel-ish controller screen on a laptop -------------------
COVER_1 = f"""
<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>
<circle cx="1010" cy="120" r="170" fill="{LIGHT}" opacity=".22"/>
<circle cx="150" cy="560" r="130" fill="{ACCENT}" opacity=".12"/>

<!-- laptop screen -->
<rect x="290" y="130" width="620" height="360" rx="16" fill="{INK}"/>
<rect x="306" y="146" width="588" height="328" rx="9" fill="{CARD}"/>
<rect x="306" y="146" width="588" height="30" rx="9" fill="{LINE}"/>
<circle cx="326" cy="161" r="5" fill="{MUTED}"/>
<circle cx="342" cy="161" r="5" fill="{MUTED}"/>
<circle cx="358" cy="161" r="5" fill="{MUTED}"/>
<rect x="330" y="200" width="150" height="10" rx="5" fill="{ACCENT}"/>
<rect x="330" y="226" width="420" height="9" rx="4" fill="{LINE}"/>
<rect x="330" y="248" width="380" height="9" rx="4" fill="{LINE}"/>
<rect x="330" y="282" width="96" height="9" rx="4" fill="{LIGHT}"/>
<rect x="330" y="304" width="520" height="9" rx="4" fill="{LINE}"/>
<rect x="330" y="326" width="460" height="9" rx="4" fill="{LINE}"/>
<rect x="330" y="360" width="130" height="34" rx="8" fill="{ACCENT}"/>
<rect x="476" y="360" width="130" height="34" rx="8" fill="none" stroke="{LINE}" stroke-width="2"/>
<!-- laptop base -->
<path d="M 232 492 h 736 l -44 30 h -648 z" fill="{MUTED}"/>
<rect x="556" y="530" width="88" height="9" rx="4" fill="{MUTED}" opacity=".7"/>

<!-- side notes -->
<rect x="60" y="150" width="180" height="12" rx="6" fill="{ACCENT}" opacity=".8"/>
<rect x="60" y="182" width="140" height="10" rx="5" fill="{LINE}"/>
<rect x="60" y="212" width="160" height="10" rx="5" fill="{LINE}"/>
<rect x="960" y="300" width="180" height="150" rx="12" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
<rect x="982" y="326" width="120" height="10" rx="5" fill="{LIGHT}"/>
<rect x="982" y="352" width="90" height="10" rx="5" fill="{LINE}"/>
<rect x="982" y="378" width="110" height="10" rx="5" fill="{LINE}"/>
<rect x="982" y="404" width="70" height="10" rx="5" fill="{LINE}"/>
"""

# --- Cover 2: a study desk with a spaced-repetition card stack ---------------
COVER_2 = f"""
<rect width="{WIDTH}" height="{HEIGHT}" fill="#FBF9F4"/>
<circle cx="140" cy="110" r="140" fill="{LIGHT}" opacity=".20"/>
<circle cx="1090" cy="540" r="150" fill="{ACCENT}" opacity=".12"/>

<!-- card stack -->
<g>
  <rect x="330" y="330" width="300" height="180" rx="14" fill="{LINE}" transform="rotate(-6 480 420)"/>
  <rect x="352" y="300" width="300" height="180" rx="14" fill="{CARD}" stroke="{LINE}" stroke-width="2" transform="rotate(-2 502 390)"/>
  <rect x="374" y="268" width="300" height="180" rx="14" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="400" y="300" width="180" height="12" rx="6" fill="{ACCENT}"/>
  <rect x="400" y="330" width="230" height="10" rx="5" fill="{LINE}"/>
  <rect x="400" y="358" width="200" height="10" rx="5" fill="{LINE}"/>
  <rect x="400" y="392" width="120" height="30" rx="8" fill="{ACCENT}" opacity=".9"/>
  <rect x="532" y="392" width="120" height="30" rx="8" fill="none" stroke="{LINE}" stroke-width="2"/>
</g>

<!-- study clock -->
<circle cx="890" cy="230" r="86" fill="{CARD}" stroke="{INK}" stroke-width="8"/>
<path d="M 890 230 L 890 176" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>
<path d="M 890 230 L 932 254" stroke="{ACCENT}" stroke-width="7" stroke-linecap="round"/>
<circle cx="890" cy="230" r="7" fill="{INK}"/>

<!-- check list -->
<rect x="820" y="380" width="250" height="170" rx="12" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
<g stroke="{ACCENT}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M 848 418 l 10 10 l 18 -20"/>
  <path d="M 848 458 l 10 10 l 18 -20"/>
</g>
<rect x="892" y="412" width="150" height="10" rx="5" fill="{LINE}"/>
<rect x="892" y="452" width="110" height="10" rx="5" fill="{LINE}"/>

<!-- pencil -->
<g transform="rotate(34 210 430)">
  <rect x="120" y="410" width="170" height="30" rx="6" fill="{ACCENT}"/>
  <rect x="120" y="410" width="40" height="30" rx="6" fill="{LIGHT}"/>
  <path d="M 120 410 l -34 15 l 34 15 z" fill="{INK}"/>
</g>
"""

# --- Cover 3: hills and a road, for the trip post ---------------------------
COVER_3 = f"""
<rect width="{WIDTH}" height="{HEIGHT}" fill="#EAF1F5"/>
<circle cx="935" cy="155" r="78" fill="#F6D48A"/>

<!-- far hills -->
<path d="M 0 400 L 210 250 L 340 340 L 470 210 L 640 380 L 780 280 L 940 400 L 1060 320 L 1200 420 L 1200 630 L 0 630 Z" fill="#A9C4D4"/>
<!-- near hills -->
<path d="M 0 470 L 180 360 L 330 440 L 520 330 L 700 450 L 860 370 L 1010 460 L 1200 400 L 1200 630 L 0 630 Z" fill="#7BA3B8"/>
<!-- valley floor -->
<path d="M 0 520 C 240 490 420 545 640 520 C 860 495 1020 540 1200 515 L 1200 630 L 0 630 Z" fill="#4E7C93"/>

<!-- winding road -->
<path d="M 640 630 C 620 570 700 540 660 500 C 620 460 540 460 560 420 C 580 385 660 375 700 360"
      fill="none" stroke="#F3F1EA" stroke-width="26" stroke-linecap="round"/>

<!-- foreground ridge -->
<path d="M 0 630 L 0 560 C 120 545 200 580 300 600 C 380 615 440 625 500 630 Z" fill="#33566B"/>
<g fill="#2C4A5E">
  <path d="M 90 590 l 22 -58 l 22 58 z"/>
  <path d="M 140 600 l 26 -70 l 26 70 z"/>
  <path d="M 205 612 l 20 -52 l 20 52 z"/>
  <path d="M 258 622 l 24 -64 l 24 64 z"/>
</g>

<!-- birds -->
<g stroke="#33566B" stroke-width="4" fill="none" stroke-linecap="round">
  <path d="M 250 170 q 16 -14 32 0 q 16 -14 32 0"/>
  <path d="M 340 130 q 12 -11 24 0 q 12 -11 24 0"/>
</g>
"""

COVERS = {
    "laravel-app": COVER_1,
    "study-system": COVER_2,
    "sajek-trip": COVER_3,
}

# --- Inline body illustrations, 1200x750 -------------------------------------
BODY_W = 1200
BODY_H = 750

# Body 1: the lost-and-found board — a grid of item cards with a filter rail.
BODY_1 = f"""
<rect width="{BODY_W}" height="{BODY_H}" fill="{PAPER}"/>

<!-- filter rail -->
<rect x="60" y="60" width="250" height="630" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
<rect x="88" y="92" width="120" height="12" rx="6" fill="{INK}" opacity=".85"/>
<g>
  <rect x="88" y="132" width="194" height="40" rx="8" fill="{ACCENT}" opacity=".14"/>
  <rect x="100" y="146" width="86" height="10" rx="5" fill="{ACCENT}"/>
  <rect x="100" y="196" width="120" height="10" rx="5" fill="{LINE}"/>
  <rect x="100" y="238" width="150" height="10" rx="5" fill="{LINE}"/>
  <rect x="100" y="280" width="100" height="10" rx="5" fill="{LINE}"/>
  <rect x="100" y="322" width="134" height="10" rx="5" fill="{LINE}"/>
</g>

<!-- item grid -->
<g>
  <rect x="346" y="60" width="410" height="190" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="366" y="80" width="150" height="86" rx="10" fill="{LIGHT}" opacity=".35"/>
  <rect x="366" y="184" width="200" height="12" rx="6" fill="{INK}" opacity=".8"/>
  <rect x="366" y="212" width="140" height="10" rx="5" fill="{LINE}"/>

  <rect x="776" y="60" width="364" height="190" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="796" y="80" width="130" height="86" rx="10" fill="{ACCENT}" opacity=".18"/>
  <rect x="796" y="184" width="180" height="12" rx="6" fill="{INK}" opacity=".8"/>
  <rect x="796" y="212" width="120" height="10" rx="5" fill="{LINE}"/>

  <rect x="346" y="270" width="410" height="190" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="366" y="290" width="120" height="86" rx="10" fill="{ACCENT}" opacity=".22"/>
  <rect x="366" y="394" width="170" height="12" rx="6" fill="{INK}" opacity=".8"/>
  <rect x="366" y="422" width="210" height="10" rx="5" fill="{LINE}"/>

  <rect x="776" y="270" width="364" height="190" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="796" y="290" width="140" height="86" rx="10" fill="{LIGHT}" opacity=".32"/>
  <rect x="796" y="394" width="150" height="12" rx="6" fill="{INK}" opacity=".8"/>
  <rect x="796" y="422" width="190" height="10" rx="5" fill="{LINE}"/>
</g>

<!-- bottom row, fading out -->
<rect x="346" y="480" width="410" height="180" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="2" opacity=".7"/>
<rect x="366" y="500" width="130" height="80" rx="10" fill="{LINE}" opacity=".6"/>
<rect x="366" y="598" width="180" height="12" rx="6" fill="{LINE}"/>
<rect x="776" y="480" width="364" height="180" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="2" opacity=".7"/>
<rect x="796" y="500" width="110" height="80" rx="10" fill="{LINE}" opacity=".6"/>
<rect x="796" y="598" width="160" height="12" rx="6" fill="{LINE}"/>

<!-- claimed badge -->
<rect x="1080" y="498" width="86" height="30" rx="15" fill="{ACCENT}" opacity=".9"/>
"""

# Body 2: a desk from above — notebook, index cards, a pen, a mug.
BODY_2 = f"""
<rect width="{BODY_W}" height="{BODY_H}" fill="#FBF9F4"/>
<circle cx="1050" cy="120" r="150" fill="{LIGHT}" opacity=".16"/>
<circle cx="140" cy="660" r="130" fill="{ACCENT}" opacity=".1"/>

<!-- notebook, open -->
<g transform="rotate(-3 420 400)">
  <rect x="150" y="150" width="540" height="470" rx="14" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="415" y="150" width="5" height="470" fill="{LINE}"/>
  <g stroke="{LINE}" stroke-width="3" stroke-linecap="round">
    <path d="M 190 210 h 190"/>
    <path d="M 190 246 h 190"/>
    <path d="M 190 282 h 150"/>
  </g>
  <g stroke="{ACCENT}" stroke-width="7" stroke-linecap="round" opacity=".9">
    <path d="M 190 210 h 190"/>
    <path d="M 190 246 h 190"/>
    <path d="M 190 282 h 150"/>
  </g>
  <!-- margin question marks -->
  <g fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linecap="round">
    <path d="M 350 196 q 14 -14 26 0 q 6 8 -4 14 l -8 6"/>
    <path d="M 366 224 l 0 2"/>
  </g>
  <g stroke="{LINE}" stroke-width="3" stroke-linecap="round">
    <path d="M 455 210 h 190"/>
    <path d="M 455 246 h 190"/>
    <path d="M 455 282 h 120"/>
  </g>
  <g stroke="{INK}" stroke-width="6" stroke-linecap="round" opacity=".55">
    <path d="M 455 210 h 190"/>
    <path d="M 455 246 h 160"/>
    <path d="M 455 282 h 120"/>
  </g>
  <!-- checklist -->
  <g stroke="{ACCENT}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 470 350 l 10 10 l 18 -20"/>
    <path d="M 470 394 l 10 10 l 18 -20"/>
  </g>
  <g stroke="{LINE}" stroke-width="3" stroke-linecap="round">
    <path d="M 520 356 h 120"/>
    <path d="M 520 400 h 90"/>
  </g>
  <g stroke="{INK}" stroke-width="6" stroke-linecap="round" opacity=".55">
    <path d="M 520 356 h 120"/>
    <path d="M 520 400 h 90"/>
  </g>
</g>

<!-- index cards, fanned -->
<g transform="rotate(7 940 300)">
  <rect x="800" y="200" width="230" height="150" rx="12" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="822" y="226" width="120" height="11" rx="5" fill="{ACCENT}"/>
  <rect x="822" y="256" width="180" height="9" rx="4" fill="{LINE}"/>
  <rect x="822" y="282" width="140" height="9" rx="4" fill="{LINE}"/>
  <rect x="822" y="312" width="60" height="9" rx="4" fill="{LINE}"/>
</g>
<g transform="rotate(-4 950 420)">
  <rect x="810" y="330" width="230" height="150" rx="12" fill="{CARD}" stroke="{LINE}" stroke-width="2"/>
  <rect x="832" y="356" width="140" height="11" rx="5" fill="{ACCENT}" opacity=".75"/>
  <rect x="832" y="386" width="170" height="9" rx="4" fill="{LINE}"/>
  <rect x="832" y="412" width="120" height="9" rx="4" fill="{LINE}"/>
</g>

<!-- mug -->
<g transform="rotate(-6 940 570)">
  <rect x="860" y="520" width="150" height="110" rx="16" fill="{CARD}" stroke="{LINE}" stroke-width="3"/>
  <path d="M 1010 546 q 42 12 42 40 q 0 30 -42 40" fill="none" stroke="{LINE}" stroke-width="10" stroke-linecap="round"/>
  <rect x="880" y="540" width="110" height="26" rx="8" fill="{ACCENT}" opacity=".22"/>
</g>

<!-- pen -->
<g transform="rotate(-32 200 470)">
  <rect x="120" y="452" width="150" height="26" rx="6" fill="{ACCENT}"/>
  <rect x="120" y="452" width="36" height="26" rx="6" fill="{LIGHT}"/>
  <path d="M 120 452 l -28 13 l 28 13 z" fill="{INK}"/>
</g>
"""

# Body 3: the hill road — a wider view with the bamboo grove in the foreground.
BODY_3 = f"""
<rect width="{BODY_W}" height="{BODY_H}" fill="#EAF1F5"/>
<circle cx="960" cy="150" r="86" fill="#F6D48A"/>

<!-- far ridges -->
<path d="M 0 400 L 190 270 L 330 350 L 470 230 L 640 390 L 790 300 L 950 410 L 1080 330 L 1200 420 L 1200 750 L 0 750 Z" fill="#A9C4D4"/>
<path d="M 0 480 L 170 380 L 320 450 L 500 350 L 690 460 L 850 385 L 1000 470 L 1200 415 L 1200 750 L 0 750 Z" fill="#7BA3B8"/>

<!-- valley -->
<path d="M 0 540 C 260 505 430 560 660 535 C 880 510 1030 555 1200 528 L 1200 750 L 0 750 Z" fill="#4E7C93"/>

<!-- road -->
<path d="M 700 750 C 676 670 748 632 700 585 C 655 542 578 545 596 500 C 614 460 700 448 742 430"
      fill="none" stroke="#F3F1EA" stroke-width="30" stroke-linecap="round"/>

<!-- bamboo grove in the foreground -->
<g>
  <g stroke="#2C4A5E" stroke-width="9" stroke-linecap="round" fill="none">
    <path d="M 120 750 L 96 470"/>
    <path d="M 190 750 L 214 440"/>
    <path d="M 258 750 L 246 520"/>
  </g>
  <g fill="#3E6274">
    <path d="M 96 560 q 54 -34 92 -14 q -44 34 -92 14 z"/>
    <path d="M 214 520 q 58 -32 96 -10 q -46 32 -96 10 z"/>
    <path d="M 246 640 q 50 -30 84 -12 q -40 30 -84 12 z"/>
    <path d="M 96 640 q 46 -26 76 -10 q -36 26 -76 10 z"/>
  </g>
</g>

<!-- tea stall -->
<g>
  <rect x="840" y="556" width="180" height="110" rx="8" fill="#F3F1EA"/>
  <path d="M 820 556 h 220 l -22 -46 h -176 z" fill="#C96A4A"/>
  <rect x="872" y="592" width="52" height="74" rx="4" fill="{INK}" opacity=".55"/>
  <circle cx="966" cy="612" r="20" fill="{ACCENT}" opacity=".5"/>
</g>

<!-- birds -->
<g stroke="#33566B" stroke-width="4" fill="none" stroke-linecap="round">
  <path d="M 330 200 q 18 -15 36 0 q 18 -15 36 0"/>
  <path d="M 440 155 q 13 -12 26 0 q 13 -12 26 0"/>
  <path d="M 520 220 q 10 -9 20 0 q 10 -9 20 0"/>
</g>
"""

BODIES = {
    "laravel-app": BODY_1,
    "study-system": BODY_2,
    "sajek-trip": BODY_3,
}


def render(cdp, session, body, width, height):
    """Rasterise one SVG body and return the JPEG bytes."""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">{body}</svg>'
    )
    html = (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        "html,body{margin:0;padding:0;overflow:hidden}"
        "svg{display:block}"
        "</style></head><body>" + svg + "</body></html>"
    )
    url = "data:text/html;base64," + base64.b64encode(html.encode()).decode()
    cdp.call("Page.navigate", {"url": url}, session)
    time.sleep(1.0)
    shot = cdp.call(
        "Page.captureScreenshot",
        {"format": "jpeg", "quality": 86, "captureBeyondViewport": False},
        session,
    )
    return base64.b64decode(shot["data"])


def set_viewport(cdp, session, width, height):
    cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": False,
            "screenWidth": width,
            "screenHeight": height,
        },
        session,
    )


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    port = free_port()
    profile = tempfile.mkdtemp(prefix="cover-profile-")
    proc = start_chrome(port, profile)
    try:
        ws = wait_for_devtools(port)
        cdp = Cdp(ws)
        cdp.connect()
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        cdp.call("Page.enable", {}, session)

        set_viewport(cdp, session, WIDTH, HEIGHT)
        for name, body in COVERS.items():
            out = os.path.join(OUTDIR, name + ".jpg")
            with open(out, "wb") as fh:
                fh.write(render(cdp, session, body, WIDTH, HEIGHT))
            print(f"OK  {name}.jpg {WIDTH}x{HEIGHT} {os.path.getsize(out)} bytes")

        set_viewport(cdp, session, BODY_W, BODY_H)
        for name, body in BODIES.items():
            out = os.path.join(OUTDIR, name + "-body.jpg")
            with open(out, "wb") as fh:
                fh.write(render(cdp, session, body, BODY_W, BODY_H))
            print(f"OK  {name}-body.jpg {BODY_W}x{BODY_H} {os.path.getsize(out)} bytes")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
