"""Draw the thumbnails for Ratul's five course projects.

Design constraints (docs/DESIGN.md): no stock photos, no AI-generated look,
no glossy 3D blobs. These are flat illustrations drawn with simple geometry —
a diagram or a piece of a console screen — so they read as a diagram of
what the program does rather than as a screenshot of something that never
ran.

Each one is 16:10, which is the ratio docs/DESIGN.md asks for, and the
palette is the graphite style's own, because graphite is the style the
site uses.

Files written:
    personal/photos/project-1.jpg   Hospital Management System
    personal/photos/project-2.jpg   Library Management System
    personal/photos/project-3.jpg   Smart Attendance Tracker
    personal/photos/project-4.jpg   Clap-Controlled Light Switch
    personal/photos/project-5.jpg   IoT Smart Energy Meter

Usage: python tools/make_project_covers.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "personal", "photos")

# The graphite palette from docs/DESIGN.md.
BG = (255, 255, 255)       # #FFFFFF
SURFACE = (245, 247, 249)  # #F5F7F9
ACCENT = (28, 102, 219)    # #1C66DB
INK = (31, 35, 40)         # #1F2328
MUTED = (89, 99, 110)      # #59636E
LINE = (225, 228, 232)     # #E1E4E8
PANEL = (255, 255, 255)


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


def save(img, path, quality=82):
    img.convert("RGB").save(path, "JPEG", quality=quality, optimize=True)
    size = os.path.getsize(path) // 1024
    print("%-40s %4d KB" % (os.path.relpath(path, ROOT), size))


def base(w=1600, h=1000):
    """A blank canvas with the faint grid the other drawings sit on."""
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    step = 80
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(248, 250, 252), width=2)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(248, 250, 252), width=2)
    return img, d


def window(d, x0, y0, x1, y1, title=None):
    """A console window: a title bar, a body, and a prompt line."""
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=PANEL, outline=LINE, width=3)
    if title:
        d.rounded_rectangle([x0, y0, x1, y0 + 56], radius=14, fill=SURFACE)
        d.rectangle([x0, y0 + 40, x1, y0 + 56], fill=SURFACE)
        d.line([(x0, y0 + 56), (x1, y0 + 56)], fill=LINE, width=3)
        f = font(24, bold=True)
        d.text((x0 + 26, y0 + 15), title, font=f, fill=INK)


def lines(d, x, y, widths, colour=MUTED, gap=34, height=13):
    """Rows of 'text', drawn as flat bars."""
    for i, wdt in enumerate(widths):
        d.rounded_rectangle([x, y + i * gap, x + wdt, y + i * gap + height],
                            radius=height // 2, fill=colour)


def chip(d, x, y, w, h, label, fill=SURFACE, outline=LINE, text=INK):
    """A small labelled box, like a menu entry or a pill."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill,
                        outline=outline, width=2)
    f = font(22, bold=True)
    bbox = d.textbbox((0, 0), label, font=f)
    d.text((x + (w - (bbox[2] - bbox[0])) / 2, y + (h - (bbox[3] - bbox[1])) / 2 - 4),
           label, font=f, fill=text)


def hospital(path):
    """A hospital system: patients, doctors and appointments in one file."""
    img, d = base()

    # A hospital block on the left.
    d.rounded_rectangle([90, 250, 430, 700], radius=16, fill=SURFACE,
                        outline=LINE, width=3)
    d.rectangle([90, 250, 430, 340], fill=ACCENT)
    d.rounded_rectangle([90, 250, 430, 700], radius=16, outline=LINE, width=3)
    f = font(30, bold=True)
    d.text((140, 278), "HOSPITAL", font=f, fill=(255, 255, 255))

    # A cross on the front.
    d.rectangle([238, 372, 282, 480], fill=ACCENT)
    d.rectangle([205, 405, 315, 447], fill=ACCENT)

    # Three rows of "patients" with a bed and a name bar.
    for i in range(3):
        y = 520 + i * 62
        d.rounded_rectangle([120, y, 180, y + 48], radius=10, fill=PANEL,
                            outline=LINE, width=2)
        d.ellipse([134, y + 8, 162, y + 36], fill=(200, 214, 232))
        lines(d, 200, y + 12, (140,), colour=(214, 220, 228), gap=0, height=11)
        lines(d, 200, y + 30, (100,), colour=(228, 232, 238), gap=0, height=10)

    # The three tables the system keeps, as stacked cards.
    labels = ("PATIENTS", "DOCTORS", "BILLING")
    for i, label in enumerate(labels):
        y = 190 + i * 230
        d.rounded_rectangle([600, y, 1130, y + 190], radius=14, fill=PANEL,
                            outline=LINE, width=3)
        d.rounded_rectangle([600, y, 624, y + 190], radius=12, fill=ACCENT)
        f = font(26, bold=True)
        d.text((656, y + 26), label, font=f, fill=INK)
        for row in range(3):
            ry = y + 78 + row * 34
            d.rounded_rectangle([656, ry, 656 + 180, ry + 14], radius=7,
                                fill=(222, 228, 236))
            d.rounded_rectangle([860, ry, 860 + 130, ry + 14], radius=7,
                                fill=(234, 237, 242))
            d.rounded_rectangle([1012, ry, 1012 + 80, ry + 14], radius=7,
                                fill=(240, 242, 245))

    # The file the records live in.
    d.rounded_rectangle([1180, 330, 1500, 640], radius=14, fill=SURFACE,
                        outline=LINE, width=3)
    f = font(24, bold=True)
    d.text((1214, 366), "patients.dat", font=f, fill=INK)
    lines(d, 1214, 420, (250, 200, 230, 170), colour=(216, 222, 230), gap=40)
    d.rounded_rectangle([1214, 566, 1400, 606], radius=10, fill=ACCENT)

    save(img, path)


