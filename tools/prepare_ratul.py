"""Prepare Ratul's photos for the site.

Every input image was opened and looked at before this script was written.
The decisions are in docs/reports/FRIEND-ratul-report.md.

The script:
  * crops the portrait to 4:5 with the face near the centre,
  * copies each chosen image to its fixed name under personal/photos/,
  * re-saves every image, which drops the EXIF block (the input files
    carry no EXIF anyway, but a re-save guarantees it).

Run from the repository root:
    python tools/prepare_ratul.py
"""
import os
import shutil

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_friends-input", "ratul")
DST = os.path.join(ROOT, "personal", "photos")

# Fixed name -> (source path relative to SRC, crop box or None)
#
# The crop boxes were worked out by eye against the pictures. A box is
# (left, upper, right, lower) in the source image's own pixels.
#
# The portrait is the campus photo: Ratul in a white shirt in front of the
# dome at DIU. The source is 1024x1036, which is almost square. A 4:5 crop
# is 829x1036, so the picture is narrowed rather than shortened, and the
# crop is centred on him with the dome still behind his head.
PORTRAIT_CROP = (111, 0, 940, 1036)  # 4:5, Ratul centred, dome behind him

# The avatar is the small formal photo: a square crop of the black suit
# picture, so the head sits in the middle of the circle.
AVATAR_CROP = (0, 0, 1108, 1108)  # square, head centred

PHOTOS = {
    # The portrait: Ratul in a white shirt, DIU campus, the dome behind him.
    "profile.jpg": ("1-profile-photo/ratul-main-portrait.jpg", PORTRAIT_CROP, 0),
    # The small formal photo: black suit, used for the avatar spots.
    "avatar.jpg": ("1-profile-photo/ratul-suit-avatar.png", AVATAR_CROP, 0),
    # Education, newest first. The list in profile.yaml is DIU, Milestone
    # College, then the school, so the photos are numbered the same way.
    #
    #   edu-1  Daffodil International University — the main building.
    #   edu-2  Milestone College — the campus with the academic block and
    #          the convocation on the field. Both of the college photos
    #          supplied are real campus photographs; neither is a logo.
    #   edu-3  Liaquat Ali Memorial High School — the school building
    #          under its trees.
    "edu-1.jpg": ("5-school-college-photos/3-university/images.jpg", None, 0),
    "edu-2.jpg": ("5-school-college-photos/2-college/WhatsApp Image 2026-11-23 at 21.29.43.jpeg",
                   None, 0),
    "edu-3.jpg": ("5-school-college-photos/1-school/WhatsApp Image 2026-11-23 at 21.29.40.jpeg",
                   None, 0),
    # Achievement: the "Unlock the Algorithm" certificate. It was
    # photographed sideways, so it is turned a quarter turn anticlockwise
    # here and the text reads the right way round from then on.
    "award-1.jpg": ("6-achievements-certificates/WhatsApp Image 2026-11-23 at 21.30.49.jpeg",
                    None, 90),
    # Hobby: Ratul on the motorcycle at golden hour.
    "hobby-1.jpg": ("3-hobby-photos/WhatsApp Image 2026-11-23 at 21.29.41.jpeg", None, 0),
    # Hobby: a second one, the trees.
    "hobby-2.jpg": ("3-hobby-photos/WhatsApp Image 202-23 at 21.29.41.jpeg", None, 0),
}

# The gallery: the rest of the pictures that look good on their own.
#
# The university appears twice, as the education entry photo and as a
# gallery picture: the cover is the whole campus from the air.
GALLERY = {
    "campus-congregation.jpg": ("5-school-college-photos/2-college/WhatsApp Image 2026-11-23 at 21.29.43.jpeg", 0),
    "campus-pool.jpg": ("5-school-college-photos/2-college/WhatsApp Image 2026-11-23 at 21.29.44.jpeg", 0),
    "campus-aerial.jpg": ("5-school-college-photos/3-university/daffodil_international_university_cover.jpg", 0),
    "night-ride.jpg": ("WhatsApp Image 2026-11-23 at 21.29.42.jpeg", 0),
    "trees.jpg": ("3-hobby-photos/WhatsApp Image 2026-11-23 at 21.29..jpeg", 0),
    "birds.jpg": ("3-hobby-photos/WhatsApp Image 2026-11-23 at 21.29.42.jpeg", 0),
    "dusk.jpg": ("3-hobby-photos/WhatsApp Image 2026-11-23 at eg.jpeg", 0),
    "bridge.jpg": ("3-hobby-photos/WhatsApp Image 2026-11-23 at 21.21.jpeg", 0),
    "river.jpg": ("3-hobby-photos/WhatsApp Image 2026-11-23 at .jpeg", 0),
    "cow.jpg": ("3-hobby-photos/WhatsApp Image 2026-11-2peg.jpeg", 0),
}


def save(src_path, out_path, crop=None, rotate=0):
    im = Image.open(src_path)
    im.load()
    if rotate:
        # The certificate was photographed sideways. There is no EXIF
        # orientation tag on it, so the turn has to be baked into the file.
        im = im.rotate(rotate, expand=True)
    if crop:
        im = im.crop(crop)
    # Re-saving without the exif argument drops the EXIF block. The inputs
    # have none, but this makes sure of it for anything added later.
    im.convert("RGB").save(out_path, "JPEG", quality=88, optimize=True)
    return im.size


def main():
    os.makedirs(os.path.join(DST, "gallery"), exist_ok=True)

    for name, (rel, crop, rotate) in PHOTOS.items():
        src = os.path.join(SRC, rel)
        out = os.path.join(DST, name)
        size = save(src, out, crop, rotate)
        print(f"{name:<14} {size!s:<14} <- {rel}")

    for name, (rel, rotate) in GALLERY.items():
        src = os.path.join(SRC, rel)
        out = os.path.join(DST, "gallery", name)
        size = save(src, out, None, rotate)
        print(f"gallery/{name:<9} {size!s:<14} <- {rel}")


if __name__ == "__main__":
    main()
