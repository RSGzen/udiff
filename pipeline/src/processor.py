"""Extract structured skills from job descriptions using Ollama (qwen3:8b)."""

import pandas as pd
import ollama
import json
import re
import time
import hashlib
import config

from locations import normalize_location

config.ensure_utf8_stdout()

log = config.get_logger("gpu", "gpu.log")

# --- CONFIGURATION ---
job_details_csv_filepath = config.JOB_DETAILS_CSV
job_analysis_json_filepath = config.JOB_ANALYSIS_JSON
# ---------------------

def clean_text(text):
    if pd.isna(text):
        return ""

    # 1. Convert to string
    text = str(text)

    # 2. Collapse excessive whitespace
    # Replace 3+ newlines with 2, keeping paragraph breaks but removing
    # huge gaps.
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # 3. Strip leading/trailing whitespace
    return text.strip()

def parse_salary(salary_str):
    """
    Parses strings like "RM 3,000 - RM 4,500 per month" into structured integers.
    Returns: {'min_salary': int, 'max_salary': int, 'currency': str}
    """
    if pd.isna(salary_str) or 'Hidden' in str(salary_str):
        return {'min_salary': None, 'max_salary': None, 'currency': None}

    # 1. Clean the string (remove "per month", commas)
    clean_str = str(salary_str).replace(',', '').upper()

    # 2. Extract numbers using Regex
    # This pattern finds digits that might appear in the string
    numbers = re.findall(r'\d+', clean_str)
    numbers = [int(n) for n in numbers]

    # 3. Detect Currency (Naive check for MYR/RM)
    currency = 'MYR' if 'RM' in clean_str or 'MYR' in clean_str else 'UNKNOWN'

    if not numbers:
        return {'min_salary': None, 'max_salary': None, 'currency': currency}

    # 4. Logic for Range vs Single Value
    if len(numbers) == 1:
        return {'min_salary': numbers[0], 'max_salary': numbers[0], 'currency': currency}
    elif len(numbers) >= 2:
        return {'min_salary': min(numbers), 'max_salary': max(numbers), 'currency': currency}

    return {'min_salary': None, 'max_salary': None, 'currency': None}

def extract_data(description, label=""):
    """Sends the job description to the local LLM and requests JSON."""

    # System prompt: fix the exact JSON schema the model must return.
    system_prompt = """
    You are an expert technical recruiter. Extract information into strictly valid JSON.

    Structure:
    {
        "hard_skills": ["List", "of", "skills"],
        "soft_skills": ["List", "of", "skills"],
        "technical_context": ["List", "of", "domains"],
        "experience_level": "Junior" | "Mid" | "Senior" | "Lead" | "Unknown"
    }
    """

    # User prompt: the extraction rules and field definitions.
    user_message = f"""
    Analyze this job description.

    1. Extract Hard Skills (Tools, Languages, Frameworks).
    2. Extract Soft Skills.
    3. Extract 'Technical Context': What is the specific application of these skills?
       - If they ask for Python for AI, is it for 'NLP', 'Computer Vision', or 'Data Engineering'?
       - If they ask for Java, is it for 'Android' or 'Spring Boot Backend'?
       - Be specific but concise (1-3 words per context tag).
    4. Determine Experience Level:
       - "Junior": 0-2 years, Fresh Grad, Entry Level, Intern.
       - "Mid": 3-5 years, "Experienced", or no specific year mentioned but implies autonomy.
       - "Senior": 5+ years, "Senior", "Principal", "Architect".
       - "Lead": Management focus, "Lead", "Manager".
       - "Unknown": If ambiguous.

    Job Description:
    {description[:config.MAX_DESCRIPTION_CHARS]}
    """

    started = time.time()
    try:
        response = ollama.chat(
            model=config.MODEL_NAME,
            messages=[{'role': 'system',
                       'content': system_prompt},
                      {'role': 'user',
                       'content': user_message}],
            format='json',  # JSON mode guarantees a parseable response
            think=False,  # extraction needs no long reasoning; ~2.6x faster
        )
        elapsed_ms = (time.time() - started) * 1000
        log.info(
            "gpu extract %s | model=%s eval_tokens=%s prompt_tokens=%s %.0f ms",
            label, config.MODEL_NAME,
            response.get("eval_count"), response.get("prompt_eval_count"), elapsed_ms,
        )
        # Parse the string response into a real dictionary
        return json.loads(response['message']['content'])

    except Exception as e:
        log.error("gpu extract %s | failed after %.0f ms: %s",
                  label, (time.time() - started) * 1000, e)
        print(f"Error processing row: {e}")
        return None

def generate_fingerprint(text):
    """
    Creates a unique signature for a text block.
    Removes whitespace to ensure formatting differences don't break the match.
    """
    if pd.isna(text):
        return "empty"

    # 1. Normalize: Remove all whitespace and make lowercase
    # This ensures that "Python  Developer" and "Python Developer" match
    clean_text = "".join(str(text).split()).lower()

    # 2. Hash: Create MD5 signature
    return hashlib.md5(clean_text.encode('utf-8')).hexdigest()

def self_test():
    """Offline checks for the CPU-side helpers (no GPU / API calls)."""
    assert parse_salary("RM 3,000 - RM 4,500 per month")["min_salary"] == 3000
    assert normalize_location("Bayan Lepas, Penang")["state"] == "Penang"
    assert generate_fingerprint("Python  Dev") == generate_fingerprint("python dev")
    print("self-test OK")


