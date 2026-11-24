"""Check the contrast of every colour token in every style file.

Usage: python tools/check_contrast.py [style ...]

With no arguments every file in themes/folio/assets/css/styles/ is checked.

For each style the light tokens come from the `:root` block and the dark tokens
from the `[data-theme="dark"]` block. Text colours are checked against `--bg`
and `--surface`; `--accent-ink` is checked against `--accent`, because that is
the colour it is actually drawn on.

Exit code is 1 if any text colour falls below 4.5:1 in either theme, so the
script can be used as a gate in CI.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(ROOT, "themes", "folio", "assets", "css", "styles")

# Tokens that carry text. The rest are surfaces, rules and separators.
TEXT_TOKENS = ["--ink", "--muted", "--accent"]

# Tokens that are never text and therefore need no contrast ratio.
SKIP = {"--bg", "--surface", "--surface-2", "--line", "--focus-ring", "--spark"}


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color):
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (
        0.2126 * srgb_to_linear(r)
        + 0.7152 * srgb_to_linear(g)
        + 0.0722 * srgb_to_linear(b)
    )


def contrast(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def vars_in(block):
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", block))


def blocks_of(text):
    root = re.search(r":root\s*\{(.*?)\n\}", text, re.S)
    dark = re.search(r'\[data-theme="dark"\]\s*\{(.*?)\n\}', text, re.S)
    return root.group(1), dark.group(1)


def check_style(style):
    path = os.path.join(CSS_DIR, style + ".css")
    text = io.open(path, encoding="utf-8").read()
    root_block, dark_block = blocks_of(text)

    light = vars_in(root_block)
    dark = dict(light)
    dark.update(vars_in(dark_block))

    rows = []
    failed = False

    for theme, mapping in (("light", light), ("dark", dark)):
        bg = mapping.get("--bg", "#FFFFFF")
        surface = mapping.get("--surface", bg)
        for name in TEXT_TOKENS:
            if name not in mapping:
                continue
            value = mapping[name]
            for label, other in (("bg", bg), ("surface", surface)):
                ratio = contrast(value, other)
                ok = ratio >= 4.5
                if not ok:
                    failed = True
                rows.append((theme, name, value, label, other, ratio, ok))
        # --accent-ink is drawn on top of --accent.
        if "--accent-ink" in mapping and "--accent" in mapping:
            value = mapping["--accent-ink"]
            other = mapping["--accent"]
            ratio = contrast(value, other)
            ok = ratio >= 4.5
            if not ok:
                failed = True
            rows.append(
                (theme, "--accent-ink", value, "accent", other, ratio, ok)
            )

    return rows, failed


def main():
    args = sys.argv[1:]
    if args:
        styles = args
    else:
        styles = sorted(
            f[:-4]
            for f in os.listdir(CSS_DIR)
            if f.endswith(".css")
        )

    print("=" * 78)
    print("CONTRAST — text tokens against --bg and --surface")
    print("=" * 78)

    all_failed = False
    for style in styles:
        rows, failed = check_style(style)
        if failed:
            all_failed = True
        print(f"\n{style}")
        print(f"  {'theme':6} {'token':14} {'value':9} {'on':8} {'against':9} {'ratio':>7}  ")
        for theme, name, value, label, other, ratio, ok in rows:
            mark = "PASS" if ok else "FAIL"
            if not ok:
                mark = "FAIL"
            print(
                f"  {mark:4} {theme:6} {name:14} {value:9} {label:8} {other:9} "
                f"{ratio:6.2f}:1"
            )

    print()
    print("=" * 78)
    if all_failed:
        print("RESULT: FAIL — at least one text colour is below 4.5:1")
        return 1
    print("RESULT: PASS — every text colour is at least 4.5:1 in both themes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
