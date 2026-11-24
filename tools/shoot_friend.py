"""Take the screenshots for a friend's site.

Usage: python tools/shoot_friend.py <base_url> <out_dir> <prefix>

Writes <prefix>-<page>-<device>-<theme>.png for the home page and the
about page, at desktop (1280) and mobile (375), in light and dark.
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

PAGES = [
    ("home", "/"),
    ("about", "/about/"),
]

DEVICES = [
    ("desktop", 1280, 900),
    ("mobile", 375, 780),
]

THEMES = ["light", "dark"]


def main():
    base = sys.argv[1]
    outdir = sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else "friend"
    os.makedirs(outdir, exist_ok=True)

    port = free_port()
    profile = tempfile.mkdtemp(prefix="friend-profile-")
    proc = start_chrome(port, profile)
    try:
        ws = wait_for_devtools(port)
        cdp = Cdp(ws)
        cdp.connect()
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call(
            "Target.attachToTarget", {"targetId": tid, "flatten": True}
        )["sessionId"]
        cdp.call("Page.enable", {}, session)

        for slug, path in PAGES:
            for device, w, h in DEVICES:
                for theme in THEMES:
                    cdp.call(
                        "Emulation.setDeviceMetricsOverride",
                        {
                            "width": w, "height": h, "deviceScaleFactor": 1,
                            "mobile": device == "mobile",
                            "screenWidth": w, "screenHeight": h,
                        },
                        session,
                    )
                    cdp.call("Page.navigate", {"url": base + path}, session)
                    time.sleep(0.6)
                    cdp.call(
                        "Runtime.evaluate",
                        {"expression": "try{localStorage.clear()}catch(e){}"},
                        session,
                    )
                    cdp.call(
                        "Emulation.setEmulatedMedia",
                        {"features": [{"name": "prefers-color-scheme", "value": theme}]},
                        session,
                    )
                    cdp.call("Page.reload", {"ignoreCache": True}, session)
                    time.sleep(2.0)

                    shot = cdp.call(
                        "Page.captureScreenshot", {"format": "png"}, session
                    )
                    data = base64.b64decode(shot["data"])
                    name = f"{prefix}-{slug}-{device}-{theme}.png"
                    with open(os.path.join(outdir, name), "wb") as fh:
                        fh.write(data)
                    print(f"OK  {name} ({w}x{h} {theme}) {len(data)} bytes")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
