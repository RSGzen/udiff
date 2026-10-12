# UDiff — Frontend Revamp Plan

> **Created:** 12 Oct 2026 · **Updated:** 13 Oct 2026 (M9.0/M9.1 landed; M10 scope revised)
> **Owner:** assistant (mentor) + user (junior systems designer)
> **Status legend:** `Todo` · `In progress` · `Done` · `Deferred`
> **Related files:** [`Tech Stack.md`](Tech%20Stack.md) (web side) · [`Milestones and Logs.md`](Milestones%20and%20Logs.md) (M6, M9–M11)

---

## 1. Why this plan exists

The UDiff web app works, but the UI reads as a generic "AI-generated dashboard" and
looks dated. The cause is **structural, not cosmetic**: two styling systems coexist.

- A real token layer lives in `src/app/globals.css` (`oklch`, shadcn `--background/--card/--primary`…).
- Almost every component **ignores it** and hardcodes Tailwind colors
  (`bg-slate-900 border-slate-800 text-blue-400`, cyan accents, chart hex `#3b82f6`).

On top of that: gradient text on headings, mono "bracket" tooltips (`[ name : 42% ]`),
`transition-all` everywhere, leftover `Create Next App` metadata, **fake dark mode**
(`layout.tsx` never applies `.dark`, so it is only dark because everything is hardcoded dark),
and a fixed `w-64` sidebar + `pl-64` content that breaks on mobile.

This plan fixes that in three tiers. **Agreed direction:** Tier 1 is the baseline
(re-skin), Tier 2 is a later restructure. No new UI library — the problem is tokens
and restraint, not missing components.

---

## 2. Design direction (the reference)

| Purpose | Reference | Why |
|---|---|---|
| Visual language | **Linear + Vercel Geist** | Neutral near-black, one accent, hairline borders, tight type, no gradients — the "serious tool" look |
| Dashboard composition | **Tremor** (`tremor.so`) | Built on **Recharts + Radix + Tailwind** — UDiff's exact stack. Use it for KPI cards / chart patterns; adopt by copy-paste, no dependency required |
| Craft rules | Emil Kowalski design-engineering skills | Installed in the agent's global skills (`emil-design-eng`, `review-animations`, `animation-performance`, `apple-design`, `mobile-native`, `break-ui`) |

**The goal is restraint + one accent + honest data** — not more decoration.

---

## 3. Design rules (the style guide)

Single source of truth = tokens in `src/app/globals.css`. **No component may hardcode a
palette color** (only the theme file declares colors).

### Color
- **Dark-first.** Surface near-black, card one step lighter, hairline borders (`border-border`, ~10% white).
- **One accent** = `--primary`. Accent only for emphasis / active state. Everything else neutral.
- **No gradient text.** **No second accent** (drop cyan; keep a single blue/indigo if a brand hue is wanted).

### Typography
- **Geist Sans** for prose; **Geist Mono + `tabular-nums` for every number** (metrics, %, salary).
- Fixed scale: `12 / 14 / 16 / 20 / 24 / 32`. Use weight for hierarchy, not runaway size.

### Space, radius, motion
- 4px base spacing scale.
- Radius: controls `rounded-md`, containers `rounded-lg`, pills `rounded-full`.
- Motion = feedback only. `--ease-out: cubic-bezier(0.23, 1, 0.32, 1)`; UI duration **120–200ms**;
  press = `scale(0.97)`; honour `prefers-reduced-motion`; transition **exact properties, never `all`**.

---

## 4. Relationship to other milestones

- **M6 (Web cleanup)** = *code hygiene* (`as any`, `@ts-ignore`, lint, dead assets).
  Intended to run before M9, but **M9.0/M9.1 landed first** (13 Oct) because the site did not render
  at all against the v3 schema. Run M6 before/with **M9.2** to get `npm run lint` green.
- **M9 / M10 / M11** = this plan (*design*).
- Backlog item *"UI: more modern design…"* is now tracked here (see Milestones §4).
- **Locked decisions:** scope = re-skin **+ core `UDiff.md` §4 views**; **no map dependency**
  (states → ranked bar, companies → ranked list/treemap); **shell country switcher + `/compare` view**;
  salary stays **min–max monthly nominal MYR** with a **PPP toggle** in M10.

---

## 5. Tier 0 — Data layer + de-slop (`M9`) `In progress`

**Goal:** make the app render the v3 data and kill the obvious tells. **No layout changes.**
**~1–2 days, low risk.** **New dependencies:** none.

- **M9.0 — Data layer (schema v3)** `Done (13 Oct)` — rewrote `src/types/index.ts`; added
  `src/lib/data.ts` (single data gateway); repointed `page.tsx` + `curriculum/page.tsx`; salary card
  reads `salary_estimate`; dashboard country switcher; `@ts-ignore`s removed. *Also: header wrap fix
  (dropped `" Engineer"`) + `SkillChart` label truncation.*
