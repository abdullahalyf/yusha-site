# Personal website — a Hugo template with five styles

> New friend? Start at [docs/LAUNCH.md](docs/LAUNCH.md) and pick a look from [docs/VARIANTS.md](docs/VARIANTS.md).

A fast, accessible personal website you can fork and fill in about ten minutes.
One YAML file holds everything about you; five styles decide how it looks.

- No build step beyond Hugo. No JavaScript framework. The whole page works
  with JavaScript switched off.
- Every page is already written: home, about, projects, blog, contact.
- Dark mode in all five styles, with a toggle that remembers your choice.
- Your photos are resized and converted to WebP automatically.

## The five styles

One line in `hugo.toml` picks the style.

### harbor — calm, engineering

![harbor](docs/reports/screens/task02-harbor-desktop-light.png)

Cool grey-blue, a Manrope display face and the portrait on the right. The
calmest of the five. **Suits** engineers and anyone whose work should speak
before their personality does.

### grove — warm academic

![grove](docs/reports/screens/task02-grove-desktop-light.png)

Soft green on paper-warm white, set in Fraunces over Work Sans, with the
portrait in a green ring. **Suits** researchers, students and academics.

### orchid — creative, confident

![orchid](docs/reports/screens/task02-orchid-desktop-light.png)

Magenta on pale lilac, the name set enormous in Space Grotesk. The loudest
of the five. **Suits** designers, writers and portfolio sites that want to
be remembered.

### graphite — résumé, precise

![graphite](docs/reports/screens/task02-graphite-desktop-light.png)

Pure white, a single blue accent, IBM Plex Serif over IBM Plex Sans, and a
sticky profile column beside the work. **Suits** people applying for jobs.

### saffron — bright, friendly

![saffron](docs/reports/screens/task02-saffron-desktop-light.png)

Indigo and warm amber, set in Sora over Source Sans 3, with a colour band
across the top. **Suits** freelancers, community builders and teachers.

Full details, including how to change the hero layout: **[docs/styles.md](docs/styles.md)**.

## Make your site in 10 minutes

### 1. Fork this repository

Click **Fork** at the top right of this page on GitHub. Your copy is now
yours to edit.

### 2. Fill in `personal/profile.yaml`

Everything about you lives in one file:
[`personal/profile.yaml`](personal/profile.yaml). It has comments on every
field explaining what goes there.

If you would rather not edit YAML yourself, fill in
[`docs/INTAKE-FORM.md`](docs/INTAKE-FORM.md) and ask Alif's agent to do it
for you.

### 3. Replace the files in `personal/photos/` and `personal/cv.pdf`

Keep the file names exactly the same — the site looks the files up by name.

| What you put in | What it is used for |
|---|---|
| `personal/photos/profile.jpg` | your portrait (required, at least 800×800) |
| `personal/photos/project-1.jpg` | the screenshot for your **first** project in `profile.yaml` |
| `personal/photos/project-2.jpg` | the screenshot for your **second** project, and so on |
| `personal/photos/hobby-1.jpg` | the photo for your **first** hobby |
| `personal/cv.pdf` | your CV — the "Download CV" button disappears without it |

`.jpg`, `.jpeg`, `.png` and `.webp` all work. Anything you leave out is
simply not shown; nothing breaks.

**Delete the demo files you do not need.** The template ships with a demo
person in it, and the photo names are positional — `project-1.jpg` is always
the first project. So if you have two projects, delete `project-3.jpg` and
`project-4.jpg`; if you have no hobbies, delete `hobby-1.jpg` and
`hobby-2.jpg`; if you have no CV, delete `cv.pdf`, or the button will open
somebody else's CV.

The demo's blog posts live in `content/blog/`. Delete them there if you are
not writing your own — the Blog link disappears from the navigation by
itself. To check that nothing of the demo is left after a build:

```bash
grep -ril "tanvir" public/
```

### 4. Pick a style

In `hugo.toml`:

```toml
[params]
  style = "harbor"   # harbor | grove | orchid | graphite | saffron
```

### 5. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. **Add New… → Project**, then import your fork.
3. Press **Deploy**.

That is the whole setup — no build settings, no environment variables, no
configuration. Vercel detects Hugo, reads the version from `.hugo-version`
and builds it.

### 6. Run it locally (optional)

