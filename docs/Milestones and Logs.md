# UDiff — Milestones & Logs

> **IMPORTANT:** This project **is in need of polishing/rework.** It is a working prototype assembled across a school year, partly AI-assisted. The pipeline scripts are **old experimental code**; the merged repo structure and the `docs/` folder are **new** (11 Oct 2026).
>
> **Status legend:** `Done` · `In progress` · `Pending` · `Blocked`

---

## 1. Repository status — old vs. new (read this first)

> **Snapshot dated 11 Oct 2026.** This section is the pre-polish baseline. Most of the
> "old" items below have since been refactored or removed (M0–M7, all done); see the
> milestone results in §2 and the work log in §3 for the current state.

**Newly written on 11 Oct 2026 (the only "new" content):**

- `docs/` — this file, `UDiff.md`, `Tech Stack.md`
- The **merged repo structure** (pipeline relocated under `pipeline/`, docs added, README rewritten)
- The **pre-merge safety commit** in the original `RSGzen/UDiff` repo

**Old / experimental content carried over (needs polish, refactor, or retirement):**

| Path | Origin | State |
|---|---|---|
| `pipeline/src/scraper.py` | old `jobstreet_scraper/` | Legacy prototype; hard-coded selectors, `os.getcwd()` paths, not headless |
| `pipeline/src/scraper_details.py` | old `jobstreet_scraper/` | Legacy; same issues |
| `pipeline/src/processor.py` | old `info_extract/` | Legacy; prompt-based LLM extraction, `os.getcwd()` paths |
| `pipeline/src/analyzer.py` | old `analyzer/` | Legacy; keyword-heuristic categorization |
| `pipeline/src/inspect_others.py` | old `analyzer/` | Dev utility; imports `analyzer` from cwd |
| `pipeline/src/curriculum_generation.py` | old `curriculum_match/` | Legacy; LLM-generated course names |
| `pipeline/src/pipeline.py` | old `pipelining/` | Legacy orchestrator; **omits the curriculum step** |
| `pipeline/requirements.txt` | old root | **Incomplete** — missing `playwright`, `beautifulsoup4`, `ollama` |
| `pipeline/legacy/dashboard.py` | old root | **Retired** Streamlit dashboard |
| `pipeline/legacy/Dockerfile`, `pipeline/legacy/.streamlit/` | old root | Belonged to the retired Streamlit dashboard |
| `pipeline/data/**` | old repos | Point-in-time scraped data (raw CSV kept as fallback) |
| `web/src/**`, `web/public/**` | old `udiff-web` | Mostly AI-assisted front-end; works but needs cleanup |
| `web/README.md` | old | **Stale** (wrong framework versions + clone URL) — now rewritten |

**Data artifacts:** the raw CSVs (`job_links.csv`, `job_details_full.csv`) and interim JSON are committed so the pipeline can be re-run from an existing dataset if re-scraping fails.

---

## 2. Milestones (polish plan)

### M0 — Triage & baseline `Done (12 Oct 2026)`
- Confirm `web`: `npm install`, `npm run build`, `npm run lint` all pass; record current output.
- Map every script's inputs/outputs and current path assumptions.
- Decide keep/drop for `legacy/` (currently retired, not deleted).
- **Result:** `next build` and `tsc --noEmit` pass; `npm run lint` fails (15 errors); pipeline un-runnable (dead post-merge paths).
- **Done when:** a written baseline exists and the web app builds locally. ✅

### M1 — Publish the pipeline `Done (11 Oct 2026)`
- The entire pipeline was previously **unpushed** (only `dashboard.py` + one JSON were public).
- Committed and pushed everything in the original repo; merged into this repo under `pipeline/`.
- **Done when:** all pipeline scripts are visible on GitHub. ✅

### M2 — Restructure into a clean package `Done (12 Oct 2026)`
- Introduce a central `config.py` (queries, page depth, model name, paths).
- Replace every `os.getcwd()` path with `pathlib` paths resolved **relative to the repo root**.
- Group code as a proper module (`pipeline/src/udiff/…`) or keep a flat `src/` with a clear `__init__.py`.
- **Result:** `pipeline/src/config.py` is the single source of truth; all six scripts resolve paths from `Path(__file__)`. `pipeline.py`'s dead `SCRIPTS` folder names are handled under M3.
- **Done when:** scripts run identically from the repo root regardless of cwd. ✅

### M3 — Single robust entrypoint `Done (12 Oct 2026)`
- Extend `pipeline/src/pipeline.py` to include **step 5 (curriculum generation)** and expose step selection flags.
- Add resume/checkpointing, retries, and clear failure messages.
- **Result:** 4-step orchestrator (`fetch → extract → analyze → curriculum`) with `--steps`, `--skip`, `--skip-scrape`, `--dry-run`, `--list`; logs to `pipeline/pipeline_log.log`. Resume/checkpointing deferred (steps are re-runnable).
- **Done when:** one command runs the full pipeline (or a chosen subset) and fails gracefully. ✅

### M4 — Documentation `Done (12 Oct 2026)`
- ✅ `docs/UDiff.md`, `docs/Tech Stack.md`, this file.
- ✅ `pipeline/requirements.txt` trimmed to `pandas` + `ollama` (fetch uses the stdlib).
- ✅ Module docstrings + a short `pipeline/README.md`.
- ✅ Architecture reflected in `README.md` and the mermaid diagram in `docs/UDiff.md`.

### M5 — Data refresh `Done (data) 13 Oct 2026`
- JobStreet scraping is disallowed by its robots.txt (`Disallow: */job/`, `*?`) and ToS cl. 7.d/9.b, so the scrapers were retired and replaced by the **JSearch API** (`fetch_jobs.py`, OpenWebNinja).
- First MY fetch (12 Oct): **935 Malaysian postings** (salary 100% null). Raw ad text is gitignored.
- Superseded by the M5.7 multi-country fetch (13 Oct): **2,300 postings** (MY/SG/ID), LLM-extracted and aggregated → `gap_report.json` / `skill_class.json` regenerated.
- **Still to do (not pipeline):** the live site must be redeployed with the new data (schema consumption landed in **M9.0**; redeploy pending M6).
- **Done when:** the live site reflects freshly generated data. ⬜ *(data delivered; deploy pending M6)*

