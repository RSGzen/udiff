"""
Enrich gap_report.json with estimated market salaries from the JSearch
/estimated-salary endpoint (publisher data via Glassdoor).

This is a *separate*, labelled metric: it does NOT replace the posting-derived
`salary` (which search-v2 rarely provides). Each category's `All`/`Junior`/
`Mid`/`Senior` block gets a `salary_estimate` dict.
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


def main():
    parser = argparse.ArgumentParser(description="Add estimated salaries to gap_report.json.")
    parser.add_argument("--self-test", action="store_true", help="Offline checks.")
    args = parser.parse_args()
    config.ensure_utf8_stdout()

    if args.self_test:
        self_test()
        return

    with open(config.GAP_REPORT_JSON, "r", encoding="utf-8") as f:
        report = json.load(f)

    for category, levels in report["categories"].items():
        title = CATEGORY_TITLES.get(category, category)
        for level, block in levels.items():
            estimate = fetch_estimate(title, level)
            if estimate:
                block["salary_estimate"] = estimate
            median = estimate and estimate.get("median")
            print(f"{category} / {level}: {median} {estimate and estimate.get('currency')}")

    with open(config.GAP_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"Saved estimated salaries to {config.GAP_REPORT_JSON}")


def self_test():
    """Offline check of the mapping and parsing (no API call)."""
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
    print("self-test OK")


if __name__ == "__main__":
    main()
