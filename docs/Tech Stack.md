# UDiff — Tech Stack

UDiff is two halves: a **Python data pipeline** and a **Next.js web app**. They are decoupled through JSON files (the pipeline writes them; the web app reads them).

---

## 1. Data side (Python pipeline)

| Layer | Technology | Used for |
|---|---|---|
| Language | **Python 3.x** | All pipeline scripts |
| Job data | **JSearch API** (OpenWebNinja) over stdlib `urllib` | Fetch Malaysian job postings + descriptions |
| Data wrangling | **pandas** | CSV/JSON I/O, de-duplication, group-by aggregation |
| LLM extraction | **Ollama** running **Qwen3 8B** | Structured skill/context/experience extraction (JSON mode), and course-name generation. Runs locally on an RTX 4060 Ti 8 GB |
| Std library | `re`, `json`, `hashlib`, `subprocess`, `argparse`, `pathlib`, `urllib`, `time`, `datetime` | Text cleaning, fingerprinting, orchestration |

Data artifacts:

| File | Produced by | Notes |
|---|---|---|
| `pipeline/data/raw/job_links.csv` | `fetch_jobs.py` | Listing-level records |
| `pipeline/data/raw/job_details_full.csv` | `fetch_jobs.py` | Adds full descriptions (gitignored) |
| `pipeline/data/interim/job_analysis_final.json` | `processor.py` | LLM-extracted skills per job |
| `pipeline/data/output/gap_report.json` | `analyzer.py` (+ `salary_estimate.py`, `comparisons.py`) | Aggregated per-country report (consumed by the web app) |
| `pipeline/data/output/skill_class.json` | `curriculum_generation.py` | Per-country skill→course synonym dictionary (consumed by the web app) |
| `pipeline/data/ppp.json`, `fx.json` | hand-filled | Dated static reference tables (World Bank PPP + FX) for MYR views |
| `pipeline/logs/api.log`, `gpu.log` | `config.get_logger()` | API GET + LLM call tracing (stdout and file) |

> **Note:** paths now resolve from the repo root via `pipeline/src/config.py` (M2, done), so scripts run from any directory.

---

## 2. Web side (Next.js app)

| Layer | Technology | Used for |
|---|---|---|
| Framework | **Next.js (App Router)** | Routing/pages for dashboard, roadmap, curriculum checker |
| Language | **TypeScript** | Type-safe components and data models (`src/types`) |
| UI runtime | **React 19** | Component model |
| Styling | **Tailwind CSS 4** | Utility-first styling |
| Design system | **Tailwind 4 tokens in `src/app/globals.css`** | Single source of truth for color/radius/type (dark-first). shadcn config: `new-york`, baseColor `slate` |
| Typography | **Geist Sans + Geist Mono** (`next/font`) | Prose + tabular numbers for metrics |
| Components | **shadcn/ui** on **Radix UI** primitives | Buttons, cards, tabs, select, checkbox, progress, etc. |
| Charts | **Recharts** | Bar charts, treemap |
| Icons | **lucide-react** | UI icons |
| Data | **JSON bundled in `src/data`** | `gap_report.json`, `skill_class.json`, `roadmaps.json` |
| Deployment | **Vercel** | Live site (`udiff-web.vercel.app`) |

> **Web UI is mid-revamp.** See [`Frontend Revamp Plan.md`](Frontend%20Revamp%20Plan.md) for the
> design direction, style rules, and the Tier 0/1/2 task lists (**milestones M9–M11**).
> Known debt: components still **hardcode `slate-*` / `blue-*` colors** instead of using the
> `globals.css` tokens — that parallel palette is the #1 fix, tracked as Tier 0.

> ⚠️ `README.md` badges/claims are **stale** (they say Next.js 14 / Tailwind 3). The actual `package.json` pins **Next.js 16.1.4 / React 19.2 / Tailwind 4** — trust `package.json`.

---

## 3. Data contract between the two halves

The only interface is a set of JSON files. The pipeline emits them into `src/data/`:

- `gap_report.json` — country-nested (schema v3):
  ```jsonc
  {
    "schema_version": 3,
    "generated_at": "...",
    "countries": {
      "my": {
        "name": "Malaysia",
        "total_jobs_analyzed": 651,
        "job_distribution": { "<Role>": 0 },
        "states": { "<Region>": 0 },
        "top_companies": [{ "name": "", "count": 0, "kind": "company" }],
        "placeholder_companies": { "name": "Recruiters & confidential", "count": 0 },
        "observed_salaries": [{ "raw": "", "category": "", "title": "" }],
        "categories": {
          "<Role>": {
            "All": {
              "job_count": 0, "low_sample": false,
              "salary": { "avg_min": 0, "avg_max": 0 },
              "salary_estimate": {
                "min": 0, "median": 0, "max": 0, "currency": "", "period": "",
                "source": "", "confidence": "", "sample_size": 0, "fetched_at": "",
                "nominal_myr": { "min": 0, "median": 0, "max": 0 },
                "ppp_myr": { "min": 0, "median": 0, "max": 0 },
                "broad_estimate": false
              },
              "top_hard_skills": [{ "name": "", "count": 0, "percentage": 0 }],
              "top_soft_skills": [{ "name": "", "count": 0, "percentage": 0 }],
              "top_technical_context": [{ "name": "", "count": 0, "percentage": 0 }],
              "distinct_skills": 0
            },
            "Junior": {}, "Mid": {}, "Senior": {},
            "unknown_level": 0
          }
        }
      },
      "sg": {}, "id": {}
    },
    "comparisons": {
      "my-vs-sg": {
        "skill_gaps": [{ "skill": "", "my_pct": 0, "peer_pct": 0, "delta": 0 }],
        "salary_delta_nominal": [{ "role": "", "level": "", "my": 0, "peer": 0, "delta": 0 }],
        "salary_delta_ppp": [{ "role": "", "level": "", "my": 0, "peer": 0, "delta": 0 }]
      }
    }
  }
  ```
- `skill_class.json` — `{ generated_at, countries: { "my"|"sg"|"id": { categories: { "<Role>": { "<Skill>": ["CourseName", ...] } } } } }`.
- `roadmaps.json` — hand-authored career roadmaps (not pipeline-generated).

> ⚠️ **Schema v3 is a breaking change.** `gap_report.json` and `skill_class.json` are
> now country-nested (they were flat before M5.7). The web app must read
> `gap_report.countries.my.categories` and `skill_class.countries.my.categories`.
> `pipeline/data/ppp.json` / `fx.json` are dated static reference tables.

Keeping this contract explicit (and automating the copy step) is a goal of the planned polish (done: `sync_web_data.py`).
