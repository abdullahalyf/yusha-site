# FRIEND-SITE.md — the recipe for building somebody else's site

This is the recipe for an agent (or a person) who is building a personal
website for a friend, using this template.

**The rule that matters most: do not invent anything.** Every word on the
site has to come from the friend's own answers. If they did not answer
something, leave it empty — the site hides the section — and list it in the
report at the end. A site with three honest sections is better than a site
with seven sections somebody made up.

---

## What you get

Two things:

1. The friend's filled-in copy of `docs/INTAKE-FORM.md` — their answers, in
   Bangla or English, however they wrote them.
2. Their photos: a portrait, optionally a CV, optionally photos for their
   projects and hobbies.

## What you produce

1. Their fork of this repository, with `personal/` filled in.
2. A report at `docs/reports/FRIEND-<name>-report.md`.

---

## Step 1 — get their fork

Ask the friend to fork the repository on GitHub and give you the URL. Their
username is question 24 on the intake form.

```bash
git clone https://github.com/<their-username>/<their-repo>.git
cd <their-repo>
```

Do not work in this repository. Every friend gets their own fork, and their
content goes into their fork.

Check that the fork has the theme and the template, not just the `personal/`
folder:

```bash
ls themes/folio/layouts/ hugo.toml .hugo-version
```

If those are missing, their fork was made from the wrong base — ask them to
re-fork from `abdullahalyf/hugo-personal-website`.

## Step 2 — read their answers properly

Read the whole intake form first, before touching any file. Then read
`personal/profile.yaml` in their fork: it holds the demo content, and every
field you need is already there with a comment explaining it.

Work through the form in order and note, for each answer:

- what it maps to in `profile.yaml`
- whether it is present or missing
- whether it needs rewriting or can be used close to as written

**The rewriting rule.** Their answers will be in Bangla, in casual English, or
in shorthand. The site is in plain, professional English. Rewrite each answer
into that voice — but only the words. Do not add a project they did not
mention, do not sharpen a claim they did not make, do not guess a year, a
grade, a company or a link. If they said "made a website for my uncle's
shop", write that. If they did not say what tech it uses, leave `tech: []`.

## Step 3 — fill in `personal/profile.yaml`

Replace the demo content. The fields, in the order they appear in the file:

| Field | From the form | Notes |
|---|---|---|
| `name` | Q1 | Required. The name as it should appear on the site. |
| `short_name` | Q2 | Optional. Used in greetings. |
| `role` | Q3 | Required. One line: who they are. |
| `now` | Q4 | Required. One sentence: what they are doing now. |
| `photo_alt` | — | `Portrait of <name>`. Write it for someone who cannot see the photo. |
| `location` | Q5 | City or area only. They were asked not to give a full address. |
| `facts` | Q3, Q5, Q17–Q19 | 3–4 short facts for the home page. |
| `bio` | Q6 | Required. 4–6 lines, in English. The first paragraph is the one shown on the home page. |
| `education` | Q10 | Newest first. `degree`, `institution`, `start`, `end`, `detail`. |
| `experience` | Q11 | Newest first. `title`, `org`, `start`, `end`, `detail`. |
| `skills` | Q12–Q14 | Groups of `items`. The first two groups appear on the home page. |
| `projects` | Q15 | 2–6. `title`, `summary`, `tech`, `live`, `code`, `featured`. |
| `achievements` | Q16 | `year`, `title`, `issuer`. |
| `languages` | Q17 | Plain list. |
| `hobbies` | Q18 | `title` and `text` for each. |
| `gallery` | — | Optional. `file` (name without extension) and `caption` for each photo in `photos/gallery/`. |
| `highlight_academics` | — | `true` puts CGPA/GPA first in the facts row on the home page. |
| `academics` | Q10 | Optional. Short results, e.g. `"CGPA 3.70 / 4.00"`. |
| `contact.email` | Q19 | Required. |
| `contact.phone` | Q20 | Only if they said yes. |
| `contact.note` | Q22 | One line for the contact page. |
| `socials` | Q21 | `name` and `url` for each. Allowed names: `github`, `linkedin`, `facebook`, `x`, `instagram`, `youtube`, `website`, `behance`, `dribbble`, `medium`. |

### What to leave empty

Anything the friend did not answer. The site hides those sections by itself:

```yaml
projects: []          # the whole projects section disappears
achievements: []      # and the achievements section
hobbies: []           # and the hobbies section
languages: []         # and the languages list
socials: []           # and the social row
phone: ""             # and the phone number
cv_url: ""            # and the Download CV button
```

