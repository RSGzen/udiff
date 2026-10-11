"""Dev utility: list the job titles the role categoriser leaves as 'Other'."""

import pandas as pd
import json
import config

from analyzer import categorize_role

# --- CONFIGURATION ---
job_analysis_json_filepath = config.JOB_ANALYSIS_JSON

# Load the LLM-extracted job data.
try:
    with open(job_analysis_json_filepath, 'r') as f:

        data = json.load(f)
    df = pd.DataFrame(data)

    # Apply the current role categorisation.
    df['category'] = df['job_title'].apply(categorize_role)

    # Filter for 'Other' and count the top titles
    others = df[df['category'] == 'Other']
    print(f"--- Top 30 Unclassified Job Titles (Total: {len(others)}) ---")
    print(others['job_title'].value_counts().head(30))

except Exception as e:
    print(f"Error: {e}")
