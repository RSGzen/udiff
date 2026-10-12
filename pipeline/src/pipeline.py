"""
UDiff pipeline orchestrator.

Runs the whole pipeline (or a chosen subset) as subprocesses, streaming each
step's output to the console and to a log file.

    python pipeline/src/pipeline.py                          # full run
    python pipeline/src/pipeline.py --steps analyze,curriculum
    python pipeline/src/pipeline.py --skip fetch             # reuse existing data
    python pipeline/src/pipeline.py --dry-run                # show what would run
    python pipeline/src/pipeline.py --list                   # list steps
"""

import argparse
import datetime
import subprocess
import sys
import time
from pathlib import Path

import config

SRC_DIR = Path(__file__).resolve().parent
LOG_FILE = config.PIPELINE_DIR / "pipeline_log.txt"

STEPS = [
    {
        "key": "fetch",
        "name": "Job Fetcher",
        "file": "fetch_jobs.py",
        "description": "Fetching job postings from the JSearch API...",
    },
    {
        "key": "extract",
        "name": "Skill Extractor",
        "file": "processor.py",
        "description": "Extracting skills with Ollama...",
    },
    {
        "key": "analyze",
        "name": "Market Analyzer",
        "file": "analyzer.py",
        "description": "Generating the gap report...",
    },
    {
        "key": "curriculum",
        "name": "Curriculum Generator",
        "file": "curriculum_generation.py",
        "description": "Generating curriculum synonyms...",
    },
]


def tee_output(process, log_handle):
    """Stream a subprocess's stdout to both the console and the log file."""
    for line in iter(process.stdout.readline, ""):
        if not line:
            continue
        try:
            print(line.rstrip())
        except UnicodeEncodeError:
            print(line.encode("ascii", "ignore").decode("ascii").rstrip())
        log_handle.write(line)
        log_handle.flush()


def run_step(step, log_handle):
    """Run one step as a subprocess; return True on success."""
    header = f"\n{'=' * 60}\nSTEP: {step['name']}\n{step['description']}\n{'=' * 60}\n"
    print(header, end="")
    log_handle.write(header)

    script = SRC_DIR / step["file"]
    start = time.time()
    try:
        process = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )
        tee_output(process, log_handle)
        code = process.wait()
    except FileNotFoundError:
        message = f"ERROR: could not find {script}\n"
        print(message, end="")
        log_handle.write(message)
        return False

    duration = time.time() - start
    if code == 0:
        line = f"{step['name']} completed in {duration:.1f}s\n"
        print(line, end="")
        log_handle.write(line)
        return True
    line = f"ERROR: {step['name']} failed (exit code {code}) after {duration:.1f}s\n"
    print(line, end="")
    log_handle.write(line)
    return False


def select_steps(args):
    """Apply --steps/--skip/--skip-scrape to choose which steps run."""
    keys = [step["key"] for step in STEPS]

    if args.steps:
        wanted = [k.strip() for k in args.steps.split(",") if k.strip()]
        unknown = [k for k in wanted if k not in keys]
        if unknown:
            raise SystemExit(f"Unknown step(s): {', '.join(unknown)}. Valid: {', '.join(keys)}")
        return [step for step in STEPS if step["key"] in wanted]

    skipped = {k.strip() for k in (args.skip or "").split(",") if k.strip()}
    if args.skip_scrape:
        skipped.add("fetch")
    unknown = [k for k in skipped if k not in keys]
    if unknown:
        raise SystemExit(f"Unknown step(s): {', '.join(unknown)}. Valid: {', '.join(keys)}")
    return [step for step in STEPS if step["key"] not in skipped]


def main():
    parser = argparse.ArgumentParser(description="UDiff data pipeline")
    parser.add_argument("--steps", help="Comma-separated steps to run (fetch,extract,analyze,curriculum).")
    parser.add_argument("--skip", help="Comma-separated steps to skip.")
    parser.add_argument("--skip-scrape", action="store_true", help="Alias for --skip fetch.")
    parser.add_argument("--dry-run", action="store_true", help="Print steps that would run, then exit.")
    parser.add_argument("--list", action="store_true", help="List steps and exit.")
    args = parser.parse_args()

    if args.list:
        for step in STEPS:
            print(f"{step['key']:<10} {step['name']:<20} {step['description']}")
        return

    steps = select_steps(args)
    if not steps:
        raise SystemExit("No steps selected.")

    if args.dry_run:
        for step in steps:
            print(f"would run: {step['key']} ({step['file']})")
        return

    config.ensure_utf8_stdout()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        intro = f"UDiff pipeline started at {start}\n"
        print(intro, end="")
        log.write(intro)

        total = time.time()
        for step in steps:
            if not run_step(step, log):
                print("Pipeline stopped due to an error.")
                log.write("Pipeline stopped due to an error.\n")
                sys.exit(1)

        elapsed = (time.time() - total) / 60
        outro = f"\n{'=' * 60}\nPipeline finished in {elapsed:.1f} minutes\n{'=' * 60}\n"
        print(outro, end="")
        log.write(outro)

    print(f"Full log saved to {LOG_FILE}")


if __name__ == "__main__":
    main()
