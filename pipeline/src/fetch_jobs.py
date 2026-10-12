"""
Fetch Malaysian tech job postings from JSearch (OpenWebNinja) into the
pipeline data contract. Replaces the retired JobStreet scrapers.

Reads config.SEARCH_QUERIES, calls the /search-v2 API, and writes:
    data/raw/job_links.csv         search_term,title,company,location,salary,link
    data/raw/job_details_full.csv  the same columns + description

Requires JSEARCH_API_KEY (environment or pipeline/.env).
"""

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

import config

SEARCH_ENDPOINT = f"{config.JSEARCH_BASE_URL}/search-v2"
LINK_COLUMNS = ["search_term", "title", "company", "location", "salary", "link"]


def build_search_url(query, cursor="", pages=None):
    """Build the /search-v2 URL for one query batch (one page = one credit)."""
    params = {
        "query": query,
        "country": config.JSEARCH_COUNTRY,
        "num_pages": pages or config.JSEARCH_PAGES_PER_QUERY,
        "date_posted": config.JSEARCH_DATE_POSTED,
    }
    if cursor:
        params["cursor"] = cursor
    return f"{SEARCH_ENDPOINT}?{urllib.parse.urlencode(params)}"


def format_salary(job):
    """Format JSearch salary numbers into the string the processor expects."""
    lo = job.get("job_min_salary")
    hi = job.get("job_max_salary")
    if not lo and not hi:
        return "Not Specified"
    lo, hi = lo or hi, hi or lo
    currency = job.get("job_salary_currency") or "RM"
    value = (
        f"{currency} {lo:,.0f}"
        if lo == hi
        else f"{currency} {lo:,.0f} - {hi:,.0f}"
    )
    period = (job.get("job_salary_period") or "").lower()
    return f"{value} per {period}" if period else value


def to_row(query, job):
    """Map one JSearch job object onto our CSV row."""
    location = job.get("job_location") or ", ".join(
        part
        for part in (job.get("job_city"), job.get("job_state"), job.get("job_country"))
        if part
    )
    return {
        "search_term": query,
        "title": job.get("job_title") or "",
        "company": job.get("employer_name") or "Confidential",
        "location": location or "Malaysia",
        "salary": format_salary(job),
        "link": job.get("job_apply_link") or job.get("job_google_link") or "",
        "description": job.get("job_description") or "",
    }


def fetch_query(query, cursor="", pages=None, attempts=4):
    """Call the API once, retrying transient gateway/rate-limit errors."""
    request = urllib.request.Request(
        build_search_url(query, cursor, pages),
        headers={"x-api-key": config.JSEARCH_API_KEY},
    )
    last_error = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise last_error


def fetch_query_pages(query, total_pages):
    """Fetch up to total_pages for one query, chunked via the cursor."""
    jobs = []
    cursor = ""
    fetched = 0
    while fetched < total_pages:
        chunk = min(config.JSEARCH_PAGES_PER_REQUEST, total_pages - fetched)
        payload = fetch_query(query, cursor=cursor, pages=chunk)
        data = payload.get("data") or {}
        if not isinstance(data, dict):
            jobs.extend(data)
            break
        jobs.extend(data.get("jobs") or [])
        fetched += chunk
        cursor = data.get("cursor")
        if not cursor:
            break
    return jobs


def fetch_all(queries=None, pages=None):
    """Run the given queries and return a de-duplicated DataFrame."""
    if not config.JSEARCH_API_KEY:
        raise SystemExit(
            "JSEARCH_API_KEY is not set. Add it to pipeline/.env or the environment."
        )

    target = pages or config.JSEARCH_PAGES_PER_QUERY
    rows = []
    seen = set()
    for query in queries or config.SEARCH_QUERIES:
        print(f"Searching '{query}'...", end=" ", flush=True)
        jobs = fetch_query_pages(query, target)
        new = 0
        for job in jobs:
            key = job.get("job_id") or job.get("job_apply_link")
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append(to_row(query, job))
            new += 1
        print(f"{new} new (total {len(rows)})")
    return pd.DataFrame(rows, columns=LINK_COLUMNS + ["description"])


def save(df):
    config.JOB_DETAILS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.JOB_LINKS_CSV, columns=LINK_COLUMNS, index=False)
    df.to_csv(config.JOB_DETAILS_CSV, index=False)
    print(f"Saved {len(df)} jobs to {config.JOB_DETAILS_CSV}")


def self_test():
    """Offline check of the mapping/salary/URL logic (no API call)."""
    sample = {
        "job_title": "Backend Developer",
        "employer_name": "Acme",
        "job_location": "Kuala Lumpur, Malaysia",
        "job_city": "Kuala Lumpur",
        "job_country": "MY",
        "job_min_salary": 5000,
        "job_max_salary": 7000,
        "job_salary_currency": "MYR",
        "job_salary_period": "MONTH",
        "job_apply_link": "https://example.com/job/1",
        "job_description": "Python and AWS.",
    }
    row = to_row("Backend Developer", sample)
    assert row["title"] == "Backend Developer"
    assert row["location"] == "Kuala Lumpur, Malaysia"
    assert row["salary"] == "MYR 5,000 - 7,000 per month", row["salary"]
    assert row["description"] == "Python and AWS."
    # job_location is preferred; city/state/country is the fallback.
    assert to_row("x", {})["company"] == "Confidential"
    assert to_row("x", {"job_city": "Penang"})["location"] == "Penang"
    assert format_salary({}) == "Not Specified"
    assert "search-v2?" in build_search_url("x")
    print("self-test OK")


def main():
    parser = argparse.ArgumentParser(description="Fetch jobs from JSearch into the pipeline.")
    parser.add_argument("--self-test", action="store_true", help="Offline mapping checks.")
    parser.add_argument("--pages", type=int, help="Pages per query (default from config; 1-20).")
    parser.add_argument("--only", help="Comma-separated subset of search queries to run.")
    args = parser.parse_args()

    config.ensure_utf8_stdout()
    if args.self_test:
        self_test()
        return

    queries = args.only.split(",") if args.only else None
    df = fetch_all(queries=queries, pages=args.pages)
    if df.empty:
        print("No jobs fetched.")
        return
    save(df)


if __name__ == "__main__":
    main()
