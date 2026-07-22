#!/usr/bin/env python3
"""
GBP Ops  —  Digital Ops Systems SEO/EEAT engine, Phase 3.

The two recurring weekly GBP tasks, made paste-ready (no OAuth needed):
  1. Weekly GBP post   — a rotating library of on-brand, ready-to-paste posts.
  2. Review responses  — a playbook + templates so every review gets a fast,
                         human, on-brand reply within 48h.

Renders a brand "GBP Ops Kit" (HTML + optional PDF) + a plain-text paste file.
Human-in-the-loop by design: nothing auto-posts. Manager, never Owner.
Standards: Lee's voice, never over-promise, never promise a ranking,
real reviews only, respond within 48h, keep it short and genuine.

Usage:
  python3 tools/gbp_ops.py [--weeks 8] [--out FILE.html] [--txt FILE.txt] [--pdf]
"""
import sys, os, html, subprocess
from datetime import date

SITE = "https://digitalopsystems.com"
L = {
    "crm": SITE + "/crm.html",
    "search": SITE + "/search-ai.html",
    "websites": SITE + "/websites.html",
    "barbershops": SITE + "/for-barbershops.html",
    "blog_barber": SITE + "/blog/2026-07-21-baton-rouge-barbers-get-found-online.html",
    "contact": SITE + "/contact.html",
    "newsletter": SITE + "/newsletter.html",
}

# --- weekly post library (rotates) ---------------------------------------
POSTS = [
    {"type": "Tip", "cta": "Learn more", "photo": "CRM dashboard screenshot",
     "body": "Losing customers to a full inbox? The fix isn't working harder — it's a system that "
             "remembers every follow-up, birthday and renewal for you and sends the reminder so you "
             "don't have to. That's what a good CRM does.\n\nSee how it works → {crm}"},
    {"type": "Educational", "cta": "Learn more", "photo": "Service-area map graphic",
     "body": "People don't just Google anymore — they ask ChatGPT and Perplexity \"who's the best "
             "near me?\" If your business isn't in those answers, you're invisible to a growing share of "
             "customers. Here's how we fix that → {search}"},
    {"type": "Offer", "cta": "Book", "photo": "A real site you built",
     "body": "Your website should pay for itself. Get a professional, mobile-ready site built and run "
             "for you — free when you're on an annual CRM plan. No big upfront bill, no tech "
             "headaches.\n\nBook a free call → {contact}"},
    {"type": "Local / Blog", "cta": "Learn more", "photo": "Barbershop photo",
     "body": "New on the blog: how local barbershops actually get found on Google — and fill the "
             "empty chair. Plain English, no jargon. Worth three minutes if you run a shop.\n\n"
             "Read it → {blog_barber}"},
    {"type": "Service spotlight", "cta": "Learn more", "photo": "Barbershop photo",
     "body": "Barbers: great cuts don't matter if new clients can't find you. We build the website, set "
             "up your Google profile and reviews, and run the CRM that keeps clients coming back — "
             "built for shops in Baton Rouge & Houston.\n\n{barbershops}"},
    {"type": "Tip", "cta": "Learn more", "photo": "Storefront / happy customer",
     "body": "Reviews are the cheapest marketing you're probably not doing yet. A steady trickle of "
             "honest Google reviews is what turns a \"maybe\" into a booking. Ask every happy customer "
             "— we'll help you build the habit.\n\n{search}"},
    {"type": "Tip", "cta": "Book", "photo": "Baton Rouge local image",
     "body": "Someone near you just searched \"[your service] near me\" and picked a business in about "
             "30 seconds. Were you even in the running? Getting found in that moment is a system, not "
             "luck.\n\nLet's talk → {contact}"},
    {"type": "Educational", "cta": "Learn more", "photo": "Website mockup",
     "body": "Booksy and Instagram are great — but you're renting your visibility. A website you "
             "own builds lasting search presence and can't be throttled by someone else's app. Own your "
             "corner of the internet → {websites}"},
]

