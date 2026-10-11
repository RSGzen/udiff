# UDiff — Tech Stack

UDiff is two halves: a **Python data pipeline** and a **Next.js web app**. They are decoupled through JSON files (the pipeline writes them; the web app reads them).

---

## 1. Data side (Python pipeline)

| Layer | Technology | Used for |
|---|---|---|
| Language | **Python 3.x** | All pipeline scripts |
| Scraping | **Playwright** (sync API, Chromium) | Drive the job board, paginate, click "Next", render lazy content, extract listing fields |
| HTML parsing | **BeautifulSoup 4** (+ `html.parser`) | Pull the job-description container out of the fetched page |
| Data wrangling | **pandas** | CSV/JSON I/O, de-duplication, group-by aggregation |
| LLM extraction | **Ollama** running **Qwen3 8B** | Structured skill/context/experience extraction (JSON mode), and course-name generation. Runs locally on an RTX 4060 Ti 8 GB |
| Std library | `re`, `json`, `hashlib`, `subprocess`, `argparse`, `pathlib`/`os`, `time`, `datetime` | Text cleaning, fingerprinting, orchestration |
| Legacy dashboard | **Streamlit** + **Plotly** + **WordCloud** + **matplotlib** | The retired prototype dashboard (`pipeline/legacy/dashboard.py`) |
| Legacy packaging | **Docker** | Used to deploy the retired Streamlit dashboard |

Data artifacts:

| File | Produced by | Notes |
|---|---|---|
| `pipeline/data/raw/job_links.csv` | `scraper.py` | Listing-level records |
| `pipeline/data/raw/job_details_full.csv` | `scraper_details.py` | Adds full descriptions |
| `pipeline/data/interim/job_analysis_final.json` | `processor.py` | LLM-extracted skills per job |
| `pipeline/data/output/gap_report.json` | `analyzer.py` | Aggregated market report (consumed by the web app) |
| `pipeline/data/output/skill_class.json` | `curriculum_generation.py` | Skill→course synonym dictionary (consumed by the web app) |

> **Note:** paths now resolve from the repo root via `pipeline/src/config.py` (M2, done), so scripts run from any directory.

---

## 2. Web side (Next.js app)

| Layer | Technology | Used for |
|---|---|---|
| Framework | **Next.js (App Router)** | Routing/pages for dashboard, roadmap, curriculum checker |
| Language | **TypeScript** | Type-safe components and data models (`src/types`) |
| UI runtime | **React 19** | Component model |
| Styling | **Tailwind CSS 4** | Utility-first styling |
| Components | **shadcn/ui** on **Radix UI** primitives | Buttons, cards, tabs, select, checkbox, progress, etc. |
| Charts | **Recharts** | Bar charts, treemap |
| Icons | **lucide-react** | UI icons |
| Data | **JSON bundled in `src/data`** | `gap_report.json`, `skill_class.json`, `roadmaps.json` |
| Deployment | **Vercel** | Live site (`udiff-web.vercel.app`) |

> ⚠️ `README.md` badges/claims are **stale** (they say Next.js 14 / Tailwind 3). The actual `package.json` pins **Next.js 16.1.4 / React 19.2 / Tailwind 4** — trust `package.json`.

---

## 3. Data contract between the two halves

The only interface is a set of JSON files. The pipeline must emit them into `web/src/data/`:

- `gap_report.json` — `{ generated_at, total_jobs_analyzed, job_distribution, categories: { <Role>: { All|Junior|Mid|Senior: { job_count, salary, top_hard_skills, top_soft_skills, top_technical_context } } } }`
- `skill_class.json` — skill → candidate course names (rename of the pipeline's `skill_curriculum_synonyms.json`).
- `roadmaps.json` — hand-authored career roadmaps (not pipeline-generated).

Keeping this contract explicit (and ideally automating the copy step) is a goal of the planned polish.