### M5.5 — Salary estimates `Done (pipeline) 13 Oct 2026`
- **Problem:** `search-v2` returns no salary, so the posting-derived `salary` in `gap_report.json` is `0` / `N/A`.
- **Approach:** add a **separate, attributed** market estimate — never overwrite `salary` (doing so would change what the metric means).
- ✅ Added `pipeline/src/salary_estimate.py` as the `salary` orchestrator step. It calls `/estimated-salary` per category (representative title via `CATEGORY_TITLES`) × level (years bucket via `LEVEL_YEARS`: `All→ALL`, `Junior→ONE_TO_THREE`, `Mid→FOUR_TO_SIX`, `Senior→SEVEN_TO_NINE`), `location_type=COUNTRY`. Under M5.7 this runs **per country** (`location` = "Malaysia" / "Singapore" / "Indonesia").
- Stored as `salary_estimate {min, median, max, currency, period, source, confidence, sample_size, fetched_at}` inside each category→level block; `salary` is untouched. Reuses `fetch_jobs.api_url` / `api_get`. M5.7 adds `nominal_myr` and `ppp_myr` (`{min,median,max}`) via `ppp.json`/`fx.json`.
- **Reliability guard:** keep only `confidence ∈ {HIGH, VERY_HIGH}` with `sample_size ≥ 3`; a `--prune` flag drops stored estimates that fail the guard **without an API call**.
- **Run (13 Oct, per country):** MY 53 / SG 55 / ID 43 blocks estimated; noisy outliers (e.g. a LOW-confidence `Solutions Engineer` at 520M IDR) dropped by the guard.
- ⬜ **Web task (M6/design):** render the estimate as a labelled **"market estimate (Glassdoor via JSearch)"** card alongside the honest `N/A`, surfacing `confidence` / `sample_size`. Pipeline side is done.
- **Done when:** the dashboard shows the labelled market estimate alongside the observed-pay `N/A`. ⬜ (web pending — M6)

### M5.6 — Data enrichment (P1–P9) `Done (pipeline) 13 Oct 2026`
- **Goal:** fill the weak/empty data sections (see `docs/UDiff.md` §4 "Data") so the sections are real *before* scaling to SEA. Works off the **existing MY outputs**; only **P8** needs a re-fetch.
- **Tasks:**
  - **P1 — Salary from text:** regex `(?:RM|MYR)\s?[\d,]{3,}` over `description` → heuristic `salary_text` per posting (82/935 MY ads matched). Clearly label it as text-mined, not authoritative.
  - **P2 — States section:** emit `states` (jobs by normalised state) into `gap_report.json` (the data already exists in `job_analysis_final.json`).
  - **P3 — Category floor:** lower the analyzer's `<3` to `<2` and add a `low_sample` flag so `IT Support` (2) and `Project & Sales Engineering` (1) appear instead of being dropped.
  - **P4 — Experience:** keep `Unknown` visible; suppress levels below a min count with an `n=` note.
  - **P5 — Salary fallback:** when a level has no `salary_estimate`, fall back to the `All` bucket, labelled "broad estimate".
  - **P6 — Curriculum robustness:** retry once + regex-salvage the JSON array on parse failure (removes the ~13% empty subject lists).
  - **P7 — Soft skills + breadth:** store soft-skill counts/percentages; add a `distinct_skills` count per category.
  - **P8 — Recency:** map `job_posted_at_datetime_utc` → a `posted_at` column + a "% posted in last 30 days" metric. **The column does not exist in the current CSV, so this lands with the M5.7 re-fetch.**
  - **P9 — Companies:** `top_companies: [{name, count, kind}]` per category, where `kind ∈ {company, placeholder}`. Placeholder = `confidential` + a recruiter/staffing name list (Michael Page, superjobs, Randstad, Hays, …). New `pipeline/src/companies.py`.
- **Bubble-map contract (P9, for the web agent):** toggle **OFF** → top-15 `company` bubbles; toggle **ON** → those + one aggregated `placeholder` bubble (centre). Use `sqrt`/`log` **area** scaling (or a separate panel) so the aggregate doesn't dwarf the rest. *(Emitter side: `top_companies` (top-15 `company`) + `placeholder_companies` aggregate.)*
- **Files:** `processor.py` (P1 moved to analyzer), `analyzer.py` (P1–P4, P7, P9), `salary_estimate.py` (P5), `curriculum_generation.py` (P6), `fetch_jobs.py` (P8), new `companies.py` + `locations.py`.
- **Verification:** module `--self-test`s, `ruff` E/W/F, then confirm the new sections exist and are sane after a run.
- **Done when:** the MY `gap_report.json` carries `states`, `top_companies`, soft-skill counts, `distinct_skills`, text-mined salary; `IT Support` / `Project & Sales Engineering` are present; curriculum empty-lists ≈ 0.
- **Result (13 Oct 2026):** all P1–P9 landed. `states` uses the full MY state map in the new
  `locations.py` (recomputed from `location`; also fixes the old `kl`→"Klang" bug).
  Soft skills are now `{name,count,percentage}`; `distinct_skills`, `low_sample`,
  `unknown_level`, `top_companies`/`placeholder_companies` (`companies.py`),
  text-mined `observed_salaries` (82/935 ads match — P1), and `schema_version` added.
  `salary_estimate` gets an `All`-bucket fallback flagged `broad_estimate` (P5).
  `curriculum_generation` retry + regex-salvage took empty lists **13.1% → 0.0%** (P6).
  Categories with 1 job (`Project & Sales Engineering`) now appear — the milestone's
  `<2` floor would still have dropped them, so the floor is "≥1".
  **Verify:** every module has an offline `--self-test`; `ruff` E/W/F clean. P8
  (`posted_at`) landed with the M5.7 re-fetch.

