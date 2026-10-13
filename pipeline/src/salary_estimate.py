"""
Enrich gap_report.json with estimated market salaries from the JSearch
/estimated-salary endpoint (publisher data via Glassdoor), per country (M5.7).

This is a *separate*, labelled metric: it does NOT replace the posting-derived
`salary` (which search-v2 rarely provides). Each category's `All`/`Junior`/
`Mid`/`Senior` block gets a `salary_estimate` dict — but only when the publisher
sample is trustworthy (see is_reliable). For non-MY markets the local currency
estimate is also converted to nominal MYR (FX) and PPP-adjusted MYR.
"""

import argparse
import json
import time

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

# Ordinal rank used to keep the broad (All) fallback from inverting seniority.
LEVEL_RANK = {"Junior": 1, "Mid": 2, "Senior": 3}

# Keep only estimates the publisher is reasonably sure about.
MIN_CONFIDENCE = {"HIGH", "VERY_HIGH"}
MIN_SAMPLE_SIZE = 3

MONEY_KEYS = ("min", "median", "max")


def is_reliable(estimate):
    """True if the publisher sample is large and confident enough to show."""
    if not estimate:
        return False
    return (
        estimate.get("confidence") in MIN_CONFIDENCE
        and (estimate.get("sample_size") or 0) >= MIN_SAMPLE_SIZE
    )


def normalize_period(estimate):
    """Convert year-based estimates to monthly so every level is comparable.

    The /estimated-salary endpoint returns YEAR for some (title, level, country)
    combos; treating those as monthly inflated them ~12x (e.g. SG AI&ML Mid).
    """
    if not estimate:
        return estimate
    period = (estimate.get("period") or "").upper()
    estimate["period_raw"] = period or None
    if period == "YEAR":
        for key in MONEY_KEYS:
            if estimate.get(key) is not None:
                estimate[key] = round(estimate[key] / 12, 2)
        estimate["period"] = "MONTH"
    return estimate


def parse_estimate(rows):
    """Turn the endpoint's list response into our salary_estimate dict."""
    if not rows:
        return None
    row = rows[0]
    estimate = {
        "min": row.get("min_salary"),
        "median": row.get("median_salary"),
        "max": row.get("max_salary"),
        "currency": row.get("salary_currency"),
        "period": row.get("salary_period"),
        "source": f"{row.get('publisher_name') or 'publisher'} via JSearch",
        "confidence": row.get("confidence"),
        "sample_size": row.get("salary_count"),
        "fetched_at": time.strftime("%Y-%m-%d"),
    }
    return normalize_period(estimate)


def load_table(path):
    """Load a JSON reference table, or {} if it is missing/blank."""
    if not path.is_file():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_conversions(estimate, code, ppp_factors, fx_rates):
    """Add nominal-MYR and PPP-MYR views (M5.7) when the tables are filled in."""
    per = fx_rates.get(code)
    f_local = ppp_factors.get(code)
    f_my = ppp_factors.get("my")

    def scale(factor):
        return {k: round(estimate[k] * factor, 2)
                for k in MONEY_KEYS if estimate.get(k) is not None}

    if per and per > 0:
        estimate["nominal_myr"] = scale(1 / per)
    if f_local and f_local > 0 and f_my:
        estimate["ppp_myr"] = scale(f_my / f_local)
    return estimate


