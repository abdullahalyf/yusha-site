"""Check keyboard navigation with headless Chrome over CDP.

Usage: python tools/check_keyboard.py <base_url>

Walks the page with Tab and records, for every element that receives focus:
  - whether a visible focus ring is drawn (outline width above zero, or a
    box-shadow), and
  - whether the element is inside a landmark or is a text field.

A focusable element with no visible ring is a failure: a keyboard user
would not know where they are.
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shoot import Cdp, free_port, start_chrome, wait_for_devtools  # noqa: E402

PAGES = [
    ("home", "/"),
    ("about", "/about/"),
    ("projects", "/projects/"),
    ("blog", "/blog/"),
    ("post", "/blog/learning-laravel-app/"),
    ("contact", "/contact/"),
]

PROBE = """
(() => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const cs = getComputedStyle(el);
  const outlineWidth = parseFloat(cs.outlineWidth) || 0;
  const hasOutline = outlineWidth > 0 && cs.outlineStyle !== 'none';
  const hasShadow = cs.boxShadow !== 'none' && cs.boxShadow !== '';
  const rect = el.getBoundingClientRect();
  const visible = rect.width > 0 && rect.height > 0;
  const label = (el.getAttribute('aria-label') || el.textContent || el.tagName).trim().slice(0, 40);
  return {
    tag: el.tagName.toLowerCase(),
    label,
    visible,
    hasOutline,
    hasShadow,
    outline: cs.outline,
    inLandmark: !!el.closest('header,nav,main,footer,section,article'),
  };
})()
"""

TALLY = """
(() => {
  const out = [];
  document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]').forEach(el => {
    if (el.disabled) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    if (el.getAttribute('tabindex') === '-1') return;
    out.push({
      tag: el.tagName.toLowerCase(),
      label: (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0, 50),
    });
  });
  return out;
})()
"""


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:1313"
    port = free_port()
    profile = tempfile.mkdtemp(prefix="kbd-profile-")
    proc = start_chrome(port, profile)
    failures = 0
    try:
        ws = wait_for_devtools(port)
        cdp = Cdp(ws)
        cdp.connect()
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        cdp.call("Page.enable", {}, session)
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1280, "height": 900, "deviceScaleFactor": 1, "mobile": False},
            session,
        )

        for slug, path in PAGES:
            cdp.call("Page.navigate", {"url": base + path}, session)
            time.sleep(2.0)

            total = cdp.call(
                "Runtime.evaluate", {"expression": TALLY, "returnByValue": True}, session
            )["result"]["value"]

            # Walk the tab order from the top of the document.
            cdp.call(
                "Runtime.evaluate",
                {"expression": "document.body.focus();window.scrollTo(0,0);"},
                session,
            )
            seen = []
            for _ in range(min(len(total) + 4, 40)):
                cdp.call(
                    "Input.dispatchKeyEvent",
                    {
                        "type": "rawKeyDown",
                        "windowsVirtualKeyCode": 9,
                        "key": "Tab",
                        "code": "Tab",
                        "nativeVirtualKeyCode": 9,
                    },
                    session,
                )
                cdp.call(
                    "Input.dispatchKeyEvent",
                    {
                        "type": "keyUp",
                        "windowsVirtualKeyCode": 9,
                        "key": "Tab",
                        "code": "Tab",
                        "nativeVirtualKeyCode": 9,
                    },
                    session,
                )
                time.sleep(0.05)
                r = cdp.call(
                    "Runtime.evaluate", {"expression": PROBE, "returnByValue": True}, session
                )
                info = r["result"].get("value")
                if not info:
                    continue
                if info["label"] in seen:
                    break
                seen.append(info["label"])
                if not info["visible"]:
                    print(f"  FAIL {slug}: {info['tag']} '{info['label']}' is not visible")
                    failures += 1
                elif not (info["hasOutline"] or info["hasShadow"]):
                    print(
                        f"  FAIL {slug}: {info['tag']} '{info['label']}' "
                        f"has no visible focus ring"
                    )
                    failures += 1

            print(f"OK  {slug}: {len(total)} focusable elements, {len(seen)} tab stops checked")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()

    print()
    if failures:
        print(f"{failures} focus problem(s) found")
        return 1
    print("every focus stop is visible and has a focus ring")
    return 0


if __name__ == "__main__":
    sys.exit(main())