### M5.7 — SEA expansion + country comparisons `Done (pipeline) 13 Oct 2026`
- **Goal:** extend UDiff across SEA and add cross-country comparisons.
- **Scope (phase 1):** **MY, SG, ID, VN** (TH, PH later). ~**1,000 jobs/country**, `language=en`.
- **Currency:** each salary shown **two ways** — **nominal MYR** (FX) and **PPP-adjusted MYR**. PPP formula: `ppp_myr = salary_local / ppp_factor_local × ppp_factor_my`, where `ppp_factor` = *World Bank PPP conversion factor, private consumption (LCU per international $)*. Reads as "what this salary buys in Malaysia's prices".
- **PPP/FX source:** dated **static** tables — `pipeline/data/ppp.json` and `pipeline/data/fx.json` (record source + date; note PPP is an economy-wide basket, not expat cost-of-living).
- **Phase 0 — verify (~$0.03):** 1 page per country with `language=en` → measure English yield, salary presence, description language → finalise caps and confirm ID/VN viability.
- **Phase 1 — country-aware:** `config.py` adds `COUNTRIES` (GDP order), `LANGUAGE="en"`, per-country cap, PPP/FX paths; `fetch_jobs.py` loops countries and adds a **`country`** column; `processor.py` carries `country` (+ `posted_at`).
- **Phase 2 — analysis + comparison:** `analyzer.py` groups by country → `countries: {iso: {…}}` (reuses the existing per-country shape so web components can be reused); new `comparisons.py` emits deltas of **every market vs MY** (`my-vs-sg`, `my-vs-id`; VN dropped — see Result).
- **Phase 3 — salary + curriculum:** `salary_estimate.py` runs per country and computes nominal MYR + PPP-MYR (same confidence guard); `curriculum_generation.py` per country.
- **Phase 4 — sync + contract:** `sync_web_data.py` syncs the new schema; publish the type contract for the M6/web agent.
- **Data model (planned; the delivered v3 adds `name`, `low_sample`, `distinct_skills`, `unknown_level`, `placeholder_companies`, `observed_salaries`, `fetched_at`, and `nominal_myr`/`ppp_myr` as `{min,median,max}` dicts — see `docs/Tech Stack.md` §3 for the final shape):**
  ```jsonc
  gap_report.json {
    "schema_version": 3,
    "generated_at": "...",
    "countries": {
      "my": {
        "total_jobs_analyzed": 0,
        "job_distribution": {},
        "states": {},
        "top_companies": [{ "name": "", "count": 0, "kind": "company|placeholder" }],
        "categories": {
          "<Role>": {
            "All|Junior|Mid|Senior": {
              "job_count": 0,
              "salary": { "avg_min": 0, "avg_max": 0 },
              "salary_estimate": { "min": 0, "median": 0, "max": 0,
                "nominal_myr": { "min": 0, "median": 0, "max": 0 },
                "ppp_myr": { "min": 0, "median": 0, "max": 0 },
                "currency": "", "period": "", "source": "",
                "confidence": "", "sample_size": 0, "fetched_at": "" },
              "top_hard_skills": [{ "name": "", "count": 0, "percentage": 0 }],
              "top_soft_skills": [{ "name": "", "count": 0, "percentage": 0 }],
              "top_technical_context": [{ "name": "", "count": 0, "percentage": 0 }],
              "distinct_skills": 0
            },
            "unknown_level": 0
          }
        }
      },
      "sg": { "...": "same shape" }, "id": {}
    },
    "comparisons": {
      "my-vs-sg": {   // one key per peer market: my-vs-sg | my-vs-id
        "skill_gaps": [{ "skill": "", "my_pct": 0, "peer_pct": 0, "delta": 0 }],
        "salary_delta_nominal": [{ "role": "", "level": "", "my": 0, "peer": 0, "delta": 0 }],
        "salary_delta_ppp":     [{ "role": "", "level": "", "my": 0, "peer": 0, "delta": 0 }]
      }
    }
  }
  ```
  ```jsonc
  skill_class.json { "generated_at": "...",
    "countries": { "my": { "categories": { "<Role>": { "<Skill>": ["CourseName", "..."] } } }, "sg": {}, "id": {} } }
  ```
