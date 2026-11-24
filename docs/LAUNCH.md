# LAUNCH.md — from photos to a live site (for any agent: Puku, Codex, others)

Read `AGENTS.md` first. Rule number one: **invent nothing.** Empty = hidden.

## 0. What Alif gives you
A folder `_friends-input/<name>/` with `info.md` (answers) and photos in the
numbered subfolders, plus the friend's GitHub username and repo name.

## 1. Work copy
Clone **Alif's private repo** `abdullahalyf/hugo-personal-website`, branch
`template/v1`. Make a branch `friend/<name>`. Never push to `main`.

## 2. Fill `personal/` (fixed names, see `personal/README.md`)
- `1-profile-photo` → `personal/photos/profile.jpg` (big portrait) and `avatar.jpg` (small crop)
- `2-project-photos` → `project-N.jpg` (same order as `projects` in profile.yaml)
- `3-hobby-photos` → `hobby-N.jpg`, `5-school-college-photos` → `edu-N.jpg`
  (N = position in `education`, newest first), `6-achievements-certificates` → `award-N.jpg`
- `7-other-photos` → `personal/photos/gallery/` (names there match `gallery:` in profile.yaml)
- `4-cv` → `personal/cv.pdf` (no file = no CV button)
- `info.md` → `personal/profile.yaml`. Delete every demo fact. Delete demo blog posts
  unless the friend wants blog posts; write only what is true.
- Convert photos to JPG, max 1400 px, quality about 84.

## 3. Look
Choose a free recipe in `docs/VARIANTS.md`. It must differ from every site already made.

## 4. Build and check
```bash
hugo --gc --minify -b https://<user>.github.io/<repo>/ -d docs
```
- Zero warnings, zero errors.
- Every `href`/`src` starts with `/<repo>/` or `https:` / `#` / `mailto:` / `tel:`.
- Look at Home, About, Projects, Blog, Contact at 1440 px and 390 px.

## 5. Deliver — public repo holds ONLY `docs/`
The friend's public repo must **not** contain the source (themes, content, personal).
GitHub's web uploader takes at most 100 files per upload: if `docs/` has more,
split it into `part-1/docs/...`, `part-2/docs/...` (80 files each).
Put the result in `_friends-input/<name>/UPLOAD/` and tell Alif only:

1. Repo → Add file → Upload files → drag the `docs` folder (each part in turn) → Commit.
2. Settings → Pages → Deploy from a branch → `main` / `/docs` → Save.
3. Open `https://<user>.github.io/<repo>/` and press Ctrl+F5.

Later changes: rebuild, then send **only the changed files** inside `docs/`.

## 6. Report
`docs/reports/FRIEND-<name>-report.md`: what is filled, what is missing
(email, CV, photos), which recipe was used.
