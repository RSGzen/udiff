"""Aggregate LLM-extracted job data into a per-country, per-role gap report."""

import argparse
import json
import re
import time

import pandas as pd

import companies
import config
from locations import normalize_location

config.ensure_utf8_stdout()

# --- CONFIGURATION ---
job_analysis_json_filepath = config.JOB_ANALYSIS_JSON

gap_report_json_filepath = config.GAP_REPORT_JSON

SCHEMA_VERSION = 3
# P3: show small-but-real categories. The milestone said "<2", but that still
# drops 1-job categories like "Project & Sales Engineering", which the done-when
# requires to appear — so the floor is "at least 1 job".
MIN_CATEGORY_JOBS = 1
SAMPLE_FLOOR = 3        # a block below this is flagged low_sample
# ---------------------

# P1: best-effort salary mined from the ad text (JSearch's salary is usually
# null). Text-mined, not authoritative — clearly labelled for the web.
# ponytail: naive first-match regex; fine for a best-effort signal.
SALARY_TEXT_PATTERN = re.compile(r"(?:RM|MYR)\s?[\d,]{3,}", re.IGNORECASE)


def extract_salary_text(description):
    """Return the first RM/MYR amount found in the ad text, or None."""
    if description is None:
        return None
    match = SALARY_TEXT_PATTERN.search(str(description))
    return match.group(0).strip() if match else None


SKILL_ALIASES = {
    # Variations : Master Term
    'c programming': 'C',
    'react.js': 'React',
    'reactjs': 'React',
    'node.js': 'Node.js',
    'amazon web services': 'AWS',
    'golang': 'Go',
    'c sharp': 'C#',
    # Add more as you see them
}


def normalize_skill(skill_name):
    s = skill_name.lower().strip()
    for variant, master in SKILL_ALIASES.items():
        if s == variant:
            return master

    # Capitalize properly if not in alias list
    return skill_name.title()


def categorize_role(title):
    """
    Bucket a raw job title into a standardised role.

    Hierarchy matters: specific niches are checked before generic titles.
    """

    t = str(title).lower()

    # 1. INTERNSHIP & ENTRY
    if any(x in t for x in ['intern', 'trainee', 'student', 'fresh graduate', 'protege']):
        return 'Internship & Entry Level'

    # 2. FULLSTACK
    if any(x in t for x in ['fullstack', 'full-stack', 'mern', 'mean', 'full stack']):
        return 'Fullstack'

    # 3. HIGH SPECIALIZATION (AI / DATA / SECURITY)
    if any(x in t for x in ['cyber', 'security', 'infosec', 'penetration', 'soc analyst']):
        return 'Cybersecurity'

    if any(x in t for x in ['ai ', 'ai engineer', 'ai/', 'artificial intelligence', 'machine learning', 'deep learning', 'nlp', 'vision', 'data scientist', 'modeler']):
        # Double check it's not "Maintenance" (contains 'ai')
        if 'maint' not in t:
            return 'AI & Machine Learning'

    if any(x in t for x in ['data', 'analyst', 'business intelligence', 'bi ', 'tableau', 'sql', 'big data']):
        return 'Data & Analytics'

    if any(x in t for x in ['devops', 'sre', 'site reliability', 'ci/cd', 'platform engineer', 'cloud', 'aws', 'azure']):
        return 'Cloud & DevOps'

    # 4. CORE SOFTWARE ENGINEERING
    if any(x in t for x in ['frontend', 'front-end', 'react', 'angular', 'vue', 'web designer', 'ui/ux', 'ui ', 'ux ', 'user interface', 'multimedia']):
        return 'Frontend Web'

    if any(x in t for x in ['backend', 'back-end', 'java', 'spring', 'node', 'php', 'laravel', 'golang', '.net', 'c#']):
        return 'Backend'

    if any(x in t for x in ['qa', 'test', 'quality', 'automation', 'sdet']):
        return 'QA & Testing'

    if any(x in t for x in ['mobile', 'ios', 'android', 'flutter', 'react native', 'app developer']):
        return 'Mobile Development'

    # 5. INFRASTRUCTURE & SUPPORT
    if any(x in t for x in ['network', 'infrastructure', 'system engineer', 'sysadmin', 'server', 'noc ']):
        return 'Network & Infrastructure'

    if any(x in t for x in ['support', 'helpdesk', 'service desk', 'it executive', 'technician', 'it engineer', 'operations engineer']):
        return 'IT Support'

    # 6. HARDWARE & MANUFACTURING
    # This catches the Service Engineers and QC roles
    if any(x in t for x in ['electrical', 'mechanical', 'process', 'manufacturing', 'semiconductor', 'hardware', 'field service', 'service engineer', 'electronic', 'qc ', 'yield', 'smt', 'component', 'maintenance']):
        return 'Hardware & Manufacturing'

    if any(x in t for x in ['project', 'product', 'application engineer', 'sales engineer', 'consultant']):
        return 'Project & Sales Engineering'

    if any(x in t for x in ['embedded', 'firmware', 'iot', 'fpga', 'driver']):
        return 'Embedded/Systems'

    # 7. CATCH-ALL
    # Catches "Software R&D Engineer"
    if 'software' in t or 'developer' in t or 'programmer' in t or 'engineer' in t:
        # 'engineer' is broad, but all specific roles above are already filtered,
        # so the remainder are likely generic software/tech roles.
        return 'General Software Engineering'

    return 'Other'


