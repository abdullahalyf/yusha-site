---
# This file documents the folder for whoever edits the blog next. It is not a
# post, so Hugo must not turn it into a page or list it anywhere.
build:
  render: never
  list: never
---

# Blog posts

This folder holds the blog. Every `.md` file in it becomes a post at
`/blog/<file-name>/`. Files whose name starts with `_` are not published, so
this README stays out of the site.

## Add a post

1. Create a new file, `content/blog/my-post.md`. The file name becomes the
   URL, so keep it short and lowercase with hyphens.
2. Add front matter. Only `title` and `date` are required.

   ```yaml
   ---
   title: "The title of the post"
   date: 2026-09-14
   summary: "One or two sentences. Shown on the blog list and used for the meta description."
   description: "Optional. Overrides the summary for the meta description."
   tags: ["laravel", "php"]
   cover: "my-post"
   ---
   ```

   `tags` are optional. `cover` is the base name of a file in
   `personal/blog/` — for the example above, put an image at
   `personal/blog/my-post.jpg`. If the file does not exist, the post simply has
   no cover image; nothing breaks.

3. Write the post in Markdown. Headings, lists, tables, block quotes and code
   fences all work.

   ```markdown
   ## A heading

   Some text.

   - a list item
   - another one

   ```php
   echo 'code';
   ```
   ```

4. Add an image inside the post by referring to a file in
   `personal/blog/`:

   ```markdown
   ![Alt text describing the image.](blog/my-post-body.jpg)
   ```

   Always write alt text. It is what a screen reader reads out and what shows
   if the image fails to load.

5. Save the file. The post appears on `/blog/` immediately, newest first, and
   in the two most recent posts on the home page.

## Delete a post

Delete the `.md` file. Nothing else needs to change — there is no index to
update and no menu entry to remove.

If the post had a cover image, the image in `personal/blog/` becomes unused.
Deleting it is optional, but keeping the folder tidy helps.

## Writing style

Short sentences. Plain English. No filler opening paragraph. Say what you did,
what broke and what you would change. Bullets and short sections beat long
paragraphs.

## Assets

| Place | Purpose |
| --- | --- |
| `personal/blog/<name>.jpg` | The wide cover image, used at the top of a post |
| `personal/blog/<name>-body.jpg` | An illustration used inside the post text |

Keep images under 200 KB. The cover is displayed at 1200×630; body images work
at 1200×750.