# --- review responses ----------------------------------------------------
PLAYBOOK = [
    "Respond within 48 hours — to every review, good or bad.",
    "Use their name, and say something specific to what they wrote.",
    "Keep it short: one to three sentences.",
    "Never argue or get defensive. For a complaint: own it, apologize once, move it offline.",
    "Sign it so it reads human — “— Lee, Digital Ops Systems.”",
    "Never fake, buy, or incentivize a review. Real customers only.",
]
RESPONSES = {
    "5 stars, with a comment": [
        "Thank you so much, {name} — this means a lot. It was a pleasure building this with you, and we're just getting started. — Lee, Digital Ops Systems",
        "Appreciate you taking the time, {name}. Glad it's working the way you hoped — call us anytime you need anything. — Lee",
    ],
    "5 stars, no comment": [
        "Thanks for the five stars, {name}! Grateful for your support — let us know if there's ever anything you need. — Lee, Digital Ops Systems",
    ],
    "4 stars": [
        "Thanks for the honest feedback, {name} — glad you're happy with the work. If there's one thing that would've made it a five, I'd genuinely like to hear it: contact@digitalopsystems.com. — Lee",
    ],
    "1–3 stars (critical)": [
        "I'm sorry we fell short here, {name} — that's on us, and I want to make it right. Could you email me directly at contact@digitalopsystems.com so I can look into exactly what happened? — Lee, Digital Ops Systems",
        "Thank you for telling us, {name}. This isn't the experience we want anyone to have. I'd like to understand what went wrong and fix it — please reach me at contact@digitalopsystems.com. — Lee",
    ],
}

NAVY = "#0D1B2A"; NAVY2 = "#1b2a4a"; GOLD = "#d4a53a"; INK = "#20304f"
SLATE = "#5b6472"; PAPER = "#f6f2e7"; LINE = "#e3ddcd"; CREAM = "#fbf9f2"


def fill(body):
    return body.format(**L)


def weekly_posts(weeks):
    out = []
    for i in range(weeks):
        p = POSTS[i % len(POSTS)]
        out.append({"week": i + 1, "type": p["type"], "cta": p["cta"],
                    "photo": p["photo"], "body": fill(p["body"])})
    return out


def esc(s):
    return html.escape(str(s), quote=True)


def build_txt(posts, stamp):
    lines = ["DIGITAL OPS SYSTEMS — GBP OPS KIT  (prepared %s)" % stamp,
             "Paste-ready. Nothing auto-posts. Manager, never Owner.", "",
             "=" * 60, "WEEKLY GBP POSTS (one per week, rotates)", "=" * 60]
    for p in posts:
        lines += ["", "-- Week %d · %s · button: %s · photo: %s --"
                  % (p["week"], p["type"], p["cta"], p["photo"]), p["body"]]
    lines += ["", "=" * 60, "REVIEW RESPONSES", "=" * 60, "", "Playbook:"]
    lines += ["  • " + r for r in PLAYBOOK]
    for scenario, temps in RESPONSES.items():
        lines += ["", scenario + ":"]
        for t in temps:
            lines.append("  " + t)
    return "\n".join(lines) + "\n"


def _card(title, meta, body_html):
    return (f'<div class="card"><div class="ct"><span class="tt">{title}</span>'
            f'<span class="mt">{meta}</span></div>{body_html}</div>')


