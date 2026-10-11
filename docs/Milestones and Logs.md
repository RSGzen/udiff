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

### M3 — Single robust entrypoint `In progress`
- Extend `pipeline/src/pipeline.py` to include **step 5 (curriculum generation)** and expose step selection flags (`--steps`, `--skip-scrape`).
- Add resume/checkpointing, retries, and clear failure messages.
- **Done when:** one command runs the full pipeline (or a chosen subset) and fails gracefully.

### M4 — Documentation `In progress`
- ✅ `docs/UDiff.md`, `docs/Tech Stack.md`, this file.
- ⬜ Fix `pipeline/requirements.txt` (add `playwright`, `beautifulsoup4`, `ollama`; consider a `pyproject.toml`).
- ⬜ Add module docstrings + a short `pipeline/README.md`.
- ⬜ Add an architecture diagram to the top-level `README.md` (partially done).

### M5 — Data refresh `Pending`
- **Preferred:** fix the scraper for the current JobStreet DOM, then attempt a **full re-scrape** and regenerate all data + the website.
- **Fallback:** if re-scraping fails, re-run only the downstream steps (`processor.py → analyzer.py → curriculum_generation.py`) on the committed raw CSV.
- Rebuild/redeploy the web app with the refreshed JSONs.
- **Done when:** the live site reflects freshly generated data (or a documented fallback run).

### M6 — Web cleanup `Pending`
- Remove the `as any` casts and unused default assets; ensure types are honest.
- Verify `npm run build` + `npm run lint`; add a screenshot/GIF to the README.
- **Done when:** build/lint pass with no dead cruft and docs show the live link.

### M7 — Automate the data contract `Pending`
- Add a build/sync step that copies `pipeline/data/output/*.json` into `web/src/data/`.
- **Done when:** the web app consumes pipeline output without manual file copying.

### M8 — Portfolio packaging `Pending`
- Add the UDiff project entry to the résumé (held until docs are finalised).
- **Done when:** the repo reads cleanly to a reviewer end-to-end.

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
- **Streamlit retirement:** `pipeline/legacy/` is kept for now; delete once confirmed unnecessary.
- **Original `RSGzen/UDiff` repo:** retained as the pre-merge backup; can be archived later.

### 12_10_2026 — M2 refactor + LLM upgrade, docs pass (assistant)
**Did:**
- M0 triage: `next build`/`tsc` pass, `npm run lint` fails (15 errors), pipeline un-runnable.
- M2: added `pipeline/src/config.py` (single source of truth); converted all six scripts off `os.getcwd()` to `Path(__file__)`; PEP-8 comment/whitespace pass (`ruff`).
- Upgraded the extraction model `llama3.1` → `qwen3:8b` (fits 8 GB VRAM fully) and set `think=False`; measured ~13 s → ~5 s per posting.
- Updated `README.md`, `docs/UDiff.md`, `docs/Tech Stack.md` to match.

**Did not do (next):** M3 orchestrator repair; M4 `requirements.txt`; M5 re-scrape; M6 web cleanup.
**Open items:** planned order changed to M5 (re-scrape) before finishing M4/M3, because refreshing data gates the value of the run.

---

## 4. Backlog (feature requests, carried from `future_changes.txt`)

- Compare how roles differ by years of experience (soft/hard/technical skills + salary).
- Compare university curriculums against industry reality; extract curricula that offer the courses matching demanded job skills.
- Skill detail pages: hover a skill → quick explanation + verified learning resources.
- Compare a student's current curriculum progress against industry standards (cross-off mastered skills, personal roadmap).
- UI: more modern design, more interaction/animation, and a better-fitting visual for skill distributions.

---

## 5. How to run (current, pre-refactor)

```bash
# Web (from repo root)
npm install
npm run dev            # http://localhost:3000

# Pipeline (paths resolve from the repo root; run from anywhere after `pip install -r`)
# requires: Python 3.x, Ollama running the qwen3:8b model
pip install -r pipeline/requirements.txt
python pipeline/src/pipeline.py --skip-scrape   # steps 1-4 (orchestrator repair = M3)
python pipeline/src/curriculum_generation.py    # step 5
```

> Expect path fixes in M2–M3; the above reflects the current prototype.