- **Budget/time (4 markets, ~1,000/country):** fetch ≈ $2.0; salary estimates ≈ $1.1 (**≈ $3 API total**, inside the $20 budget); GPU extraction ≈ 3.5–4 h; curriculum ≈ 30–40 min. *(Actual 3 markets: fetch ≈ $1.5, ~2.5 h extraction.)*
- **Risks:** non-English leakage (mitigated by `language=en`); uneven per-country coverage (take what exists); PPP/FX staleness; schema handoff to the web agent.
- **Execution order:** M5.6 → Phase 0 probe → Phases 1–4.
- **Done when:** `gap_report.json` is country-aware with `comparisons`, salary shows nominal + PPP, and the web contract is published.
- **Result (13 Oct 2026):**
  - **Phase 0 found the milestone's key assumption wrong:** non-US queries need the
    location **inside the query** and `country`+`language` together, or results fall
    back to the US. Post-fix, MY/SG/ID yield clean English pages; **VN returns 0 under
    `language=en`** (vi-only ads) → VN dropped. Structured skill fields are confirmed
    **absent** live, so LLM extraction stays.
  - `config.COUNTRIES = my, sg, id`; fetch loops countries and adds `country` +
    `posted_at`; `processor.py` is now **resumable** (per-country, checkpoints every 25).
  - `analyzer.py` groups by country → `countries`; new **`comparisons.py`** emits
    `my-vs-sg` / `my-vs-id` (skill-gap % deltas + nominal & PPP salary deltas as arrays);
    `salary_estimate.py` computes `nominal_myr` + `ppp_myr` (per min/median/max) from
    `ppp.json`/`fx.json`; `curriculum_generation.py` is per country.
  - **Run:** 2,300 fetched → **1,701 analysed** (MY 651, SG 575, ID 475); 632 curriculum
    subjects, 0 empty; `my-vs-sg` 25 skill gaps + 51 salary deltas, `my-vs-id` 25 + 40.
  - **Tracing:** `config.get_logger()` → `pipeline/logs/api.log` (every GET) and
    `gpu.log` (every LLM call); also on stdout.
  - **Web schema break (resolved in M9.0, 13 Oct):** `gap_report.json`/`skill_class.json` are v3
    country-nested. `page.tsx` and `curriculum/page.tsx` now read `countries.<cc>` via
    `src/lib/data.ts` (M9.0).
  - **Follow-up (13 Oct, later):** a data-quality pass normalised salary `period`
    (`YEAR`→`MONTH`), applied skill aliasing, guarded the broad fallback, made
    `comparisons` skip broad/non-month rows, and widened `observed_salaries` to all
    currencies — see the work log.

