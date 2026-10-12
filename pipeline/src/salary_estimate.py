"""
Enrich gap_report.json with estimated market salaries from the JSearch
/estimated-salary endpoint (publisher data via Glassdoor).

This is a *separate*, labelled metric: it does NOT replace the posting-derived
`salary` (which search-v2 rarely provides). Each category's `All`/`Junior`/
`Mid`/`Senior` block gets a `salary_estimate` dict — but only when the publisher
sample is trustworthy (see is_reliable).
"""

import argparse
import json

import config
from fetch_jobs import api_get, api_url

# A representative job title per category, used for the salary lookup.
CATEGORY_TITLES = {
    "General Software Engineering": "Software Engineer",
    "Backend": "Backend Developer",
    "Frontend Web": "Frontend Developer",
    "Fullstack": "Full Stack Developer",
    "Mobile Development": "Mobile Developer",
    "Data & Analytics": "Data Analyst",
    "AI & Machine Learning": "Machine Learning Engineer",
    "Cloud & DevOps": "DevOps Engineer",
    "Cybersecurity": "Cybersecurity Analyst",
    "QA & Testing": "QA Engineer",
    "Network & Infrastructure": "Network Engineer",
    "IT Support": "IT Support Engineer",
    "Hardware & Manufacturing": "Hardware Engineer",
    "Embedded/Systems": "Embedded Software Engineer",
    "Project & Sales Engineering": "Solutions Engineer",
    "Internship & Entry Level": "Software Engineer",
}

# Map our experience levels onto the endpoint's years-of-experience buckets.
LEVEL_YEARS = {
    "All": "ALL",
    "Junior": "ONE_TO_THREE",
    "Mid": "FOUR_TO_SIX",
    "Senior": "SEVEN_TO_NINE",
}

# Keep only estimates the publisher is reasonably sure about.
MIN_CONFIDENCE = {"HIGH", "VERY_HIGH"}
MIN_SAMPLE_SIZE = 3


def is_reliable(estimate):
    """True if the publisher sample is large and confident enough to show."""
    if not estimate:
        return False
    return (
        estimate.get("confidence") in MIN_CONFIDENCE
        and (estimate.get("sample_size") or 0) >= MIN_SAMPLE_SIZE
    )


def parse_estimate(rows):
    """Turn the endpoint's list response into our salary_estimate dict."""
    if not rows:
        return None
    row = rows[0]
    return {
        "min": row.get("min_salary"),
        "median": row.get("median_salary"),
        "max": row.get("max_salary"),
        "currency": row.get("salary_currency"),
        "period": row.get("salary_period"),
        "source": f"{row.get('publisher_name') or 'publisher'} via JSearch",
        "confidence": row.get("confidence"),
        "sample_size": row.get("salary_count"),
    }


def fetch_estimate(title, level):
    """Return a salary_estimate for one title + level, or None."""
    url = api_url("estimated-salary", {
        "job_title": title,
        "location": "Malaysia",
        "location_type": "COUNTRY",
        "years_of_experience": LEVEL_YEARS.get(level, "ALL"),
    })
    payload = api_get(url)
    rows = payload.get("data") if isinstance(payload, dict) else payload
    if isinstance(rows, dict):
        rows = rows.get("jobs") or []
    return parse_estimate(rows)


def load_report():
    with open(config.GAP_REPORT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_report(report):
    with open(config.GAP_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)


def prune(report):
    """Remove stored estimates that no longer pass the reliability guard."""
    removed = 0
    for levels in report["categories"].values():
        for block in levels.values():
            if block.get("salary_estimate") and not is_reliable(block["salary_estimate"]):
                del block["salary_estimate"]
                removed += 1
    return removed


def main():
    parser = argparse.ArgumentParser(description="Add estimated salaries to gap_report.json.")
    parser.add_argument("--self-test", action="store_true", help="Offline checks.")
    parser.add_argument("--prune", action="store_true",
                        help="Drop low-confidence stored estimates (no API call).")
    args = parser.parse_args()
    config.ensure_utf8_stdout()

    if args.self_test:
        self_test()
        return

    report = load_report()

    if args.prune:
        removed = prune(report)
        save_report(report)
        print(f"Pruned {removed} unreliable estimate(s) from {config.GAP_REPORT_JSON}")
        return

    for category, levels in report["categories"].items():
        title = CATEGORY_TITLES.get(category, category)
        for level, block in levels.items():
            estimate = fetch_estimate(title, level)
            if is_reliable(estimate):
                block["salary_estimate"] = estimate
            median = estimate and estimate.get("median")
            conf = estimate and estimate.get("confidence")
            size = estimate and estimate.get("sample_size")
            print(f"{category} / {level}: {median} {estimate and estimate.get('currency')} "
                  f"[{conf}, n={size}]")

    save_report(report)
    print(f"Saved estimated salaries to {config.GAP_REPORT_JSON}")


def self_test():
    """Offline check of the mapping, parsing and reliability guard."""
    sample = [{
        "location": "Malaysia",
        "job_title": "Backend Developer",
        "min_salary": 5000,
        "max_salary": 9000,
        "median_salary": 7000,
        "salary_period": "MONTH",
        "salary_currency": "MYR",
        "salary_count": 5,
        "publisher_name": "Glassdoor",
        "confidence": "CONFIDENT",
    }]
    estimate = parse_estimate(sample)
    assert estimate["median"] == 7000
    assert estimate["currency"] == "MYR"
    assert estimate["source"] == "Glassdoor via JSearch"
    assert estimate["sample_size"] == 5
    assert parse_estimate([]) is None
    assert LEVEL_YEARS["Mid"] == "FOUR_TO_SIX"
    assert "estimated-salary?" in api_url("estimated-salary", {"a": "b"})
    # reliability guard
    assert is_reliable({"confidence": "HIGH", "sample_size": 5})
    assert is_reliable({"confidence": "VERY_HIGH", "sample_size": 600})
    assert not is_reliable({"confidence": "LOW", "sample_size": 2})
    assert not is_reliable({"confidence": "HIGH", "sample_size": 1})
    assert not is_reliable(None)
    print("self-test OK")


if __name__ == "__main__":
    main()
