"""Take the TASK-04 screenshots: the new photo sections.

Captures the three things Part A added — the education photo beside a
timeline entry, the achievement certificate, and the "Moments" gallery —
plus the lightbox open over a certificate.

Usage: python tools/shoot_media.py <base_url> <out_dir>
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

# label, path, device, width, height, theme, selector to scroll to, full page
SHOTS = [
    ("about-edu", "/about/", "desktop", 1280, 900, "light",
     ".timeline__item--with-photo", False),
    ("about-award", "/about/", "desktop", 1280, 900, "light",
     ".rows__item--with-image", False),
    ("about-gallery", "/about/", "desktop", 1280, 900, "light",
     ".section--gallery", False),
    ("about-gallery-mobile", "/about/", "mobile", 375, 780, "dark",
     ".section--gallery", False),
    ("lightbox-award", "/about/", "desktop", 1280, 900, "dark",
     ".rows__item--with-image", False),
]


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:1313"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "docs/reports/screens"
    os.makedirs(outdir, exist_ok=True)

    port = free_port()
    profile = tempfile.mkdtemp(prefix="shootmedia-profile-")
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

        for label, path, device, w, h, theme, selector, full in SHOTS:
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

            # Scroll the target into view and let its lazy images load.
            cdp.call(
                "Runtime.evaluate",
                {
                    "expression": (
                        "(async()=>{"
                        "const el=document.querySelector('" + selector + "');"
                        "if(el){el.scrollIntoView({block:'center'});}"
                        "await new Promise(r=>setTimeout(r,400));"
                        "window.scrollBy(0,80);"
                        "await new Promise(r=>setTimeout(r,900));"
                        "})()"
                    ),
                    "awaitPromise": True,
                },
                session,
            )
            time.sleep(0.8)

            if label == "lightbox-award":
                # Click the certificate so the lightbox opens over it.
                cdp.call(
                    "Runtime.evaluate",
                    {
                        "expression": (
                            "(()=>{const b=document.querySelector("
                            "'.rows__item--with-image .award');"
                            "if(b)b.click();})()"
                        )
                    },
                    session,
                )
                time.sleep(1.2)

            shot = cdp.call(
                "Page.captureScreenshot",
                {"format": "png", "captureBeyondViewport": full},
                session,
            )
            data = base64.b64decode(shot["data"])
            name = f"task04-{label}.png"
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