def fetch_estimate(title, level, location="Malaysia"):
    """Return a salary_estimate for one title + level + market, or None."""
    url = api_url("estimated-salary", {
        "job_title": title,
        "location": location,
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
    for block in report["countries"].values():
        for levels in block["categories"].values():
            for level, entry in levels.items():
                if isinstance(entry, dict) and entry.get("salary_estimate") \
                        and not is_reliable(entry["salary_estimate"]):
                    del entry["salary_estimate"]
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

    ppp_factors = load_table(config.PPP_JSON).get("factor", {})
    fx_rates = load_table(config.FX_JSON).get("per_myr", {})

    for country in config.COUNTRIES:
        code = country["code"]
        block = report.get("countries", {}).get(code)
        if not block:
            continue
        print(f"\n=== {country['name']} ({code.upper()}) ===")
        for category, levels in block["categories"].items():
            title = CATEGORY_TITLES.get(category, category)
            all_estimate = None
            level_medians = {}
            for level, entry in levels.items():
                if not isinstance(entry, dict):   # skips 'unknown_level' etc.
                    continue
                estimate = fetch_estimate(title, level, country["name"])
                if is_reliable(estimate):
                    add_conversions(estimate, code, ppp_factors, fx_rates)
                    entry["salary_estimate"] = estimate
                if level == "All" and entry.get("salary_estimate"):
                    all_estimate = entry["salary_estimate"]
                elif level != "All" and "salary_estimate" not in entry and all_estimate:
                    # P5: no level-specific sample -> show the All-market
                    # estimate, but only if it won't invert seniority order.
                    rank = LEVEL_RANK.get(level, 0)
                    lower = [m for lv, m in level_medians.items()
                             if LEVEL_RANK.get(lv, 0) < rank]
                    all_median = all_estimate.get("median")
                    if all_median is not None and (not lower or all_median >= max(lower)):
                        entry["salary_estimate"] = {**all_estimate, "broad_estimate": True}
                    else:
                        print(f"  {category} / {level}: broad fallback suppressed "
                              f"(would invert order)")
                se = entry.get("salary_estimate")
                if isinstance(se, dict) and se.get("median") is not None \
                        and not se.get("broad_estimate"):
                    level_medians[level] = se["median"]
                median = estimate and estimate.get("median")
                conf = estimate and estimate.get("confidence")
                print(f"  {category} / {level}: {median} "
                      f"{estimate and estimate.get('currency')} [{conf}]")

    save_report(report)
    print(f"\nSaved estimated salaries to {config.GAP_REPORT_JSON}")


def self_test():
    """Offline check of the mapping, parsing, reliability and conversion."""
    sample = [{
        "location": "Singapore",
        "job_title": "Backend Developer",
        "min_salary": 5000,
        "max_salary": 9000,
        "median_salary": 7000,
        "salary_period": "MONTH",
        "salary_currency": "SGD",
        "salary_count": 5,
        "publisher_name": "Glassdoor",
        "confidence": "HIGH",
    }]
    estimate = parse_estimate(sample)
    assert estimate["median"] == 7000
    assert estimate["currency"] == "SGD"
    assert estimate["source"] == "Glassdoor via JSearch"
    assert estimate["sample_size"] == 5
    assert estimate["fetched_at"]
    assert parse_estimate([]) is None
    assert LEVEL_YEARS["Mid"] == "FOUR_TO_SIX"
    assert "estimated-salary?" in api_url("estimated-salary", {"a": "b"})
    # reliability guard
    assert is_reliable({"confidence": "HIGH", "sample_size": 5})
    assert not is_reliable({"confidence": "LOW", "sample_size": 2})
    assert not is_reliable(None)
    # conversions: 7000 SGD at 0.30 SGD per MYR -> 23,333.33 MYR nominal
    add_conversions(estimate, "sg", {"my": 1.8, "sg": 0.9}, {"my": 1.0, "sg": 0.30})
    assert estimate["nominal_myr"]["median"] == round(7000 / 0.30, 2)
    assert estimate["ppp_myr"]["median"] == round(7000 / 0.9 * 1.8, 2)
    # YEAR is normalised to MONTH (kept period_raw for provenance)
    year = parse_estimate([{**sample[0], "salary_period": "YEAR",
                            "min_salary": 90000, "median_salary": 120000,
                            "max_salary": 180000}])
    assert year["period"] == "MONTH" and year["period_raw"] == "YEAR"
    assert year["median"] == 10000.0 and year["min"] == 7500.0
    # missing tables -> no conversion keys
    bare = parse_estimate(sample)
    add_conversions(bare, "sg", {}, {})
    assert "nominal_myr" not in bare and "ppp_myr" not in bare
    print("self-test OK")


if __name__ == "__main__":
    main()