def library(path):
    """A library system: books, members, and an issue slip."""
    img, d = base()

    # Shelves on the left.
    d.rounded_rectangle([80, 180, 560, 820], radius=14, fill=SURFACE,
                        outline=LINE, width=3)
    for row in range(3):
        y = 230 + row * 190
        d.line([(110, y + 150), (530, y + 150)], fill=LINE, width=6)
        x = 118
        heights = (110, 130, 96, 140, 104)
        for i, bh in enumerate(heights):
            if x + 42 > 520:
                break
            colour = ACCENT if (row + i) % 4 == 0 else (206, 214, 224)
            d.rectangle([x, y + 150 - bh, x + 34, y + 150], fill=colour)
            d.rectangle([x, y + 150 - bh + 18, x + 34, y + 150 - bh + 26],
                        fill=(255, 255, 255) if (row + i) % 4 == 0 else (224, 229, 236))
            x += 42

    # The member card.
    d.rounded_rectangle([620, 180, 1080, 470], radius=14, fill=PANEL,
                        outline=LINE, width=3)
    f = font(28, bold=True)
    d.text((656, 214), "MEMBER", font=f, fill=INK)
    d.rounded_rectangle([656, 272, 736, 352], radius=10, fill=SURFACE,
                        outline=LINE, width=2)
    d.ellipse([672, 286, 720, 334], fill=(200, 214, 232))
    lines(d, 762, 280, (250, 180), colour=(216, 222, 230), gap=40)
    d.rounded_rectangle([656, 382, 900, 424], radius=10, fill=SURFACE,
                        outline=LINE, width=2)
    f2 = font(22, bold=True)
    d.text((676, 392), "FINE: 2.00", font=f2, fill=MUTED)

    # The issue slip.
    d.rounded_rectangle([620, 520, 1500, 820], radius=14, fill=PANEL,
                        outline=LINE, width=3)
    f = font(26, bold=True)
    d.text((656, 552), "ISSUE / RETURN", font=f, fill=INK)
    d.line([(656, 602), (1464, 602)], fill=LINE, width=3)
    for i, (left, right) in enumerate((("BOOK", "DATE"), ("RETURNED", "STATUS"))):
        y = 634 + i * 78
        f2 = font(22, bold=True)
        d.text((656, y), left, font=f2, fill=MUTED)
        d.text((1000, y), right, font=f2, fill=MUTED)
        d.rounded_rectangle([656, y + 32, 900, y + 48], radius=8,
                            fill=(228, 233, 240))
        d.rounded_rectangle([1000, y + 32, 1200, y + 48], radius=8,
                            fill=(228, 233, 240))
    d.rounded_rectangle([1290, 690, 1464, 742], radius=10, fill=ACCENT)

    save(img, path)


