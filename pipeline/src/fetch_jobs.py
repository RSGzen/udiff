"""
Fetch tech job postings from JSearch (OpenWebNinja) into the pipeline data
contract, across config.COUNTRIES (M5.7). Replaces the retired JobStreet scrapers.

Reads config.SEARCH_QUERIES and config.COUNTRIES, calls the /search-v2 API, and
writes:
    data/raw/job_links.csv         search_term,title,company,location,salary,link,country
    data/raw/job_details_full.csv  the same columns + description + posted_at

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

LINK_COLUMNS = ["search_term", "title", "company", "location", "salary", "link", "country"]

log = config.get_logger("api", "api.log")


def api_url(path, params):
    """Build a full JSearch URL for an endpoint path and query params."""
    return f"{config.JSEARCH_BASE_URL}/{path}?{urllib.parse.urlencode(params)}"


def api_get(url, attempts=4):
    """GET a JSearch URL with the API key, retrying transient errors.

    Every attempt is logged to stdout and pipeline/logs/api.log. The API key
    travels in the header, so the logged URL is safe to keep.
    """
    request = urllib.request.Request(url, headers={"x-api-key": config.JSEARCH_API_KEY})
    last_error = None
    for attempt in range(1, attempts + 1):
        started = time.time()
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read()
                log.info(
                    "GET %s -> %s (%d bytes, %.0f ms, attempt %d/%d)",
                    url, response.status, len(body),
                    (time.time() - started) * 1000, attempt, attempts,
                )
                return json.loads(body)
        except urllib.error.HTTPError as error:
            last_error = error
            log.warning("GET %s -> HTTP %s (attempt %d/%d)",
                        url, error.code, attempt, attempts)
            if error.code in (429, 500, 502, 503, 504):
                time.sleep(2 * attempt)
                continue
            raise
        except urllib.error.URLError as error:
            last_error = error
            log.warning("GET %s -> %s (attempt %d/%d)",
                        url, error.reason, attempt, attempts)
            time.sleep(2 * attempt)
    raise last_error


def build_search_url(query, cursor="", pages=None, country=None):
    """Build the /search-v2 URL for one query batch (one page = one credit)."""
    params = {
        "query": query,
        "country": country or config.JSEARCH_COUNTRY,
        "num_pages": pages or config.JSEARCH_PAGES_PER_QUERY,
        "date_posted": config.JSEARCH_DATE_POSTED,
        "language": config.LANGUAGE,   # required with `country` for non-US results
    }
    if cursor:
        params["cursor"] = cursor
    return api_url("search-v2", params)


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


def to_row(query, job, country="my"):
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
        "location": location or "Unknown",
        "salary": format_salary(job),
        "link": job.get("job_apply_link") or job.get("job_google_link") or "",
        "country": country,
        "description": job.get("job_description") or "",
        "posted_at": job.get("job_posted_at_datetime_utc") or "",
    }


def fetch_query(query, cursor="", pages=None, country=None):
    """Fetch one /search-v2 batch."""
    return api_get(build_search_url(query, cursor, pages, country))


def fetch_query_pages(query, total_pages, country=None):
    """Fetch up to total_pages for one query, chunked via the cursor."""
    jobs = []
    cursor = ""
    fetched = 0
    while fetched < total_pages:
        chunk = min(config.JSEARCH_PAGES_PER_REQUEST, total_pages - fetched)
        payload = fetch_query(query, cursor=cursor, pages=chunk, country=country)
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


def fetch_all(queries=None, pages=None, countries=None):
    """Run the given queries for every country; return a de-duplicated DataFrame.

    De-dup key is (country, job_id) so the same posting can legitimately appear
    in two markets.
    """
    if not config.JSEARCH_API_KEY:
        raise SystemExit(
            "JSEARCH_API_KEY is not set. Add it to pipeline/.env or the environment."
        )

    target = pages or config.JSEARCH_PAGES_PER_QUERY
    rows = []
    seen = set()
    for country in countries or config.COUNTRIES:
        code, place = country["code"], country["location"]
        country_total = 0
        for role in queries or config.SEARCH_QUERIES:
            query = f"{role} in {place}"
            print(f"[{code.upper()}] Searching '{query}'...", end=" ", flush=True)
            jobs = fetch_query_pages(query, target, country=code)
            new = 0
            for job in jobs:
                key = job.get("job_id") or job.get("job_apply_link")
                if not key or (code, key) in seen:
                    continue
                seen.add((code, key))
                rows.append(to_row(query, job, code))
                new += 1
            country_total += new
            print(f"{new} new (country {country_total})")
        print(f"[{code.upper()}] {country['name']}: {country_total} jobs")
    return pd.DataFrame(rows, columns=LINK_COLUMNS + ["description", "posted_at"])


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
    assert "posted_at" in row
    # job_location is preferred; city/state/country is the fallback.
    assert to_row("x", {})["company"] == "Confidential"
    assert to_row("x", {"job_city": "Penang"})["location"] == "Penang"
    assert to_row("x", {}, "sg")["country"] == "sg"
    assert format_salary({}) == "Not Specified"
    assert "country=my" in build_search_url("x")
    assert "language=en" in build_search_url("x")
    print("self-test OK")


def main():
    parser = argparse.ArgumentParser(description="Fetch jobs from JSearch into the pipeline.")
    parser.add_argument("--self-test", action="store_true", help="Offline mapping checks.")
    parser.add_argument("--pages", type=int, help="Pages per query (default from config; 1-20).")
    parser.add_argument("--only", help="Comma-separated subset of search queries to run.")
    parser.add_argument("--countries", help="Comma-separated country codes (default: all).")
    args = parser.parse_args()

    config.ensure_utf8_stdout()
    if args.self_test:
        self_test()
        return

    queries = args.only.split(",") if args.only else None
    wanted = args.countries.split(",") if args.countries else None
    countries = [c for c in config.COUNTRIES if not wanted or c["code"] in wanted]
    # Save after each country so a long run can't lose everything on a timeout.
    frames = []
    for country in countries:
        frame = fetch_all(queries=queries, pages=args.pages, countries=[country])
        if not frame.empty:
            frames.append(frame)
            save(pd.concat(frames, ignore_index=True))
    if not frames:
        print("No jobs fetched.")


if __name__ == "__main__":
    main()
