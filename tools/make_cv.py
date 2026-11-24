"""Generate a one-page placeholder CV at static/files/cv.pdf.

Reads data/profile.yaml so the placeholder stays in sync with the site data.
No third-party dependencies: the PDF is written by hand with base-14 fonts.
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "static", "files", "cv.pdf")

# Minimal YAML reader for this flat profile file.
def load_profile():
    data, key = {}, None
    with open(os.path.join(ROOT, "data", "profile.yaml"), encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            m = re.match(r'^([A-Za-z_][\w]*):\s*(.*)$', line)
            if m and not line.startswith(" "):
                key = m.group(1)
                val = m.group(2).strip()
                if val.startswith("[") and val.endswith("]"):
                    items = [v.strip().strip('"') for v in val[1:-1].split(",") if v.strip()]
                    data[key] = items
                elif val.startswith('"') and val.endswith('"'):
                    data[key] = val[1:-1]
                elif val:
                    data[key] = val
                else:
                    data[key] = []
    return data


def esc(s):
    return (s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)"))


def text(x, y, size, font, s):
    return f"BT /{font} {size} Tf 1 0 0 1 {x} {y} Tm ({esc(s)}) Tj ET\n"


def build(p):
    W, H = 595.28, 841.89  # A4
    c = []
    c.append("0.055 0.455 0.565 rg 6 0 0 6 56 760 re f")  # accent swatch
    c.append(text(76, 762, 22, "F2", p.get("name", "")))
    c.append(text(76, 742, 10.5, "F1", p.get("role", "")))
    c.append(text(76, 726, 9.5, "F1", p.get("now", "")))
    c.append("0.055 0.455 0.565 RG 1 w 56 712 m 539 712 l S")

    y = 688
    c.append(text(56, y, 13, "F2", "Profile"))
    y -= 18
    bio = p.get("bio", "").split("\n\n")[0]
    for line in wrap(bio, 92):
        c.append(text(56, y, 10, "F1", line))
        y -= 13.5

    y -= 16
    c.append(text(56, y, 13, "F2", "Education"))
    y -= 18
    for line in [
        "B.Sc. in Computer Science and Engineering",
        "Daffodil International University, 2024 - Present",
        "Higher Secondary Certificate (Science)",
        "Savar Cantonment Public School & College, 2021 - 2023",
    ]:
        c.append(text(56, y, 10, "F1", line))
        y -= 13.5

    y -= 16
    c.append(text(56, y, 13, "F2", "Experience"))
    y -= 18
    for line in ["Web development intern, Example Tech Ltd.", "Jun 2026 - Aug 2026"]:
        c.append(text(56, y, 10, "F1", line))
        y -= 13.5

    y -= 16
    c.append(text(56, y, 13, "F2", "Skills"))
    y -= 18
    skills = ", ".join(p.get("skills", []))
    for line in wrap(skills, 92):
        c.append(text(56, y, 10, "F1", line))
        y -= 13.5

    y -= 16
    c.append(text(56, y, 13, "F2", "Contact"))
    y -= 18
    contact = p.get("contact", {})
    for line in [p.get("email", ""), p.get("location", "")]:
        if line:
            c.append(text(56, y, 10, "F1", line))
            y -= 13.5

    c.append(text(56, 56, 8.5, "F3", "Placeholder CV - replace with a real document."))

    stream = "".join(c)
    objs = []
    objs.append("<< /Type /Catalog /Pages 2 0 R >>")
    objs.append("<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objs.append(
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] "
        "/Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R >> >> "
        "/Contents 4 0 R >>" % (W, H)
    )
    objs.append(
        "<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream)
    )
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n".encode("latin-1", "replace")
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(out)


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pdf = build(load_profile())
    with open(OUT, "wb") as fh:
        fh.write(pdf)
    print("wrote", OUT, len(pdf), "bytes")
