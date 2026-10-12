"""Classify employers as real companies vs recruiter/confidential placeholders.

A recruiter or "Confidential" posting is not a real employer, so the bubble
map treats them separately (P9). Keep this list small and boring.
"""

import pandas as pd

PLACEHOLDER_EXACT = {
    "confidential", "private", "n/a", "na", "none", "unknown", "-",
}

# Substrings that mark a staffing agency / recruiter / aggregator.
PLACEHOLDER_TOKENS = [
    "confidential",
    "agensi pekerjaan",          # Malay for "employment agency"
    "recruitment", "recruiter", "staffing", "headhunt", "talent acquisition",
    "people search", "peoplesearch",
    "michael page", "randstad", "hays", "robert walters", "robert half",
    "adecco", "manpower", "kelly services", "recruit express", "reeracoen",
    "pasona", "persol", "rgf", "charterhouse", "ambition", "eames", "hudson",
    "spring professional", "talentbank", "jobstore", "superjobs", "jobstreet",
    "caldic", "btc recruitment",
]


def classify_company(name):
    """Return 'placeholder' for recruiters/confidential, else 'company'."""
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return "placeholder"
    text = str(name).strip().lower()
    if not text or text in PLACEHOLDER_EXACT:
        return "placeholder"
    if any(token in text for token in PLACEHOLDER_TOKENS):
        return "placeholder"
    return "company"


def top_companies(company_series, limit=15):
    """Split employers into real companies and a placeholder aggregate."""
    counts = company_series.dropna().astype(str).str.strip()
    counts = counts[counts != ""].value_counts()
    companies, placeholder_jobs = [], 0
    for name, count in counts.items():
        if classify_company(name) == "placeholder":
            placeholder_jobs += int(count)
        else:
            companies.append({"name": name, "count": int(count), "kind": "company"})
    return companies[:limit], {"name": "Recruiters & confidential", "count": placeholder_jobs}


def self_test():
    assert classify_company("Acme Sdn Bhd") == "company"
    assert classify_company("Confidential") == "placeholder"
    assert classify_company("Michael Page International") == "placeholder"
    assert classify_company("Agensi Pekerjaan ABC") == "placeholder"
    assert classify_company(None) == "placeholder"

    series = pd.Series(["Acme", "Acme", "Globex", "Confidential", "Michael Page"])
    companies, placeholder = top_companies(series)
    assert companies == [{"name": "Acme", "count": 2, "kind": "company"},
                         {"name": "Globex", "count": 1, "kind": "company"}]
    assert placeholder["count"] == 2
    print("self-test OK")


if __name__ == "__main__":
    self_test()
