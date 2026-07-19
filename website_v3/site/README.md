# Endflo website — v3 (canonical)

**This is the current / canonical Endflo marketing site.** It supersedes `../../website_v2/`
(kept as history) and the original `../../website/`. Built from `endflo-website-copy.md`,
`endflo-subpages-copy.md`, and the brand system in `../../website_v2/Endflo logo design request/`
(the shared brand kit, now updated to this terracotta direction), then moved
toward the coffee-tech.com direction: one warm signature colour and real product elements in
place of abstract SVG diagrams.

## What changed from v2

- **Single terracotta accent** (`--terra #C25B3D` / `--terra-deep #9E4429`) replaces the old
  indigo + amber split; `--paper` warmed toward cream. One token swap reskins every page.
- **Real product elements** replace the abstract "flow" SVGs: a live WhatsApp/Telegram chat,
  Google-Sheets / Data-Table windows, a KPI dashboard, PDF + screenshot chips, Jotform forms,
  and floating result cards. Component library lives at the bottom of `css/site.css`.
- **De-carded homepage**: "The problem" and "Why Endflo" are numbered editorial columns;
  "What we automate" is alternating real-element showcases + a slim divided link list.

## Pages

- `index.html` — landing (hero, problem, what Endflo does, how it works, what we automate, who we work with, why Endflo, closing CTA)
- `services.html` — six service categories, each a problem → fix → result flow with a real element
- `how-it-works.html` — five-step timeline (its process diagrams are intentionally kept abstract)
- `faq.html` — accordion FAQ

## Structure

- `css/site.css` — brand tokens (terracotta/ink/cream, Manrope/Sora/Space Mono) + all site styles + the real-element component library
- `js/site.js` — GSAP ScrollTrigger animations, Lucide icons, nav + FAQ behaviour, real-element loops
- `assets/` — logo SVGs from the brand kit

## Dependencies (CDN, no build step)

- GSAP 3.12.5 (+ ScrollTrigger, MotionPathPlugin)
- Lucide 0.469.0 — UI icons
- Google Fonts — Manrope, Sora, Space Mono

Just open `index.html` in a browser, or serve the folder with any static server.

## Motion system

- **Real elements** (`[data-real]` + the `[data-hero-stage]` phone) each run a looping
  assemble → hold → fade timeline: frames rise, chat bubbles type in on a slow readable beat,
  fresh table rows pulse terracotta. Each loop **plays only while the element is at least half
  in view** (`ScrollTrigger` `center bottom` → `center top`) and pauses off-screen.
- How-it-works page: vertical timeline rail fills with scroll, dots activate as you pass them.
- All content is fully visible without JavaScript; `prefers-reduced-motion` disables the animations.
- Note: don't GSAP-animate `.btn` elements directly — they carry CSS transitions on opacity/transform
  which conflict with GSAP from-tweens. Animate a wrapper instead.

## Placeholders to replace before launch

- Footer contact email is `mleeweirong@gmail.com` (fallback only — primary CTAs link to WhatsApp at `wa.me/6581041890`, site-wide)
- WhatsApp number `6581041890` in all CTA links — swap once a dedicated business number is set up
- Project timeline "two to four weeks" on `how-it-works.html` (copy doc had `[X to X weeks]`)
- The pricing answer on `faq.html` (copy doc left it bracketed; a neutral "quote after mapping session" answer is in place)
- Service categories are the illustrative ones from the copy doc — swap once the real service list is confirmed
- The real-element demos use sample data (Acme, Nimbus Co, invoice #1042, etc.) — swap for real cases if desired