Do not write `null`, do not write "TBD", do not write "Not provided yet".
Leave them empty and say so in the report.

### When the friend has no projects

A friend who has not shared any projects should not have four invented
ones. Leave `projects: []` and let the home page lead with the
achievements instead — the template does that on its own once there are two
or more achievements and fewer than two projects.

Keep one commented example in `profile.yaml` so the friend can fill it in
later:

```yaml
projects:
  # - title: "Campus Lost & Found"
  #   summary: "A web app where students post and claim lost items."
  #   tech: ["Laravel", "MySQL"]
  #   live: ""
  #   code: ""
  #   featured: true
```

To make the results stand out, set `highlight_academics: true` and fill in
`academics`. The CGPA then leads the facts row on the home page instead of
being buried in the education list.

### The six required fields

The build fails if any of these is empty, and the error message says which:

- `name`
- `role`
- `now`
- `bio`
- `contact.email`
- `photos/profile.jpg` (a file, not a field)

If the friend did not answer one of these, ask them. Do not guess.

## Step 4 — put their files in place

The site finds files by name, so the names have to match exactly.

```
personal/photos/profile.jpg     ← their portrait          (required)
personal/photos/avatar.jpg      ← small formal photo      (optional)
personal/photos/project-1.jpg   ← screenshot of project 1
personal/photos/project-2.jpg   ← screenshot of project 2
personal/photos/hobby-1.jpg     ← photo of hobby 1
personal/photos/edu-1.jpg       ← photo of education entry 1
personal/photos/award-1.jpg     ← certificate of achievement 1
personal/photos/gallery/        ← any number of photos, "Moments"
personal/cv.pdf                 ← their CV                (optional)
```

The number is the **position in `profile.yaml`**, not a number the friend
chose. If their first project in the file has no screenshot, the second
project's photo is `project-1.jpg`, and there is no `project-2.jpg`.

To be sure, check what the site actually asks for:

```bash
grep -rn "photos/project-" themes/folio/layouts/
```

`.jpg`, `.jpeg`, `.png` and `.webp` all work. The site converts them to
WebP itself, so leave them as they are.

A missing file is not an error. If they have no photo for a project, that
project is simply shown without one.

### The five photo sections

Every one of these is optional, and every one of them hides itself when the
file is missing. Add only the ones the friend has photos for.

**Portrait** — `photos/profile.jpg` is the big one: the hero on the home
page and the portrait on the About page. Crop it 4:5, with the person
centred.

**Avatar** — `photos/avatar.jpg` is the small formal photo. It is used
for every round avatar spot on the site: the header next to the name, the
author byline on a blog post, the contact block, and the Open Graph image
that link previews use. It is cropped to a square, so pick a picture that
survives a square crop — head and shoulders works best.

If `avatar.jpg` is missing, the site falls back to `profile.jpg` for all
of those, so nothing breaks and nothing needs to be done. The big portrait
always uses `profile.*`; the avatar never replaces it.

**Education photos** — `photos/edu-1.jpg` belongs to the first entry in
`education`, `edu-2.jpg` to the second, and so on. The image sits beside
the timeline entry, cropped to 4:3, and stacks above the text on a phone.

**Achievement certificates** — `photos/award-1.jpg` belongs to the first
entry in `achievements`. Certificates are usually portrait scans, so they
are shown whole on a light panel, never cropped, and clicking one opens it
full size.

**Gallery** — drop any number of files into `photos/gallery/`. They appear
in a "Moments" section on the About page, two across on a phone and three on
a desktop. To order them and give them captions, list them in
`profile.yaml`:

```yaml
gallery:
  - file: "ride"
    caption: "On the way to the hills"
  - file: "market"
    caption: "Saturday at the market"
```

`file` is the name without the extension. Images you do not list are shown
after the listed ones, with no caption, so a gallery works with no YAML at
all.

**Hobby photos** — `photos/hobby-1.jpg` belongs to the first entry in
`hobbies`, as with projects.

### Looking at the images

Open every photo before you put it in the folder. Blurry shots, duplicates
of the same moment and images where the face is cut off or the subject is
awkwardly framed belong in neither the gallery nor the timeline — leave them
out and say so in the report.

Certificates are scans of paper: keep them whole. A cropped certificate
that hides the name on it is worse than no certificate at all.

Strip location data before you add a photo. The site does not need it and
neither does anyone else:

```bash
exiftool -all= personal/photos/*.jpg
```

### Delete the demo leftovers

The template ships with a demo person in it: Tanvir Rahman, four projects,
two hobbies and a CV. **Delete the files that do not belong to your friend**,
or the site will show Tanvir's photos on a page about somebody else.

