# UDiff — University Diff

> **Status:** Working prototype, **pending polish/rework** (see `Milestones and Logs.md`).
> **One-line pitch:** A data pipeline + dashboard that measures the gap between what universities teach and what the Malaysian tech job market actually demands.

---

## 1. Problem statement

University curricula move slowly; the job market does not. A final-year student has no data-driven way to answer "which skills does a Backend / AI / Frontend role actually demand right now in Malaysia, and how much of that does my degree cover?" Job postings are unstructured, scattered across pages, and full of noise (sponsored repeats, hidden salaries, vague titles). Turning them into a clean, comparable view of market demand requires scraping, LLM extraction, and aggregation — which is exactly what UDiff automates.

## 2. Aim

Build and deploy an end-to-end system that:

1. **Harvests** real job postings from a job board for a fixed set of role queries.
2. **Extracts** structured skills from each free-text posting using a local LLM (hard skills, soft skills, *technical context*, and experience level).
3. **Aggregates** the results into a "market gap report" — top skills, dominant technical contexts, and salary ranges — segmented by role and experience level.
4. **Presents** the findings through an interactive web dashboard, supplemented by gamified career roadmaps and a curriculum gap checker.

## 3. General idea — how UDiff works

The system is a **batch data pipeline** that feeds a **static web dashboard**. Data flows one way:

```mermaid
flowchart LR
    A[JSearch API] -->|fetch_jobs.py · MY/SG/ID| C[job_details_full.csv]
    C -->|clean / dedupe / parse| D[Qwen3 8B via Ollama]
    D --> E[job_analysis_final.json]
    E -->|categorize + aggregate per country| F[gap_report.json]
    F -->|/estimated-salary + PPP/FX| S[salary_estimate.py]
    S -->|my-vs-sg / my-vs-id| X[comparisons.py]
    X --> G[LLM curriculum generator]
    G --> H[skill_class.json]
    F --> W[Next.js dashboard]
    H --> W
    R[roadmaps.json] --> W
```

| Step | Module | Input → Output | What it does |
|---|---|---|---|
| 1. Fetch jobs | `pipeline/src/fetch_jobs.py` | JSearch API → `job_links.csv`, `job_details_full.csv` | Loops `config.COUNTRIES` (MY, SG, ID); queries the JSearch API per role keyword **with the location in the query**; maps title, company, location, salary, link, country, full description and `posted_at`; de-duplicates by (country, job id) |
| 2. Extract skills | `pipeline/src/processor.py` | CSV → `job_analysis_final.json` | Cleans text, parses salary, normalises location (`locations.py`), de-duplicates, then asks **Qwen3 8B** (Ollama, JSON mode) for `hard_skills`, `soft_skills`, `technical_context`, `experience_level`. Resumable (`--country`, checkpoints) |
| 3. Analyze market | `pipeline/src/analyzer.py` | JSON → `gap_report.json` | Buckets titles into role categories, then aggregates per **country** × category × level: top skills/contexts, `states`, `top_companies`, soft-skill counts, `distinct_skills`, salary stats, `observed_salaries` |
| 3b. Salary estimates | `pipeline/src/salary_estimate.py` | gap_report → gap_report | Calls JSearch `/estimated-salary` per category × level × country (reliability-guarded); adds nominal-MYR + PPP-MYR views from `ppp.json`/`fx.json`. Never overwrites observed `salary` |
| 3c. Comparisons | `pipeline/src/comparisons.py` | gap_report → gap_report | Emits `my-vs-sg` / `my-vs-id`: skill-gap % deltas and nominal/PPP salary deltas |
| 4. Curriculum generator | `pipeline/src/curriculum_generation.py` | `gap_report.json` → `skill_class.json` | Per country, for each category's top skills, asks the LLM for plausible university course names (retry + salvage) → a skill→course synonym dictionary |
| 5. Sync + dashboard | `pipeline/src/sync_web_data.py` + `src/` (Next.js) | JSONs → website | Copies the outputs into the app, which renders the gap report, roadmaps, and curriculum checker |

Supporting files:
- `pipeline/src/pipeline.py` — orchestrator that chains every step (fetch → extract → analyze → salary → compare → curriculum → sync) as subprocesses.
- `pipeline/src/config.py` — paths, settings, `COUNTRIES`, and the `.env` secret loader; also `get_logger()`.
- `pipeline/src/locations.py` — raw location → MY state / country region.
- `pipeline/src/companies.py` — employer → `company` vs `placeholder` (recruiter/confidential).
- `pipeline/src/probe_countries.py` — Phase-0 probe for English yield / field coverage per country.
- `pipeline/src/inspect_others.py` — dev utility that prints unclassified job titles (helps tune the category heuristics).

## 4. Data

