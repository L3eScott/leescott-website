#!/usr/bin/env python3
"""
Competitor & Citation Scan  —  Digital Ops Systems SEO/EEAT engine, Phase 4.

The quarterly intelligence pass from the delivery model:
  - Who's ranking / in the local 3-pack, and what they have that we don't.
  - AI-citation check: when someone asks an assistant "who should I hire for X
    in [city]", are WE named?
  - An honest gap analysis + the one or two things to focus on next quarter.

Unlike the deterministic modules, the scan itself is a research pass (live web +
asking the assistants). This tool takes the findings as a JSON and renders a
repeatable, brand-conformant report (HTML + PDF) so every quarter looks the same.

Guardrails: verified findings only (no fabricated competitor data), never promise
a ranking, intel is a map — not a badge we wear.

Usage:
  python3 tools/competitor_scan.py <scan.json> [--pdf] [--out FILE]
"""
import sys, os, json, html, subprocess
from datetime import date

NAVY = "#0D1B2A"; NAVY2 = "#1b2a4a"; GOLD = "#d4a53a"; INK = "#20304f"
SLATE = "#5b6472"; PAPER = "#f6f2e7"; LINE = "#e3ddcd"; CREAM = "#fbf9f2"
GOOD = "#2c8a5b"; WARN = "#b23b1e"


def esc(s):
    return html.escape(str(s), quote=True)


def yesno(v):
    if v is True:
        return '<span class="tag no">yes</span>'
    if v is False:
        return '<span class="tag yes">no</span>'
    return '<span class="tag part">%s</span>' % esc(v)


def comp_rows(comps):
    if not comps:
        return "<tr><td colspan='5' class='muted'>No competitors recorded.</td></tr>"
    out = []
    for c in comps:
        has = ", ".join(c.get("has", [])) or "&mdash;"
        out.append(
            "<tr><td><b>%s</b><div class='sub'>%s</div></td><td class='n'>%s</td>"
            "<td class='n'>%s</td><td>%s</td><td>%s</td></tr>" % (
                esc(c.get("name", "")), esc(c.get("url", "")),
                esc(c.get("since", "&mdash;")), esc(c.get("reviews", "&mdash;")),
                has, esc(c.get("gap_vs_us", "&mdash;"))))
    return "".join(out)


def ai_rows(items):
    if not items:
        return "<tr><td colspan='3' class='muted'>No citation checks recorded.</td></tr>"
    out = []
    for a in items:
        out.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            esc(a.get("query", "")), yesno(a.get("cited_us")), esc(a.get("notes", ""))))
    return "".join(out)


def li(items, empty="&mdash;"):
    if not items:
        return "<p class='muted'>%s</p>" % empty
    return "<ul class='list'>" + "".join("<li>%s</li>" % esc(x) for x in items) + "</ul>"


def build_html(d, stamp):
    us = d.get("us", {})
    sample = d.get("sample")
    banner = ('<div class="sample">SAMPLE SCAN &mdash; illustrative, verify before use</div>'
              if sample else "")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Competitive &amp; AI-Citation Scan — {esc(d.get('market',''))} — {esc(d.get('period',''))}</title><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',-apple-system,Segoe UI,Roboto,Arial,sans-serif;color:{INK};background:{CREAM};line-height:1.55;font-size:15px}}
