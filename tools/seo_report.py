#!/usr/bin/env python3
"""
SEO / Search & AI — Monthly Report generator.
Digital Ops Systems SEO/EEAT engine, Phase 2 (Monitoring & Reporting).

Turns a Google Search Console Performance CSV export + a small config into the
plain-English 4-number report the delivery model specifies:
  1. How many people SAW you on Google      (impressions + optional GBP views)
  2. How many TOOK AN ACTION                 (clicks + optional GBP actions)
  3. WHERE YOU RANK                          (top queries + honest position)
  4. WHAT WE DID this month                  (the work list)
plus "next month" and "what we need from you". Never only-good-news:
pass --prev last month's CSV to show honest up/down deltas.

Export-driven v1 (no OAuth needed): in GSC, open Performance, export, and hand
this the queries CSV. The same generator later plugs into the GSC API.

Usage:
  python3 tools/seo_report.py config.json queries.csv [--prev prev.csv] [--pdf] [--out FILE]
"""
import sys, os, csv, json, io, html, subprocess
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVY = "#0D1B2A"; NAVY2 = "#1b2a4a"; GOLD = "#d4a53a"; INK = "#20304f"
SLATE = "#5b6472"; PAPER = "#f6f2e7"; LINE = "#e3ddcd"; CREAM = "#fbf9f2"


def die(m): print("ERROR: " + m); sys.exit(1)


def _num(s):
    """'1,234' -> 1234 ; '3.4%' -> 3.4 ; '' -> 0"""
    s = (s or "").strip().replace(",", "").replace("%", "")
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_gsc_csv(path):
    """Parse a GSC Performance 'Queries' CSV -> totals + rows.
    Tolerant of column-name variants (Top queries/Query, etc.)."""
    if not os.path.exists(path):
        die("GSC csv not found: " + path)
    raw = open(path, encoding="utf-8-sig").read()
    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    if not rows:
        die("GSC csv is empty: " + path)
    header = [h.strip().lower() for h in rows[0]]

    def col(*names):
        for n in names:
            for i, h in enumerate(header):
                if n in h:
                    return i
        return None

    qi = col("quer", "page", "keyword")
    ci = col("click")
    ii = col("impression")
    pi = col("position")
    if ci is None or ii is None:
        die("GSC csv needs Clicks and Impressions columns (got: %s)" % header)

    out, tot_c, tot_i = [], 0.0, 0.0
    for r in rows[1:]:
        if not r or all(not c.strip() for c in r):
            continue
        clicks = _num(r[ci]) if ci < len(r) else 0
        imps = _num(r[ii]) if ii < len(r) else 0
        tot_c += clicks; tot_i += imps
        out.append({
            "query": (r[qi].strip() if qi is not None and qi < len(r) else ""),
            "clicks": int(clicks), "impressions": int(imps),
            "position": (_num(r[pi]) if pi is not None and pi < len(r) else None),
        })
    out.sort(key=lambda x: x["impressions"], reverse=True)
    return {"clicks": int(tot_c), "impressions": int(tot_i), "rows": out}


def fmt(n):
    return "{:,}".format(int(round(n)))


def delta_badge(now, prev):
    """Honest up/down badge vs last period. Never hides a drop."""
    if prev is None:
        return ""
    d = now - prev
    if d == 0:
        return '<span class="d flat">no change</span>'
    if d > 0:
        return '<span class="d up">&#9650; +%s vs last month</span>' % fmt(d)
    return '<span class="d down">&#9660; %s vs last month</span>' % fmt(d)


def esc(s):
    return html.escape(str(s), quote=True)


def rank_table(rows, limit=12):
    if not rows:
        return '<p class="muted">No query data yet for this period.</p>'
    body = []
    for r in rows[:limit]:
        pos = "&mdash;" if r["position"] is None else ("%.1f" % r["position"])
        body.append(
            "<tr><td>%s</td><td class='n'>%s</td><td class='n'>%s</td><td class='n'>%s</td></tr>"
            % (esc(r["query"] or "(not set)"), fmt(r["impressions"]), fmt(r["clicks"]), pos))
    return (
        "<table class='rank'><thead><tr><th>Search phrase</th><th class='n'>Times shown</th>"
        "<th class='n'>Clicks</th><th class='n'>Avg. position</th></tr></thead><tbody>"
        + "".join(body) + "</tbody></table>")


