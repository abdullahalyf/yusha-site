"""Generate personal/cv.pdf from personal/profile.yaml and tools/cv/cv.html.

Usage: python tools/cv/make_cv.py

The HTML template holds the layout; the text comes from the profile, so the
CV cannot drift away from the site. Chrome renders the page and prints it
to PDF, which keeps the typography identical to the markup.
"""
import base64
import os
import shutil
import subprocess
import sys
import tempfile
import time

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shoot import Cdp, free_port, start_chrome, wait_for_devtools  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE = os.path.join(ROOT, "tools", "cv", "cv.html")
PROFILE = os.path.join(ROOT, "personal", "profile.yaml")
OUT = os.path.join(ROOT, "personal", "cv.pdf")


def first_paragraph(text):
    return (text or "").strip().split("\n\n")[0].strip()


def experience_html(items):
    out = []
    for item in items:
        when = " – ".join(x for x in (item.get("start"), item.get("end")) if x)
        out.append(
            '<div class="entry">'
            f'<div class="row"><span class="what">{item["title"]}</span>'
            f'<span class="when">{when}</span></div>'
            f'<div class="where">{item.get("org", "")}</div>'
            f'<div class="detail">{item.get("detail", "")}</div>'
            "</div>"
        )
    return "\n".join(out)


def education_html(items):
    out = []
    for item in items:
        when = " – ".join(x for x in (item.get("start"), item.get("end")) if x)
        out.append(
            '<div class="entry">'
            f'<div class="row"><span class="what">{item["degree"]}</span>'
            f'<span class="when">{when}</span></div>'
            f'<div class="where">{item.get("institution", "")}</div>'
            f'<div class="detail">{item.get("detail", "")}</div>'
            "</div>"
        )
    return "\n".join(out)


def projects_html(items):
    out = []
    for item in items:
        tech = ", ".join(item.get("tech", []))
        out.append(
            '<div class="entry">'
            f'<div class="what">{item["title"]}</div>'
            f'<div class="detail">{item.get("summary", "")} <i>Tech: {tech}.</i></div>'
            "</div>"
        )
    return "\n".join(out)


def skills_html(groups):
    out = []
    for group in groups:
        items = ", ".join(group.get("items", []))
        out.append(f"<li><b>{group['group']}:</b> <span>{items}</span></li>")
    return "\n".join(out)


def languages_html(items):
    return "\n".join(f"<li>{x}</li>" for x in items)


def achievements_html(items):
    out = []
    for item in items:
        out.append(f"<li>{item['year']} — {item['title']}, {item.get('issuer', '')}</li>")
    return "\n".join(out)


def social_label(profile, name):
    for social in profile.get("socials", []):
        if social.get("name") == name:
            url = social.get("url", "")
            slug = url.rstrip("/").rsplit("/", 1)[-1]
            return f'{name.capitalize()}: <span>{slug}</span>'
    return ""


def main():
    with open(PROFILE, encoding="utf-8") as fh:
        profile = yaml.safe_load(fh)

    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()

    replacements = {
        "{{name}}": profile["name"],
        "{{role}}": profile["role"],
        "{{email}}": profile["contact"]["email"],
        "{{phone}}": profile["contact"].get("phone", ""),
        "{{location}}": profile.get("location", ""),
        "{{summary}}": first_paragraph(profile.get("bio", "")),
        "{{github_label}}": social_label(profile, "github"),
        "{{linkedin_label}}": social_label(profile, "linkedin"),
        "{{experience}}": experience_html(profile.get("experience", [])),
        "{{education}}": education_html(profile.get("education", [])),
        "{{projects}}": projects_html(profile.get("projects", [])),
        "{{skills}}": skills_html(profile.get("skills", [])),
        "{{languages}}": languages_html(profile.get("languages", [])),
        "{{achievements}}": achievements_html(profile.get("achievements", [])),
    }
    for key, value in replacements.items():
        html = html.replace(key, value)

    port = free_port()
    profile_dir = tempfile.mkdtemp(prefix="cv-profile-")
    proc = start_chrome(port, profile_dir)
    try:
        ws = wait_for_devtools(port)
        cdp = Cdp(ws)
        cdp.connect()
        tid = cdp.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        session = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        cdp.call("Page.enable", {}, session)

        data_url = "data:text/html;base64," + base64.b64encode(html.encode()).decode()
        cdp.call("Page.navigate", {"url": data_url}, session)
        time.sleep(1.2)

        result = cdp.call(
            "Page.printToPDF",
            {
                "printBackground": True,
                "preferCSSPageSize": True,
                "marginTop": 0.5,
                "marginBottom": 0.5,
                "marginLeft": 0.5,
                "marginRight": 0.5,
            },
            session,
        )
        with open(OUT, "wb") as fh:
            fh.write(base64.b64decode(result["data"]))
        print(f"OK  personal/cv.pdf {os.path.getsize(OUT)} bytes")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