### M6 — Web cleanup `Done (13 Oct 2026)`
- **Result:** `npm run lint` is now **clean** (was 15+ errors). Removed every `any` / `@ts-ignore`;
  typed the roadmap JSON (`Roadmap`/`RoadmapPhase`), the two Recharts tooltip/content props, and the
  treemap content props; moved the bar-chart tooltip **out of render** (fixes the "component created
  during render" rule); replaced the roadmap `useEffect` progress-load with **`useSyncExternalStore`**
  (fixes `react-hooks/set-state-in-effect`); deleted 5 unused default Next.js SVGs.
- Screenshots already live under `public/screenshots/` and are referenced by the README.
- **Verified:** `npx tsc --noEmit` + `npm run lint` + `npm run build` all pass.
- **Done when:** build/lint pass with no dead cruft and docs show the live link. ✅

### M7 — Automate the data contract `Done (12 Oct 2026)`
- Added `pipeline/src/sync_web_data.py` (the final orchestrator step) that copies `gap_report.json` + `skill_class.json` into `src/data/`.
- **Done when:** the web app consumes pipeline output without manual file copying. ✅

### M8 — Portfolio packaging `Pending`
- Add the UDiff project entry to the résumé (held until docs are finalised).
- **Done when:** the repo reads cleanly to a reviewer end-to-end.

### M9 — Frontend revamp: Tier 0 (schema v3 data layer + de-slop) `Done (13 Oct 2026)`
- **Goal:** make the web app render the **v3 country-nested schema** and kill the "AI-generated"
  tells, with **no layout change** and **no new dependencies**.
- **Sub-steps:**
  - **M9.0 — Data layer (schema v3)** `Done (13 Oct)` — rewrote `src/types/index.ts` to v3; added
    `src/lib/data.ts` as the single data gateway (`getCountry`, `getRoles`, `getLevelBucket`,
    `getSkillClass`, `getComparison`); repointed `page.tsx` + `curriculum/page.tsx` (both were
    crashing on the old v2 shape); salary card now reads `salary_estimate` (was `N/A`); added a
    dashboard **country switcher**; removed the `@ts-ignore`s in curriculum. Also fixed header wrap
    (dropped the redundant `" Engineer"` suffix, badge moved beside the switcher) and truncated long
    chart labels in `SkillChart`.
  - **M9.1 — Dark tokens + metadata** `Done (13 Oct)` — `className="dark"` +
    `suppressHydrationWarning` on `<html>`; real page title/description. (The console hydration
    error was **Dark Reader**, a browser extension — not app code.)
  - **M9.2 — Token swap** `Done (13 Oct)` — hardcoded `slate-*`/`blue-*`/cyan/hex replaced with
    semantic tokens across every component; brand accent set to a blue `--primary`; added `--success`
    / `--warning` tokens; removed the colored left-strips on the curriculum result cards and
    neutralised the beta notice.
  - **M9.3 — Remove gradient text** `Done (13 Oct)` — logo → solid blue, page titles → `text-foreground`.
  - **M9.4 — Motion fixes** `Done (13 Oct)` — `transition-all` → exact props (button/tabs/progress/
    page/roadmap); inline chart `transition:'all'` → `fill/opacity` 150ms; `animate-in` 500ms → 200ms.
  - **M9.5 — Press feedback + charts + honesty** `Done (13 Oct)` — `active:scale-[0.97]` on buttons;
    bars/tiles now single-hue with a visible low-opacity track; tooltips drop the bracket style and use
    `tabular-nums`; salary card labelled as a market estimate; MetricCard values bumped to `text-4xl`
    and vertically centred.
- **No new dependencies.** Full task list in [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md) §5.
- **Note:** M6 (lint hygiene) still **pending** — Tier 0 landed without it; get `npm run lint` green in M6.
- **Result (13 Oct 2026):** Tier 0 complete. `npm run build` + `npx tsc --noEmit` pass; no palette
  hardcoding, gradient text, or `transition-all` left in components. ✅

### M10 — Frontend revamp: Tier 1 (re-skin + core data views) `Done (13 Oct 2026)`
- **Result:** every route shares one responsive `AppShell`; all **core `UDiff.md` §4 views** render for
  MY/SG/ID; `npm run build` + `npx tsc --noEmit` pass. Dark-only theming kept (no `next-themes` — not
  needed); **no map dependency** (geo shown as ranked bars).
- **Sub-steps:**
  - **M10.1 — AppShell + nav** `Done` — shared shell (Dashboard · Compare · Roadmap · Curriculum) on
    every route; dashboard role list split into `RolePanel`; old `Sidebar` deleted; `/compare` stub.
  - **M10.2 — Collapsible nav** `Done` — icon rail (desktop) + mobile top bar/drawer; `overflow-hidden`
    during the width transition (no scrollbar flash).
  - **M10.3 — Motion/type tokens** `Done` — `--ease-out`/`--ease-in-out`/`--ease-drawer`;
    `prefers-reduced-motion`; drawer enter animation.
  - **M10.4 — Core §4 views** `Done` — soft skills (arrow bars), openings by role, experience split
    (donut), jobs by location, top hiring companies (+ recruiters toggle), salary estimate
    (nominal/PPP toggle). Dashboard **sectioned** (`SectionHeading`) to separate `role × level` cards
    from `country only` cards.
  - **M10.5 — `/compare`** `Done` — peer toggle (SG/ID) + skill-gap and salary **diverging bars**.
  - **M10.6 — Polish** `Done` — shared `ChartTooltip`; `localStorage` roadmap progress (fixes the
    README claim); a11y (`aria-label`, single `h1` per page).
- **Decisions:** the country switcher stays in the dashboard header (not the shell); `/compare` is a
  separate route. **Deferred:** posting recency (not aggregated in the pipeline yet); observed-salary
  scatter (MY-only, country-level only).
- **Note:** M6 (lint hygiene) still **pending**.
- Full detail: [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md) §6.

### M11 — Frontend revamp: Tier 2 (restructure) `In progress (13 Oct 2026)`
- **Sub-steps:**
  - **M11.1 — Types** `Done` — `ObservedSalary` → `{ raw, value, currency, likely_annual, category, title }`;
    added `SalaryEstimate.period_raw`.
  - **M11.2 — Observed Salary Mentions** `Done` — country-scoped card (top 8, `annual` badge, count footer)
    in the dashboard *Market overview*.
  - **M11.3 — Methodology page** `Done` — new **`/methodology`** route (added to the shell nav): sources,
    processing, caveats, known quirks, per-country sample sizes, and the **full** observed-salary lists
    *(decision (c)).*
  - **M11.4 — Landing/About + route moves** `Next` — `/` becomes a landing page; the dashboard moves to
    **`/dashboard`**.
  - **M11.5 — Chart redesign + motion polish + a11y/perf audit** `Todo`
- **Deferred:** distinct-skills metric card; regional role-distribution on `/compare`; posting recency
  (needs a pipeline aggregate).
- **New dep:** `motion` (optional). Plan: [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md) §7.
- **Done when:** a stranger understands UDiff without context and the app passes an a11y audit.

---

## 3. Work log

### 11_10_2026 — Merge & documentation pass (assistant)
**Did:**
- Safety-committed and pushed all previously-untracked files in `RSGzen/UDiff` (`091f67c..9357fcc`) so the pre-merge state is fully recoverable.
- Merged the two repos into one: the Next.js app stays at the repo root (Vercel unchanged); the Python pipeline was relocated under `pipeline/` with a clean `src/` + `data/{raw,interim,output}` layout.
- Retired the Streamlit dashboard and its Dockerfile/config into `pipeline/legacy/`.
- Relicensed the pipeline to MIT and removed the original GPLv3 text (repo is now MIT-only).
- Wrote `docs/UDiff.md`, `docs/Tech Stack.md`, and this file.
- Rewrote the top-level `README.md` (the old one had stale versions and a placeholder clone URL).

**Did not do (left for the next agent):** refactor code / fix paths, extend the pipeline entrypoint, fix `requirements.txt`, re-scrape, web cleanup. See milestones M0, M2–M8.

**Open items / decisions:**
- **License reconciliation:** resolved — relicensed to MIT; GPLv3 file removed.
- **Repo name:** the GitHub repo is still `udiff-web`; renaming to `udiff` requires manual action (no `gh` CLI available). Renaming may affect the Vercel Git connection.
- **Streamlit retirement:** resolved — `pipeline/legacy/` (dashboard + Dockerfile + scrapers) has been deleted.
- **Original `RSGzen/UDiff` repo:** retained as the pre-merge backup; can be archived later.

### 12_10_2026 — M2 refactor + LLM upgrade, docs pass (assistant)
**Did:**
- M0 triage: `next build`/`tsc` pass, `npm run lint` fails (15 errors), pipeline un-runnable.
- M2: added `pipeline/src/config.py` (single source of truth); converted all six scripts off `os.getcwd()` to `Path(__file__)`; PEP-8 comment/whitespace pass (`ruff`).
- Upgraded the extraction model `llama3.1` → `qwen3:8b` (fits 8 GB VRAM fully) and set `think=False`; measured ~13 s → ~5 s per posting.
- Updated `README.md`, `docs/UDiff.md`, `docs/Tech Stack.md` to match.

**Did not do (next):** M3 orchestrator repair; M4 `requirements.txt`; M5 re-scrape; M6 web cleanup.
**Open items:** planned order changed to M5 (re-scrape) before finishing M4/M3, because refreshing data gates the value of the run.

### 12_10_2026 (later) — M5 data source + M3 orchestrator (assistant)
**Did:**
- M5: retired the JobStreet scrapers to `pipeline/legacy/` (robots.txt/ToS forbid scraping) and added `fetch_jobs.py` for the JSearch API; fetched **935 MY postings**; gitignored `job_details_full.csv`.
- Probed the API: `search-v2` returns **no** structured skills/seniority, so the LLM extraction stays; salary is always null.
- M3: rewrote `pipeline.py` as a 4-step orchestrator (`fetch → extract → analyze → curriculum`) with `--steps/--skip/--skip-scrape/--dry-run/--list`.

**Next:** run the pipeline on the new data (LLM extract ≈ 80 min), then M4 `requirements.txt`, M6 web cleanup, M7 data-contract sync.

### 12_10_2026 (night) — Frontend design audit + revamp plan (assistant)
**Did:**
- Reviewed the entire web UI (`src/app/**`, `src/components/**`, `globals.css`, `layout.tsx`).
- Diagnosed the "AI-generated / outdated" look: **two parallel styling systems** (the `globals.css`
  token layer is unused; components hardcode `slate-*`/`blue-*`/cyan/hex), gradient text on headings,
  bracket mono tooltips, `transition-all`, fake dark mode, and a non-responsive fixed sidebar.
- Agreed the direction with the user: **Tier 1 as baseline, Tier 2 later**; reference = Linear /
  Vercel Geist (visual) + Tremor (dashboard, same Recharts/Radix/Tailwind stack); no new UI library.
- Wrote [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md): style guide (color/type/space/
  radius/motion), tiered task lists with done-when criteria, effort table, agent guardrails, and a
  before→after audit appendix.
- Updated [`Tech Stack.md`](Tech%20Stack.md) web section (design system, typography, plan pointer)
  and this file: added **M9–M11**, linked them from M6, and repointed the "modern UI" backlog item.

**Did not do:** any UI/code changes. This pass was docs-only by explicit request.
**Next:** M6 (web cleanup) → M9 (Tier 0 de-slop).

### 12_10_2026 (evening) — run + curriculum fix, M4 + M7 (assistant)
**Did:**
- Ran the pipeline on the 935 fetched jobs → 677 analysed; `gap_report.json` regenerated (14 categories).
- Fixed `curriculum_generation.py`: use `min()` instead of raising on small categories, and keep the model resident (`keep_alive='30m'`) with bounded output — the first curriculum run crawled due to model unload/reload gaps.
- Removed the retired `pipeline/legacy/` (dashboard, Dockerfile, both scrapers).
- M4: `requirements.txt` → `pandas` + `ollama`; module docstrings; `pipeline/README.md`; `docs/UDiff.md` / `docs/Tech Stack.md` updated.
- M7: added `sync_web_data.py` as the final orchestrator step.

### 13_10_2026 — M5.5 + M5.6 + M5.7 (assistant)
**Did:**
- **Logger (M5.7 ask):** `config.get_logger()` writes to stdout AND a file; wired into
  `fetch_jobs.api_get` (`pipeline/logs/api.log`) and the GPU calls in `processor.py` /
  `curriculum_generation.py` (`pipeline/logs/gpu.log`). The orchestrator's existing stdout
  tee (`pipeline_log.log`) still covers whole-run output.
- **M5.5:** `salary_estimate` now stamped `fetched_at`; `All`-bucket fallback (P5, `broad_estimate`).
- **M5.6:** `locations.py` (full MY state map — `Other` 54→36, fixes `kl`→"Klang");
  `companies.py` (P9 `company`/`placeholder`); analyzer emits `states`, `top_companies`,
  `placeholder_companies`, `observed_salaries`, soft-skill objects, `distinct_skills`,
  `low_sample`, `unknown_level`, `schema_version`; curriculum retry+salvage (empty 13.1%→0%).
  Corrected the milestone's `<2` floor so 1-job categories (`Project & Sales Engineering`) show.
- **M5.7 Phase 0:** discovered non-US queries need the location **in the query** +
  `country`+`language` (else US fallback). SG/ID viable; **VN not** (`language=en` → 0). VN dropped.
- **M5.7:** `config.COUNTRIES=my,sg,id`; per-country fetch (`country`+`posted_at`, location in query);
  resumable `processor.py` (`--country`, checkpoints); country-nested `analyzer.py`;
  new `comparisons.py` (`my-vs-sg`/`my-vs-id`); per-country `salary_estimate.py` with
  `nominal_myr`+`ppp_myr` (from hand-filled `ppp.json`/`fx.json`, 2025/13-10-2026); per-country
  curriculum; `compare` step added to `pipeline.py`.
- **Run:** 2,300 raw → 1,701 analysed (MY 651, SG 575, ID 475); 632 curriculum subjects,
  0 empty. `my-vs-sg`/`my-vs-id` each carry 25 skill gaps + salary deltas (51 and 40 rows).
  Fetch cost ≈ $1.5 (300 pages); salary estimates ≈ 150 calls.
- **Static tables:** `ppp.json` (World Bank PA.NUS.PRVT.PP, 2025: my 1.43, sg 1.02,
  id 5065.97); `fx.json` (wise.com, 13-10-2026: sg 0.31, id 4391 per MYR). `vn` keys
  remain but are unused.
- **New files:** `locations.py`, `companies.py`, `comparisons.py`, `probe_countries.py`.
- Docs updated (`UDiff.md`, `Tech Stack.md`, `README.md`, `pipeline/README.md`, `AGENTS.md`, this file).

**Open items / decisions:**
- **VN:** dropped for now (no English postings); the comparison schema is ready if VN is
  added later via `language=vi` or no language filter.
- **`observed_salaries`:** was MY-only (`RM|MYR` regex) — **fixed later the same day**
  (all currencies + `likely_annual`; see the data-audit entry below).
- All modules: per-module `--self-test` + `ruff` clean; no test framework.

**Did not do (next):** web rendering of the new schema — *(resolved in M9.0 below).*

### 13_10_2026 (web) — M9.0 + M9.1 + dependency bump (assistant)
**Did:**
- **Audit:** bumped `next` + `eslint-config-next` 16.1.4 → **16.4.0** (clears the Next *critical* +
  the postcss/sharp highs). Did **not** run `npm audit fix --force` — it would downgrade
  `eslint-config-next` to v14. Remaining `braces` is **dev-only** (eslint toolchain, never shipped).
- **M9.0 (schema v3 data layer):** rewrote `src/types/index.ts` to v3; added `src/lib/data.ts` as the
  single data gateway; repointed `src/app/page.tsx` + `src/app/curriculum/page.tsx` (both crashed on
  the old v2 shape → the site did not render); salary card now reads `salary_estimate`; added a
  dashboard country switcher; removed the curriculum `@ts-ignore`s. Also fixed header wrap (dropped
  the redundant `" Engineer"` suffix, moved the level badge beside the switcher) and truncated long
  `SkillChart` labels.
- **M9.1 (tokens + metadata):** `className="dark"` + `suppressHydrationWarning` on `<html>`;
  real page title/description.
- **Files:** `package.json`, `src/types/index.ts`, `src/lib/data.ts` (new), `src/app/page.tsx`,
  `src/app/curriculum/page.tsx`, `src/app/layout.tsx`, `src/components/dashboard/SkillChart.tsx`.

**Verified:** `npx tsc --noEmit` + `npm run build` pass (all routes); user confirmed MY/SG/ID render.
**Notes:** the console "hydration" error is the **Dark Reader** browser extension, not app code.
**Next:** M9.2 (token swap) → M9.3–M9.5 → M10.

**Open items / decisions:**
- Role headings now show the raw category name (no `" Engineer"` suffix). A `ROLE_LABELS` display map
  can be added later if proper role titles ("Software Engineer") are wanted.
- Salary: keep **min–max, monthly, nominal MYR**; **PPP toggle** lands in M10.
- Sidebar: collapse/rail + mobile drawer confirmed as part of the M10 `AppShell`.

### 13_10_2026 (web, later) — M9.2–M9.5 (Tier 0 complete) (assistant)
**Did:**
- **M9.2 (token swap):** replaced every hardcoded `slate-*`/`blue-*`/cyan/hex color in the components
  with semantic tokens (`bg-background`, `bg-card`, `border-border`, `text-muted-foreground`, …); set
  the dark `--primary`/`--ring` to a blue brand accent; added `--success`/`--warning` tokens (+ `@theme`
  mappings); removed the colored left-strips on the curriculum *Missing*/*Covered* cards and
  neutralised the beta notice.
- **M9.3:** removed the three gradient headings (logo → solid blue, page titles → `text-foreground`).
- **M9.4:** `transition-all` → explicit properties (button, tabs, progress, page, roadmap); inline
  chart `transition:'all'` → `fill/opacity` 150 ms; `animate-in` 500 ms → 200 ms.
- **M9.5:** `active:scale-[0.97]` on buttons; chart bars/tiles single-hue with a visible low-opacity
  track; tooltips drop the `[ name : % ]` bracket style and use `tabular-nums`; salary card labelled
  "market estimate"; MetricCard value bumped to `text-4xl` and vertically centred on the card.
- **Files:** `src/app/globals.css`, `page.tsx`, `curriculum/page.tsx`, `roadmap/page.tsx`,
  `Sidebar.tsx`, `dashboard/{MetricCard,SkillChart,ContextTreemap}.tsx`, `ui/{button,tabs,progress}.tsx`.

**Verified:** `npx tsc --noEmit` + `npm run build` pass; user reviewed each increment live.
**Next:** M10 (Tier 1) — shell + country switcher + core `UDiff.md` §4 views.

### 13_10_2026 (web, M10) — Tier 1: shell + core §4 views (assistant)
**Did (incremental, reviewed live each step):**
- **M10.1:** added `AppShell` (global nav: Dashboard · Compare · Roadmap · Curriculum) used by every
  route; split the dashboard role list into `RolePanel`; deleted the old `Sidebar`; added the
  `/compare` route.
- **M10.2:** collapsible nav → icon rail on desktop; mobile top bar + slide-in drawer; compact mobile
  dashboard filter row (role/level/country). Fixed a scrollbar flash with `overflow-hidden`.
- **M10.3:** motion tokens (`--ease-out`/`--ease-in-out`/`--ease-drawer`) + `prefers-reduced-motion`;
  drawer enter animation.
- **M10.4:** built the core §4 views — Top Soft Skills (arrow-tipped bars), Openings by Role,
  Experience Split (donut), Jobs by Location, Top Hiring Companies (+ recruiters checkbox), Salary
  Estimate (nominal/PPP toggle). Added `SectionHeading` to group `role × level` vs `country only`
  cards. (Fixed the bar-chart hover flash: dropped the `null` between bars.)
- **M10.5:** `/compare` — peer toggle (SG/ID) + skill-gap and salary **diverging bars** (nominal/PPP).
- **M10.6:** shared `ChartTooltip`; `localStorage` roadmap progress; a11y (`aria-label`, single `h1`).
- **Data types:** `placeholder_companies` corrected to a single object; `unknown_level` is a number.

**Verified:** `npx tsc --noEmit` + `npm run build` pass (routes `/`, `/compare`, `/curriculum`,
`/roadmap`); user reviewed each increment.
**Decisions:** dark-only (no `next-themes`); no map dependency; country switcher in the dashboard header.
**Deferred:** posting recency (needs a pipeline aggregate); observed-salary scatter (MY-only).
**Next:** M6 (lint hygiene) → M11 (Tier 2: landing, route moves, methodology, motion polish).

### 13_10_2026 (data audit) — salary/skill irregularities fixed (assistant)
**Did:**
- Audited `gap_report.json` + `job_analysis_final.json` (read-only) and fixed 5 irregularities:
  - **Salary period:** `/estimated-salary` returned `YEAR` for SG `AI & ML Mid` and
    SG `Project & Sales Eng Mid`, which were being treated as monthly (~12× inflation).
    `salary_estimate.normalize_period` now converts `YEAR`→`MONTH` and keeps `period_raw`.
  - **Skill aliasing:** `analyzer.skill_key` / `skill_display` are now applied in
    `top_items` / `distinct_skills`, so `React.js`/`ReactJS`/`React.JS` → `React` (and
    `Golang`→`Go`, `NodeJS`→`Node.js`, …). Previously the alias table was dead code.
  - **Broad-fallback guard:** the `All`-bucket fallback is suppressed when it would
    invert seniority (**5** cases, e.g. SG Cybersecurity Senior).
  - **Comparisons:** `salary_deltas` skips `broad_estimate` and non-`MONTH` rows, so the
    bogus SG AI&ML Mid delta (**−176k MYR**) is gone.
  - **Observed salaries:** regex widened to `RM|MYR|S$|SGD|Rp|IDR` and now emits
    `{raw,value,currency,likely_annual}`; SG/ID are populated (were 0).
- Re-ran `analyze → salary → compare → sync` (no GPU; ~150 salary API calls, ~4 min).
- **Verification:** all 146 estimates are `MONTH`; no junior>senior inversions; no alias
  duplicates; every structural check clean (`dist` sums, no missing `All`, skill % ≤ 100).

**Known residual (source data, not a pipeline bug):** SG Cybersecurity Junior (5908, n=34) >
Mid (4175, n=6) and ID Fullstack Mid ≈ Senior (11.0M vs 10.7M) — upstream
`/estimated-salary` variance; the pipeline normalises period and suppresses inverting
fallbacks but does not smooth real reported values.

**Contract change for the web agent:** `observed_salaries` is now multi-country with
`value`/`currency`/`likely_annual` (the deferred observed-salary scatter can be enabled);
`salary_estimate` gained `period_raw` (its `period` is always `MONTH`).

### 13_10_2026 (web, planning) — M11 scoped against refreshed data (assistant)
**Did:**
- Reviewed the refreshed `src/data/gap_report.json` (generated `2026-10-13 17:09`) + the data-audit log.
  The only dashboard-relevant **new** data is **`observed_salaries`** — now multi-country
  (MY 33 · SG 13 · ID 5) with `value`/`currency`/`likely_annual` — plus `salary_estimate.period_raw`.
  (No `posted_at`/recency field exists in the report.)
- Reconciled `UDiff.md` §4 against what M9/M10 actually built; corrected the chart-type column
  (donut / ranked list / range-bar toggle) and marked **Posting recency** as *no data*.
- Scoped **M11**: add an **Observed Salary Mentions** view (per-country **list + `likely_annual` flag**)
  as a compact dashboard *Market overview* card **and** a full explanation on the Methodology page
  *(decision (c))*; prereq = update the `ObservedSalary` type + add `period_raw`.
- **Decision:** run **M6** (lint hygiene) **before** M11.
- Deferred: distinct-skills metric card; regional role-distribution on `/compare`; posting recency.

**Next:** M6 → M11.

### 13_10_2026 (web, M6) — lint hygiene (assistant)
**Did:**
- Removed all `any` / `@ts-ignore` from the app: typed `roadmaps.json` (`Roadmap`/`RoadmapPhase`), the
  `SkillChart` + `ExperienceSplit` tooltip props, and the `ContextTreemap` content props.
- Moved `ChartBarTooltip` to module scope (was created during render — `react-hooks/static-components`).
- Replaced the roadmap `useEffect` progress-load with **`useSyncExternalStore`** (+ a
  `udiff-roadmap-progress-change` event), removing `react-hooks/set-state-in-effect` while keeping
  persistence.
- Deleted 5 unused default Next.js SVGs from `public/`.

**Verified:** `npx tsc --noEmit` + `npm run lint` + `npm run build` all pass (lint clean; was 15+ errors).
**Next:** M11 (Tier 2).

### 13_10_2026 (web, M11.1–11.3) — observed salaries + methodology (assistant)
**Did:**
- **M11.1:** `ObservedSalary` type → `{ raw, value, currency, likely_annual, category, title }`; added
  `SalaryEstimate.period_raw`.
- **M11.2:** new `ObservedSalaries` card (top 8, `annual` badge, count footer) in the dashboard
  *Market overview* — country-scoped.
- **M11.3:** new **`/methodology`** route + shell-nav entry: data source, processing pipeline, caveats,
  known quirks, per-country sample sizes, and the **full** observed-salary lists *(decision (c) full half)*.

**Verified:** `npx tsc --noEmit` + `npm run lint` + `npm run build` pass (now 5 routes: `/`, `/compare`,
`/curriculum`, `/methodology`, `/roadmap`).
**Next:** M11.4 (landing page + route moves).

---

## 4. Backlog (feature requests, carried from `future_changes.txt`)

- Compare how roles differ by years of experience (soft/hard/technical skills + salary).
- Compare university curriculums against industry reality; extract curricula that offer the courses matching demanded job skills.
- Skill detail pages: hover a skill → quick explanation + verified learning resources.
- Compare a student's current curriculum progress against industry standards (cross-off mastered skills, personal roadmap).
- UI: more modern design, more interaction/animation, and a better-fitting visual for skill distributions.
  → **M9 (Tier 0) done; M10/M11 planned** (see [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md)).

---

## 5. How to run

```bash
# Web (from repo root)
npm install
npm run dev            # http://localhost:3000

# Pipeline (single entrypoint; settings from pipeline/src/config.py)
# requires: Python 3.x, Ollama running qwen3:8b, JSEARCH_API_KEY in pipeline/.env
pip install -r pipeline/requirements.txt
python pipeline/src/pipeline.py                 # full run
python pipeline/src/pipeline.py --skip fetch    # reuse existing data
python pipeline/src/pipeline.py --list          # list steps
python pipeline/src/pipeline.py --steps analyze,salary,compare,curriculum,sync
```

> Steps: `fetch → extract → analyze → salary → compare → curriculum → sync`. Each
> step streams to stdout + `pipeline/pipeline_log.log`; API GET calls and LLM calls
> also go to `pipeline/logs/api.log` and `pipeline/logs/gpu.log`.
> The single-country helper scripts accept `--self-test` for offline checks.