```bash
hugo server
```

The site is then at <http://localhost:1313>.

You need **Hugo extended** 0.170.1 or newer. Check with `hugo version` —
the word "extended" has to be in the output, because the theme uses Hugo's
image processing to make the WebP versions of your photos.

To try a style without editing the file:

```bash
HUGO_PARAMS_STYLE=saffron hugo server
```

## Troubleshooting

### The build fails with a message about `personal/profile.yaml`

The site checks the required fields before it renders anything, so a missing
field stops the build with a message naming exactly what is wrong. Each of
these means one thing:

| Message | What it means |
|---|---|
| `"name" is required but empty (or missing).` | `name:` is missing or `""` at the top level of `personal/profile.yaml`. |
| `"role" is required but empty (or missing).` | `role:` is missing or `""`. One line: who you are. |
| `"now" is required but empty (or missing).` | `now:` is missing or `""`. One sentence: what you are doing now. |
| `"bio" is required but empty (or missing).` | `bio:` is missing or `""`. A few lines about you. |
| `the "contact" section is required but missing.` | There is no `contact:` block at all. |
| `"contact.email" is required but empty.` | `contact:` exists but has no `email:`. |

Anything that is *not* in this list is optional. Leave it empty and the
section hides itself: no projects, no achievements, no hobbies, no phone
number, no CV button, no social links.

### The demo person's name is still on my site

The template ships with a demo person in it. Their name must not survive
anywhere — not in a page title, not in a meta description, not in the RSS
feed. After a build:

```bash
grep -ril "tanvir" public/
```

Anything listed is a leftover. The usual causes are a `description:` in
`content/*.md` that still names them, a `params.description` in
`hugo.toml`, and the demo blog posts in `content/blog/`.

You should not need to touch any of those: the page descriptions take
`{name}` and `{role}`, and the site fills them in from
`personal/profile.yaml`.

### The build fails with "personal/photos/profile.jpg is missing"

Your portrait is not there, or it has the wrong name. It has to be called
`profile.jpg` (or `profile.jpeg`, `profile.png`, `profile.webp`) and live in
`personal/photos/`.

### Vercel: "Hugo version not found" or the build uses the wrong version

`vercel.json` sets `HUGO_VERSION` to the version in `.hugo-version`, so the
two can never drift apart. If Vercel still builds with the wrong version,
check that `.hugo-version` still exists in your fork and that `vercel.json`
was not edited.

### Vercel: the site is live but every page looks unstyled

The CSS is bundled at build time. If the styles are missing, the build did
not finish — check the Vercel build log. A common cause is a missing photo:
the site refuses to render rather than ship a broken page.

### The build is slow the first time

Hugo resizes and converts every photo to WebP on the first build and caches
the result. Later builds are fast. The build on Vercel has the same effect:
the first deployment is slower, the ones after it are quick.

### A photo looks stretched or blurry

The site resizes photos to the size they are displayed at, in two widths,
and never upscales. A photo smaller than the size it is shown at will look
soft — use a bigger original. Very wide photos are cropped to the shape the
style wants; that is intentional.

### The dark mode does not stick

The choice is remembered in the browser's local storage. In a private window
it is forgotten when the window closes, which is the browser's behaviour,
not a bug.

### Something is wrong and the error message is not helpful

Run the build locally, where you get the full output:

```bash
hugo --gc --minify --panicOnWarning
```

`--panicOnWarning` turns warnings into errors, which is what CI does.

## For agents and contributors

- [`AGENTS.md`](AGENTS.md) — the rules for working in this repository.
- [`docs/DESIGN.md`](docs/DESIGN.md) — the design system: tokens, type scale,
  the five styles, the five hero layouts.
- [`docs/FRIEND-SITE.md`](docs/FRIEND-SITE.md) — the recipe for building
  somebody else's site from their filled intake form.
- [`docs/tasks/`](docs/tasks/) and [`docs/reports/`](docs/reports/) — the
  work that has been done and the evidence for it.

## Credits

Fonts (IBM Plex, Fraunces, Work Sans, Space Grotesk, Figtree, Sora, Source
Sans 3, Manrope) are self-hosted in `themes/folio/static/fonts/` under the
SIL Open Font License. See [`personal/CREDITS.md`](personal/CREDITS.md).
