# A0 — CSS Conflict Surface Audit

*Read-only inventory. Source of truth for Step 4 consolidation.*
*Date: 2026-05-19. Branch: `feat/releases-page`. Scope: `landing/` only.*

---

## TL;DR

The site runs **two independent CSS systems that do not cross**:

- **System A:** `index.html` inline `<style>` block (1976 lines, lines 26–2002). Self-contained. **Loads no external stylesheets.** Defines Scholar / Wizard / LLMAGE token sets via `[data-theme="X"]`.
- **System B:** `style.css` (1952 lines) + `style-wizard.css` (571 lines), linked by every other page. Wizard-default tokens. No persona variants.

Step 4 is not a three-way merge. It is a two-system reconciliation under one canonical `loci.css`. **Step 5 (persona strip) lands first** simplifies this enormously: when index.html drops its triple-spanned markup and its `[data-theme]` blocks, System A collapses to a single Scholar-token tree, after which merging with System B is a `[data-theme]`-overlay decision, not a value reconciliation.

Recommendation: **run Step 5 before Step 4**, swapping the plan order. The audit makes this swap safe to call.

---

## 1. Stylesheet inventory

| Source | Lines | Has `:root`? | Theme variants? | Linked by |
|--------|-------|--------------|------------------|-----------|
| `style.css` | 1952 | yes, line 6 | no | 11 secondary pages |
| `style-wizard.css` | 571 | no | no | same 11 pages |
| `index.html` inline `<style>` | 1976 (lines 26–2002) | yes (3 theme variants) | yes: `[data-theme=scholar/wizard/llmage]` at lines 41, 76, 111 | itself only |
| `releases/releases.css` | 292 | no | no | `releases/index.html` |

**Total in-tree CSS: 4,791 lines across 4 sources.**

## 2. Per-page stylesheet dependency map

| Page | `style.css` | `style-wizard.css` | Inline `<style>` blocks | Inline `style=` count |
|------|:-:|:-:|:-:|:-:|
| `index.html` | — | — | 1 (1976 lines) | 15 |
| `about.html` | ✓ | ✓ | 0 | 7 |
| `comparison.html` | ✓ | ✓ | 1 | 5 |
| `download.html` | ✓ | ✓ | 1 | 9 |
| `guide.html` | ✓ | ✓ | 1 | 13 |
| `manifesto.html` | ✓ | ✓ | 1 | 7 |
| `privacy.html` | ✓ | ✓ | 0 | 8 |
| `roadmap.html` | ✓ | ✓ | **2** | 5 |
| `start.html` | ✓ | ✓ | 1 | 11 |
| `seed/index.html` | ✓ | ✓ | 1 | 6 |
| `seed/rendszerbontas.html` | ✓ | ✓ | **2** | (uncounted, dispatch-internal) |
| `seed/beagyazas.html` | ✓ | ✓ | **2** | (uncounted, dispatch-internal) |
| `zoku/index.html` | ✓ | ✓ | 0 | 10 |
| `releases/index.html` (new) | ✓ (relative) | — | 0 | 0 |

**Three files carry two inline `<style>` blocks:** `roadmap.html`, `seed/rendszerbontas.html`, `seed/beagyazas.html`. Worth reviewing whether those second blocks are intentional extensions or stale duplicates before Step 4 consolidates.

## 3. `position: fixed` rules — 16 total

The Plan agent estimated 7. Actual count: 16. Distribution:

| Source | Count | Locations |
|--------|-------|-----------|
| `index.html` inline | 6 | lines 160, 170, 187, 1229, 1284, 1539 |
| `style.css` | 4 | lines 73, 250, 717, 1922 |
| `style-wizard.css` | 3 | lines 184, 194, 524 |
| `start.html` inline | 1 | line 19 |
| `comparison.html` inline | 1 | line 68 |
| `seed/rendszerbontas.html` inline | 1 | line 577 |

**Cross-system collision risk:** zero. Index.html's 6 rules apply only to index.html (System A). The 7 rules in style.css + style-wizard.css apply only to secondary pages (System B). The 3 page-inline rules override their local System B sheet within one file.

Several of these `position: fixed` rules are modal/overlay related (z-index 1000) — not navigation. Worth tagging per rule in Step 4:

| Source:line | Likely role | Notes |
|-------------|-------------|-------|
| `style.css:73` | top nav | the canonical nav rule for System B |
| `style.css:250` | (TBD — needs context read in Step 4) | |
| `style.css:717` | inside `@media` (likely a modal or overlay) | |
| `style.css:1922` | inside `@media` (likely responsive nav override) | |
| `style-wizard.css:184/194/524` | wizard-skin overrides for System B nav | |
| `index.html:160/170/187` | top nav (System A) | one wins per `[data-theme]` |
| `index.html:1229/1284` | `z-index: 1000` overlays — modals | |
| `index.html:1539` | (TBD) | |
| `start.html:19` | scoped to entry-ritual overlay | known: from the stash@{0} entry ritual |
| `comparison.html:68` | (TBD) | |
| `seed/rendszerbontas.html:577` | (TBD — likely scroll-progress bar) | |

## 4. Token (`:root`) duplication

Only two sources define a `:root` block:
- `style.css:6` — Wizard-canonical token set (`--bg: #0d0d0e`, `--accent: #c87c2c`)
- `index.html:35`-ish — base `:root` (Scholar-canonical), with `[data-theme="scholar"]` at line 41, `[data-theme="wizard"]` at line 76, `[data-theme="llmage"]` at line 111