def load_existing():
    """Load already-analysed jobs so a long run can resume."""
    if not job_analysis_json_filepath.is_file():
        return []
    try:
        with open(job_analysis_json_filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_results(results):
    job_analysis_json_filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(job_analysis_json_filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)


def run(country=None):
    print(f"Loading {job_details_csv_filepath}...")

    try:
        df = pd.read_csv(job_details_csv_filepath)
        print(f"Retrieving data for {len(df)} jobs... ")

    except FileNotFoundError:
        print("CSV not found. Did you run the scraper?")
        return

    print(f"Initial Raw Count: {len(df)} jobs")

    if country and 'country' in df.columns:
        df = df[df['country'] == country]
        print(f"Filtered to country={country}: {len(df)} jobs")

    # --- FILTER LEVEL 1: TECHNICAL DEDUPLICATION (URL) ---
    # Removes "Sticky/Sponsored" ads that appear on multiple pages.
    # We strip query parameters (like ?track=123) to ensure links are truly unique.
    # Country is part of the key so the same ad can exist in two markets.
    if 'link' in df.columns:
        df['clean_link'] = df['link'].apply(lambda x: str(x).split('?')[0])
        key = ['country', 'clean_link'] if 'country' in df.columns else ['clean_link']
        df = df.drop_duplicates(subset=key, keep='first')
        print(f"Count after URL Dedup: {len(df)} (Removed sticky ads)")

    # --- FILTER LEVEL 2: EXACT CONTENT DUPLICATION ---
    # This catches "lazy copy-paste" but allows same description for different TITLES.
    # (e.g. "Frontend Dev" and "Backend Dev" might share boilerplate, but
    # they are different jobs)
    if 'description' in df.columns:
        # Generate hash
        df['content_hash'] = df['description'].apply(generate_fingerprint)

        # We allow duplicate descriptions ONLY IF the 'title' is different.
        # This solves the issue of losing too many jobs.
        subset = ['company', 'title', 'content_hash']
        if 'country' in df.columns:
            subset.append('country')
        df = df.drop_duplicates(subset=subset, keep='first')
        print(f"Count after Content Dedup: {len(df)} (Removed exact duplicates)")

    # Re-indexing DataFrame
    df = df.reset_index(drop=True)

    print(f"Final Processing Count: {len(df)} unique jobs")

    print(f"\nStarting extraction on {len(df)} jobs using {config.MODEL_NAME}...")
    print("This runs on your RTX 4060-Ti. Watch your GPU usage!")

    # Resume: keep prior results and skip links already analysed.
    results = load_existing()
    done_links = {str(item.get('original_link')).split('?')[0] for item in results}
    if results:
        print(f"Resuming: {len(results)} jobs already analysed.")

    new_count = 0
    for i, (index, row) in enumerate(df.iterrows()):
        index_val = i + 1

        print(f"Processing {index_val}/{len(df)}: {row['title']}...", end="", flush=True)

        clean_link = str(row['link']).split('?')[0]
        if clean_link in done_links:
            print(" [Skipped - already analysed]")
            continue

        t_lower = row['title'].lower()

        # EXCLUSION LIST: Roles that are irrelevant for students/juniors
        if any(x in t_lower for x in ['manager', 'head of', 'director', 'lead', 'principal', 'vp', 'chief']):
            print(" [Skipped - Management-level job not counted]")
            done_links.add(clean_link)
            continue  # Skip this row; it must not count in stats

        # 1. Fast CPU Extraction (Salary and Location)
        c = row['country'] if 'country' in df.columns else 'my'
        salary_data = parse_salary(row['salary'])

        location_data = normalize_location(row['location'], country=c)

        # 2. Slow GPU Extraction (Skills)
        description = clean_text(row['description'])

        if len(description) < 50:
            print(" [Skipped - Description too short]")
            done_links.add(clean_link)
            continue

        label = f"[{c}] {index_val}/{len(df)} {row['title']}"
        start_time = time.time()
        data = extract_data(description, label=label)
        duration = time.time() - start_time

        if data:
            # Add metadata back so we know which job this is
            data['job_title'] = row['title']
            data['company'] = row['company']
            data['location'] = row['location']
            data['country'] = c

            data['original_link'] = row['link']
            if 'posted_at' in df.columns:
                data['posted_at'] = row['posted_at']

            # Inject the parsed salary
            data.update(salary_data)

            # Inject the location data
            data.update(location_data)

            results.append(data)
            done_links.add(clean_link)
            new_count += 1

            # Checkpoint every 25 new jobs so a crash/timeout is recoverable.
            if new_count % 25 == 0:
                save_results(results)

            print(f" Done ({duration:.2f}s)")
        else:
            print(" Failed.")

    save_results(results)
    print(f"\nSuccess! {new_count} new jobs analysed; {len(results)} total.")
    print(f"Data saved to {job_analysis_json_filepath}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract skills from job descriptions.")
    parser.add_argument("--self-test", action="store_true", help="Offline checks.")
    parser.add_argument("--country", help="Only process one country code (resumable).")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        run(country=args.country)


if __name__ == "__main__":
    main()
