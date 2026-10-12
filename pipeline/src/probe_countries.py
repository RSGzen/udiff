"""Phase 0 probe (M5.7): one page per SEA country.

Per the API FAQ, non-US queries must put the location IN the query and pass
`country` + `language` together. This measures English yield, salary presence,
structured-field coverage, and description quality before the full fetch.

Run: python pipeline/src/probe_countries.py
"""

import config
from fetch_jobs import api_get, api_url

ROLE = "Software Engineer"
COUNTRIES = {
    "my": "Malaysia",
    "sg": "Singapore",
    "id": "Jakarta, Indonesia",
    "vn": "Ho Chi Minh City, Vietnam",
}
STRUCTURED_FIELDS = ["required_technologies", "soft_skills", "seniority_level",
                     "required_experience_years", "job_highlights"]
ENGLISH_STOPWORDS = (" the ", " and ", " with ", " for ", " you ", " experience ")


def ascii_ratio(text):
    if not text:
        return 0.0
    return sum(1 for ch in text if ord(ch) < 128) / len(text)


def probe(country, location):
    params = {"query": f"{ROLE} in {location}", "country": country,
              "num_pages": 1, "date_posted": "all", "language": "en"}
    payload = api_get(api_url("search-v2", params))
    jobs = (payload.get("data") or {}).get("jobs") or []
    total = len(jobs)
    desc = [j.get("job_description") or "" for j in jobs]
    with_desc = sum(1 for d in desc if len(d) > 50)
    with_salary = sum(1 for j in jobs
                      if j.get("job_min_salary") or j.get("job_max_salary"))
    with_posted = sum(1 for j in jobs if j.get("job_posted_at_datetime_utc"))
    english = sum(
        1 for d in desc
        if len(d) > 50 and ascii_ratio(d) > 0.98
        and any(word in f" {d.lower()} " for word in ENGLISH_STOPWORDS)
    )
    avg_len = int(sum(len(d) for d in desc) / total) if total else 0
    countries = {}
    for j in jobs:
        key = j.get("job_country")
        countries[key] = countries.get(key, 0) + 1
    print(f"\n{country.upper()}  query='{ROLE} in {location}'")
    print(f"  jobs={total}  desc>50={with_desc}  avg_len={avg_len}  "
          f"salary={with_salary}  posted_at={with_posted}  english~={english}")
    print(f"  job_country={countries}")
    if jobs:
        coverage = {f: sum(1 for j in jobs if j.get(f)) for f in STRUCTURED_FIELDS}
        print(f"  structured-field coverage={coverage}")


if __name__ == "__main__":
    config.ensure_utf8_stdout()
    for code, loc in COUNTRIES.items():
        try:
            probe(code, loc)
        except Exception as e:
            print(f"{code.upper()}: FAILED -> {e}")