**Token collision pattern:** same variable names (`--bg`, `--accent`, `--text`, `--border`, `--serif`, `--mono`, `--radius`, `--nav-height`) used in both systems with **different values per system**. style-wizard.css and releases.css **inherit** from these without redefining `:root`.

After Step 5 strips persona variants from index.html, the index `:root` collapses to a single Scholar token set. The reconciliation then becomes:

```
loci.css :root  →  Scholar tokens (the public canonical voice)
loci.css [data-theme="wizard"]  →  pull from current style.css :root values
loci.css [data-theme="llmage"]  →  pull from current index.html lines 111-141
```

No cross-system value reconciliation needed — each system contributes its own theme tree under one roof.

## 5. Persona variant rules and markup

**CSS scope:** persona variant CSS lives **only in `index.html`** (lines 41-181 plus scattered `[data-theme]` rules through the inline block). No `[data-theme]` selectors in style.css, style-wizard.css, or releases.css.

**Markup scope:** `t-scholar` / `t-wizard` / `t-llmage` spans:

| File | Occurrences |
|------|-------------|
| `index.html` | **188** |
| all other pages | **0** |

**Step 5 is single-file work.** Strip the triple markup from index.html, drop the inline `[data-theme="wizard"]` and `[data-theme="llmage"]` CSS blocks, default to Scholar copy. Every other page is untouched.

## 6. `<nav>` trap status

The memory crystal **style.css nav trap** warned: `nav { position: fixed }` applies to every `<nav>` element on the page; in-page TOCs using `<nav>` would silently break.

**Audit result: zero victims.** Every HTML file has exactly one `<nav>` element (the top page navigation). No in-page TOCs use `<nav>`. The trap is theoretical, not active.

| Page | `<nav>` count |
|------|:-:|
| every page | 1 |

## 7. Cascade fight candidates

Because the two systems do not cross (index.html is self-contained, secondary pages never load index.html's CSS), cascade fights happen only within System B (style.css vs style-wizard.css vs per-page inline `<style>`).

Top selectors styled in 2+ places within System B (worth reading line-by-line during Step 4 merge):

- `nav`, `.nav-container`, `.nav-links`, `.nav-link`, `.logo`
- `body`, `main`, `footer`
- `a`, `h1`, `h2`, `h3`

A full per-selector diff (style.css vs style-wizard.css) is deferred to Step 4 implementation time — the audit's job is to flag the surface, not pre-resolve it.

## 8. Inline `style=` soup

Total inline `style="..."` attributes across landing pages: **~109**, concentrated in:

1. `index.html` (15) — mostly hero CTA + footer link colors
2. `guide.html` (13)
3. `start.html` (11)
4. `zoku/index.html` (10) — known: charter typography overrides
5. `download.html` (9)

Step 4 should fold these into `loci.css` utility classes where the same override repeats 3+ times. One-off inline styles can stay inline if cheaper.

## 9. Recommended consolidation order

The Plan workflow had **Step 5 (persona strip) after Step 4 (CSS consolidation)**. The audit recommends **swapping these two steps.**

### Revised order

1. **Step 3 (unchanged):** Extract shared `_nav.html` + `_footer.html` partials. Pure markup move, no CSS impact.
2. **Step 5 (moved earlier):** Strip the 188 persona spans + `[data-theme="wizard"]/[llmage]` CSS blocks from `index.html`. Single-file deletion PR. After this, System A collapses to ~600-800 lines of Scholar-canonical CSS (estimate, exact count after the strip).
3. **Step 4 (now lighter):** Consolidate three CSS sources into `loci.css`:
   - Take collapsed System A as Scholar canonical baseline
   - Fold style.css contents under `[data-theme="wizard"]` (its canonical voice)
   - Fold legacy LLMAGE block from old index.html under `[data-theme="llmage"]`
   - style-wizard.css merges into Wizard theme block
   - Result: one stylesheet, three theme layers, one canonical default.

### Why this order is safer

- After Step 5, the persona system collapses from a token-collision risk to a single source of truth per persona.
- Step 4's "decide which `--bg` wins on `about.html`" question disappears: about.html will read from `loci.css :root` (Scholar) unless `[data-theme="wizard"]` is explicitly set on the page.
- Each step's blast radius is constrained.

## 10. Open questions for Hux

1. **Secondary pages' default theme.** Today `about.html`, `manifesto.html`, etc. render with Wizard tokens (dark amber/charcoal) because they link `style.css` + `style-wizard.css` directly. After Step 4 merges everything under Scholar canonical, **should secondary pages default to Scholar (light/garden) for visual consistency with the canonical voice, or stay Wizard-dark by carrying `data-theme="wizard"` on `<html>`?** This is the call that decides whether the lean pass produces a unified-aesthetic site or preserves the current Scholar-home / Wizard-secondary split.

2. **The `roadmap.html` / `seed/rendszerbontas.html` / `seed/beagyazas.html` double inline `<style>` blocks.** Intentional? Or stale duplicates worth merging into one block during Step 4?

3. **Inline overlay rules** (`index.html:1229`, `index.html:1284`, `start.html:19`, `comparison.html:68`). Worth keeping as page-scoped during Step 4, or worth folding into `loci.css` as a `.modal-overlay` utility class?

---

*End of audit. Next: Step 3 (partials extraction) — independent of the swap above — and Hux's call on the three open questions.*
