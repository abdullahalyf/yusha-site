# AGENTS.md — rules for every coding agent (Codex, Puku, others)

## What this repo is
A reusable **Hugo personal-website template**. One person = one fork. All personal
content lives in the **`personal/`** folder: `profile.yaml` + photos and CV with **fixed file
names** (see `personal/README.md`). Hugo mounts it (`[[module.mounts]]`). The theme is
our own, lightweight, inside `themes/folio/` — no third-party theme, no CSS framework,
no npm/Node dependency.

## Read before you start
1. Your task file: `docs/tasks/TASK-NN-*.md` (the one you were told to run).
2. `docs/DESIGN.md` — the design system. It is binding. Do not invent new colors/fonts.
3. `personal/profile.yaml` — the content schema. Do not rename or remove keys; you may only
   add optional keys if the task says so.

## Hard rules
- Hugo **extended**, version pinned in ONE place (`.hugo-version`) and reused by CI and
  `vercel.json`. Install it yourself if missing (Windows/Puku: `winget install Hugo.Hugo.Extended`;
  Linux/Codex: `.deb` from github.com/gohugoio/hugo releases).
- Zero runtime JS frameworks. Allowed JS: one small vanilla file (`theme.js`) for the dark
  mode toggle + mobile menu, < 3 KB minified. Site must work with JS disabled
  (dark mode then follows the OS).
- No copy, names or links hard-coded in templates. Everything comes from
  `personal/profile.yaml` or `hugo.toml` params. Templates must not break when an optional
  section is empty — they simply hide it.
- Images go through Hugo image processing (`resources.Get` → `.Resize`/`.Fill` → WebP,
  with `width`/`height` attributes and `loading="lazy"` except the hero photo).
- Every animation/transition respects `prefers-reduced-motion: reduce`.
- Accessibility: semantic landmarks, one `h1` per page, visible `:focus-visible`,
  skip-link, alt text from data, colour contrast ≥ 4.5:1 in both themes.
- Targets: Lighthouse mobile Performance ≥ 95, Accessibility ≥ 95, Best Practices ≥ 95,
  SEO ≥ 95.
- `hugo --gc --minify` must finish with **zero warnings and zero errors**.

## Git workflow
- Work on a branch `task/NN-short-name`. **Never push to `main`.** Open a Pull Request.
- Small, meaningful commits.
- Before opening the PR write your report to **`docs/reports/TASK-NN-report.md`**
  (in the same branch) with:
  - what you built (files list), what you skipped and why
  - commands you ran and their real output (build, checks)
  - Lighthouse scores if you could run them (otherwise say "not run")
  - anything the reviewer must check by eye
  - open questions
- Don't claim something works unless you ran it.

## Writing style for any copy you write
Plain, specific English. No buzzwords ("passionate", "cutting-edge", "seamless",
"unleash"), no emoji in UI, sentence case everywhere, buttons say exactly what they do
("Download CV", "Send email").
