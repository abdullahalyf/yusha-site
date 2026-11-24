"""Check that every style works with every hero layout.

The layout is chosen by the style by default, but a site owner can override
it with `layout = "..."` in hugo.toml. That has to keep working for all
5 styles x 5 layouts, and the rendered page has to have exactly one <h1>,
no horizontal overflow and no missing images.

Usage: python tools/check_layouts.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shoot import Cdp, free_port, start_chrome, wait_for_devtools  # noqa: E402
from polish_check import audit_all  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUGO = os.environ.get("HUGO_BIN", "hugo")
PUBLIC = os.path.join(ROOT, "public-layouts")

STYLES = ["harbor", "grove", "orchid", "graphite", "saffron"]
LAYOUTS = ["split", "centered", "typographic", "sidebar", "band"]


def build(style, layout):
    env = dict(os.environ)
    env["HUGO_PARAMS_STYLE"] = style
    env["HUGO_PARAMS_LAYOUT"] = layout
    res = subprocess.run(
        [HUGO, "--gc", "--minify", "--panicOnWarning", "--destination", PUBLIC],
        cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if res.returncode != 0:
        return res.stdout.decode("utf-8", "replace")
    return None


def serve(port, style, layout):
    env = dict(os.environ)
    env["HUGO_PARAMS_STYLE"] = style
    env["HUGO_PARAMS_LAYOUT"] = layout
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
    failures = []
    cport = free_port()
    cprofile = tempfile.mkdtemp(prefix="layouts-profile-")
    chrome = start_chrome(cport, cprofile)
    try:
        ws = wait_for_devtools(cport)
        cdp = Cdp(ws)
        cdp.connect()
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call(
            "Target.attachToTarget", {"targetId": tid, "flatten": True}
        )["sessionId"]

        for style in STYLES:
            for layout in LAYOUTS:
                label = f"{style}/{layout}"
                err = build(style, layout)
                if err:
                    failures.append(f"{label}: BUILD FAILED\n{err}")
                    print(f"FAIL {label}: build failed")
                    continue
                port = free_port()
                proc = serve(port, style, layout)
                try:
                    problems = audit_all(cdp, session, f"http://127.0.0.1:{port}",
                                         style)
                finally:
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                if problems:
                    failures.extend(f"{label}: {p}" for p in problems)
                    print(f"FAIL {label}")
                    for p in problems:
                        print(f"     {p}")
                else:
                    print(f"OK   {label}")
    finally:
        chrome.terminate()
        try:
            chrome.wait(timeout=10)
        except subprocess.TimeoutExpired:
            chrome.kill()
        shutil.rmtree(cprofile, ignore_errors=True)
        shutil.rmtree(PUBLIC, ignore_errors=True)

    print(f"\n{'=' * 60}")
    if failures:
        print(f"{len(failures)} failure(s)")
        return 1
    print(f"All {len(STYLES) * len(LAYOUTS)} style/layout combinations clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