What the dashboard surfaces and how each view is meant to be used. Rows marked `*` are produced by **M5.6** (data enrichment); `†` by **M5.7** (SEA expansion — **MY, SG, ID**; VN was dropped, see below). Unmarked rows are live today.

| Data / comparison | Data type | Chart type | Aim of data |
|---|---|---|---|
| Top hard skills (per role × level) | ranked categorical + % | horizontal bar | Most-demanded technologies for a role |
| Technical context / domains | weighted categories | treemap | Which application areas skills are used in (NLP, Android, Spring…) |
| Soft skills `*` | ranked list + count/% | bar (arrow) | Non-technical demand (communication, ownership) |
| Job distribution by role | category counts | bar | Market composition — which roles have the most openings |
| Experience split (All / Junior / Mid / Senior) | ordinal buckets | donut | Demand by seniority, incl. junior-market size |
| Jobs by location `*` | geographic category | ranked bar | Where hiring is concentrated (KL, Selangor, Penang…) |
| Top hiring companies `*` | ranked category + `kind` flag | ranked list (+ placeholders toggle) | Who is hiring; recruiter/confidential share |
| Salary estimate — nominal (MYR) | range per role × level | range bar | Market pay bands (estimated, attributed) |
| Salary estimate — PPP-adjusted (MYR) | range per role × level | range bar (nominal/PPP toggle) | Real purchasing power (cost-of-living adjusted) |
| Observed salary mentions `*` | sparse per-posting values | list (+ `likely_annual` flag) | Best-effort observed-pay signal from ad text |
| Distinct skills `*` | scalar | metric card | Breadth of demand for a role |
| Posting recency `*` | time series | — **(no data)** | Data freshness ("% posted in last 30 days") — **not aggregated in the pipeline yet** |
| Curriculum skill→course map | lookup dictionary | table / checker UI | Match a syllabus against demanded skills |
| Country skill gap (e.g. MY vs SG) `†` | signed deltas | diverging bar | Skills the local market is missing vs a peer |
| Country salary delta (nominal & PPP) `†` | signed deltas / ranges | diverging bar | Pay comparison between countries |
| Regional role distribution `†` | multi-category counts | grouped bar | Market composition across SEA |
| Career roadmaps | hand-authored phases | timeline / checklist | Guided learning path per role |

> **Built status (M9/M10):** every row is rendered **except** *Observed salary mentions* (planned M11)
> and *Posting recency* (no pipeline aggregate yet). *Distinct skills* and *Regional role distribution*
> have data but are deferred. Asia/geo rows use ranked bars — **no map dependency**.

## 5. Expected outcome

- A **live, interactive dashboard** showing, for each role and experience level, the most in-demand hard skills, the technical contexts they appear in, and average salary ranges.
- **Gamified career roadmaps** (foundation → core → advanced) for 15+ roles.
- A **curriculum gap checker** that maps course/skill keywords to market demand via a pre-computed synonym dictionary.
- A reusable, explainable dataset of Malaysian, Singaporean and Indonesian tech job-market demand (a point-in-time snapshot).

## 6. Limitations (honest)

- **Data source:** postings come from the **JSearch API** (a Google-for-Jobs aggregator); coverage, and especially salary fields, depend on it — salary is frequently absent.
- **Regional coverage:** MY, SG and ID only. **Vietnam was dropped** — with `language=en` the API returns no VN postings (Phase-0 probe). Non-US queries also require the location *inside* the query, or results fall back to the US.
- **Currency conversion:** `nominal_myr` uses a dated FX table and `ppp_myr` the World Bank PPP conversion factor (*private consumption*, an economy-wide basket — not expat cost-of-living). Both live hand-filled in `pipeline/data/ppp.json` / `fx.json` and go stale.
- **Point-in-time data:** the dataset is a snapshot; there is no scheduler or live refresh.
- **No ground truth for LLM extraction:** skill/context extraction is prompt-based and unvalidated; quality varies per posting. Category assignment is keyword heuristics and is brittle (see `inspect_others.py`).
- **Salary sparsity:** many postings hide salary, so salary averages are noisy. The `salary_estimate` is a publisher estimate for a *representative title per category*, not per posting; its `period` is normalised to monthly (`period_raw` keeps the source period). `observed_salaries` (text-mined) matches `RM|MYR|S$|SGD|Rp|IDR` and flags `likely_annual`, but remains a best-effort signal.
- **`skill_class.json` is synthetic:** its course names are LLM-generated, not scraped from real university curricula — treat it as illustrative, not authoritative.
- **Matching is lexical, not semantic:** the curriculum checker uses keyword/synonym matching, not embeddings.
- **Code quality:** mixed human + AI-assisted code. Paths were centralised in `pipeline/src/config.py` (M2) and the orchestrator repaired (M3); there are still no automated tests beyond per-module `--self-test`s.
