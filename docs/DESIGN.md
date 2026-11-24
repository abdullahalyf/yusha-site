# Design system — binding for all agents

Audience: recruiters, professors, clients and classmates opening a student's link,
mostly on a phone over mobile data. The site's job: in 10 seconds they know **who this
person is, what they're good at, and how to reach them**, and it feels professionally
made.

## 1. Principles
1. **The name is the hero.** Each style gives the person's name a strong, confident type
   treatment next to (or over) their photo, plus one plain "now" sentence
   (`now:` in personal/profile.yaml). No stat counters, no gradient blobs, no typing effects.
2. **One bold thing per style, everything else quiet.** Bold = hero. Sections below are
   calm, well spaced, left-aligned text.
3. **Structure must mean something.** Timelines only for education/experience (real
   sequences). No "01 / 02 / 03" numbering, no ALL-CAPS eyebrow labels, no `A · B · C`
   meta strings, no `→` appended to buttons, no monospace for labels.
4. **Not a card kit.** Don't chop every section into identical rounded shadow cards.
   Use whitespace, a 1px `--line` rule, and type hierarchy. Cards are allowed only for
   project items, and only with the radius/shadow defined below.
5. **Fast and honest.** No skill-percentage bars (they mean nothing). Skills are grouped
   lists. Real content or nothing — empty sections are hidden.

## 2. Style switch
`hugo.toml` → `[params] style = "harbor"` (one of `harbor | grove | orchid | graphite | saffron`).
Implementation: `<html data-style="harbor" data-theme="light|dark">`; each style is a CSS
file `themes/folio/assets/css/styles/<style>.css` that only sets custom properties
(+ the hero layout class). Hugo bundles base CSS + the chosen style only.
Optional `params.layout` may override the style's default hero layout.

Dark mode: toggle button in header, stored in `localStorage`; default follows
`prefers-color-scheme`; inline 5-line script in `<head>` sets `data-theme` before paint
(no flash). Every style defines both light and dark tokens.

## 3. Tokens per style
Token names (all styles): `--bg --surface --ink --muted --accent --accent-ink --line`
(`--accent-ink` = text colour on top of accent). Agents must verify contrast
(`--ink`, `--muted`, `--accent` against `--bg` and `--surface` ≥ 4.5:1) and darken/lighten
**within the same hue** if a value fails. Report final values.

| style | mood | light bg / surface / ink / muted / accent / line | dark bg / surface / ink / muted / accent / line | display font | body font | hero layout |
|---|---|---|---|---|---|---|
| harbor | calm, engineering | #F6F8FB / #FFFFFF / #142033 / #52607A / #0E7490 / #DCE3EC | #0F1724 / #172234 / #E6ECF5 / #9AA8BD / #5CC8DD / #26344A | Manrope 800 | Manrope 400/600 | split |
| grove | warm academic | #F2F5F1 / #FFFFFF / #1D2B22 / #56645A / #2F6B4F / #D8E0D9 | #121A15 / #1A241D / #E4EBE5 / #9DAAA0 / #7FC4A0 / #2A372E | Fraunces 600 (opsz) | Work Sans 400/600 | centered |
| orchid | creative, confident | #FAF7FB / #FFFFFF / #2A1733 / #6A5872 / #B4236B / #E9DFEC | #170F1B / #221827 / #F1E8F4 / #B7A6BE / #F27AB0 / #352A3A | Space Grotesk 700 | Figtree 400/600 | typographic |
| graphite | résumé, precise | #FFFFFF / #F5F7F9 / #1F2328 / #59636E / #1F6FEB / #E1E4E8 | #15181D / #1D2127 / #E6E9ED / #9BA3AD / #6CA4F8 / #2D333B | IBM Plex Serif 600 | IBM Plex Sans 400/600 | sidebar |
| saffron | bright, friendly | #F7F7FB / #FFFFFF / #22223B / #5B5B76 / #4338CA / #E3E3EE (+ decorative `--spark: #F59E0B`, never for text on light) | #16152A / #1F1E38 / #ECECF6 / #A5A5C2 / #A5B4FC / #2F2E4D (`--spark: #FBBF24`) | Sora 700 | Source Sans 3 400/600 | band |

Fonts: self-host WOFF2 (latin subset only) in `themes/folio/static/fonts/`, max 2 files
per family (variable font preferred), `font-display: swap`, preload the display font.
If the agent environment can't download fonts, use `https://fonts.bunny.net` `<link>`
and say so in the report.