- **M9.1 — Dark tokens + metadata** `Done (13 Oct)` — `className="dark"` +
  `suppressHydrationWarning` on `<html>`; real title/description.
- **M9.2 — Token swap** `In progress` — replace hardcoded `slate-*` / `blue-*` / cyan / hex with
  semantic tokens in: `src/app/page.tsx`, `src/components/Sidebar.tsx`,
  `src/components/dashboard/MetricCard.tsx`, `SkillChart.tsx`, `ContextTreemap.tsx`,
  `src/app/curriculum/page.tsx`, `src/app/roadmap/page.tsx`.
- **M9.3 — Remove gradient text** `Todo` — `Sidebar.tsx` (logo), `curriculum/page.tsx`, `roadmap/page.tsx`.
- **M9.4 — Motion** `Todo` — replace `transition-all` with explicit properties (`ui/button.tsx`,
  `app/page.tsx`, `roadmap/page.tsx`, `ui/progress.tsx`); remove inline `transition: 'all 0.3s ease'`
  (`SkillChart.tsx`, `ContextTreemap.tsx`); shorten `animate-in … duration-500` → ~180ms `ease-out`
  (`curriculum/page.tsx`).
- **M9.5 — Press feedback + charts + honesty** `Todo` — `active:scale-[0.97]`; non-top bars visible;
  tooltips use `tabular-nums` and drop the bracket style; honest salary label; radius consistency in
  the treemap.

**Done when:** no palette hardcoding or `transition-all` remains in components (only in `globals.css`);
`npm run build` + `npx tsc --noEmit` pass; layout is visually unchanged.

---

## 6. Tier 1 — Re-skin + core data views (`M10`) `Todo`

**Goal:** a consistent, token-driven, responsive app that renders the **core** `UDiff.md` §4 data
surface across MY/SG/ID. **~4–7 days, medium risk.**

**Shell & system**
- [ ] **Theming:** `next-themes` `ThemeProvider` + `suppressHydrationWarning`; `.dark` on `<html>`
      (dark-only is acceptable).
- [ ] **Shared `AppShell`** (`src/components/AppShell.tsx`): sidebar + content grid used by **all** routes.
      Delete the `pl-64` hack (`page.tsx`) and the per-page "Back to Dashboard" nav.
- [ ] **Collapsible sidebar:** icon rail on desktop (collapse toggle) + `Sheet` drawer below `lg`.
- [ ] **Country switcher in the shell** (MY/SG/ID) — scopes the dashboard (moves the temporary
      switcher out of the header).
- [ ] **Type system:** Geist Sans + Geist Mono; `tabular-nums` on metrics.
- [ ] **Motion tokens:** `--ease-out` / `--ease-in-out` + duration scale + `prefers-reduced-motion`.
- [ ] **Component polish:** `Card`, `Badge`, `Tabs`, `Select`, `MetricCard` themed through tokens;
      hover gated by `@media (hover: hover) and (pointer: fine)`.
- [ ] **Charts:** colours from `--chart-*`; one shared `ChartTooltip`; remove per-cell inline transitions.
- [ ] **Persist roadmap progress** to `localStorage`; **A11y** pass (focus-visible, `aria-label`, heading order).

**Core `UDiff.md` §4 views to build** (all Recharts; **no map dependency**)

| §4 view | Chart |
|---|---|
| Hard skills / technical context | bar / treemap *(exists)* |
| Soft skills | chips / bar |
| Job distribution by role | bar |
| Experience split | stacked bar |
| Jobs by state | ranked bar (only MY has >1 state) |
| Top companies | ranked list/bar + placeholders toggle |
| Salary bands | floating range bar (`min→max`), nominal monthly MYR + **PPP toggle** |
| Country skill / salary deltas | diverging bars (`/compare` view) |

**Deferred this pass:** posting recency (needs a pipeline aggregate first); observed-salary scatter
(MY-only, country-level only).

**Done when:** every route shares one responsive shell; every **core** §4 view renders for MY/SG/ID;
`npm run build` + `npm run lint` pass; charts use tokens; sidebar works at 360px.

---

## 7. Tier 2 — Restructure `Deferred`

**Goal:** make UDiff self-explanatory to a stranger and portfolio-ready. **~1.5–3 weeks, medium-high risk.**

- [ ] **Landing / About page** — what UDiff is, who it is for, the pipeline in one diagram, data-source honesty.
- [ ] **IA + routes:** `/` (landing), `/dashboard`, `/roadmap`, `/curriculum`, `/methodology`.
- [ ] Optional **`/dashboard/[role]`** detail route (replaces client-state role switching).
- [ ] **Mobile drawer + full responsive** pass.
- [ ] **Methodology / Data page:** sources, sample size, known limits (salary null, keyword matching).
- [ ] **Chart redesign:** dot plot / lollipop for skill demand; better treemap labelling.
- [ ] **Motion polish:** page transitions, stagger; add `motion` (Framer) only where springs genuinely help.
- [ ] **Full a11y + performance audit.**