def top_items(dataframe, column, n=10):
    """Return [{name,count,percentage}] for a list-valued column."""
    if column not in dataframe.columns:
        return []
    exploded = dataframe[column].explode().dropna()
    exploded = exploded[exploded.astype(str).str.strip() != ""]
    counts = exploded.value_counts().head(n)
    total = max(len(dataframe), 1)
    return [
        {"name": k, "count": int(v), "percentage": round((v / total) * 100, 1)}
        for k, v in counts.items()
    ]


def distinct_skills(dataframe):
    """Count unique skills across hard/soft/technical-context for a subset."""
    seen = set()
    for column in ("hard_skills", "soft_skills", "technical_context"):
        if column not in dataframe.columns:
            continue
        for value in dataframe[column].dropna():
            if isinstance(value, list):
                seen.update(str(item).strip() for item in value if str(item).strip())
    return len(seen)


def load_raw_lookup():
    """Map clean link -> {salary_text, posted_at, country} from the raw CSV."""
    if not config.JOB_DETAILS_CSV.is_file():
        return {}
    raw = pd.read_csv(config.JOB_DETAILS_CSV)
    if "link" not in raw.columns:
        return {}
    raw["clean_link"] = raw["link"].astype(str).str.split("?").str[0]
    lookup = {}
    for _, row in raw.iterrows():
        lookup[row["clean_link"]] = {
            "salary_text": extract_salary_text(row.get("description")),
            "posted_at": row.get("posted_at") if "posted_at" in raw.columns else None,
        }
    return lookup