def li_list(items, empty="&mdash;"):
    if not items:
        return "<p class='muted'>%s</p>" % empty
    return "<ul class='list'>" + "".join("<li>%s</li>" % esc(x) for x in items) + "</ul>"


def build_html(cfg, gsc, prev, stamp):
    g = cfg.get("gbp") or {}
    gbp_views = g.get("views")
    saw = gsc["impressions"] + (gbp_views or 0)
    gbp_actions = sum(v for v in [g.get("calls"), g.get("directions"), g.get("website_clicks")] if v)
    acted = gsc["clicks"] + gbp_actions
    prev_imps = prev["impressions"] if prev else None
    prev_clicks = prev["clicks"] if prev else None

    sample = cfg.get("sample")
    banner = ('<div class="sample">SAMPLE REPORT &mdash; illustrative numbers, not live data</div>'
              if sample else "")

    gbp_note = ("" if gbp_views is not None else
                '<p class="tiny">Google Business Profile views/calls aren\'t in this figure yet '
                '&mdash; they\'re added once profile insights are connected.</p>')

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Search &amp; AI Report — {esc(cfg.get('customer',''))} — {esc(cfg.get('period',''))}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:{INK};background:{CREAM};line-height:1.5;font-size:15px}}
.page{{max-width:820px;margin:0 auto;background:#fff;box-shadow:0 2px 30px rgba(0,0,0,.06)}}
.hd{{background:{NAVY};color:#fff;padding:30px 44px 26px;border-bottom:5px solid {GOLD}}}
.brand{{font-weight:800;letter-spacing:.3px;font-size:20px}}
.brand small{{display:block;font-weight:500;color:{GOLD};font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-top:3px}}
.hd h1{{font-size:26px;margin-top:18px;font-weight:800}}
.hd .sub{{color:#c9d4ea;margin-top:6px;font-size:14px}}
.sample{{background:{GOLD};color:{NAVY};text-align:center;font-weight:700;padding:8px;font-size:13px;letter-spacing:.5px}}
.body{{padding:34px 44px 10px}}
.lede{{font-size:16px;color:{SLATE};margin-bottom:26px}}
.stat-row{{display:flex;gap:18px;margin-bottom:12px}}
.stat{{flex:1;border:1px solid {LINE};border-radius:12px;padding:20px 22px;background:{PAPER}}}
.stat .k{{font-size:12px;text-transform:uppercase;letter-spacing:1.5px;color:{SLATE};font-weight:700}}
.stat .v{{font-size:40px;font-weight:800;color:{NAVY};line-height:1.1;margin:6px 0 2px}}
.d{{display:inline-block;font-size:12px;font-weight:700;padding:2px 8px;border-radius:20px;margin-top:4px}}
.d.up{{background:#e4f2e7;color:#1c7a3f}}.d.down{{background:#fbe6e2;color:#b23b1e}}.d.flat{{background:#eee;color:#666}}
h2{{font-size:15px;text-transform:uppercase;letter-spacing:2px;color:{GOLD};margin:32px 0 12px;font-weight:800}}
h2 span{{color:{NAVY}}}
table.rank{{width:100%;border-collapse:collapse;font-size:14px}}
table.rank th{{text-align:left;color:{SLATE};font-size:12px;text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid {LINE};padding:8px 10px}}
table.rank td{{padding:9px 10px;border-bottom:1px solid {LINE}}}
table.rank .n{{text-align:right;font-variant-numeric:tabular-nums}}
.list{{list-style:none}}.list li{{padding:7px 0 7px 26px;position:relative;border-bottom:1px solid {LINE}}}
.list li:before{{content:"\\2713";position:absolute;left:0;color:{GOLD};font-weight:800}}
.muted{{color:{SLATE}}}.tiny{{font-size:12px;color:{SLATE};margin-top:8px}}
.honest{{background:{PAPER};border-left:4px solid {GOLD};padding:14px 18px;margin:26px 0 6px;font-size:14px;color:{INK}}}
.ft{{background:{NAVY};color:#c9d4ea;padding:20px 44px;font-size:12px;display:flex;justify-content:space-between;margin-top:30px}}
.ft b{{color:#fff}}
@media print{{body{{background:#fff}}.page{{box-shadow:none;max-width:none}}}}
</style></head><body><div class="page">
{banner}
<div class="hd">
  <div class="brand">Digital Ops Systems<small>Search &amp; AI Visibility</small></div>
  <h1>Your Monthly Search &amp; AI Report</h1>
  <div class="sub">{esc(cfg.get('customer',''))} &nbsp;&middot;&nbsp; {esc(cfg.get('period',''))}</div>
</div>
<div class="body">
  <p class="lede">Here&rsquo;s how many people found you on Google this month, what they did, where you&rsquo;re showing up, and exactly what we worked on &mdash; in plain English.</p>

  <div class="stat-row">
    <div class="stat"><div class="k">People who saw you</div><div class="v">{fmt(saw)}</div>{delta_badge(gsc["impressions"], prev_imps)}<div class="muted" style="font-size:12px;margin-top:4px">times your shop showed up in Google</div></div>
    <div class="stat"><div class="k">People who took action</div><div class="v">{fmt(acted)}</div>{delta_badge(gsc["clicks"], prev_clicks)}<div class="muted" style="font-size:12px;margin-top:4px">clicked through to your site</div></div>
  </div>
  {gbp_note}

  <h2><span>Where you&rsquo;re showing up</span></h2>
  <p class="muted" style="font-size:13px;margin-bottom:10px">The searches you appeared for &mdash; honestly, including the ones we haven&rsquo;t won yet. Lower average position is better (1 = the top).</p>
  {rank_table(gsc["rows"])}

  <h2><span>What we did this month</span></h2>
  {li_list(cfg.get("did_this_month"))}

  <h2><span>What&rsquo;s next month</span></h2>
  {li_list(cfg.get("next_month"))}

  <h2><span>What we need from you</span></h2>
  {li_list(cfg.get("we_need"), empty="Nothing right now &mdash; we&rsquo;ve got it.")}

  <div class="honest"><b>Our promise:</b> we never promise a ranking, and we never send only-good-news. If a number dropped, it&rsquo;s in here with the reason. You always see the real picture.</div>
</div>
<div class="ft"><span><b>Digital Ops Systems</b> &middot; Baton Rouge &amp; Houston</span><span>Prepared {esc(stamp)} &middot; contact@digitalopsystems.com</span></div>
</div></body></html>"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if len(args) < 2:
        die("usage: seo_report.py <config.json> <queries.csv> [--prev prev.csv] [--pdf] [--out FILE]")
    cfg = json.load(open(args[0], encoding="utf-8"))
    gsc = parse_gsc_csv(args[1])
    prev = None
    if "--prev" in flags:
        i = sys.argv.index("--prev")
        prev = parse_gsc_csv(sys.argv[i + 1])
    stamp = date.today().strftime("%B %-d, %Y")
    out = None
    for f in flags:
        if f.startswith("--out="):
            out = f.split("=", 1)[1]
    if out is None:
        slug = (cfg.get("customer", "report").lower().replace(" ", "-").replace("&", "and"))
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        out = os.path.join(os.path.dirname(os.path.abspath(args[0])), "report-%s.html" % slug)

    page = build_html(cfg, gsc, prev, stamp)
    open(out, "w", encoding="utf-8").write(page)
    print("wrote HTML : %s" % out)
    print("saw=%s  acted=%s  queries=%d" % (fmt(gsc["impressions"]), fmt(gsc["clicks"]), len(gsc["rows"])))

    if "--pdf" in flags:
        pdf = os.path.splitext(out)[0] + ".pdf"
        ch = None
        for c in ("chromium", "chromium-browser", "google-chrome"):
            from shutil import which
            if which(c):
                ch = which(c); break
        if not ch:
            die("no chromium found for --pdf")
        subprocess.run([ch, "--headless=new", "--no-sandbox", "--disable-gpu",
                        "--no-pdf-header-footer", "--print-to-pdf=" + pdf,
                        "file://" + os.path.abspath(out)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        print("wrote PDF  : %s" % pdf)


if __name__ == "__main__":
    main()