def attendance(path):
    """An attendance tracker: a mark sheet and a percentage report."""
    img, d = base()

    # The sheet of marks on the left.
    d.rounded_rectangle([80, 160, 880, 840], radius=14, fill=PANEL,
                        outline=LINE, width=3)
    f = font(26, bold=True)
    d.text((116, 196), "ATTENDANCE SHEET", font=f, fill=INK)
    d.line([(116, 244), (844, 244)], fill=LINE, width=3)

    # Column headings.
    f2 = font(20, bold=True)
    for i, label in enumerate(("D1", "D2", "D3", "D4", "D5")):
        d.text((420 + i * 84, 268), label, font=f2, fill=MUTED)
    d.text((116, 268), "STUDENT", font=f2, fill=MUTED)

    # Five students, each with their own row of marks. The percentages on
    # the right are the ones these rows add up to.
    rows = (
        ("P", "P", "P", "P", "P"),
        ("P", "P", "A", "P", "P"),
        ("P", "A", "A", "P", "P"),
        ("P", "P", "P", "P", "L"),
        ("P", "A", "P", "P", "L"),
    )
    for row, marks in enumerate(rows):
        y = 322 + row * 92
        d.rounded_rectangle([116, y, 176, y + 60], radius=10, fill=SURFACE,
                            outline=LINE, width=2)
        d.ellipse([130, y + 10, 162, y + 42], fill=(200, 214, 232))
        lines(d, 196, y + 16, (170,), colour=(216, 222, 230), gap=0, height=13)
        for i, mark in enumerate(marks):
            cx = 420 + i * 84
            if mark == "A":
                fill, text = (232, 226, 226), (168, 74, 74)
            elif mark == "L":
                fill, text = (250, 244, 226), (168, 120, 34)
            else:
                fill, text = (226, 238, 232), (44, 122, 86)
            d.ellipse([cx, y + 8, cx + 52, y + 60], fill=fill)
            f3 = font(24, bold=True)
            d.text((cx + 14, y + 20), mark, font=f3, fill=text)
        d.line([(116, y + 76), (844, y + 76)], fill=(240, 242, 245), width=2)

    # The report on the right.
    d.rounded_rectangle([950, 160, 1520, 840], radius=14, fill=PANEL,
                        outline=LINE, width=3)
    f = font(26, bold=True)
    d.text((986, 196), "PERCENTAGE", font=f, fill=INK)
    d.line([(986, 244), (1484, 244)], fill=LINE, width=3)

    # Bars, one per student. The percentages are the ones the rows on the
    # left add up to, so the two halves of the picture agree.
    pcts = (100, 80, 60, 80, 60)
    for i, pct in enumerate(pcts):
        y = 288 + i * 100
        lines(d, 986, y + 8, (140,), colour=(216, 222, 230), gap=0, height=12)
        d.rounded_rectangle([986, y + 40, 1360, y + 66], radius=13,
                            fill=(238, 241, 245))
        filled = int(374 * pct / 100)
        colour = ACCENT if pct >= 80 else (176, 190, 208)
        d.rounded_rectangle([986, y + 40, 986 + filled, y + 66], radius=13,
                            fill=colour)
        f2 = font(24, bold=True)
        d.text((1384, y + 38), "%d%%" % pct, font=f2, fill=INK)

    save(img, path)