def build_html(posts, stamp):
    post_cards = ""
    for p in posts:
        body = esc(p["body"]).replace("\n\n", "<br><br>").replace("\n", "<br>")
        # linkify the trailing URL for readability
        meta = f'Button: <b>{esc(p["cta"])}</b> &middot; Photo: {esc(p["photo"])}'
        post_cards += _card(f'Week {p["week"]} &middot; {esc(p["type"])}', meta,
                            f'<div class="paste">{body}</div>')
    resp_html = '<ul class="play">' + "".join(f"<li>{esc(x)}</li>" for x in PLAYBOOK) + "</ul>"
    for scenario, temps in RESPONSES.items():
        items = "".join(f'<div class="paste sm">{esc(t)}</div>' for t in temps)
        resp_html += f'<div class="resp"><h3>{esc(scenario)}</h3>{items}</div>'

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GBP Ops Kit — Digital Ops Systems</title><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:{INK};background:{CREAM};line-height:1.55;font-size:15px}}
.page{{max-width:860px;margin:0 auto;background:#fff;box-shadow:0 2px 30px rgba(0,0,0,.06)}}
.hd{{background:{NAVY};color:#fff;padding:30px 44px 26px;border-bottom:5px solid {GOLD}}}
.brand{{font-weight:800;font-size:20px}}.brand small{{display:block;color:{GOLD};font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-top:3px;font-weight:600}}
.hd h1{{font-size:25px;margin-top:16px}}.hd .sub{{color:#c9d4ea;margin-top:6px;font-size:14px}}
.body{{padding:32px 44px 40px}}
h2{{font-size:14px;text-transform:uppercase;letter-spacing:2px;color:{GOLD};margin:34px 0 6px;font-weight:800}}
h2:first-child{{margin-top:0}}.note{{color:{SLATE};font-size:13px;margin-bottom:16px}}
.card{{border:1px solid {LINE};border-radius:12px;padding:16px 18px;margin-bottom:14px;background:{PAPER}}}
.ct{{display:flex;justify-content:space-between;gap:12px;align-items:baseline;flex-wrap:wrap;margin-bottom:10px}}
.tt{{font-weight:800;color:{NAVY};font-size:15px}}.mt{{font-size:12px;color:{SLATE}}}.mt b{{color:{INK}}}
.paste{{background:#fff;border:1px solid {LINE};border-radius:8px;padding:13px 15px;font-size:14px;color:{INK};white-space:normal}}
.paste.sm{{margin-top:8px}}
.play{{list-style:none;margin:6px 0 8px}}.play li{{padding:6px 0 6px 24px;position:relative;border-bottom:1px solid {LINE};font-size:14px}}
.play li:before{{content:"\\2713";position:absolute;left:0;color:{GOLD};font-weight:800}}
.resp{{margin-top:14px}}.resp h3{{font-size:14px;color:{NAVY};margin-bottom:2px}}
.honest{{background:{PAPER};border-left:4px solid {GOLD};padding:13px 17px;margin-top:26px;font-size:13.5px}}
.ft{{background:{NAVY};color:#c9d4ea;padding:18px 44px;font-size:12px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px}}
.ft b{{color:#fff}}@media print{{body{{background:#fff}}.page{{box-shadow:none}}}}
</style></head><body><div class="page">
<div class="hd"><div class="brand">Digital Ops Systems<small>GBP Ops Kit</small></div>
<h1>Weekly posts &amp; review responses</h1>
<div class="sub">Paste-ready &middot; prepared {esc(stamp)}</div></div>
<div class="body">
<h2>Weekly GBP posts</h2>
<p class="note">One per week, rotating. Paste into your Google Business Profile &rarr; Add update, pick the button, attach the photo. Posts are a ranking signal &mdash; keep them steady.</p>
{post_cards}
<h2>Review responses</h2>
<p class="note">Reply to every review within 48 hours. Swap in the reviewer's name and one specific detail. Never argue; take problems to email.</p>
{resp_html}
<div class="honest"><b>How we run it:</b> nothing auto-posts &mdash; you (or we, as Manager) paste and personalize. We never promise a ranking, never fake a review, and always reply like a human.</div>
</div>
<div class="ft"><span><b>Digital Ops Systems</b> &middot; Baton Rouge &amp; Houston</span><span>contact@digitalopsystems.com</span></div>
</div></body></html>"""


def main():
    args = sys.argv[1:]
    weeks = 8
    if "--weeks" in args:
        weeks = int(args[args.index("--weeks") + 1])
    out = None; txt = None
    for a in args:
        if a.startswith("--out="): out = a.split("=", 1)[1]
        if a.startswith("--txt="): txt = a.split("=", 1)[1]
    stamp = date.today().strftime("%B %-d, %Y")
    posts = weekly_posts(weeks)
    out = out or os.path.join(os.path.expanduser("~"), "Downloads", "dops-gbp-ops-kit.html")
    txt = txt or os.path.join(os.path.expanduser("~"), "Downloads", "dops-gbp-ops-kit.txt")
    open(out, "w", encoding="utf-8").write(build_html(posts, stamp))
    open(txt, "w", encoding="utf-8").write(build_txt(posts, stamp))
    print("wrote HTML: %s" % out)
    print("wrote TXT : %s" % txt)
    print("posts=%d  response scenarios=%d" % (len(posts), len(RESPONSES)))
    if "--pdf" in args:
        from shutil import which
        ch = which("chromium") or which("chromium-browser") or which("google-chrome")
        if ch:
            pdf = os.path.splitext(out)[0] + ".pdf"
            subprocess.run([ch, "--headless=new", "--no-sandbox", "--disable-gpu",
                            "--no-pdf-header-footer", "--print-to-pdf=" + pdf,
                            "file://" + os.path.abspath(out)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            print("wrote PDF : %s" % pdf)


if __name__ == "__main__":
    main()