## 4. Hero layouts (ASCII)
```
split (harbor)                 centered (grove)
+---------------+-------+      +-------------------------+
| Name Name     | photo |      |        ( photo )        |
| Name          |  4:5  |      |      Name Surname       |
| role line     |       |      |   role line / now line  |
| now sentence  |       |      |  [Download CV] [Contact]|
| [CV] [Contact]|       |      +-------------------------+
+---------------+-------+
typographic (orchid)           sidebar (graphite)            band (saffron)
+-------------------------+    +--------+----------------+   +=========================+
| NAME SET VERY           |    | photo  | About          |   |##### accent band #######|
| LARGE ACROSS (clamp)    |    | Name   | Experience...  |   |##  (photo overlaps) ####|
| (o) role / now line    |    | role   | Projects...    |   +====( o )================+
| [CV] [Contact]          |    | links  |                |   |  Name / role / now      |
+-------------------------+    | sticky |                |   |  [CV] [Contact]         |
                               +--------+----------------+   +-------------------------+
```
Photo shape per style: harbor = 4:5 rect radius 20px; grove = circle with 6px `--accent`
ring offset; orchid = small 96px circle inline; graphite = square radius 12px;
saffron = circle with 6px `--surface` border overlapping the band.
Mobile (<720px): every layout stacks photo → name → text; sidebar becomes a top block.

## 5. Type & spacing
- Fluid scale ratio 1.25: body 1.0625rem (17px) → 1.125rem (18px) at ≥1024px.
  Display name: `clamp(2.6rem, 8vw, 5.5rem)` (orchid up to 8rem). h2 1.75rem, h3 1.25rem.
- Line-height: sans body 1.6, serif body 1.7, headings 1.1–1.2. Measure: max 68ch.
- Spacing scale (rem): 0.25 0.5 0.75 1 1.5 2 3 4 6. Section vertical padding 4rem
  (mobile 3rem). Container max 1120px, side padding 1.25rem.
- Radius: buttons 8px, project cards 14px, inputs/pills 999px. Shadow only on project
  cards: `0 1px 2px rgb(0 0 0 / .06), 0 8px 24px -12px rgb(0 0 0 / .18)`; none in dark.

## 6. Components
- **Header:** name (small, links home) left; nav right; theme toggle (sun/moon SVG,
  `aria-pressed`, label "Switch to dark theme"). Mobile: menu button → full-width panel.
- **Buttons:** primary = accent bg + accent-ink text; secondary = 1px `--line` border.
- **Facts row** (home, under hero): 3–4 short facts from `facts:` as a plain inline list
  separated by spacing (not dots).
- **Timeline:** vertical 2px `--line`, 10px accent dot per item; date in `--muted`
  above title. Used for education and experience.
- **Project item:** image 16:10 (optional) + title + one-line summary + tech list +
  links (Live, Code). Featured projects (max 3, `featured: true`) on home as alternating
  image-left/right rows; full list on Projects page as 2-column grid (1 on mobile).
- **Skills:** group heading + comma-free inline list of plain pills (1px line border).
- **Achievements:** list rows: year (muted) + title + issuer.
- **Hobbies:** short paragraph each, optional square photo.
- **Contact block:** email (mailto), phone (tel), location, socials as icon+text links
  (inline SVG icons, no icon font), CV button.
- **Footer:** © year name, "Built with Hugo", back-to-top link.

## 7. Motion
Only one moment: hero name + photo fade/rise 12px, 450ms ease-out, photo 80ms later.
Theme switch: 150ms colour transition. Nothing on scroll. All disabled under
`prefers-reduced-motion`.

## 8. Pages
- **Home** `/`: hero, facts row, short about (first paragraph of bio + "More about me"),
  featured projects, skills summary (top groups), latest 2 blog posts (hidden if none),
  contact call-out.
- **About** `/about/`: full bio, education timeline, experience timeline, achievements,
  languages, hobbies, CV download.
- **Projects** `/projects/`: all projects + full skills.
- **Blog** `/blog/`: list (title, date, summary, reading time) + post page with good
  prose styles (code blocks, quotes, images). 1 example post in `content/blog/`.
- **Contact** `/contact/`: contact block + short availability line (`contact.note`).
- 404 page in the same style. SEO: title/description from profile, Open Graph image =
  profile photo, JSON-LD `Person`, sitemap, robots.txt, favicon generated from initials (SVG).
