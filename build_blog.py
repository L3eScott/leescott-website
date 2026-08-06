#!/usr/bin/env python3
"""Build static blog pages from markdown sources.

Sources: content/posts/*.md  (with --- YAML front-matter ---)
Outputs: blog/<slug>.html     (one HTML page per post)
         blog.html            (regenerated index with cards for all posts)

Uses Python stdlib only. No frameworks, no build tools, no node_modules
(per CLAUDE.md).

Usage:
    python3 build_blog.py

Front-matter format:
    ---
    title: How to do X
    date: 2026-06-06
    category: Lead Generation
    summary: One-line summary used on the index card.
    emoji: 💡            # optional, shown on the index card
    draft: false         # optional, if true the post is skipped
    ---

Markdown subset supported: # ## ### headings, paragraphs, **bold**,
*italic*, `inline code`, [links](url), - bullet lists, 1. numbered lists,
> blockquotes, ``` fenced code blocks ```. No tables, no images
(images come later via the image branch).
"""
from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent
POSTS_DIR = SITE_ROOT / "content" / "posts"
OUT_DIR = SITE_ROOT / "blog"
INDEX_PATH = SITE_ROOT / "blog.html"
CANONICAL_BASE = "https://digitalopsystems.com"


# ─── Markdown → HTML (minimal, stdlib-only) ─────────────────────────────────

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITALIC = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\*)")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def render_inline(text: str) -> str:
    """Apply inline markdown after HTML-escaping. Order matters."""
    text = html.escape(text)
    # Inline code first (so * inside `code` isn't formatted)
    placeholders: list[str] = []

    def stash_code(m: re.Match) -> str:
        placeholders.append(f"<code>{m.group(1)}</code>")
        return f"\x00CODE{len(placeholders) - 1}\x00"

    text = INLINE_CODE.sub(stash_code, text)
    text = BOLD.sub(r"<strong>\1</strong>", text)
    text = ITALIC.sub(r"<em>\1</em>", text)

    def link_repl(m: re.Match) -> str:
        href = m.group(2)
        return f'<a href="{href}">{m.group(1)}</a>'

    text = LINK.sub(link_repl, text)
    # Restore code placeholders
    for i, code in enumerate(placeholders):
        text = text.replace(f"\x00CODE{i}\x00", code)
    return text


