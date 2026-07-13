# Endflo website

Static 4-page marketing site built from `endflo-website-copy.md`, `endflo-subpages-copy.md`,
and the brand system in `../Endflo logo design request/`.

## Pages

- `index.html` — landing page (hero, problem, what Endflo does, how it works, what we automate, who we work with, why Endflo, closing CTA)
- `services.html` — the five service categories, each as a problem → fix → result flow
- `how-it-works.html` — five-step timeline, what we need from you, timeline note
- `faq.html` — accordion FAQ

## Structure

- `css/site.css` — brand tokens (ink/paper palette, Manrope/Sora/Space Mono) + all site styles
- `js/site.js` — GSAP ScrollTrigger animations, Lucide icon init, nav + FAQ accordion behaviour
- `assets/` — logo SVGs copied from the brand kit

## Dependencies (CDN, no build step)

- GSAP 3.12.5 (+ ScrollTrigger, MotionPathPlugin) — scroll-driven "flow" visualizations
- Lucide 0.469.0 — UI icons
- Google Fonts — Manrope, Sora, Space Mono

Just open `index.html` in a browser, or serve the folder with any static server.

## The "flow" motion system

- Hero: the brand's tangled-wave-to-arrow line draws itself on load; an amber pulse travels it on loop
- Between landing sections: vertical connector lines draw with scroll — tangled after "the problem",
  settling after "what Endflo does", straight with an arrowhead before the closing sections
- "How it works" on the landing page: pinned section, progress line fills as steps activate (desktop only)
- How-it-works page: vertical timeline rail fills with scroll, dots activate as you pass them
- All content is fully visible without JavaScript; `prefers-reduced-motion` disables the animations
- Note: don't GSAP-animate `.btn` elements directly — they carry CSS transitions on opacity/transform
  which conflict with GSAP from-tweens. Animate a wrapper instead.

## Placeholders to replace before launch

- `hello@endflo.com` — all CTA/mailto links and the footer (site-wide)
- Project timeline "two to four weeks" on `how-it-works.html` (copy doc had `[X to X weeks]`)
- The pricing answer on `faq.html` (copy doc left it bracketed; a neutral "quote after mapping session" answer is in place)
- Service categories are the illustrative ones from the copy doc — swap once the real service list is confirmed
