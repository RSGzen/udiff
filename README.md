# UDiff: University Diff

![Next.js](https://img.shields.io/badge/Next.js-16-black) ![TypeScript](https://img.shields.io/badge/TypeScript-5-blue) ![Tailwind](https://img.shields.io/badge/Tailwind-CSS-4-38bdf8) ![Python](https://img.shields.io/badge/Python-3.x-3776AB) ![License](https://img.shields.io/badge/License-MIT-green)

**Bridging the gap between Academic Curricula and Industry Reality.**

UDiff is an end-to-end project that scrapes live job-market data, uses an LLM to extract the skills employers demand, and visualises the "gap" between what universities teach and what companies actually hire for.

> ⚠️ **Status: working prototype, pending polish.** This repo merges two previously separate repositories (a Python data pipeline and a Next.js web app). The pipeline code is experimental and needs refactoring. See [`docs/Milestones and Logs.md`](docs/Milestones%20and%20Logs.md).

**Docs:** [`docs/UDiff.md`](docs/UDiff.md) (what it is) · [`docs/Tech Stack.md`](docs/Tech%20Stack.md) (how it's built) · [`docs/Milestones and Logs.md`](docs/Milestones%20and%20Logs.md) (plan + logs)

## 🔗 Live site
[Have a look for yourself!](https://udiff-web.vercel.app/)

## 🧭 How it works

```
JobStreet ──scrape──▶ job_links.csv ──scrape──▶ job_details_full.csv
        ──LLM extract──▶ job_analysis_final.json
        ──aggregate──▶ gap_report.json ──LLM──▶ skill_class.json
                                                       │
                                    Next.js dashboard ◀┘ (+ roadmaps.json)
```

- **Data side (`pipeline/`)** — Python. Playwright + BeautifulSoup scrape postings; pandas cleans/dedupes; a local **Llama 3.1 8B** (Ollama) extracts hard/soft skills, technical context, and experience level; pandas aggregates a per-role gap report.
- **Web side (repo root)** — Next.js 16 / React 19 / TypeScript / Tailwind 4, with Recharts and shadcn/ui, deployed on Vercel.

## 🚀 Features

### 1. Market Gap Dashboard
- **Visualization:** interactive bar charts and treemaps (Recharts) of the most in-demand hard skills and technical contexts.
- **Smart Filtering:** segment by role (Backend, AI, Security, …) and seniority (Junior, Mid, Senior).
- **Focus Mode:** interactive "dim & focus" UX to highlight key data points.

![Dashboard Screenshot](/public/screenshots/main_page1.png)

### 2. Gamified Career Roadmaps
- A "tech tree" style roadmap for 15+ career paths (foundation → core → advanced), with phase-locking and persisted local progress.

![Roadmap Screenshot](/public/screenshots/career_path1.png)

### 3. Curriculum Gap Analyzer (Beta)
- Client-side keyword matcher that scans a syllabus against market demand using a pre-computed skill/curriculum dictionary (`skill_class.json`).

![Curriculum Screenshot](/public/screenshots/curriculum_check1.png)

## 📦 Getting started

### Web app
```bash
npm install
npm run dev        # http://localhost:3000
```

### Data pipeline (run from the repo ROOT)
```bash
# requires Python 3.x and Ollama running with the 'llama3.1' model
pip install -r pipeline/requirements.txt
python pipeline/src/pipeline.py --skip-scrape   # steps 1-4
python pipeline/src/curriculum_generation.py    # step 5 (not yet in the orchestrator)
```
> Paths currently use `os.getcwd()`, so the pipeline must be run from the repo root. This is scheduled to be fixed (see docs).

## 📂 Project structure

```
.
├── docs/                     # UDiff.md, Tech Stack.md, Milestones and Logs.md
├── pipeline/                 # Python data pipeline
│   ├── src/                  # scraper, processor, analyzer, curriculum, orchestrator
│   ├── data/{raw,interim,output}
│   ├── legacy/               # retired Streamlit dashboard
│   └── requirements.txt
├── src/                      # Next.js app (app router, components, data, types)
├── public/                   # static assets + screenshots
└── README.md
```

## 🛠️ Tech stack

- **Data:** Python, Playwright, BeautifulSoup, pandas, Ollama (Llama 3.1 8B)
- **Web:** Next.js 16, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Recharts
- **Deploy:** Vercel

## 🔮 Roadmap

See [`docs/Milestones and Logs.md`](docs/Milestones%20and%20Logs.md). Highlights: refactor pipeline paths/config, single robust entrypoint, re-scrape & refresh data, web cleanup, automate the JSON data contract.

## 📄 License

MIT (see `LICENSE`). Note: the pipeline was previously under GPLv3 (`pipeline/LICENSE-GPLv3.txt`); licensing is pending reconciliation by the owner.