def clap_switch(path):
    """A sound sensor toggling a relay, and a lamp it switches."""
    img, d = base()

    # The sound waves coming from the left, hitting the sensor.
    cx, cy = 250, 500
    for i, r in enumerate((110, 175, 240)):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=-52, end=52,
              fill=ACCENT if i == 0 else (176, 202, 240), width=9)

    # The board with the sound sensor.
    d.rounded_rectangle([540, 330, 830, 670], radius=16, fill=SURFACE,
                        outline=LINE, width=3)
    d.rounded_rectangle([540, 330, 830, 670], radius=16, outline=LINE, width=3)
    # The microphone capsule.
    d.rounded_rectangle([610, 392, 760, 500], radius=16, fill=PANEL,
                        outline=ACCENT, width=4)
    for i in range(3):
        d.line([(640 + i * 30, 416), (640 + i * 30, 476)], fill=(190, 206, 232), width=5)
    f = font(22, bold=True)
    d.text((586, 540), "SOUND", font=f, fill=MUTED)
    f2 = font(22, bold=True)
    d.text((576, 596), "SENSOR", font=f2, fill=MUTED)

    # The wiring to the relay.
    d.line([(830, 470), (960, 470)], fill=INK, width=6)
    d.line([(960, 470), (960, 300)], fill=INK, width=6)

    # The relay block.
    d.rounded_rectangle([880, 180, 1090, 320], radius=14, fill=PANEL,
                        outline=LINE, width=3)
    f = font(24, bold=True)
    d.text((906, 208), "RELAY", font=f, fill=INK)
    d.rounded_rectangle([906, 258, 1020, 296], radius=9, fill=ACCENT)

    # The lamp on the right.
    d.line([(1090, 250), (1210, 250)], fill=INK, width=6)
    d.line([(1210, 250), (1210, 360)], fill=INK, width=6)

    # The bulb and its light.
    d.ellipse([1150, 360, 1270, 480], fill=(252, 222, 158))
    d.ellipse([1168, 378, 1252, 462], fill=(254, 238, 200))
    d.rectangle([1176, 476, 1244, 508], fill=(178, 190, 200))
    # Light rays.
    for angle_x, angle_y in ((1150, 380), (1270, 380), (1210, 330)):
        d.line([(angle_x, angle_y), (angle_x + (angle_x - 1210) // 4,
                                     angle_y + (angle_y - 420) // 4)],
               fill=(236, 196, 110), width=6)

    # The label under the bulb.
    d.rounded_rectangle([1104, 560, 1316, 620], radius=12, fill=SURFACE,
                        outline=LINE, width=2)
    f = font(22, bold=True)
    d.text((1140, 578), "LIGHT", font=f, fill=INK)

    # The Arduino board.
    d.rounded_rectangle([80, 760, 520, 900], radius=14, fill=(38, 58, 84))
    f = font(22, bold=True)
    d.text((110, 786), "ARDUINO", font=f, fill=(210, 226, 240))
    for i in range(4):
        d.rectangle([360 + i * 34, 786, 380 + i * 34, 812], fill=(150, 176, 200))
    d.line([(520, 830), (600, 830)], fill=INK, width=6)
    d.line([(600, 830), (600, 670)], fill=INK, width=6)

    save(img, path)


def energy_meter(path):
    """A current sensor on the mains line, reading onto a display."""
    img, d = base()

    # The mains line across the top.
    d.line([(140, 250), (1460, 250)], fill=INK, width=8)
    d.rectangle([700, 226, 760, 274], fill=(226, 232, 238))

    # The clamp around the live wire.
    d.rounded_rectangle([660, 190, 800, 310], radius=18, fill=PANEL,
                        outline=ACCENT, width=5)
    d.rounded_rectangle([690, 226, 770, 274], radius=8, fill=(238, 241, 245))
    f = font(22, bold=True)
    d.text((646, 322), "CURRENT", font=f, fill=MUTED)
    d.text((664, 352), "SENSOR", font=f, fill=MUTED)
    # The mains label sits clear of the clamp, on the line itself.
    d.text((340, 210), "MAINS", font=font(24, bold=True), fill=MUTED)

    # The board.
    d.rounded_rectangle([620, 470, 840, 620], radius=14, fill=(38, 58, 84))
    f = font(22, bold=True)
    d.text((652, 496), "ESP32", font=f, fill=(210, 226, 240))
    for i in range(5):
        d.rectangle([664 + i * 32, 556, 682 + i * 32, 580], fill=(150, 176, 200))
    d.line([(730, 310), (730, 470)], fill=INK, width=6)

    # The display.
    d.rounded_rectangle([980, 400, 1460, 640], radius=16, fill=(30, 42, 56))
    d.rounded_rectangle([1000, 420, 1440, 620], radius=10, fill=(22, 32, 44))
    f = font(58, bold=True)
    d.text((1044, 470), "240 V", font=f, fill=(120, 232, 176))
    f2 = font(40, bold=True)
    d.text((1044, 552), "0.42 kW", font=f2, fill=(120, 232, 176))
    d.line([(840, 545), (980, 545)], fill=INK, width=6)

    # A small bar chart under the display.
    heights = (70, 120, 95, 150, 110, 60)
    for i, bh in enumerate(heights):
        x = 1000 + i * 76
        d.rounded_rectangle([x, 880 - bh, x + 48, 880], radius=8,
                            fill=ACCENT if i == 3 else (176, 202, 240))
    d.line([(980, 880), (1450, 880)], fill=LINE, width=4)

    # The house outline on the left.
    d.polygon([(140, 640), (300, 500), (460, 640)], fill=SURFACE, outline=LINE)
    d.rectangle([160, 640, 440, 840], fill=SURFACE, outline=LINE, width=3)
    d.rectangle([260, 730, 340, 840], fill=PANEL, outline=LINE, width=3)
    d.rectangle([200, 680, 250, 730], fill=PANEL, outline=LINE, width=3)
    d.rectangle([350, 680, 400, 730], fill=PANEL, outline=LINE, width=3)
    d.line([(140, 250), (160, 640)], fill=INK, width=8)
    f = font(22, bold=True)
    d.text((236, 866), "HOME", font=f, fill=MUTED)

    save(img, path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    hospital(os.path.join(OUT, "project-1.jpg"))
    library(os.path.join(OUT, "project-2.jpg"))
    attendance(os.path.join(OUT, "project-3.jpg"))
    clap_switch(os.path.join(OUT, "project-4.jpg"))
    energy_meter(os.path.join(OUT, "project-5.jpg"))