def build_country_block(code, name, df, raw_lookup):
    """Everything the report says about one market (mirrors the old MY shape)."""
    df = df.copy()
    df['category'] = df['job_title'].apply(categorize_role)
    if 'location' in df.columns:
        df['state'] = df['location'].apply(
            lambda loc: normalize_location(loc, country=code)['state'])
    elif 'state' not in df.columns:
        df['state'] = 'Unknown'

    block = {
        "name": name,
        "total_jobs_analyzed": int(len(df)),
        "job_distribution": df['category'].value_counts().to_dict(),
        "states": df['state'].value_counts().to_dict(),
        "top_companies": [],
        "placeholder_companies": {},
        "observed_salaries": [],
        "categories": {},
    }

    if 'company' in df.columns:
        top, placeholder = companies.top_companies(df['company'])
        block["top_companies"] = top
        block["placeholder_companies"] = placeholder

    if 'original_link' in df.columns:
        for _, row in df.iterrows():
            entry = raw_lookup.get(str(row['original_link']).split('?')[0])
            if entry and entry.get("salary_text"):
                block["observed_salaries"].append({
                    "raw": entry["salary_text"],
                    "category": row['category'],
                    "title": row.get('job_title', ''),
                })

    for cat in df['category'].unique():
        if cat == 'Other':
            continue
        cat_df = df[df['category'] == cat]
        if len(cat_df) < MIN_CATEGORY_JOBS:   # P3
            continue

        levels = {
            'All': cat_df,
            'Junior': cat_df[cat_df['experience_level'].isin(['Junior', 'Internship & Entry Level'])],
            'Mid': cat_df[cat_df['experience_level'] == 'Mid'],
            'Senior': cat_df[cat_df['experience_level'].isin(['Senior', 'Lead'])],
        }
        category_report = {}
        for level_name, subset in levels.items():
            if len(subset) == 0:
                continue
            avg_min = subset['min_salary'].mean() if 'min_salary' in subset else None
            avg_max = subset['max_salary'].mean() if 'max_salary' in subset else None
            category_report[level_name] = {
                "job_count": int(len(subset)),
                "low_sample": len(subset) < SAMPLE_FLOOR,
                "salary": {
                    "avg_min": int(avg_min) if pd.notna(avg_min) else 0,
                    "avg_max": int(avg_max) if pd.notna(avg_max) else 0,
                },
                "top_hard_skills": top_items(subset, 'hard_skills'),
                # P7: soft skills carry counts/percentages (were bare strings)
                "top_soft_skills": top_items(subset, 'soft_skills', 5),
                "top_technical_context": top_items(subset, 'technical_context'),
                "distinct_skills": distinct_skills(subset),   # P7
            }

        # P4: keep Unknown experience visible instead of silently dropping it
        category_report["unknown_level"] = int(
            (~cat_df['experience_level'].isin(['Junior', 'Internship & Entry Level',
                                               'Mid', 'Senior', 'Lead'])).sum()
        )
        block["categories"][cat] = category_report

    return block


def analyze_market():
    try:
        with open(job_analysis_json_filepath, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} jobs for analysis.")
    except Exception as e:
        print(f"Error loading source JSON: {e}")
        return

    if df.empty:
        print("No analysed jobs to report.")
        return

    if 'country' not in df.columns:
        df['country'] = 'my'

    raw_lookup = load_raw_lookup()

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "countries": {},
        "comparisons": {},
    }

    for country in config.COUNTRIES:
        code = country["code"]
        subset = df[df['country'] == code]
        if subset.empty:
            continue
        print(f"\n--- {country['name']} ({code.upper()}) ---")
        print(subset['job_title'].apply(categorize_role).value_counts())
        report["countries"][code] = build_country_block(code, country["name"], subset, raw_lookup)

    with open(gap_report_json_filepath, 'w') as f:
        json.dump(report, f, indent=4)

    print(f"\nAnalysis saved to {gap_report_json_filepath}")


def self_test():
    assert extract_salary_text("Pay RM 5,000 - RM 7,000") == "RM 5,000"
    assert extract_salary_text("No pay") is None
    assert categorize_role("Senior Backend Engineer") == "Backend"
    assert categorize_role("Data Scientist") == "AI & Machine Learning"
    assert normalize_skill("react.js") == "React"
    assert top_items(pd.DataFrame({"hard_skills": [["a", "b"], ["a"]]}), "hard_skills")[0] == {
        "name": "a", "count": 2, "percentage": 100.0}
    assert distinct_skills(pd.DataFrame({
        "hard_skills": [["a", "b"]], "soft_skills": [["b"]], "technical_context": [["c"]]})) == 3
    print("self-test OK")


def main():
    parser = argparse.ArgumentParser(description="Build the gap report from job_analysis_final.json.")
    parser.add_argument("--self-test", action="store_true", help="Offline checks.")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    analyze_market()


if __name__ == "__main__":
    main()
