"""Generate the demo education, award and gallery images.

Design constraints (docs/DESIGN.md, TASK-01): no stock photos of people,
no AI-generated look, no glossy 3D blobs. These are flat, style-neutral
illustrations drawn with simple geometry: a campus building silhouette, a
certificate sheet, and a set of abstract scene cards.

Files written:
    personal/photos/edu-1.jpg          (4:3, campus)
    personal/photos/edu-2.jpg          (4:3, campus)
    personal/photos/award-1.jpg        (portrait, certificate sheet)
    personal/photos/award-2.jpg        (portrait, certificate sheet)
    personal/photos/award-3.jpg        (portrait, certificate sheet)
    personal/photos/gallery/ride.jpg   (4:3)
    personal/photos/gallery/market.jpg  (4:3)
    personal/photos/gallery/evening.jpg(3:4)
    personal/photos/gallery/road.jpg   (4:3)

Usage: python tools/make_media.py
"""
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "personal", "photos")
GALLERY = os.path.join(OUT, "gallery")

# The harbour palette from docs/DESIGN.md, so the demo images sit with the
# demo style rather than fighting it.
BG = (246, 248, 251)      # #F6F8FB
SURFACE = (255, 255, 255)
ACCENT = (14, 116, 144)    # #0E7490
INK = (20, 32, 51)        # #142033
MUTED = (82, 96, 122)     # #52607A
LINE = (220, 227, 236)    # #DCE3EC


def save(img, path, quality=78):
    img.convert("RGB").save(path, "JPEG", quality=quality, optimize=True)
    size = os.path.getsize(path) // 1024
    print("%-44s %4d KB" % (os.path.relpath(path, ROOT), size))


def campus(path, w=960, h=720, variant=0):
    """A flat campus building on a soft ground: no people, no stock photo."""
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    ground = int(h * 0.74)
    d.rectangle([0, ground, w, h], fill=(238, 242, 246))

    # A long academic block with a taller centre tower.
    if variant == 0:
        blocks = [(150, 250, 360, ground), (360, 170, 600, ground),
                  (600, 250, 810, ground)]
        tower = (420, 120, 540, ground)
    else:
        blocks = [(110, 270, 300, ground), (300, 200, 520, ground),
                  (520, 270, 700, ground), (700, 230, 860, ground)]
        tower = (370, 140, 490, ground)

    for x0, y0, x1, y1 in blocks:
        d.rectangle([x0, y0, x1, y1], fill=SURFACE, outline=LINE, width=3)

    d.rectangle(tower, fill=SURFACE, outline=LINE, width=3)
    d.rectangle([tower[0], tower[1], tower[2], tower[1] + 26], fill=ACCENT)

    # Windows: a regular grid, drawn as flat rectangles.
    for x0, y0, x1, y1 in blocks:
        cols = max(2, (x1 - x0) // 54)
        rows = max(1, (y1 - y0 - 40) // 62)
        pad_x = (x1 - x0 - cols * 30) // (cols + 1)
        for c in range(cols):
            for r in range(rows):
                wx = x0 + pad_x * (c + 1) + 30 * c
                wy = y0 + 46 + 62 * r
                if wy + 30 > y1 - 12:
                    continue
                d.rectangle([wx, wy, wx + 24, wy + 30], fill=(210, 226, 233))

    # A path to the door.
    door_x = (tower[0] + tower[2]) // 2
    d.polygon([(door_x - 46, ground), (door_x + 46, ground),
               (door_x + 90, h), (door_x - 90, h)], fill=(226, 232, 238))
    d.rectangle([door_x - 20, ground - 34, door_x + 20, ground], fill=ACCENT)

    # A few trees: flat circles on a trunk.
    for tx in (70, 250, 690, 890):
        d.rectangle([tx - 4, ground - 46, tx + 4, ground], fill=(178, 190, 200))
        d.ellipse([tx - 34, ground - 96, tx + 34, ground - 18], fill=(196, 216, 210))

    save(img, path)


def certificate(path, w=800, h=1067, label=None):
    """A portrait certificate sheet: a document, shown whole, no crop."""
    img = Image.new("RGB", (w, h), (233, 238, 243))
    d = ImageDraw.Draw(img)

    m = 60
    d.rectangle([m, m, w - m, h - m], fill=SURFACE, outline=LINE, width=3)

    # A ribbon band across the top, like a printed certificate.
    d.rectangle([m, m, w - m, m + 96], fill=ACCENT)
    d.rectangle([m, m + 88, w - m, m + 96], fill=(20, 92, 115))

    # A gold seal.
    cx, cy, r = w // 2, int(h * 0.52), 74
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 172, 74))
    d.ellipse([cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12],
              outline=(176, 138, 52), width=3)

    # Lines of "text" on the certificate — no real words baked in.
    d.rectangle([cx - 150, cy - 8, cx + 150, cy + 4], fill=(196, 202, 210))
    d.rectangle([cx - 96, cy + 22, cx + 96, cy + 31], fill=(216, 221, 227))

    for i, y in enumerate((int(h * 0.66), int(h * 0.70), int(h * 0.74))):
        inset = 40 if i == 2 else 0
        d.rectangle([m + 90 + inset, y, w - m - 90 - inset, y + 9],
                    fill=(214, 219, 225))

    # A signature line and a stamp.
    d.rectangle([m + 90, int(h * 0.82), m + 300, int(h * 0.82) + 3],
                fill=(180, 188, 197))
    d.ellipse([w - m - 170, int(h * 0.78), w - m - 80, int(h * 0.78) + 90],
              outline=ACCENT, width=4)

    save(img, path)


