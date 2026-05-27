# CLAUDE.md

**Last updated:** 2026-05-23. The brand has evolved from "website development agency" to **AI-enabled operational systems consultancy** — delivered through smart websites, workflows, reporting, and automation. Direction is **evolution, not pivot**: keep what works, layer in the broader capability.

## Project
This is the website for **Digital Ops Systems**, founded by Lee Scott.

## Domain
`digitalopsystems.com` (double s — "ops" + "systems"). Any reference to `digitalopsystems.com` (single s) is a bug; correct it on sight.

## Business Positioning
Digital Ops Systems builds **Smart Websites + AI Automation Systems For Growing Businesses.** We are an AI-enabled operational systems consultancy, delivered through smart websites, workflows, reporting, and automation. We are not a generic agency.

## Two Tiers, One Practice

**Entry tier — Smart Website + AI Workers** (public pricing):
- Starter $1,497 + $197/mo
- Growth $3,997 + $497/mo  *(most popular)*
- Professional $7,497 + $997/mo
- Lead capture, fast follow-up, booking, lightweight reporting, the visible "front door" of the business

**Premium tier — AI Automation Systems — Custom Engagements** (no public pricing):
- Workflow automation, reporting infrastructure, intake systems, document generation, email triage, AI-assisted internal tools, dashboards, operational backend
- For growing businesses (5–50 staff) that need more than a website
- CTA: "Schedule a Discovery Call"

## Core Metaphor
The **website** is the digital storefront — the front door customers walk through.
The **AI Workers** are the automations inside the storefront — capturing, following up, booking.
The **AI Automation Systems** are the operational backend — the back office that runs the business when nobody is watching.
We build all three layers, sized to where the client actually is.

## Core Message
We build the digital storefront, the AI workers inside it, and the operational systems that run the business behind both.

## Hero H1 (locked)
**"Smart Websites + AI Automation Systems For Growing Businesses."**

Subhead should bridge from websites into operational automation and intelligent business systems. Three draft subheads live in `/mnt/devdrive/projects/digital-ops-systems/02-website-rewrite/WEBSITE-REFRAME.md`.

## Brand Identity
- Header logo, metadata, schema `name`: **Digital Ops Systems** (primary brand)
- Footer brand h3: **Lee Scott** (current state is correct — do not change)
- Voice across the site: **"We"** (consultancy framing, not personal brand)

## Audience
- **Entry tier:** small service businesses, contractors, founders. Strong regional anchor across Louisiana and Texas.
- **Premium tier:** growing businesses (5–50 staff) anywhere with operational work to automate. Geography-agnostic but does not de-emphasize the regional roots.

## Regional Focus (do not remove)
HQ: Baton Rouge, LA. Service areas: Louisiana + Texas (Houston, Austin, San Antonio, Dallas-Fort Worth), plus remote nationwide. LocalBusiness schema, sitemap, footer service-areas block, and regional SEO investment are intentional and load-bearing. **Do not strip them in pursuit of "national" framing.**

## Revenue Goal
$100,000 within 12 months.

## Design Rules
- Simple HTML/CSS/JS. No frameworks unless explicitly asked.
- One consistent header, nav, footer, spacing, and visual style across all pages.
- Colors: navy `#0D1B2A`, gold `#C9A84C`, white.
- Font: Inter (Google Fonts).
- Modern, clear, business-focused, reassuring.
- Do not make it feel overly technical.

## Tone (evolved direction)
The site should feel **trustworthy, operational, intelligent, practical, systems-oriented, consultant-led** — not a generic agency.

**Favor these words:** smart, system, operational, workflow, automation, intake, follow-up, reporting, dashboard, infrastructure, backend, intelligent, capability, capture, respond, run, build, design, deliver.

**Avoid these words:** bespoke, transformative, leverage, unlock, synergy, ecosystem, holistic, paradigm, disrupt, "AI-powered" (table stakes now), revolutionize, next-level, game-changing.

## Messaging Rules
- **Outcomes first, mechanisms second.** What it does for the business comes before how it works.
- **Lead with the cost of doing nothing.** Name the pain; then show the system that closes it.
- **Show, don't claim.** The Projects page is where capability gets proven.
- **Two clear entry points.** Smart Website packages (front door) and AI Automation Systems (depth). Don't blur them on the same CTA.
- **Businesses don't care about AI by itself.** They care about more customers, less missed opportunity, faster follow-up, saved time.
- The website should communicate that we help a business website act like a working employee — and that we build the operational systems behind it too.

## File Rules

**Top-level pages (do not rename or remove without explicit instruction):**
- `index.html` — Home
- `about.html` — About Lee Scott
- `services.html` — Packages + Custom Engagements
- `projects.html` — Project listings
- `blog.html` — Blog index
- `contact.html` — Contact + lead form
- `thank-you.html`, `privacy-policy.html`, `terms-of-service.html` — supporting pages

**Case study URL pattern (scalable for future projects):**
- `/projects/<slug>/index.html`
- First case study: `/projects/automation-stack/index.html`
- Source-of-truth content for the Automation Stack case study lives at `/mnt/devdrive/projects/digital-ops-systems/03-automation-stack-case-study/AUTOMATION-STACK-CASE-STUDY.md` — adapt to the site's design system, do not rewrite from scratch.

**Assets:**
- `assets/css/styles.css`
- `assets/js/script.js`
- `assets/images/*`

**Do not add frameworks, build tools, package.json, node_modules, or unnecessary files unless explicitly asked.**

## What NOT to do

- Do not change the brand name, domain, or color system.
- Do not remove Blog or Projects from the navigation.
- Do not drop the regional/local SEO investment (LocalBusiness schema, Baton Rouge address, Louisiana + Texas service areas, sitemap, robots.txt, Google site verification meta).
- Do not switch the site voice from "we" to "I."
- Do not add a chat widget, popup, or newsletter modal.
- Do not add a team page (still a single-author practice).
- Do not run a visual redesign — the existing design system holds up.
- Do not frame the brand, the case study, or any project as a "Raspberry Pi business." The Pi is proof-of-concept infrastructure only. The AI Automation Stack architecture is **portable** across Raspberry Pi, mini PC, Mac, Linux server, Windows + Docker, VPS, cloud VM, and hybrid client environments.
- Do not publish pricing for the AI Automation Systems premium tier. The three Smart Website packages keep their public prices.
- Do not retire the "founding clients" offer on the homepage without explicit instruction — it's working.
- Do not break the LocalBusiness JSON-LD schema. Validate after any homepage edit.

## Source of truth for direction
The full Day 1 / website reframe plan lives at:
`/mnt/devdrive/projects/digital-ops-systems/02-website-rewrite/WEBSITE-REFRAME.md`

If anything in this file appears to conflict with that doc, the reframe doc wins — and this file should be updated to match before any further site edits.
