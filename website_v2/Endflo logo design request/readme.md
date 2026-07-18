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
- `tokens/motion.css` — durations, easings, press-state values.
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
- **Backgrounds**: flat ink or flat paper only. No gradients, no photography treatments defined yet, no textures/patterns. Two scoped exceptions in product UI: the ink-raised card surface in dark mode (see Dark theme) and frosted sticky chrome (see Frosted chrome & scrims).
- **Icons**: none adopted yet beyond the brand symbol itself (see Iconography below).
- **Motion**: calm and functional — see the Motion section and `tokens/motion.css`. No bounce or overshoot anywhere.

## Dark theme — "ink mode"

Product UI (e.g. the Telegram miniapp) supports a dark theme, toggled via a `data-theme="dark"` attribute on the root element. It is the light theme mirrored, not a second palette:

- Page background stays pure ink `#0B0B0C`; text inverts to paper.
- Cards lift one step to **ink-raised** `#161614` — a *warm* dark gray in the same family as paper/mist. Never cool or blue-tinted neutrals.
- Muted/faint text mirror their light counterparts: `#A9A69B` / `#767369` (warm grays).
- Borders remain flat solid 1–1.5px lines (mist-dark `#2B2A26`, strong `#4D4B44`). Still no shadows or glows — elevation is expressed only by the one-step surface lift.
- Accents keep their hue and rise in lightness to pass contrast on ink: Flow Indigo → `#8DA2F2`, Signal Amber → `#E7A95F` (still a matched pair). Success `#53B88C`, danger `#D98577`. Roles unchanged — interactive states and alerts only, never the logo.
- **Soft fills**: an accent at 12% alpha on paper / ~20% alpha on ink (`--accent-soft`, `--success-soft`, `--danger-soft`) may sit behind accent-colored text or icons (tinted badges, secondary buttons). This is the only permitted translucent color use.
- Scope: **product UI only.** Brand/marketing surfaces (logo lockups, hero sections, print) remain strictly ink-or-paper; ink-raised never appears there.

Tokens live in `tokens/colors.css` under `:root[data-theme="dark"]` — semantic aliases (`--surface-card`, `--text-muted`, `--link`, …) remap automatically, so components built on aliases get dark mode for free.

## Motion

The product is "the invisible worker in the background" — motion follows the same temperament: quick, quiet, and always in service of state feedback, never decoration. Tokens in `tokens/motion.css`.

- **Durations**: 200ms for micro changes (hover, press, color/border/opacity), 300ms for structural changes (tab fades, bottom sheets, expand/collapse). 300ms is the ceiling — nothing animates longer, except an ambient loading pulse.
- **Easings**: `cubic-bezier(0.4, 0, 0.2, 1)` as the standard curve; `cubic-bezier(0.32, 0.72, 0, 1)` only for large surfaces entering (bottom sheets). Plain `ease` is acceptable for simple fades. **No bounce, spring, or overshoot curves, ever** — an overshoot is an exclamation point.
- **Press state**: 0.75 opacity, optionally with a 0.95–0.98 scale-down (subtler on small controls). This is the one brand-defined interaction state.
- **Entry**: elements may fade in with at most a 6px translate — motion should be felt, not watched. Bottom sheets slide from the edge they belong to.
- **Loading**: skeleton placeholders pulse opacity (1 → 0.5, ~1.5s loop). No spinners, no shimmer gradients.
- Respect `prefers-reduced-motion`: reduce structural animations to plain fades or nothing.

## Frosted chrome & scrims

Two scoped exceptions to the flat-surfaces rule, both product-UI-only and both defined as tokens (`--surface-chrome`, `--scrim` in `tokens/colors.css`):

- **Sticky chrome** (tab bars, headers that float over scrolling content): page background at 92% opacity with a 12px backdrop blur. This is the only blur in the system — cards, sheets, and marketing surfaces stay flat and fully opaque. Where `backdrop-filter` is unsupported, it degrades to the flat page background.
- **Modal scrim**: ink at 55% opacity behind sheets/dialogs, in both themes. Never blurred.

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
