"""Generate neutral placeholder images for personal/photos/.

Design constraints (docs/DESIGN.md): no stock photos of people. Placeholders are
solid tone + initials / simple geometric shapes only.

File names are fixed (personal/README.md):
    profile.jpg     the portrait
    project-1.jpg   1st project in profile.yaml
    project-2.jpg   2nd project in profile.yaml
    hobby-1.jpg     1st hobby in profile.yaml
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "personal", "photos")
os.makedirs(OUT, exist_ok=True)

HARBOR_BG = (246, 248, 251)      # #F6F8FB
HARBOR_ACCENT = (14, 116, 144)   # #0E7490
HARBOR_INK = (20, 32, 51)        # #142033
HARBOR_MUTED = (82, 96, 122)     # #52607A
HARBOR_SURFACE = (255, 255, 255)


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeui%s.ttf" % ("bd" if bold else ""),
        "C:/Windows/Fonts/arial%s.ttf" % ("bd" if bold else ""),
        "C:/Windows/Fonts/verdana.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def initials_image(path, size=(1200, 1500), initials="TR"):
    """4:5 portrait placeholder: soft tone, accent rule, initials."""
    w, h = size
    img = Image.new("RGB", size, HARBOR_BG)
    d = ImageDraw.Draw(img)

    # Subtle vertical tone shift so it does not look like a dead flat swatch.
    for y in range(h):
        t = y / h
        r = int(HARBOR_BG[0] - 6 * t)
        g = int(HARBOR_BG[1] - 6 * t)
        b = int(HARBOR_BG[2] - 4 * t)
        d.line([(0, y), (w, y)], fill=(r, g, b))

    # Large soft circle behind the initials.
    cx, cy = w // 2, int(h * 0.46)
    radius = int(min(w, h) * 0.30)
    d.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=HARBOR_SURFACE,
        outline=(220, 227, 236),
        width=3,
    )

    # Initials.
    f = font(int(radius * 0.86), bold=True)
    bbox = d.textbbox((0, 0), initials, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), initials,
           font=f, fill=HARBOR_ACCENT)

    # Accent rule below the circle.
    rule_w = int(w * 0.22)
    rule_y = int(h * 0.74)
    d.rectangle(
        [cx - rule_w // 2, rule_y, cx + rule_w // 2, rule_y + 8],
        fill=HARBOR_ACCENT,
    )

    # Quiet baseline label.
    f2 = font(int(h * 0.030))
    label = "photo placeholder"
    bbox = d.textbbox((0, 0), label, font=f2)
    d.text((cx - (bbox[2] - bbox[0]) / 2, rule_y + int(h * 0.035)), label,
           font=f2, fill=HARBOR_MUTED)

    img.save(path, "JPEG", quality=88, optimize=True)
    print("wrote", path, img.size)


def project_image(path, size=(1600, 1000)):
    """16:10 project placeholder: calm blocks + a single accent shape."""
    w, h = size
    img = Image.new("RGB", size, HARBOR_BG)
    d = ImageDraw.Draw(img)

    # Faint grid so it reads as a UI placeholder rather than a photo.
    step = 80
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(240, 244, 249), width=2)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(240, 244, 249), width=2)

    # Card blocks.
    d.rounded_rectangle([120, 150, 700, 470], radius=18,
                        fill=HARBOR_SURFACE, outline=(220, 227, 236), width=3)
    d.rounded_rectangle([760, 150, 1340, 470], radius=18,
                        fill=HARBOR_SURFACE, outline=(220, 227, 236), width=3)
    d.rounded_rectangle([120, 530, 1340, 850], radius=18,
                        fill=HARBOR_SURFACE, outline=(220, 227, 236), width=3)

    # Accent shape: a simple rounded square, not a logo.
    d.rounded_rectangle([240, 220, 460, 400], radius=14, fill=HARBOR_ACCENT)
    d.rounded_rectangle([880, 220, 1100, 400], radius=14,
                        fill=(220, 227, 236))

    # Text lines to suggest content.
    for i, wdt in enumerate((320, 260, 300, 240)):
        d.rounded_rectangle(
            [780, 220 + i * 46, 780 + wdt, 220 + i * 46 + 16],
            radius=8, fill=HARBOR_MUTED if i == 0 else (224, 230, 238),
        )
    for i, wdt in enumerate((700, 560, 620)):
        d.rounded_rectangle(
            [200, 600 + i * 52, 200 + wdt, 600 + i * 52 + 18],
            radius=9, fill=(232, 237, 244),
        )

    img.save(path, "JPEG", quality=88, optimize=True)
    print("wrote", path, img.size)


if __name__ == "__main__":
    initials_image(os.path.join(OUT, "profile.jpg"))
    project_image(os.path.join(OUT, "project-1.jpg"))
    project_image(os.path.join(OUT, "project-2.jpg"))
    initials_image(os.path.join(OUT, "hobby-1.jpg"), size=(900, 900))
