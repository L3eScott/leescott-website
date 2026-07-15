#!/usr/bin/env python3
"""
Blog Publishing Pipe - Digital Ops Systems
Turns a draft spec into a live-ready blog post:
  1. renders blog/<date>-<slug>.html from tools/blog_post_template.html
  2. inserts a card at the top of the blog grid in blog.html
  3. adds the URL to sitemap.xml
  4. enforces the EEAT rule: >=1 external cited+linked source in the body

Usage:
  python3 tools/publish_post.py tools/drafts/<slug>.post [--dry-run] [--force]

Draft spec format (see tools/drafts/EXAMPLE.post):
  title: ...
  slug: ...
  category: ...
  date: YYYY-MM-DD
  emoji: 📊
  description: ...            (meta description, 1 line)
  excerpt: ...                (blog-card teaser, 1 line)
  ---BODY---
  <p>...raw HTML body...</p>
"""
import sys, os, re, html
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO, "tools", "blog_post_template.html")
BLOG_INDEX = os.path.join(REPO, "blog.html")
SITEMAP = os.path.join(REPO, "sitemap.xml")
OWN_HOST = "digitalopsystems.com"

def die(msg):
    print("ERROR: " + msg); sys.exit(1)

def parse_spec(path):
    if not os.path.exists(path): die("draft not found: " + path)
    raw = open(path, encoding="utf-8").read()
    if "---BODY---" not in raw: die("draft missing '---BODY---' marker")
    head, body = raw.split("---BODY---", 1)
    meta = {}
    for line in head.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if ":" not in line: continue
        k, v = line.split(":", 1)
        meta[k.strip().lower()] = v.strip()
    return meta, body.strip()

def require(meta, *keys):
    for k in keys:
        if not meta.get(k): die("draft missing required field: " + k)

def check_eeat(body, force):
    # EEAT standing rule: every article needs >=1 real quote CITED + LINKED to source.
    links = re.findall(r'href="(https?://[^"]+)"', body)
    external = [u for u in links if OWN_HOST not in u]
    if not external:
        msg = ("EEAT VIOLATION: body has no external cited+linked source. "
               "Every article needs >=1 real quote linked to its source.")
        if force:
            print("WARNING (overridden by --force): " + msg)
        else:
            die(msg + " Add a linked citation, or re-run with --force.")
    else:
        print("EEAT check OK: %d external citation(s) found." % len(external))

def esc(s):
    return html.escape(s, quote=True)

def build_card(meta, filename):
    return (
'          <div class="blog-card">\n'
'            <div class="blog-img"><img src="assets/images/%s" alt="" loading="lazy"></div>\n'
'            <div class="blog-content">\n'
'              <div class="blog-meta">\n'
'                <span class="category">%s</span>\n'
'                <span class="dot">&middot;</span>\n'
'                <span>%s</span>\n'
'              </div>\n'
'              <h3><a href="blog/%s">%s</a></h3>\n'
'              <p>%s</p>\n'
'              <a href="blog/%s" class="read-more">Read Article &rarr;</a>\n'
'            </div>\n'
'          </div>\n'
    ) % (meta.get("image", "thumb-default.jpg"), esc(meta["category"]), meta["date_human"],
         filename, esc(meta["title"]), esc(meta["excerpt"]), filename)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = set(a for a in sys.argv[1:] if a.startswith("--"))
    if not args: die("usage: publish_post.py <draft.post> [--dry-run] [--force]")
    dry = "--dry-run" in flags
    force = "--force" in flags

    meta, body = parse_spec(args[0])
    require(meta, "title", "slug", "category", "date", "emoji", "description", "excerpt")
    try:
        d = datetime.strptime(meta["date"], "%Y-%m-%d")
    except ValueError:
        die("date must be YYYY-MM-DD")
    meta["date_human"] = d.strftime("%B %-d, %Y")
    meta["date_iso"] = meta["date"]
    slug = re.sub(r'[^a-z0-9-]', '', meta["slug"].lower())
    if not slug: die("slug empty after sanitising")
    filename = "%s-%s.html" % (meta["date"], slug)
    post_path = os.path.join(REPO, "blog", filename)

    check_eeat(body, force)

    if os.path.exists(post_path) and not force:
        die("post already exists: blog/%s (use --force to overwrite)" % filename)

    # 1. render post
    tpl = open(TEMPLATE, encoding="utf-8").read()
    page = (tpl
        .replace("{{TITLE}}", esc(meta["title"]))
        .replace("{{DESCRIPTION}}", esc(meta["description"]))
        .replace("{{FILENAME}}", filename)
        .replace("{{CATEGORY}}", esc(meta["category"]))
        .replace("{{DATE_HUMAN}}", meta["date_human"])
        .replace("{{DATE_ISO}}", meta["date_iso"])
        .replace("{{BODY}}", body))
    if "{{" in page:
        die("unfilled placeholder left in rendered page: " + re.search(r'\{\{[^}]+\}\}', page).group(0))

    # 2. blog.html card (insert at top of grid)
    idx = open(BLOG_INDEX, encoding="utf-8").read()
    if ('blog/%s' % filename) in idx:
        print("SKIP card: blog.html already links blog/%s" % filename)
        new_idx = idx
    else:
        anchor = '<div class="blog-grid">\n'
        if anchor not in idx: die("could not find '<div class=\"blog-grid\">' anchor in blog.html")
        new_idx = idx.replace(anchor, anchor + build_card(meta, filename), 1)

    # 3. sitemap
    sm = open(SITEMAP, encoding="utf-8").read()
    loc = "https://digitalopsystems.com/blog/%s" % filename
    if loc in sm:
        print("SKIP sitemap: %s already present" % loc)
        new_sm = sm
    else:
        entry = '  <url><loc>%s</loc><priority>0.5</priority></url>\n' % loc
        new_sm = sm.replace("</urlset>", entry + "</urlset>", 1)

    if dry:
        print("\n--- DRY RUN (no files written) ---")
        print("would write : blog/%s (%d bytes)" % (filename, len(page)))
        print("blog.html   : %s" % ("card added" if new_idx != idx else "unchanged"))
        print("sitemap.xml : %s" % ("url added" if new_sm != sm else "unchanged"))
        return

    open(post_path, "w", encoding="utf-8").write(page)
    open(BLOG_INDEX, "w", encoding="utf-8").write(new_idx)
    open(SITEMAP, "w", encoding="utf-8").write(new_sm)
    print("\nPUBLISHED (local, not yet pushed):")
    print("  page    : blog/%s" % filename)
    print("  index   : blog.html card added")
    print("  sitemap : %s" % loc)
    print("\nNext: review in a browser, then git add/commit/push to deploy.")

if __name__ == "__main__":
    main()
