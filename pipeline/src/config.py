"""
Central configuration for the UDiff pipeline.

Every path is resolved from THIS file's location, so scripts work no matter
which directory you run them from. Import what you need; never use os.getcwd().

    from config import JOB_LINKS_CSV, MODEL_NAME
"""

import logging
import os
import sys
from pathlib import Path

# --- Locations (resolved from this file, not the cwd) ---
SRC_DIR = Path(__file__).resolve().parent        # pipeline/src
PIPELINE_DIR = SRC_DIR.parent                    # pipeline
PROJECT_ROOT = PIPELINE_DIR.parent               # repo root

DATA_DIR = PIPELINE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
OUTPUT_DIR = DATA_DIR / "output"
LOG_DIR = PIPELINE_DIR / "logs"

# The Next.js app bundles its JSON from here (see docs: data contract).
WEB_DATA_DIR = PROJECT_ROOT / "src" / "data"


def load_env_key(name: str) -> str:
    """Read a secret from the environment, then fall back to pipeline/.env."""
    value = os.environ.get(name)
    if value:
        return value
    env_file = PIPELINE_DIR / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            if key.strip() == name:
                return val.strip().strip('"').strip("'")
    return ""

# --- Pipeline artifacts (single source of truth) ---
JOB_LINKS_CSV = RAW_DIR / "job_links.csv"
JOB_DETAILS_CSV = RAW_DIR / "job_details_full.csv"
JOB_ANALYSIS_JSON = INTERIM_DIR / "job_analysis_final.json"
GAP_REPORT_JSON = OUTPUT_DIR / "gap_report.json"
SKILL_CLASS_JSON = OUTPUT_DIR / "skill_class.json"
# Static, dated reference tables for the SEA salary comparison (M5.7).
PPP_JSON = DATA_DIR / "ppp.json"
FX_JSON = DATA_DIR / "fx.json"

# --- Job search queries (used by fetch_jobs.py) ---
SEARCH_QUERIES = [
    # Core Engineering
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Fullstack Developer", "Mobile Developer",
    # Niche / High Value
    "Data Scientist", "DevOps Engineer", "Cybersecurity",
    "Embedded Engineer", "QA Engineer",
]

# --- LLM ---
MODEL_NAME = "qwen3:8b"  # fits fully on an 8 GB GPU (~5.2 GB, Q4)
MAX_DESCRIPTION_CHARS = 3500

# --- Job API (JSearch by OpenWebNinja) ---
# Replaces the retired JobStreet scrapers. Each page returns up to 10 jobs and
# consumes one API credit (~$0.005 on pay-per-use).
JSEARCH_BASE_URL = "https://api.openwebninja.com/jsearch"
JSEARCH_COUNTRY = "my"
JSEARCH_PAGES_PER_QUERY = 10  # multi-country budget: 10 queries x 10 pages ~= 1,000/country
JSEARCH_PAGES_PER_REQUEST = 5  # pages per HTTP call, to avoid gateway timeouts
JSEARCH_DATE_POSTED = "all"  # all | today | 3days | week | month
JSEARCH_API_KEY = load_env_key("JSEARCH_API_KEY")

# --- Multi-country expansion (M5.7) ---
# The API needs the location IN the query plus `country` + `language` together,
# or non-US results fall back to US (verified in Phase 0, 12 Oct 2026).
LANGUAGE = "en"
COUNTRIES = [
    {"code": "my", "name": "Malaysia", "location": "Malaysia"},
    {"code": "sg", "name": "Singapore", "location": "Singapore"},
    {"code": "id", "name": "Indonesia", "location": "Jakarta, Indonesia"},
]
# VN dropped: language=en returns zero postings (Phase 0); VN ads are vi-only.


def ensure_utf8_stdout() -> None:
    """Force UTF-8 stdout on Windows (emojis in logs would otherwise crash)."""
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        # `reconfigure` lives on io.TextIOWrapper; sys.stdout is only typed as
        # TextIO, hence the scoped ignore. It exists at runtime.
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def get_logger(name, filename=None):
    """Return a logger that writes to the terminal AND (optionally) pipeline/logs/.

    Traceability for the API GET calls and the GPU extraction runs: each line
    reaches stdout (so the orchestrator's tee also captures it) and its own
    text file. Repeated calls with the same name reuse the same logger.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if filename:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_DIR / filename, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


if __name__ == "__main__":
    # Self-check: paths must point inside this repo, and exist.
    assert SRC_DIR.is_dir() and (SRC_DIR / "config.py").is_file()
    assert PIPELINE_DIR.name == "pipeline"
    assert JOB_LINKS_CSV.parent == RAW_DIR
    assert PPP_JSON.parent == DATA_DIR and FX_JSON.parent == DATA_DIR
    assert [c["code"] for c in COUNTRIES] == ["my", "sg", "id"]
    assert LANGUAGE == "en"
    print("SRC_DIR      ", SRC_DIR)
    print("DATA_DIR     ", DATA_DIR)
    print("LOG_DIR      ", LOG_DIR)
    print("WEB_DATA_DIR ", WEB_DATA_DIR)
    print("JOB_LINKS_CSV", JOB_LINKS_CSV)
    # Logger self-check: two handlers (stdout + file), same logger on reuse.
    test_log = get_logger("config_self_test", "self_test.log")
    assert len(test_log.handlers) == 2
    assert get_logger("config_self_test", "other.log") is test_log
    print("OK: config resolves correctly")
