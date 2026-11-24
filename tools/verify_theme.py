"""Run the TASK-01 acceptance checks that need a modified profile.

Usage: python tools/verify_theme.py

Three checks, each one building the site and reading the output:

1. Empty test — experience, achievements, hobbies and socials are emptied and
   personal/cv.pdf plus one project image are deleted. The build must pass and
   the sections must disappear without leaving empty headings behind.
2. Remove-name test — the `name` key is removed from profile.yaml. The build
   must fail with the validation error naming the file to fix.
3. Contrast — every harbour colour token is read out of the CSS and the
   contrast ratio against its background is calculated for both themes.

The profile and the deleted files are restored at the end, whatever happens.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE = os.path.join(ROOT, "personal", "profile.yaml")
HUGO = os.environ.get("HUGO_BIN", "hugo")


def run_hugo(args):
    return subprocess.run(
        [HUGO] + args, cwd=ROOT, capture_output=True, text=True
    )


def read_profile():
    return io.open(PROFILE, encoding="utf-8").read()


def write_profile(text):
    io.open(PROFILE, "w", encoding="utf-8", newline="\n").write(text)


def empty_section(text, key):
    """Replace a top-level YAML list section with an empty list."""
    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(key + ":"):
            # Keep any trailing comment, but it has to stay a YAML comment.
            comment = ""
            if "#" in line:
                comment = "  #" + line.split("#", 1)[1].strip()
            out.append(f"{key}: []{comment}".rstrip())
            i += 1
            # Skip every indented line that belongs to this section.
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("-")):
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


# --- colour maths -----------------------------------------------------------

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


def css_variables(path):
    """Read every --token: #hex declaration out of a CSS file."""
    text = io.open(path, encoding="utf-8").read()
    found = {}
    for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", text):
        found.setdefault(name, value)
    return found


def main():
    backup_dir = tempfile.mkdtemp(prefix="task01-verify-")
    saved_profile = os.path.join(backup_dir, "profile.yaml")
    shutil.copy(PROFILE, saved_profile)
    saved_files = {}
    for rel in ["personal/cv.pdf", "personal/photos/project-2.jpg"]:
        path = os.path.join(ROOT, rel)
        if os.path.exists(path):
            dest = os.path.join(backup_dir, os.path.basename(rel))
            shutil.copy(path, dest)
            saved_files[rel] = dest

    results = []
    try:
        # ---------------------------------------------------------------- 1
        print("=" * 72)
        print("CHECK 1 — empty sections, no CV, one project image removed")
        print("=" * 72)
        text = read_profile()
        for key in ["experience", "achievements", "hobbies", "socials"]:
            text = empty_section(text, key)
        write_profile(text)
        for rel in saved_files:
            os.remove(os.path.join(ROOT, rel))

        r = run_hugo(["--gc", "--minify", "--panicOnWarning"])
        print(r.stdout.strip()[-1200:])
        if r.stderr.strip():
            print("STDERR:", r.stderr.strip()[-1200:])
        print("EXIT CODE:", r.returncode)
        results.append(("empty test build passes", r.returncode == 0))

        # The built site must not contain the headings for the removed
        # sections, and must not contain an empty list where they were.
        built = os.path.join(ROOT, "public")
        checks = {}
        for label, needle in [
            ("no Experience heading", ">Experience<"),
            ("no Achievements heading", ">Achievements<"),
            ("no Hobbies heading", ">Hobbies<"),
            ("no socials list", "social-list"),
            ("no Download CV link", "Download CV"),
        ]:
            found = False
            for root, _dirs, files in os.walk(built):
                for fn in files:
                    if fn.endswith(".html"):
                        body = io.open(os.path.join(root, fn), encoding="utf-8").read()
                        if needle in body:
                            found = True
                            break
                if found:
                    break
            checks[label] = not found
            print(f"  {'PASS' if not found else 'FAIL'}  {label}")
        results.extend(checks.items())

        # Restore for the next check.
        write_profile(io.open(saved_profile, encoding="utf-8").read())
        for rel, dest in saved_files.items():
            shutil.copy(dest, os.path.join(ROOT, rel))

        # ---------------------------------------------------------------- 2
        print()
        print("=" * 72)
        print("CHECK 2 — name removed from profile.yaml")
        print("=" * 72)
        text = read_profile()
        text = re.sub(r"^name:.*$", "", text, count=1, flags=re.M)
        write_profile(text)
        r = run_hugo(["--gc", "--minify", "--panicOnWarning"])
        output = (r.stdout + r.stderr).strip()
        print(output[-2000:])
        print("EXIT CODE:", r.returncode)
        ok = r.returncode != 0 and "profile.yaml" in output
        print(f"  {'PASS' if ok else 'FAIL'}  build fails and names profile.yaml")
        results.append(("remove-name build fails with a clear message", ok))
        write_profile(io.open(saved_profile, encoding="utf-8").read())

        # ---------------------------------------------------------------- 3
        print()
        print("=" * 72)
        print("CHECK 3 — contrast ratios for every colour token")
        print("=" * 72)
        css_dir = os.path.join(ROOT, "themes", "folio", "assets", "css")
        harbor_text = io.open(os.path.join(css_dir, "styles", "harbor.css"), encoding="utf-8").read()

        def vars_in(block):
            return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", block))

        # The light theme is the :root block; the dark theme overrides the
        # tokens inside [data-theme="dark"].
        root_block = re.search(r":root\s*\{(.*?)\n\}", harbor_text, re.S).group(1)
        dark_block = re.search(r'\[data-theme="dark"\]\s*\{(.*?)\n\}', harbor_text, re.S).group(1)

        lv = vars_in(root_block)
        dv = dict(lv)
        dv.update(vars_in(dark_block))

        # --accent-ink is the text colour drawn on top of --accent, not on
        # top of the page background, so it is checked against --accent.
        def report(label, mapping):
            bg = mapping.get("--bg", "#FFFFFF")
            print(f"\n  {label} (background {bg})")
            rows = []
            for name in sorted(mapping):
                if name in ("--bg", "--surface", "--surface-2", "--line", "--focus-ring"):
                    continue
                if name == "--accent-ink":
                    other = mapping.get("--accent", "#FFFFFF")
                    ratio = contrast(mapping[name], other)
                    rows.append((name, mapping[name], ratio, "on --accent " + other))
                    continue
                ratio = contrast(mapping[name], bg)
                rows.append((name, mapping[name], ratio, "on --bg " + bg))
            for name, value, ratio, note in rows:
                mark = "PASS" if ratio >= 4.5 else ("AA-large" if ratio >= 3.0 else "FAIL")
                print(f"    {mark:8} {name:22} {value:9} {ratio:5.2f}:1  {note}")
            return rows

        light_rows = report("LIGHT theme", lv)
        dark_rows = report("DARK theme", dv)

        worst_light = min(r[2] for r in light_rows)
        worst_dark = min(r[2] for r in dark_rows)
        results.append(
            (
                f"all text tokens >= 4.5:1 (light worst {worst_light:.2f}, dark worst {worst_dark:.2f})",
                worst_light >= 4.5 and worst_dark >= 4.5,
            )
        )
    finally:
        shutil.copy(saved_profile, PROFILE)
        for rel, dest in saved_files.items():
            shutil.copy(dest, os.path.join(ROOT, rel))
        shutil.rmtree(backup_dir, ignore_errors=True)
        # Leave the tree in the state the checks found it in.
        run_hugo(["--gc", "--minify"])

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for label, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    failed = [label for label, ok in results if not ok]
    print()
    print(f"{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
