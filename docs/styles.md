# The five styles

The whole site is restyled by one line in `hugo.toml`:

```toml
[params]
  style = "harbor"   # harbor | grove | orchid | graphite | saffron
```

Every style uses the same pages, the same components and the same content —
only the colours, the type and the shape of the hero change. A dark mode is
built into all of them; the theme toggle in the header switches it.

The screenshots below are the home page, desktop, light.

---

## harbor — calm, engineering

![harbor](reports/screens/task02-harbor-desktop-light.png)

A cool grey-blue on white with a Manrope display face and a portrait on the
right. The calmest of the five and the one that stays out of the way.

**Suits:** engineers, developers and anyone whose work should speak before
their personality does.

---

## grove — warm academic

![grove](reports/screens/task02-grove-desktop-light.png)

A soft green on a paper-warm white, set in Fraunces (a serif with real
personality) over Work Sans. The portrait is a circle in a green ring, and
the hero is centred, so it reads like a title page.

**Suits:** researchers, students and academics — anyone who writes and wants
the site to look like a publication.

---

## orchid — creative, confident

![orchid](reports/screens/task02-orchid-desktop-light.png)

Magenta on pale lilac, with the name set enormous in Space Grotesk — the
name *is* the hero, and the portrait is a small 96px circle beside it. The
loudest of the five without becoming loud.

**Suits:** designers, writers, illustrators and portfolio sites that want to
be remembered.

---

## graphite — résumé, precise

![graphite](reports/screens/task02-graphite-desktop-light.png)

Pure white, a single blue accent, and IBM Plex Serif over IBM Plex Sans. The
portrait is a square in the corner and the whole page is a résumé: a sticky
profile column on the left, the work on the right.

**Suits:** people applying for jobs, and anyone whose page has to be read
once, carefully, by somebody busy.

---

## saffron — bright, friendly

![saffron](reports/screens/task02-saffron-desktop-light.png)

Indigo and a warm amber accent, set in Sora over Source Sans 3. A full-bleed
colour band runs across the top with the portrait overlapping it, which makes
the page feel less like a document and more like a poster.

**Suits:** freelancers, community builders, teachers and anybody who would
rather the site be approachable than impressive.

---

## Changing the style

`hugo.toml`:

```toml
[params]
  style = "saffron"
```

Or, for a quick look without editing the file:

```bash
HUGO_PARAMS_STYLE=saffron hugo server
```

## Changing the hero layout

Each style has a default hero layout. It can be replaced with any of the
five, independently of the style:

| layout   | shape of the hero                          |
|----------|--------------------------------------------|
| split    | text left, portrait right                  |
| centered | portrait above, everything centred         |
| typographic | the name is the hero, portrait inline   |
| sidebar  | a sticky profile column beside the content |
| band     | a full-bleed colour band, portrait overlapping it |

```toml
[params]
  style = "harbor"
  layout = "band"   # split | centered | typographic | sidebar | band
```

The layout is a property of the page, not of the style, so any style can be
paired with any layout. The only thing that changes is the hero — the rest
of the page keeps the style's colours and type.
