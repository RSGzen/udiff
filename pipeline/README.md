# UDiff data pipeline

Fetches job postings for Malaysia, Singapore and Indonesia, and turns them into
the two JSON files the web app reads (the shape is defined in `src/types/index.ts`).

## Layout

```
pipeline/
  src/
    config.py               # paths, settings, countries, secrets (.env loader)
    fetch_jobs.py           # JSearch API per country -> data/raw/*.csv
    processor.py            # Ollama (resumable) -> data/interim/job_analysis_final.json
    analyzer.py             # per-country aggregation -> data/output/gap_report.json
    salary_estimate.py      # JSearch /estimated-salary (+ MYR & PPP views)
    comparisons.py          # my-vs-sg / my-vs-id deltas -> gap_report.comparisons
    curriculum_generation.py# Ollama per country -> data/output/skill_class.json
    companies.py            # company vs recruiter/confidential classifier (P9)
    locations.py            # raw location -> MY state / country region
    sync_web_data.py        # -> ../../src/data/*.json
    probe_countries.py      # dev utility: Phase-0 English-yield probe
    inspect_others.py       # dev utility: unclassified job titles
    pipeline.py             # orchestrator (runs the steps above)
  data/
    raw/ interim/ output/
    ppp.json fx.json        # dated static reference tables (PPP + FX)
  logs/                     # api.log, gpu.log (terminal + file tracing)
```

## Run

```bash
pip install -r pipeline/requirements.txt
python pipeline/src/pipeline.py                 # full run
python pipeline/src/pipeline.py --skip fetch    # reuse existing data
python pipeline/src/pipeline.py --list
```

Requires Python 3.x, Ollama serving `qwen3:8b`, and `JSEARCH_API_KEY` in
`pipeline/.env` (see `.env.example`).

## Tracing

Every pipeline step writes to stdout (also teed to `pipeline_log.log` by the
orchestrator). The API GET calls and every LLM call additionally get their own
timestamped file: `pipeline/logs/api.log` and `pipeline/logs/gpu.log`.

## Notes

- Non-US JSearch queries need the location **inside** the query string plus
  `country` + `language` together, or results silently fall back to the US.
- Vietnam is not covered: `language=en` returns zero VN postings (see the
  Phase-0 probe in `probe_countries.py`).
- `pipeline/data/ppp.json` and `fx.json` are hand-filled, dated reference tables.