**Done when:** a reviewer understands the product without context and the app passes an a11y audit.

---

## 8. Effort summary

| Tier | Effort | Risk | Milestone | New deps |
|---|---|---|---|---|
| 0 — De-slop | ~1–2 days | Very low | M9 | none |
| 1 — Re-skin + core views | ~4–7 days | Medium | M10 | `next-themes` (optional) |
| 2 — Restructure | ~1.5–3 weeks | Medium-high | M11 | `motion` (optional) |

---

## 9. Guardrails for agents

- **Do not add a new UI library.** The fix is tokens + restraint. Tier 0 = **zero** new deps.
- New dependencies require an explicit justification in the work log.
- Every tier must leave `npm run build` and `npx tsc --noEmit` passing (and `npm run lint` once M6 lands).
- **Keep the JSON data contract unchanged** (see `Tech Stack.md` §3).
- Non-negotiables: one accent · no gradient text · no `transition-all` · honour `prefers-reduced-motion`.
- Respect the staged plan: land Tier 0 before Tier 1; do not start Tier 2 until Tier 1 ships.

---

## Appendix A — Audit findings (before → after)

Source: full read of `src/` on 12 Oct 2026.

| Before | After | Why |
|---|---|---|
| Two palettes: tokens in `globals.css:49` unused; components hardcode `slate-950/900/800` | Semantic tokens only (`bg-background`, `bg-card`, `border-border`, `text-muted-foreground`) | One source of truth; fixable contrast/theming |
| `layout.tsx:15` title `"Create Next App"` | Real title / description + OG metadata | Visible amateur tell |
| Gradient text: `Sidebar.tsx:41`, `curriculum/page.tsx:101`, `roadmap/page.tsx:77` | Solid `text-foreground`, weight for hierarchy | Gradient text is the #1 "AI" signal; poor contrast |
| Blue **+** cyan accents; hex `#3b82f6`/`#22d3ee` (`SkillChart.tsx:84`, `ContextTreemap.tsx:33`) | One accent token; neutral scale otherwise | Restraint reads as a serious tool |
| Fake dark mode; `.dark` never applied (`globals.css:49` light) | `className="dark"` (Tier 0) → `next-themes` (Tier 1) | Current state breaks on a light OS / toggle |
| `transition-all` (`button.tsx:8`, `page.tsx:65`, `roadmap/page.tsx:106`, `progress.tsx:24`) | `transition: transform 160ms ease-out` (exact props) | `all` animates layout + paint |
| Inline `transition: 'all 0.3s ease'` (`SkillChart.tsx:99`, `ContextTreemap.tsx:67`) | Remove; transition `fill`/`opacity` only | Fires on every SVG re-render |
| `animate-in … duration-500` (`curriculum/page.tsx:177`) | ~180ms `ease-out`, enter-only | 500ms feels sluggish (< 300ms rule) |
| No `:active` press feedback | `active:scale-[0.97]` | Buttons must feel responsive |
| Bar `#1e293b` on `#0f172a` bg | Neutral track + single accent; value at bar end | Near-invisible, low contrast |
| Bracket mono tooltips `[ name : value% ]` (`SkillChart.tsx:37`, `ContextTreemap.tsx:147`) | Standard tooltip, `tabular-nums` value | Gimmick; numbers need tabular figures |
| `✓` text glyph (`roadmap/page.tsx:111`) | `<Check/>` lucide icon | Consistent iconography |
| Mixed radius + `rx={6}` (`ContextTreemap.tsx:69`) | One radius scale | Visual rhythm |
| Fixed `w-64` sidebar + `pl-64` (`Sidebar.tsx:37`, `page.tsx:65`) | Responsive shell / drawer | Broken below ~1024px |
| Two nav patterns (sidebar vs "Back to Dashboard") | One persistent `AppShell` | Route jumps feel like leaving the app |
| Salary `N/A` but subtitle "Monthly Estimate (MYR)" (`page.tsx:95`) | Honest "not reported in source data" | Salary is 100% null in the dataset |
| README claims roadmap progress persisted; it is in-memory (`roadmap/page.tsx:23`) | `localStorage` (Tier 1) | Do not mislead |

## Appendix B — File map (what each tier touches)

| Concern | Files |
|---|---|
| Theme / tokens | `src/app/globals.css`, `src/app/layout.tsx` |
| Shell / navigation | `src/components/Sidebar.tsx`, **new** `src/components/AppShell.tsx` |
| Dashboard | `src/app/page.tsx`, `src/components/dashboard/*.tsx` |
| Roadmap | `src/app/roadmap/page.tsx` |
| Curriculum | `src/app/curriculum/page.tsx` |
| Primitives | `src/components/ui/*.tsx` |
| Types | `src/types/index.ts` |
| Data (do not change) | `src/data/*.json` |
