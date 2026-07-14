# Blog Publishing Pipe

Turns a plain-text draft into a live-ready blog post — page, blog-index card,
and sitemap entry — in one command. Tooling lives here and is excluded from the
Vercel deploy via `.vercelignore`.

## Publish a post
1. Copy `drafts/EXAMPLE.post` to `drafts/<slug>.post` and fill it in.
2. Preview:  `python3 tools/publish_post.py tools/drafts/<slug>.post --dry-run`
3. Write it: `python3 tools/publish_post.py tools/drafts/<slug>.post`
4. Open `blog/<date>-<slug>.html` in a browser to eyeball it.
5. `git add -A && git commit && git push` → Vercel auto-deploys.

## What it does
- Renders `blog/<date>-<slug>.html` from `blog_post_template.html`
  (GA tag, canonical, OpenGraph, BlogPosting schema, Lee Scott as author).
- Inserts a card at the TOP of the grid in `blog.html` (newest first).
- Appends the URL to `sitemap.xml`.
- Idempotent: re-running skips a card/sitemap entry that already exists;
  refuses to overwrite an existing post without `--force`.

## Standards enforced / held (per DOPS doctrine)
- **EEAT (enforced):** the body MUST contain at least one external, non-
  digitalopsystems.com cited link. No citation → the pipe refuses to publish.
  Every article needs ≥1 real quote cited AND linked to its source.
- **Author = Lee Scott** (baked into the template + schema).
- **Human approval before publish:** draft is reviewed before the git push.
  The pipe never deploys on its own — it only writes local files.
- **$0 / no new bills:** static HTML on the existing domain.

## Draft fields
`title, slug, category, date (YYYY-MM-DD), emoji, description, excerpt`
then `---BODY---` then raw HTML (`<p>`, `<h2>`, `<h3>`, `<pre><code>`, `<a>`…).

## Categories in use
Data & Decisions · Websites & SEO · Business Strategy
(keep new posts within a small, consistent set)
