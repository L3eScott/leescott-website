#!/usr/bin/env python3
"""
GEO / AEO module  —  Digital Ops Systems SEO/EEAT engine (Phase 1).

Turns a plain FAQ block into the two things AI assistants (ChatGPT, Perplexity,
Google AI) and Google's rich results actually use:
  1. Visible on-page "answer blocks" (reuses the site's existing .faq accordion).
  2. FAQPage JSON-LD, structurally validated before it can ship.

Used by publish_post.py; also importable to add answer blocks to money pages.

FAQ spec block format (goes after a '---FAQ---' marker in a draft):
    SUMMARY: one-line direct answer (optional; may contain inline HTML links)
    Q: A question a real customer would ask
    A: A direct, quotable answer. May contain inline HTML (e.g. <a> links).
       Continuation lines are appended to the previous answer.
    Q: ...
    A: ...
"""
import json, re, html

_TAG = re.compile(r"<[^>]+>")


def parse_faq(text):
    """Parse an FAQ spec block -> (summary_or_None, [(question, answer_html), ...])."""
    summary = None
    faqs = []
    pending_q = None
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("SUMMARY:"):
            summary = s[len("SUMMARY:"):].strip()
        elif s.startswith("Q:"):
            if pending_q is not None:
                raise ValueError("FAQ: two 'Q:' in a row with no 'A:' between them")
            pending_q = s[2:].strip()
        elif s.startswith("A:"):
            if pending_q is None:
                raise ValueError("FAQ: 'A:' with no preceding 'Q:'")
            faqs.append((pending_q, s[2:].strip()))
            pending_q = None
        else:
            # continuation of the previous answer
            if faqs and pending_q is None:
                q, a = faqs[-1]
                faqs[-1] = (q, (a + " " + s).strip())
            else:
                raise ValueError("FAQ: unrecognized line (need SUMMARY:/Q:/A:): " + s)
    if pending_q is not None:
        raise ValueError("FAQ: last 'Q:' has no matching 'A:'")
    return summary, faqs


def _plain(s):
    """Strip HTML tags -> plain text for schema answer text."""
    return html.unescape(_TAG.sub("", s)).strip()


def render_answer_blocks(summary, faqs, heading="Common questions"):
    """Visible answer blocks, reusing the site's .faq accordion styles."""
    if not faqs:
        return ""
    p = ['<section class="section faq-aeo">', '  <div class="wrap">', '    <div class="faq">']
    if heading:
        p.append("      <h2>%s</h2>" % html.escape(heading))
    if summary:
        p.append('      <p class="answer-summary">%s</p>' % summary)
    for q, a in faqs:
        p.append("      <details><summary>%s</summary><p>%s</p></details>" % (html.escape(q), a))
    p += ["    </div>", "  </div>", "</section>"]
    return "\n".join(p)


def faqpage_jsonld(faqs):
    """FAQPage JSON-LD (<script> block). Answer text is plain (schema-safe)."""
    if not faqs:
        return ""
    entities = [{
        "@type": "Question",
        "name": _plain(q),
        "acceptedAnswer": {"@type": "Answer", "text": _plain(a)},
    } for q, a in faqs]
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, indent=2, ensure_ascii=False)
            + "\n</script>")


def validate_faqpage(jsonld_script):
    """Structurally validate a FAQPage <script> block. -> (ok, [errors])."""
    m = re.search(r"<script[^>]*>(.*)</script>", jsonld_script, re.S)
    if not m:
        return False, ["no <script> JSON-LD block found"]
    try:
        data = json.loads(m.group(1))
    except Exception as e:  # noqa: BLE001
        return False, ["invalid JSON: %s" % e]
    errors = []
    if data.get("@context") != "https://schema.org":
        errors.append('@context must be "https://schema.org"')
    if data.get("@type") != "FAQPage":
        errors.append('@type must be "FAQPage"')
    ents = data.get("mainEntity") or []
    if not ents:
        errors.append("mainEntity is empty (need >=1 Q&A)")
    for i, e in enumerate(ents):
        if e.get("@type") != "Question":
            errors.append("entity %d: @type must be Question" % i)
        if not (e.get("name") or "").strip():
            errors.append("entity %d: missing question name" % i)
        ans = e.get("acceptedAnswer") or {}
        if ans.get("@type") != "Answer":
            errors.append("entity %d: acceptedAnswer @type must be Answer" % i)
        if not (ans.get("text") or "").strip():
            errors.append("entity %d: answer missing text" % i)
    return (not errors), errors


if __name__ == "__main__":
    # tiny self-test
    demo = ("SUMMARY: Yes — a complete profile plus real reviews is the fastest lever.\n"
            "Q: Do I need a website if I'm on Booksy?\n"
            "A: Booksy rents you a listing; a site you own builds lasting visibility.\n"
            "Q: How do I get more reviews?\n"
            "A: Ask every happy client with a one-tap link.")
    summ, pairs = parse_faq(demo)
    js = faqpage_jsonld(pairs)
    ok, errs = validate_faqpage(js)
    print("parsed:", len(pairs), "Q&A · summary:", bool(summ))
    print("valid:", ok, errs)
    print(render_answer_blocks(summ, pairs)[:200], "...")
