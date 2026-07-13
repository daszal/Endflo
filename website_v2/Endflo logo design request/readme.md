# Endflo Design System

Brand identity system for **Endflo** — a firm automating workflows end to end: turning messy, manual processes into streamlined, invisible automation running quietly in the background.

This system was built directly in this project (no external codebase, Figma file, or existing brand was supplied) — the logo, palette, and type system below are the source of truth going forward.

## Brand concept

The logo is a single continuous vector: a stroke that ripples (tangled work) under "e", rises to literally **become the letter "n"** as a crest of the wave, then flattens into a clean baseline under "flo" and exits as a forward arrow. One shape carries three ideas at once: *end-to-end* (start node → arrow), *messy → organized* (turbulent wave → flat line), and the wordmark itself.

## Index

- `styles.css` — root stylesheet, import this one file. Pulls in all tokens + web fonts.
- `tokens/colors.css` — ink/paper/mist neutrals + two accents (semantic aliases included).
- `tokens/typography.css` — font stacks (Manrope / Sora / Space Mono) + weight/tracking tokens.
- `tokens/spacing.css` — spacing scale + corner radii.
- `assets/logo/` — SVG logo files (ink + paper lockups, standalone symbol, app-icon tile).
- `components/core/` — Button, Badge, Card React primitives.
- `guidelines/` — specimen cards for the Design System tab (Colors, Type, Brand groups).
- `SKILL.md` — portable skill file for Claude Code / other agent contexts.

## Content fundamentals

- Name is written lowercase in the logo (**endflo**) and title case in prose (**Endflo**).
- Tone: calm, precise, quietly confident — the product is "the invisible worker in the background," so copy should feel unobtrusive and clear rather than hyped. Avoid exclamation points and hustle-culture language.
- No emoji.
- Prefer verbs over adjectives: "automate," "streamline," "run" over "seamless," "powerful," "revolutionary."

## Visual foundations

- **Color**: strictly monochrome (ink #0B0B0C / paper #F6F5F0) for the logo and brand surfaces, always. Two accents — Flow Indigo and Signal Amber — share the same lightness and chroma and differ only in hue; they're reserved for interactive UI states (links, active tabs, alerts), never applied to the logo itself.
- **Type**: Manrope 800 is reserved for the wordmark and hero display moments only, set at tight tracking (-4 to -5%). Sora is the workhorse for all headings, UI and body copy. Space Mono is used only for short technical labels/captions, always uppercase with wide tracking when used as a label.
- **Shape language**: pill buttons, rounded-rectangle cards (18–28px radius), no colored left-border cards, no drop shadows on cards or the logo. Borders are a flat 1–1.5px mist line, not a shadow.
- **Backgrounds**: flat ink or flat paper only. No gradients, no photography treatments defined yet, no textures/patterns.
- **Icons**: none adopted yet beyond the brand symbol itself (see Iconography below).
- **Motion**: not yet defined beyond simple opacity-based hover/press states on buttons (0.75 opacity on press). No easing/bounce system specified yet — flag before inventing one.

## Iconography

No icon set has been provided or built. The only "icon" in the system is the Endflo symbol itself (`assets/logo/endflo-icon-ink.svg` / `-paper.svg`), used for favicons and app-icon tiles. If the product needs a general UI icon set (nav, actions, status), pick a CDN set with a similarly clean, single-weight geometric feel (e.g. a 1.5–2px stroke line-icon set) and document the substitution here before using it broadly.

## Logo usage

See `guidelines/logo-*.card.html` for full visual specimens. Key rules:
- Clearspace on all sides = the diameter of the start node.
- Minimum size: 130px / 28mm wide for the full lockup; 24px / 6mm for the symbol alone.
- Never recolor the wave separately from the wordmark, never distort/stretch, never add shadows or glows, never place on low-contrast backgrounds.
- The wordmark text is live type (Manrope), not outlined — any context using the SVG assets directly must load the Manrope webfont, or request outlined/PNG exports.

## Intentional additions

No component library or codebase was provided, so `components/core/` (Button, Badge, Card) is a minimal, intentionally small starter set authored from the visual foundations above — not sourced from an existing product. Expand it as real product screens are designed.
