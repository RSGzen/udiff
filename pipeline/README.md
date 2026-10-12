# UDiff data pipeline

Fetches Malaysian job postings and turns them into the two JSON files the web
app reads. See `docs/UDiff.md` for the full picture.

## Layout

```
pipeline/
  src/
    config.py               # paths, settings, secrets (.env loader)
    fetch_jobs.py           # JSearch API  -> data/raw/*.csv
    processor.py            # Ollama        -> data/interim/job_analysis_final.json
    analyzer.py             # aggregation   -> data/output/gap_report.json
    curriculum_generation.py# Ollama        -> data/output/skill_class.json
    sync_web_data.py        #               -> ../../src/data/*.json
    inspect_others.py       # dev utility: unclassified job titles
    pipeline.py             # orchestrator (runs the steps above)
  data/{raw,interim,output}/
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