def render_markdown(md: str) -> str:
    """Block-level render. Returns HTML body (no <html><body> wrapper)."""
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith("```"):
            i += 1
            code_lines: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(html.escape(lines[i]))
                i += 1
            i += 1  # skip closing fence
            out.append("<pre><code>" + "\n".join(code_lines) + "</code></pre>")
            continue

        # Blank
        if not stripped:
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{render_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            inner = " ".join(quote_lines)
            out.append(f"<blockquote><p>{render_inline(inner)}</p></blockquote>")
            continue

        # Bullet list
        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append(f"<li>{render_inline(item)}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        # Numbered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                item = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append(f"<li>{render_inline(item)}</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        # Paragraph (consume until blank line)
        para_lines: list[str] = []
        while i < n and lines[i].strip() and not re.match(
            r"^(#{1,3}\s|[-*]\s|\d+\.\s|>|```)", lines[i].strip()
        ):
            para_lines.append(lines[i].strip())
            i += 1
        out.append(f"<p>{render_inline(' '.join(para_lines))}</p>")
    return "\n".join(out)


# ─── Post model + parser ────────────────────────────────────────────────────


@dataclass
class Post:
    slug: str
    title: str
    date: str  # YYYY-MM-DD
    category: str
    summary: str
    emoji: str = "📝"
    draft: bool = False
    body_html: str = ""
    source_path: Path = field(default_factory=Path)


def parse_post(path: Path) -> Post:
    text = path.read_text(encoding="utf-8")
    fm: dict[str, str] = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm_block = text[3:end].strip()
            body = text[end + 4 :].lstrip("\n")
            for line in fm_block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"').strip("'")
    return Post(
        slug=path.stem,
        title=fm.get("title", path.stem.replace("-", " ").title()),
        date=fm.get("date", "1970-01-01"),
        category=fm.get("category", "Uncategorized"),
        summary=fm.get("summary", ""),
        emoji=fm.get("emoji", "📝"),
        draft=fm.get("draft", "false").lower() == "true",
        body_html=render_markdown(body),
        source_path=path,
    )


# ─── Templates ──────────────────────────────────────────────────────────────

# Header is identical across pages. Build it once; parameterize relative
# asset prefix (root pages use "", posts use "../").

HEADER_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-LY2DK30PC2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-LY2DK30PC2');
</script>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}"/>
  <link rel="canonical" href="{canonical}"/>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{asset_prefix}assets/css/styles.css" />
  <link rel="icon" href="{asset_prefix}favicon.svg" type="image/svg+xml"/>
</head>
<body>

  <a href="{asset_prefix}index.html#mission" class="mission-badge" title="Our mission: help 100 business owners build something real">
    <span class="count">1 / 100</span>
    <span class="label">built so far</span>
  </a>

  <header>
    <nav>
      <a href="{asset_prefix}index.html" class="logo">
        <img src="{asset_prefix}assets/images/logo-horizontal-white.svg" width="168" height="38" alt="Digital Ops Systems"/>
      </a>
      <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul>
        <li><a href="{asset_prefix}index.html">Home</a></li>
        <li><a href="{asset_prefix}about.html">About</a></li>
        <li><a href="{asset_prefix}services.html">Services</a></li>
        <li><a href="{asset_prefix}projects.html">Projects</a></li>
        <li><a href="{asset_prefix}blog.html">Blog</a></li>
        <li><a href="{asset_prefix}contact.html">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main>
"""

FOOTER_TMPL = """  </main>

  <footer>
    <div class="footer-inner">
      <div class="footer-brand">
        <h3>Lee Scott</h3>
        <span class="tagline">Helping Texas Businesses Win More Customers Online</span>
        <p>We build websites that capture leads, follow up fast, and keep your business from losing customers to slower competitors.</p>
        <div class="footer-contact">
          <a href="mailto:contact@digitalopsystems.com">contact@digitalopsystems.com</a>
        </div>
        <div class="footer-social">
          <a href="https://www.linkedin.com/company/digitalops-systems/posts/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
          <a href="https://x.com/Otis_S_Park" target="_blank" rel="noopener noreferrer">X</a>
        </div>
      </div>
      <div class="footer-links">
        <h4>Navigation</h4>
        <ul>
          <li><a href="{asset_prefix}index.html">Home</a></li>
          <li><a href="{asset_prefix}about.html">About</a></li>
          <li><a href="{asset_prefix}services.html">Services</a></li>
          <li><a href="{asset_prefix}projects.html">Projects</a></li>
          <li><a href="{asset_prefix}blog.html">Blog</a></li>
          <li><a href="{asset_prefix}contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="footer-links">
        <h4>Service Areas</h4>
        <ul>
          <li><a href="{asset_prefix}contact.html">Houston, TX</a></li>
          <li><a href="{asset_prefix}contact.html">Austin, TX</a></li>
          <li><a href="{asset_prefix}contact.html">San Antonio, TX</a></li>
          <li><a href="{asset_prefix}contact.html">Dallas-Fort Worth, TX</a></li>
          <li><a href="{asset_prefix}contact.html">Remote Nationwide</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 Lee Scott. All rights reserved.</p>
      <p><a href="{asset_prefix}privacy.html">Privacy Policy</a> &middot; <a href="{asset_prefix}terms-of-service.html">Terms of Service</a></p>
    </div>
  </footer>

  <script src="{asset_prefix}assets/js/script.js"></script>
</body>
</html>
"""

POST_BODY_TMPL = """
    <section class="page-hero">
      <div class="blog-meta" style="justify-content:center;margin-bottom:0.5rem;">
        <span class="category">{category}</span>
        <span class="dot">&middot;</span>
        <span>{date_display}</span>
      </div>
      <h1>{title}</h1>
    </section>

    <div class="section-wrap">
      <div class="section blog-post-body" style="max-width:760px;margin:0 auto;">
{body_html}
      </div>
    </div>

    <section class="cta-section">
      <h2>It's not as hard as you think.</h2>
      <p>The on-ramp is open. Give us a chance on a free 30-minute call &mdash; we'll look at where you are and tell you honestly what would actually help.</p>
      <div class="btn-pair">
        <a href="{asset_prefix}contact.html" class="btn">Schedule a Free Strategy Call</a>
        <a href="{asset_prefix}services.html" class="btn-outline">See the Packages</a>
      </div>
    </section>
"""

INDEX_BODY_TMPL = """
    <section class="page-hero">
      <h1>Insights &amp; Resources</h1>
      <p>Practical ideas for business owners who want to win more customers, save time, and stop leaving money on the table.</p>
    </section>

    <div class="section-wrap">
      <div class="section">
        <div class="text-center">
          <span class="section-label">Latest Articles</span>
          <h2 class="section-title">Built for Business Owners, Not Technologists</h2>
          <p class="section-sub">No jargon. No hype. Just practical insight on building smarter businesses.</p>
        </div>
        <div class="blog-grid">
{cards}
        </div>
      </div>
    </div>

    <div class="section-wrap alt">
      <div class="section text-center">
        <span class="section-label">Topics We Cover</span>
        <h2 class="section-title">What You'll Find Here</h2>
        <div class="topic-grid">
          <div class="topic-card">
            <h4>Tools &amp; Shortcuts</h4>
            <p>Practical tools that real businesses are using to grow — without hiring more people to keep up.</p>
          </div>
          <div class="topic-card">
            <h4>Know Your Numbers</h4>
            <p>How to get a clear picture of what's happening in your business — and use it to make better decisions.</p>
          </div>
          <div class="topic-card">
            <h4>Lead Generation</h4>
            <p>Website strategy, follow-up, and tactics that turn visitors into paying clients.</p>
          </div>
          <div class="topic-card">
            <h4>Running a Tighter Ship</h4>
            <p>How to set up your business so things run smoothly &mdash; fewer dropped balls, less scrambling, more consistency.</p>
          </div>
        </div>
      </div>
    </div>

    <section class="cta-section">
      <h2>Want Your Business to Run Like This?</h2>
      <p>Reading is just the start. The real change happens when you put it to work. Let's talk about your business.</p>
      <div class="btn-pair">
        <a href="contact.html" class="btn">Schedule a Free Strategy Call</a>
        <a href="services.html" class="btn-outline">View Services</a>
      </div>
    </section>
"""

CARD_TMPL = """          <div class="blog-card">
            <div class="blog-img">{emoji}</div>
            <div class="blog-content">
              <div class="blog-meta">
                <span class="category">{category}</span>
                <span class="dot">&middot;</span>
                <span>{date_display}</span>
              </div>
              <h3><a href="blog/{slug}.html">{title}</a></h3>
              <p>{summary}</p>
              <a href="blog/{slug}.html" class="read-more">Read Article &rarr;</a>
            </div>
          </div>"""


def format_date(date_iso: str) -> str:
    """2026-06-06 → 'June 6, 2026'. Returns input on parse failure."""
    try:
        from datetime import date as date_cls

        d = date_cls.fromisoformat(date_iso)
        return d.strftime("%B %-d, %Y")
    except Exception:
        return date_iso


# ─── Build ──────────────────────────────────────────────────────────────────


def build() -> None:
    if not POSTS_DIR.exists():
        print(f"No posts directory at {POSTS_DIR}; nothing to build.")
        return
    sources = sorted(POSTS_DIR.glob("*.md"))
    if not sources:
        print(f"No .md posts in {POSTS_DIR}; nothing to build.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    posts: list[Post] = []
    for src in sources:
        post = parse_post(src)
        if post.draft:
            print(f"  skipped (draft): {post.slug}")
            continue
        posts.append(post)

    # Newest first by date
    posts.sort(key=lambda p: p.date, reverse=True)

    # Write each post page
    for post in posts:
        canonical = f"{CANONICAL_BASE}/blog/{post.slug}.html"
        desc = post.summary or post.title
        header = HEADER_TMPL.format(
            title=f"{post.title} | Digital Ops Systems",
            description=html.escape(desc),
            canonical=canonical,
            asset_prefix="../",
        )
        body = POST_BODY_TMPL.format(
            category=html.escape(post.category),
            date_display=format_date(post.date),
            title=html.escape(post.title),
            body_html=post.body_html,
            asset_prefix="../",
        )
        footer = FOOTER_TMPL.format(asset_prefix="../")
        (OUT_DIR / f"{post.slug}.html").write_text(header + body + footer, encoding="utf-8")
        print(f"  wrote blog/{post.slug}.html")

    # Write index
    cards = "\n".join(
        CARD_TMPL.format(
            emoji=html.escape(p.emoji),
            category=html.escape(p.category),
            date_display=format_date(p.date),
            slug=p.slug,
            title=html.escape(p.title),
            summary=html.escape(p.summary or ""),
        )
        for p in posts
    )
    header = HEADER_TMPL.format(
        title="Small Business Website Tips & Resources | Digital Ops Systems",
        description="Practical tips for small business owners in Louisiana and Texas. No jargon — just ideas on websites, lead capture, and follow-up that help you win more customers.",
        canonical=f"{CANONICAL_BASE}/blog.html",
        asset_prefix="",
    )
    body = INDEX_BODY_TMPL.format(cards=cards)
    footer = FOOTER_TMPL.format(asset_prefix="")
    INDEX_PATH.write_text(header + body + footer, encoding="utf-8")
    print(f"  wrote {INDEX_PATH.name} ({len(posts)} cards)")

    print(f"\nBuilt {len(posts)} post(s).")


if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
