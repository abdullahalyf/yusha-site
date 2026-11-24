"""Check that the site does not move when the visitor asks for less motion.

The CSS is supposed to switch every animation and transition off under
`prefers-reduced-motion: reduce`. This drives Chrome with the media
feature emulated, then reads the computed style of every element on the
page and reports anything that still has a running animation or a
transition longer than a millisecond.

Usage: python tools/check_reduced_motion.py
"""
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
PUBLIC = os.path.join(ROOT, "public-motion")

STYLES = ["harbor", "grove", "orchid", "graphite", "saffron"]
PAGES = ["/", "/about/", "/projects/", "/blog/", "/contact/"]

AUDIT_JS = r"""
(() => {
  const moving = [];
  const els = document.querySelectorAll('body *');
  for (const el of els) {
    const cs = getComputedStyle(el);
    const name = (el.tagName.toLowerCase() + ' ' +
      String(el.className.baseVal !== undefined
        ? el.className.baseVal : (el.className || ''))).slice(0, 70);
    // An animation that is still running.
    if (cs.animationName && cs.animationName !== 'none') {
      const dur = parseFloat(cs.animationDuration) || 0;
      if (dur > 0.001) moving.push({name: name, what: 'animation',
                                    detail: cs.animationName + ' ' + cs.animationDuration});
    }
    // A transition that would still take time.
    const td = parseFloat(cs.transitionDuration) || 0;
    if (td > 0.001) {
      moving.push({name: name, what: 'transition', detail: cs.transitionDuration});
    }
  }
  const html = getComputedStyle(document.documentElement);
  return {
    moving: moving.slice(0, 10),
    scrollBehavior: html.scrollBehavior,
    matchMedia: window.matchMedia('(prefers-reduced-motion: reduce)').matches
  };
})()
"""


def build(style):
    env = dict(os.environ)
    env["HUGO_PARAMS_STYLE"] = style
    subprocess.run(
        [HUGO, "--gc", "--minify", "--panicOnWarning", "--destination", PUBLIC],
        cwd=ROOT, env=env, check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )


def serve(port, style):
    env = dict(os.environ)
    env["HUGO_PARAMS_STYLE"] = style
    proc = subprocess.Popen(
        [HUGO, "server", "--port", str(port), "--bind", "127.0.0.1",
         "--renderToMemory", "--disableFastRender"],
        cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    import urllib.request

    deadline = time.time() + 40
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r:
                if r.status == 200:
                    return proc
        except Exception:
            time.sleep(0.3)
    proc.terminate()
    raise RuntimeError("hugo server did not start")


def main():
    problems = []
    cport = free_port()
    cprofile = tempfile.mkdtemp(prefix="motion-profile-")
    chrome = start_chrome(cport, cprofile)
    try:
        ws = wait_for_devtools(cport)
        cdp = Cdp(ws)
        cdp.connect()
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call(
            "Target.attachToTarget", {"targetId": tid, "flatten": True}
        )["sessionId"]
        cdp.call("Page.enable", {}, session)
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 375, "height": 780, "deviceScaleFactor": 1,
             "mobile": True, "screenWidth": 375, "screenHeight": 780},
            session,
        )
        # The media emulation has to be in place before the document loads.
        cdp.call(
            "Emulation.setEmulatedMedia",
            {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]},
            session,
        )

        for style in STYLES:
            build(style)
            port = free_port()
            proc = serve(port, style)
            try:
                for path in PAGES:
                    cdp.call("Page.navigate",
                             {"url": f"http://127.0.0.1:{port}{path}"}, session)
                    time.sleep(0.9)
                    res = cdp.call(
                        "Runtime.evaluate",
                        {"expression": AUDIT_JS, "returnByValue": True},
                        session,
                    )
                    out = res.get("result", {}).get("value") or {}
                    if not out.get("matchMedia"):
                        problems.append(
                            f"{style} {path}: the browser did not report "
                            f"prefers-reduced-motion: reduce"
                        )
                    if out.get("scrollBehavior") != "auto":
                        problems.append(
                            f"{style} {path}: scroll-behavior is "
                            f"{out.get('scrollBehavior')}, expected auto"
                        )
                    for m in out.get("moving", []):
                        problems.append(
                            f"{style} {path}: {m['name']} still has a "
                            f"{m['what']} ({m['detail']})"
                        )
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
            print(f"checked {style}", flush=True)
    finally:
        chrome.terminate()
        try:
            chrome.wait(timeout=10)
        except subprocess.TimeoutExpired:
            chrome.kill()
        shutil.rmtree(cprofile, ignore_errors=True)
        shutil.rmtree(PUBLIC, ignore_errors=True)

    print(f"\n{'=' * 60}")
    if problems:
        for p in problems:
            print(f"FAIL {p}")
        print(f"\n{len(problems)} problem(s) found")
        return 1
    print("No motion under prefers-reduced-motion: reduce")
    return 0


if __name__ == "__main__":
    sys.exit(main())