def scene(path, kind, w=960, h=720):
    """Flat abstract scene cards for the gallery."""
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    if kind == "ride":
        # A road going to the horizon under a graded sky.
        for y in range(h):
            t = y / h
            r = int(232 + (196 - 232) * t)
            g = int(240 + (214 - 240) * t)
            b = int(246 + (226 - 246) * t)
            d.line([(0, y), (w, y)], fill=(r, g, b))
        horizon = int(h * 0.58)
        d.rectangle([0, horizon, w, h], fill=(126, 134, 142))
        d.polygon([(w * 0.44, horizon), (w * 0.56, horizon),
                   (w * 0.78, h), (w * 0.22, h)], fill=(96, 104, 112))
        for i in range(4):
            y = horizon + 30 + i * 52
            d.rectangle([w * 0.5 - 7, y, w * 0.5 + 7, y + 26], fill=SURFACE)
        for x, s in ((120, 70), (300, 52), (700, 60), (860, 46)):
            d.rectangle([x - 4, horizon - s - 40, x + 4, horizon], fill=(120, 128, 136))
            d.ellipse([x - s // 2, horizon - s - 92, x + s // 2, horizon - 40],
                      fill=(150, 176, 160))

    elif kind == "market":
        # A row of market stalls with awnings.
        d.rectangle([0, int(h * 0.62), w, h], fill=(232, 236, 240))
        for i in range(3):
            x0 = 40 + i * 300
            x1 = x0 + 250
            top = int(h * 0.26) + (i % 2) * 24
            d.rectangle([x0, top, x1, int(h * 0.62)], fill=SURFACE, outline=LINE, width=3)
            d.rectangle([x0 - 12, top - 30, x1 + 12, top], fill=ACCENT)
            for s in range(6):
                sx = x0 + 6 + s * 40
                d.rectangle([sx, top - 30, sx + 20, top], fill=(232, 244, 246))
            d.rectangle([x0 + 30, int(h * 0.48), x0 + 90, int(h * 0.62)], fill=(214, 226, 232))
            for r in range(3):
                for c in range(4):
                    cx = x0 + 110 + c * 32
                    cy = int(h * 0.52) + r * 26
                    d.ellipse([cx, cy, cx + 20, cy + 20], fill=(206, 154, 92))
        d.ellipse([w - 190, 40, w - 90, 140], fill=(232, 208, 140))

    elif kind == "evening":
        # A dusk sky: a tall portrait card. The gradient stays in the
        # harbour palette — warm near the horizon, cool blue above — so
        # it reads as one system and never as a purple wash.
        for y in range(h):
            t = y / h
            r = int(198 - 44 * t)
            g = int(206 - 42 * t)
            b = int(214 - 30 * t)
            d.line([(0, y), (w, y)], fill=(r, g, b))
        d.ellipse([w * 0.52, h * 0.12, w * 0.78, h * 0.38], fill=(246, 238, 208))
        d.rectangle([0, int(h * 0.80), w, h], fill=(64, 74, 82))
        for x, s in ((140, 150), (330, 110), (700, 132)):
            d.rectangle([x - 6, int(h * 0.80) - s, x + 6, int(h * 0.80)],
                        fill=(48, 56, 62))
            d.ellipse([x - s // 2, int(h * 0.80) - s - 70, x + s // 2, int(h * 0.80) - s],
                      fill=(66, 84, 76))
        for i in range(40):
            import random
            rx = random.Random(i * 7 + 3).randint(0, w - 4)
            ry = random.Random(i * 13 + 5).randint(0, int(h * 0.5))
            d.point((rx, ry), fill=(246, 240, 220))

    else:  # road
        # A tree-lined road seen from above.
        d.rectangle([0, 0, w, h], fill=(226, 232, 226))
        d.polygon([(w * 0.40, 0), (w * 0.60, 0), (w * 0.78, h), (w * 0.22, h)],
                  fill=(104, 110, 116))
        for i in range(6):
            y = 30 + i * 130
            d.rectangle([w * 0.5 - 6, y, w * 0.5 + 6, y + 58], fill=(240, 232, 200))
        for side in (-1, 1):
            for i in range(4):
                cx = w * 0.5 + side * (190 + i * 30)
                cy = 70 + i * 170
                d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=(178, 200, 176))
                d.rectangle([cx - 5, cy, cx + 5, cy + 90], fill=(150, 132, 112))

    save(img, path)


def main():
    os.makedirs(GALLERY, exist_ok=True)

    campus(os.path.join(OUT, "edu-1.jpg"), variant=0)
    campus(os.path.join(OUT, "edu-2.jpg"), variant=1)

    certificate(os.path.join(OUT, "award-1.jpg"))
    certificate(os.path.join(OUT, "award-2.jpg"))
    certificate(os.path.join(OUT, "award-3.jpg"))

    scene(os.path.join(GALLERY, "ride.jpg"), "ride")
    scene(os.path.join(GALLERY, "market.jpg"), "market")
    scene(os.path.join(GALLERY, "evening.jpg"), "evening", w=720, h=960)
    scene(os.path.join(GALLERY, "road.jpg"), "road")


if __name__ == "__main__":
    main()
