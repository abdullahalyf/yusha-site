"""Draw the demo portrait placeholder: personal/photos/profile.jpg.

Usage: python tools/make_portrait.py

A flat, two-tone head-and-shoulders silhouette on a soft background. It is a
deliberate placeholder, not a photo of a person: no face, no features, no
rendering tricks. 1000x1250, drawn as SVG and rasterised by Chrome.

The shapes are built to read as a person rather than as a stack of
rectangles: the neck tapers into the shoulders, the shoulders slope, and the
hair is a soft asymmetric shape instead of a flat cap.
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
OUT = os.path.join(ROOT, "personal", "photos", "profile.jpg")

WIDTH = 1000
HEIGHT = 1250

# Two tones plus the background: the whole point is that it reads as a
# placeholder at a glance, not as an attempted portrait.
BG = "#e7edf3"
HALO = "#dce5ee"
FIGURE = "#2c4257"
FIGURE_LIGHT = "#3e5a73"

SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <!-- A soft radial gradient on the disc keeps the background from
         looking like a flat sticker. -->
    <radialGradient id="halo" cx="50%" cy="36%" r="70%">
      <stop offset="0%" stop-color="#eef3f8"/>
      <stop offset="100%" stop-color="{HALO}"/>
    </radialGradient>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>

  <!-- soft disc behind the figure so the silhouette does not float -->
  <circle cx="500" cy="400" r="356" fill="url(#halo)"/>

  <!-- Shoulders and chest. A real bust is wide: the deltoids reach well past
       the edge of the head, and the chest fills the bottom of the frame.
       The top of the shape is the shoulder line, which sits high enough to
       meet the neck rather than leaving a gap under the chin. -->
  <path d="M 500 800
           C 462 800 428 806 392 822
           C 300 860 216 948 176 1054
           C 152 1120 136 1180 130 1250
           L 870 1250
           C 864 1180 848 1120 824 1054
           C 784 948 700 860 608 822
           C 572 806 538 800 500 800
           Z"
        fill="{FIGURE}"/>

  <!-- Neck. Wide and short: it starts behind the jaw and flares into the
       shoulder line, so the head and the body read as one shape. -->
  <path d="M 402 528
           C 402 528 408 596 414 640
           C 419 682 424 720 426 752
           C 446 780 470 792 500 792
           C 530 792 554 780 574 752
           C 576 720 581 682 586 640
           C 592 596 598 528 598 528
           Z"
        fill="{FIGURE_LIGHT}"/>

  <!-- Head. It overlaps the top of the neck, so there is no gap. -->
  <ellipse cx="500" cy="378" rx="180" ry="206" fill="{FIGURE}"/>

  <!-- Hair. The outer edge follows the skull. The inner edge is a hairline
       that sweeps up across the forehead, so the shape reads as hair cut
       to one side rather than as a cap sitting on the head. The sides come
       down past the ears and taper into the neck without a hard corner. -->
  <path d="M 320 378
           C 320 262 398 172 500 172
           C 602 172 680 262 680 378
           C 680 420 676 456 668 492
           C 664 512 650 518 640 506
           C 626 476 620 434 606 400
           C 592 366 570 342 544 330
           C 506 316 464 322 432 344
           C 400 366 378 400 368 440
           C 364 460 350 466 338 456
           C 326 438 320 408 320 378
           Z"
        fill="{FIGURE_LIGHT}"/>

  <!-- A soft parting line, so the hair has a direction -->
  <path d="M 512 190 C 578 214 622 262 634 324"
        fill="none" stroke="{FIGURE}" stroke-width="14"
        stroke-linecap="round" opacity=".42"/>

  <!-- Collar: a soft V that sits on the shoulders -->
  <path d="M 424 852 C 442 890 466 912 500 922 C 534 912 558 890 576 852"
        fill="none" stroke="{FIGURE_LIGHT}" stroke-width="19"
        stroke-linecap="round" stroke-linejoin="round"/>

  <!-- A single line down the middle of the chest to suggest a placket -->
  <path d="M 500 924 L 500 1250"
        fill="none" stroke="{FIGURE}" stroke-width="5" opacity=".35"/>
</svg>
"""


def main():
    port = free_port()
    profile = tempfile.mkdtemp(prefix="portrait-profile-")
    proc = start_chrome(port, profile)
    try:
        ws = wait_for_devtools(port)
        cdp = Cdp(ws)
        cdp.connect()
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        cdp.call("Page.enable", {}, session)
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": WIDTH,
                "height": HEIGHT,
                "deviceScaleFactor": 1,
                "mobile": False,
                "screenWidth": WIDTH,
                "screenHeight": HEIGHT,
            },
            session,
        )

        html = (
            "<!doctype html><html><head><meta charset='utf-8'><style>"
            "html,body{margin:0;padding:0;overflow:hidden;background:" + BG + "}"
            "svg{display:block}"
            "</style></head><body>" + SVG + "</body></html>"
        )
        data_url = "data:text/html;base64," + base64.b64encode(html.encode()).decode()
        cdp.call("Page.navigate", {"url": data_url}, session)
        time.sleep(1.2)

        shot = cdp.call(
            "Page.captureScreenshot",
            {"format": "jpeg", "quality": 88, "captureBeyondViewport": False},
            session,
        )
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "wb") as fh:
            fh.write(base64.b64decode(shot["data"]))
        print(f"OK  profile.jpg ({WIDTH}x{HEIGHT}) {os.path.getsize(OUT)} bytes")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
