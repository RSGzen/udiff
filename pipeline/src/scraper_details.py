import time
import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import config

# --- CONFIGURATION ---
headless_flag = config.HEADLESS
job_links_csv_filepath = config.JOB_LINKS_CSV
job_details_csv_filepath = config.JOB_DETAILS_CSV
# ---------------------

config.ensure_utf8_stdout()

def scrape_details():
    # 1. Load the links we harvested

    try:
        df = pd.read_csv(job_links_csv_filepath)
        print(f"Loaded {len(df)} jobs to process.")

    except FileNotFoundError:
        print(f"Error: '{job_links_csv_filepath}' not found. Run scraper.py first.")
        return

    # Create a column for the new data if it doesn't exist
    if 'description' not in df.columns:
        df['description'] = ""

    with sync_playwright() as p:
        # HEADLESS comes from config.py (False = watch the browser work).
        browser = p.chromium.launch(headless=headless_flag)
        page = browser.new_page()

        # 2. Iterate through the links
        for i, (index, row) in enumerate(df.iterrows()):
            # Skip if we already have the description (allows restarting crashed scripts)
            if pd.notna(row['description']) and row['description'] != "":
                continue

            url = row['link']
            index_val = i + 1

            print(f"[{index_val}/{len(df)}] Visiting: {row['title']}...")

            try:
                page.goto(url, timeout=60000)  # 60s timeout for slow pages

                # Wait for the description to load
                page.wait_for_selector('div[data-automation="jobAdDetails"]', timeout=5000)

                # Extract HTML
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                # 3. Target the Description Container
                # JobStreet standard tag for the body text
                desc_div = soup.find('div', attrs={"data-automation": "jobAdDetails"})

                if desc_div:
                    # A distinct separator keeps the extracted structure clean.
                    full_text = desc_div.get_text(separator="\n").strip()
                    df.at[index, 'description'] = full_text
                    print("   -> Success: Extracted description.")
                else:
                    print("   -> Warning: Description container not found.")
                    df.at[index, 'description'] = "Error: Not Found"

            except Exception as e:
                print(f"   -> Error visiting page: {e}")
                df.at[index, 'description'] = "Error: Timeout/Fail"

            # 4. Respectful Delay & Save Checkpoint
            # Don't hammer their server; sleep 1-2 seconds
            time.sleep(1)

            # Save every 5 rows so we don't lose data if it crashes
            if index_val % 5 == 0:
                df.to_csv(job_details_csv_filepath, index=False)
                print("   [Checkpoint Saved]")

        browser.close()

    # Final Save
    df.to_csv(job_details_csv_filepath, index=False)
    print("\n--- EXTRACTION COMPLETE ---")
    print(f"Data saved to '{job_details_csv_filepath}'")

if __name__ == "__main__":
    scrape_details()