.page{{max-width:880px;margin:0 auto;background:#fff;box-shadow:0 2px 30px rgba(0,0,0,.06)}}
.hd{{background:{NAVY};color:#fff;padding:30px 44px 26px;border-bottom:5px solid {GOLD}}}
.brand{{font-weight:800;font-size:20px}}.brand small{{display:block;color:{GOLD};font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-top:3px;font-weight:600}}
.hd h1{{font-size:25px;margin-top:16px}}.hd .sub{{color:#c9d4ea;margin-top:6px;font-size:14px}}
.sample{{background:{GOLD};color:{NAVY};text-align:center;font-weight:700;padding:8px;font-size:13px;letter-spacing:.5px}}
.body{{padding:32px 44px 40px}}
.lede{{font-size:16px;color:{SLATE};margin-bottom:24px}}
.pos{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:8px}}
.pos .b{{flex:1;min-width:150px;border:1px solid {LINE};border-radius:12px;padding:16px 18px;background:{PAPER}}}
.pos .k{{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:{SLATE};font-weight:700}}
.pos .v{{font-size:26px;font-weight:800;color:{NAVY};margin-top:4px;line-height:1.1}}
h2{{font-size:14px;text-transform:uppercase;letter-spacing:2px;color:{GOLD};margin:32px 0 12px;font-weight:800}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{text-align:left;color:{SLATE};font-size:11.5px;text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid {LINE};padding:8px 9px}}
td{{padding:10px 9px;border-bottom:1px solid {LINE};vertical-align:top}}
td.n{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
td .sub{{font-size:11.5px;color:{SLATE};margin-top:2px}}
.tag{{font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px}}
.tag.yes{{background:#e4f1e8;color:{GOOD}}}.tag.no{{background:#fbe6e2;color:{WARN}}}.tag.part{{background:#f1ece0;color:{SLATE}}}
.list{{list-style:none}}.list li{{padding:8px 0 8px 24px;position:relative;border-bottom:1px solid {LINE}}}
.list li:before{{content:"\\2192";position:absolute;left:0;color:{GOLD};font-weight:800}}
.muted{{color:{SLATE}}}
.honest{{background:{PAPER};border-left:4px solid {GOLD};padding:13px 17px;margin-top:26px;font-size:13.5px}}
.ft{{background:{NAVY};color:#c9d4ea;padding:18px 44px;font-size:12px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px}}
.ft b{{color:#fff}}@media print{{body{{background:#fff}}.page{{box-shadow:none}}}}
</style></head><body><div class="page">
{banner}
<div class="hd"><div class="brand">Digital Ops Systems<small>Competitive &amp; AI-Citation Scan</small></div>
<h1>Where we stand in {esc(d.get('market',''))}</h1>
<div class="sub">{esc(d.get('focus_service',''))} &nbsp;&middot;&nbsp; {esc(d.get('period',''))}</div></div>
<div class="body">
  <p class="lede">A quarterly, honest look at who we're up against, whether AI assistants recommend us yet, and the one or two things that move us forward. Intel is a map &mdash; not a badge.</p>

  <div class="pos">
    <div class="b"><div class="k">Our Google reviews</div><div class="v">{esc(us.get('reviews','&mdash;'))}</div></div>
    <div class="b"><div class="k">Our domain age</div><div class="v">{esc(us.get('domain_age','&mdash;'))}</div></div>
    <div class="b"><div class="k">Competitors scanned</div><div class="v">{len(d.get('competitors',[]))}</div></div>
  </div>
  <p class="muted" style="font-size:13px">{esc(us.get('notes',''))}</p>

  <h2>The competitive landscape</h2>
  <table><thead><tr><th>Competitor</th><th class="n">Since</th><th class="n">Reviews</th><th>What they have</th><th>Their edge on us</th></tr></thead>
  <tbody>{comp_rows(d.get('competitors',[]))}</tbody></table>

  <h2>AI-citation check &mdash; do assistants recommend us?</h2>
  <table><thead><tr><th>When someone asks&hellip;</th><th>We're named?</th><th>Notes</th></tr></thead>
  <tbody>{ai_rows(d.get('ai_citation',[]))}</tbody></table>

  <h2>Where we can win</h2>
  {li(d.get('gaps'))}

  <h2>Focus this quarter</h2>
  {li(d.get('focus'))}

  <div class="honest"><b>Reading this honestly:</b> being new means we're behind on reviews and domain age &mdash; that's expected, and it's fixable. We compete by owning the local, barber-specific searches the big agencies ignore, and by earning real reviews. We never promise a ranking; we work the levers we control.</div>
</div>
<div class="ft"><span><b>Digital Ops Systems</b> &middot; {esc(d.get('market',''))}</span><span>Prepared {esc(stamp)} &middot; contact@digitalopsystems.com</span></div>
</div></body></html>"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = sys.argv[1:]
    if not args:
        print("usage: competitor_scan.py <scan.json> [--pdf] [--out FILE]"); sys.exit(1)
    d = json.load(open(args[0], encoding="utf-8"))
    stamp = date.today().strftime("%B %-d, %Y")
    out = None
    for f in flags:
        if f.startswith("--out="):
            out = f.split("=", 1)[1]
    if out is None:
        out = os.path.join(os.path.dirname(os.path.abspath(args[0])), "scan-report.html")
    open(out, "w", encoding="utf-8").write(build_html(d, stamp))
    print("wrote HTML: %s" % out)
    print("competitors=%d  ai-checks=%d" % (len(d.get("competitors", [])), len(d.get("ai_citation", []))))
    if "--pdf" in flags:
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
