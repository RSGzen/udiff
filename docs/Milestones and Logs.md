# UDiff — Milestones & Logs

> **IMPORTANT:** This project **is in need of polishing/rework.** It is a working prototype assembled across a school year, partly AI-assisted. The pipeline scripts are **old experimental code**; the merged repo structure and the `docs/` folder are **new** (11 Oct 2026).
>
> **Status legend:** `Done` · `In progress` · `Pending` · `Blocked`

---

## 1. Repository status — old vs. new (read this first)

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

### M5 — Data refresh `In progress (fetch done 12 Oct 2026)`
- JobStreet scraping is disallowed by its robots.txt (`Disallow: */job/`, `*?`) and ToS cl. 7.d/9.b, so the scrapers were retired to `pipeline/legacy/` and replaced by the **JSearch API** (`fetch_jobs.py`, OpenWebNinja).
- Fetched **935 Malaysian postings** (all with descriptions; salary 100% null). Raw ad text is now gitignored.
- **Still to do:** run the LLM + aggregation on the new data and redeploy the site.
- **Done when:** the live site reflects freshly generated data. ⬜

### M5.5 — Salary estimates (optional) `Pending`
- `search-v2` returns no salary, so `gap_report.json` salary is `0` / `N/A`.
- Add a separate enrichment step using `/estimated-salary` (`job_title` + `location` + `years_of_experience`) to produce a **market band** per category × level (~14 × 3 ≈ 42 calls).
- **Keep it separate from observed pay:** store a clearly-attributed `salary_estimate {min, median, max, currency, period, source, confidence, sample_size}`; do **not** overwrite the posting-derived `salary` — that would change what the metric means.
- Label the web card "estimated (Glassdoor via JSearch)" and surface `confidence` / `sample_size`.
- **Done when:** the dashboard shows a labelled market estimate alongside the honest `N/A` for observed pay.

### M6 — Web cleanup `Pending`
- Remove the `as any` casts and unused default assets; ensure types are honest.
- Verify `npm run build` + `npm run lint`; add a screenshot/GIF to the README.
- **Note:** this is the **code-hygiene** pass (`as any`, `@ts-ignore`, lint), separate from the
  **design** revamp (M9–M11). Run M6 **before** M9 so the revamp starts from a typed, lint-clean base.
- **Done when:** build/lint pass with no dead cruft and docs show the live link.

### M7 — Automate the data contract `Done (12 Oct 2026)`
- Added `pipeline/src/sync_web_data.py` (the final orchestrator step) that copies `gap_report.json` + `skill_class.json` into `src/data/`.
- **Done when:** the web app consumes pipeline output without manual file copying. ✅

### M8 — Portfolio packaging `Pending`
- Add the UDiff project entry to the résumé (held until docs are finalised).
- **Done when:** the repo reads cleanly to a reviewer end-to-end.

### M9 — Frontend revamp: Tier 0 (de-slop) `Pending`
- Kill the "AI-generated" tells **without layout changes**: apply the existing dark tokens
  (`layout.tsx`), real metadata, swap hardcoded `slate-*`/`blue-*`/cyan/hex for semantic tokens,
  remove gradient text, replace `transition-all` and inline `transition:'all'`, add button press
  feedback, fix chart contrast/tooltips, honest salary label, radius consistency.
- **No new dependencies.** Full task list in [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md) §5.
- **Depends on:** M6 (typed/lint-clean base).
- **Done when:** no palette hardcoding or `transition-all` in components; `npm run build` + `tsc --noEmit` pass; layout visually unchanged.

### M10 — Frontend revamp: Tier 1 (re-skin) `Pending`
- Token-driven, responsive re-skin: `next-themes` dark theming, a shared `AppShell` used by every
  route, responsive sidebar (drawer on mobile), Geist type + `tabular-nums`, motion tokens +
  reduced-motion, tokenized charts + one shared tooltip, re-skinned roadmap/curriculum,
  `localStorage` roadmap progress, a11y pass.
- **New dep:** `next-themes` (optional if dark-only). Plan: [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md) §6.
- **Done when:** every route shares one responsive shell; build + lint pass; charts use tokens.

### M11 — Frontend revamp: Tier 2 (restructure) `Future`
- Landing/About page, IA + route moves (`/dashboard`, `/methodology`), optional role detail route,
  mobile drawer, methodology/data page, chart redesign, motion polish, full a11y + performance audit.
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

---

## 4. Backlog (feature requests, carried from `future_changes.txt`)

- Compare how roles differ by years of experience (soft/hard/technical skills + salary).
- Compare university curriculums against industry reality; extract curricula that offer the courses matching demanded job skills.
- Skill detail pages: hover a skill → quick explanation + verified learning resources.
- Compare a student's current curriculum progress against industry standards (cross-off mastered skills, personal roadmap).
- UI: more modern design, more interaction/animation, and a better-fitting visual for skill distributions.
  → **planned as M9–M11** (see [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md)).

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
```

> The above reflects the post-M2/M3 state.