The names are positional, so the rule is simple: **keep exactly as many
`project-N.jpg` files as the friend has projects, and as many `hobby-N.jpg`
files as they have hobbies.** Any file beyond that is a leftover.

```bash
# How many projects and hobbies does the friend have?
grep -c "^  - title:" personal/profile.yaml

# What is there now?
ls personal/photos/ personal/blog/
```

Delete, for the demo person replaced by somebody with 2 projects and 1 hobby:

```
personal/photos/project-3.jpg
personal/photos/project-4.jpg
personal/photos/hobby-2.jpg
personal/cv.pdf          ← only if the friend has no CV
```

The same rule applies to the education and achievement photos: keep
`edu-N.jpg` for as many `education` entries as there are, and `award-N.jpg`
for as many `achievements` entries as there are. Anything above that number
is the demo's leftover.

```bash
# The demo ships two edu photos and three award photos.
ls personal/photos/edu-*.jpg personal/photos/award-*.jpg
```

`personal/cv.pdf` is the only one that is also a "remove it" case: the
template ships a demo CV, and a friend who did not bring one must not get a
"Download CV" button that opens somebody else's CV.

### The demo blog

The blog is the one part of the site that is **not** in `personal/`. The
posts live in `content/blog/`, and the template ships three of them, written
about Tanvir's own life ("my first Laravel app", "my semester study system",
"a trip to Sajek Valley").

If the friend did not write any posts, delete them:

```bash
rm content/blog/learning-laravel-app.md
rm content/blog/semester-study-system.md
rm content/blog/trip-to-sajek-valley.md
rm personal/blog/*.jpg        # the cover images for those posts
```

Keep `content/blog/_index.md` and `content/blog/README.md` — they are the
blog's index page and its instructions, not posts.

With no posts left the site hides the Blog link in the navigation and builds
no feed, so nothing points at an empty page. If the friend *did* write posts,
put them in `content/blog/` and their cover images in `personal/blog/`;
`content/blog/README.md` explains the front matter.

## Step 5 — choose the style

The friend may have named one on the form (Q23). If they did, use it. If
they said "any", or left it blank, pick the one that has not been used yet
by the other friends — each style should belong to one person so that two
sites do not look like the same site.

| style | for |
|---|---|
| `harbor` | calm, engineering |
| `grove` | warm, academic |
| `orchid` | creative, confident |
| `graphite` | a résumé to be read carefully |
| `saffron` | bright, friendly |

Set it in `hugo.toml`:

```toml
[params]
  style = "orchid"
```

Leave `layout` alone unless the friend asked for something specific — each
style already has the right hero layout for it.

## Step 6 — check the build

```bash
hugo --gc --minify --panicOnWarning
```

This must finish with **zero warnings and zero errors**. `--panicOnWarning`
turns a warning into a failure, which is what CI does, so it catches the
same problems CI would.

If it fails, read the error: it names the file and the field.

```
ERROR personal/profile.yaml: "name" is required but empty (or missing).
```

### Check that no demo name is left anywhere

The template ships with a demo person in it. Their name must not survive
anywhere on the friend's site — not in a page title, not in a meta
description, not in the RSS feed. After the build, look for it:

```bash
grep -ril "tanvir" public/ | head
```

Any file listed is a leftover. The usual causes:

- a `description:` in `content/*.md` that still names the demo person —
  the page descriptions take `{name}` and `{role}` instead, and the theme
  fills them in from `profile.yaml`;
- `params.description` in `hugo.toml` — left unset on purpose; when it is
  missing the site builds one from the profile;
- the demo blog posts, which are still in `content/blog/`.

Then look at the site before you push:

```bash
hugo server
```

Check the home page, the about page, the projects page and the contact page.
Switch to dark mode with the toggle in the header. Narrow the window to
about 375px wide and check it again on a phone.

## Step 7 — push to their fork

```bash
git checkout -b <their-username>/<name>   # or just work on the default branch
git add personal/ hugo.toml
git commit -m "Personal site for <Name>"
git push
```

Their Vercel project rebuilds automatically. If they have not set Vercel up
yet, the steps are in the main `README.md` under "Deploy to Vercel".

## Step 8 — write the report

At `docs/reports/FRIEND-<name>-report.md`, in their fork. It should say:

1. **What was filled in** — which sections are on the site and where each
   one came from (which question).
2. **What was left out and why** — every section that is empty because the
   friend did not answer, or did not want it. List them by name. This is
   the part that matters: it tells the friend what to add later.
3. **What was rewritten** — if you rewrote an answer into English, say
   which ones, so the friend can check the wording. If you had to drop a
   detail because it was not in the form, say that too.
