"""Turn the Smart Traffic System screenshots into a project thumbnail.

The project is a real deployed web app, so its thumbnail is a real
screenshot of it rather than an illustration. That is the difference from
tools/make_project_covers.py, which draws the console projects.

Both screenshots are taken from the live deployment with the DevTools
screenshot tool, at 1440x900 CSS pixels and a device pixel ratio of 1.25,
so the PNGs are 1804x915.

The thumbnail is 16:10 (1600x1000) like every other project image, so the
crop is made from the wide viewport shot: the header and the dashboard
cards are what identify the app, and the records table is too tall to fit
without shrinking everything to nothing.

Usage:
    python tools/make_traffic_cover.py
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.path.join(ROOT, ".scratch")
OUT = os.path.join(ROOT, "personal", "photos")

# The wide shot: the app header with the title and the nav, and the
# dashboard card row underneath it.
SOURCE = os.path.join(SCRATCH, "sts-viewport.png")

# 16:10, the ratio every project thumbnail uses.
WIDTH, HEIGHT = 1600, 1000


def main():
    if not os.path.exists(SOURCE):
        raise SystemExit(
            "missing %s\n"
            "Take it from the live deployment first:\n"
            "  1. open https://252-15-826-sketch.github.io/smart-traffic-system/\n"
            "  2. resize the window to 1440x900\n"
            "  3. scroll to the top and take a viewport screenshot\n"
            "  4. save it as .scratch/sts-viewport.png" % SOURCE
        )

    im = Image.open(SOURCE).convert("RGB")

    # Crop to 16:10 out of the middle-left of the shot: the header and the
    # dashboard, without the wide empty margin on the right.
    target_ratio = WIDTH / HEIGHT
    crop_w = im.height * target_ratio
    if crop_w <= im.width:
        left = 0
    else:
        left = (im.width - crop_w) // 2
    crop = im.crop((left, 0, left + crop_w, im.height))

    crop = crop.resize((WIDTH, HEIGHT), Image.LANCZOS)

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "project-6.jpg")
    crop.save(path, "JPEG", quality=86, optimize=True)
    print("%-40s %4d KB" % (os.path.relpath(path, ROOT),
                            os.path.getsize(path) // 1024))


if __name__ == "__main__":
    main()
