"""
Central configuration for the UDiff pipeline.

Every path is resolved from THIS file's location, so scripts work no matter
which directory you run them from. Import what you need; never use os.getcwd().

    from config import JOB_LINKS_CSV, MODEL_NAME
"""

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

# --- Scraper settings ---
SEARCH_QUERIES = [
    # Core Engineering
    "Software Engineer", "Backend Developer", "Frontend Developer",
    "Fullstack Developer", "Mobile Developer",
    # Niche / High Value
    "Data Scientist", "DevOps Engineer", "Cybersecurity",
    "Embedded Engineer", "QA Engineer",
]
TARGET_PAGES = 15
HEADLESS = False  # keep False to watch the clicks happen

# --- LLM ---
MODEL_NAME = "qwen3:8b"  # fits fully on an 8 GB GPU (~5.2 GB, Q4)
MAX_DESCRIPTION_CHARS = 3500

# --- Job API (JSearch by OpenWebNinja) ---
# Replaces the retired JobStreet scrapers. Each page returns up to 10 jobs and
# consumes one API credit (~$0.005 on pay-per-use).
JSEARCH_BASE_URL = "https://api.openwebninja.com/jsearch"
JSEARCH_COUNTRY = "my"
JSEARCH_PAGES_PER_QUERY = 20  # 20 pages x 10 jobs = up to 200 jobs per query
JSEARCH_DATE_POSTED = "all"  # all | today | 3days | week | month
JSEARCH_API_KEY = load_env_key("JSEARCH_API_KEY")


def ensure_utf8_stdout() -> None:
    """Force UTF-8 stdout on Windows (emojis in logs would otherwise crash)."""
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        # `reconfigure` lives on io.TextIOWrapper; sys.stdout is only typed as
        # TextIO, hence the scoped ignore. It exists at runtime.
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


if __name__ == "__main__":
    # Self-check: paths must point inside this repo, and exist.
    assert SRC_DIR.is_dir() and (SRC_DIR / "config.py").is_file()
    assert PIPELINE_DIR.name == "pipeline"
    assert JOB_LINKS_CSV.parent == RAW_DIR
    print("SRC_DIR      ", SRC_DIR)
    print("DATA_DIR     ", DATA_DIR)
    print("WEB_DATA_DIR ", WEB_DATA_DIR)
    print("JOB_LINKS_CSV", JOB_LINKS_CSV)
    print("OK: config resolves correctly")