4. **The photos** — which photo went into which slot (portrait, education,
   achievement, hobby, gallery), what each one shows, and which images you
   left out because they were blurry, duplicated or badly framed.
5. **The style you chose**, and why.
6. **The build output** — the real command and its real result.
7. **What the friend should look at by eye** — the wording of their bio,
   whether the portrait is cropped well, whether the projects are in the
   right order.

---

## A worked example

This is the **dry run** that was done when this recipe was written: a
fictional friend, "Nusrat Jahan", taken from her filled intake form through
to a built site. It took 14 minutes, most of it spent finding out what the
template does with leftover demo files.

The friend answered:

> 1. নাম: নুসরাত জাহান
> 2. ছোট নাম: নুসরাত
> 3. এক লাইনে: Graphic designer & illustration student
> 4. এখন: Third-year graphic design student at Shanto-Bangla Institute, working on a visual identity for a local tea brand.
> 5. ঠিকানা: ঢাকা, বনানী
> 6. নিজের সম্পর্কে: আমি ভালোবাসি রং আর টাইপোগ্রাফি নিয়ে কাজ করতে। মানুষের গল্প বলার জন্য ডিজাইন শিখেছি। ভবিষ্যতে ব্র্যান্ড ডিজাইনার হতে চাই।
> 12. প্রোগ্রামিং ভাষা: একটুই না
> 13. টুল/ফ্রেমওয়ার্ক: Adobe Illustrator, Adobe Photoshop, Figma
> 14. অন্যান্য স্কিল: Typography, Branding, Color theory
> 15. প্রজেক্ট: ১. "Chai Campaign" — local tea brand poster series, made in Illustrator; live লিংক নেই; featured ২. "Book Cover" — cover for a local poetry collection, Photoshop; live লিংক নেই; featured
> 17. ভাষা: বাংলা (মাতৃভাষা), English (good)
> 18. শখ: Typography — type specimens দিয়ে খালি পাতার ডিজাইন খুঁজে বের করা।
> 19. ইমেইল: nusrat@example.com
> 20. ফোন: না
> 21. লিংক: GitHub — nusratj, Behance — nusratj
> 22. যোগাযোগ পেজে এক লাইন: ইন্টার্নশিপ ও ফ্রিল্যান্স ডিজাইন কাজের জন্য খোলা আছি।
> 23. স্টাইল: যেকোনো একটা
> 24. GitHub username: nusratj

What goes into `profile.yaml`:

```yaml
name: "Nusrat Jahan"
short_name: "Nusrat"
role: "Graphic designer & illustration student"
now: "Third-year graphic design student at Shanto-Bangla Institute, working on a visual identity for a local tea brand."
photo_alt: "Portrait of Nusrat Jahan"
location: "Dhaka, Bangladesh"

facts:
  - "Graphic Design, Shanto-Bangla Institute"
  - "Based in Dhaka"
  - "Open to internships"

bio: |
  I love working with colour and type. My focus is visual identity — the kind
  of work where a poster has to do one thing and do it well.

  I taught myself design by rebuilding brands I liked and studying why they
  worked. Most of my projects are for small local businesses that need good
  design and cannot pay a studio's prices.

  I want to work in brand design, ideally somewhere where the work ships
  often and the people making it care about the details.

education: []                      # not answered — the section hides itself

experience: []                     # not answered — the section hides itself

skills:
  - group: "Design"
    items: ["Adobe Illustrator", "Adobe Photoshop", "Typography", "Branding"]
  - group: "Tools"
    items: ["Figma", "Color theory"]

projects:
  - title: "Chai Campaign"
    summary: "A poster series for a local tea brand, made in Illustrator."
    tech: ["Adobe Illustrator"]
    live: ""
    code: ""
    featured: true
  - title: "Book Cover"
    summary: "The cover for a local poetry collection, designed in Photoshop."
    tech: ["Adobe Photoshop"]
    live: ""
    code: ""
    featured: true

achievements: []                   # not answered — the section hides itself

gallery: []                        # no photos in photos/gallery/

languages: ["Bangla (native)", "English (good)"]

hobbies:
  - title: "Typography"
    text: "Finding the design of an empty page in type specimens — setting the same word in a dozen faces and seeing which one survives."

contact:
  email: "nusrat@example.com"
  phone: ""
  note: "Open to internships and freelance design work."

socials:
  - name: "github"
    url: "https://github.com/nusratj"
  - name: "behance"
    url: "https://www.behance.net/nusratj"
```

Note what is **not** there:

