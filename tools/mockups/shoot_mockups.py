"""Capture the mockup HTML files in this folder as project screenshots.

Usage: python tools/mockups/shoot_mockups.py

Each mockup is a throwaway HTML file that stands in for a small app. This
script renders it in headless Chrome at 1600x1000 and writes the result to
personal/photos/project-N.jpg, so the demo projects show real UI rather
than an abstract placeholder.
"""
import base64
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shoot import Cdp, free_port, start_chrome, wait_for_devtools  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# mockup file, output base name
MOCKUPS = [
    ("lost-and-found.html", "project-1"),
    ("bus-bot.html", "project-2"),
    ("shop-ledger.html", "project-3"),
    ("study-deck.html", "project-4"),
]

WIDTH = 1600
HEIGHT = 1000


def shoot(cdp, session, url, out):
    cdp.call("Page.navigate", {"url": url}, session)
    time.sleep(1.2)
    shot = cdp.call(
        "Page.captureScreenshot",
        {"format": "jpeg", "quality": 88, "captureBeyondViewport": False},
        session,
    )
    with open(out, "wb") as fh:
        fh.write(base64.b64decode(shot["data"]))


def main():
    port = free_port()
    profile = tempfile.mkdtemp(prefix="mockup-profile-")
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

        outdir = os.path.join(ROOT, "personal", "photos")
        os.makedirs(outdir, exist_ok=True)

        for filename, base in MOCKUPS:
            src = os.path.join(HERE, filename)
            out = os.path.join(outdir, base + ".jpg")
            shoot(cdp, session, "file:///" + src.replace("\\", "/"), out)
            size = os.path.getsize(out)
            print(f"OK  {base}.jpg <- {filename} ({size} bytes)")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