- `education` — Q10 was not answered, so the section is hidden. **Ask her
  for it**; it is the one a visitor will look for first.
- `experience` — Q11 was not answered.
- `achievements` — Q16 was not answered.
- `phone` — Q20 was not answered, so the phone row hides itself.
- `live` and `code` on both projects — she said there are no live links, so
  the buttons are not shown.
- `cv_url` and `personal/cv.pdf` — she has no CV, so the "Download CV"
  button does not appear.

Note the two fields that **are** there because she answered them, even
though the form asked for something else: `languages` (Q17) and `hobbies`
(Q18).

### The files that were deleted

She has 2 projects, 1 hobby and no CV, so the demo's leftovers went:

```
personal/photos/project-3.jpg
personal/photos/project-4.jpg
personal/photos/hobby-2.jpg
personal/photos/edu-1.jpg
personal/photos/edu-2.jpg
personal/photos/award-1.jpg
personal/photos/award-2.jpg
personal/photos/award-3.jpg
personal/photos/gallery/ride.jpg
personal/photos/gallery/market.jpg
personal/photos/gallery/evening.jpg
personal/photos/gallery/road.jpg
personal/cv.pdf
personal/blog/*.jpg
content/blog/learning-laravel-app.md
content/blog/semester-study-system.md
content/blog/trip-to-sajek-valley.md
```

Her own files: `personal/photos/profile.jpg` and
`personal/photos/project-1.jpg` (the Chai Campaign poster).

### The style

She said "any". The demo site is `harbor`, so this one took **`orchid`** —
the magenta, creative style, which suits a graphic design student whose work
is the poster.

```toml
[params]
  style = "orchid"
```

### The build

```
$ hugo --gc --minify --panicOnWarning

 Pages            │  8    Processed images │ 10    Total in 158 ms
```

Zero warnings, zero errors. Eight pages, because the three demo blog posts
were deleted and the blog section is gone with them.

### The report

`docs/reports/FRIEND-nusrat-report.md` in her fork:

> 1. **Filled in:** name, role, now, location, facts, bio, skills (2 groups),
>    2 projects, languages, 1 hobby, email, contact note, GitHub + Behance.
> 2. **Left out:** education (Q10), experience (Q11), achievements (Q16),
>    phone (Q20), CV (Q8), live/code links on both projects, the blog, the
>    gallery.
> 3. **Rewritten:** Q6 (the Bangla answer became three English paragraphs),
>    Q12/Q13/Q14 (merged into two skill groups, "Programming languages" left
>    out because she said she does not know any), Q15 (the two project
>    descriptions became one line each), Q18 (one line became one sentence).
> 4. **Photos:** the portrait, and the Chai Campaign poster as
>    `project-1.jpg`. The Book Cover poster was too low-resolution to use.
>    The demo's education, achievement and gallery photos were deleted.
> 5. **Style:** orchid — she said "any" and it suits the work.
> 6. **Build:** `hugo --gc --minify --panicOnWarning` → 8 pages, no warnings.
> 7. **Look at this yourself:** the wording of the bio, the crop of the
>    portrait, and whether the two projects are in the right order.

---

## The checklist

- [ ] Fork cloned, and it has `themes/`, `hugo.toml` and `.hugo-version`
- [ ] `name`, `role`, `now`, `bio`, `contact.email` are all filled in
- [ ] `personal/photos/profile.jpg` exists
- [ ] `personal/photos/avatar.jpg` added if the friend has a good formal
      headshot (optional — the site falls back to the portrait)
- [ ] Project and hobby photos are named by their position in the YAML
- [ ] Education (`edu-N`) and achievement (`award-N`) photos are named by
      their position in the YAML, and only as many as there are entries
- [ ] Every photo was opened and looked at before it was placed; blurry
      and duplicate images were left out and listed in the report
- [ ] EXIF and GPS data stripped from the photos that were added
- [ ] The demo's leftover files are deleted: extra `project-N.jpg`, extra
      `hobby-N.jpg`, extra `edu-N.jpg`, extra `award-N.jpg`, the demo
      `cv.pdf`, and the demo blog posts
- [ ] The style is set in `hugo.toml`
- [ ] `hugo --gc --minify --panicOnWarning` passes with no warnings
- [ ] `grep -ril "tanvir" public/` returns nothing — no demo name is left
- [ ] The site was looked at in the browser, in light and dark, wide and narrow
- [ ] The lightbox opens a certificate and a gallery photo, and Escape
      closes it
- [ ] Pushed to their fork
- [ ] `docs/reports/FRIEND-<name>-report.md` written, listing what was left out
      and which photos were used and which were dropped
