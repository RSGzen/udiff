"""Generate course-name synonyms for each role's top skills via the LLM."""

import json
import re
import time

import ollama

import config
import dictionary_utils

config.ensure_utf8_stdout()

log = config.get_logger("gpu", "gpu.log")

# --- CONFIGURATION ---
gap_report_json_filepath = config.GAP_REPORT_JSON

skill_class_json_filepath = config.SKILL_CLASS_JSON

NUM_HARD_SKILLS = 10
NUM_TECH_CONTEXT = 5
NUM_CLASS_NAMES = 12

model_name = config.MODEL_NAME
# ---------------------

def extraction_of_skills(details, num_hard_skills, num_tech_context):
    """Return up to n hard skills and m technical contexts for one category."""
    all_level = details.get("All") or {}
    hard_skill_lst = [
        skill["name"]
        for skill in (all_level.get("top_hard_skills") or [])[:num_hard_skills]
    ]
    tech_context_lst = [
        context["name"]
        for context in (all_level.get("top_technical_context") or [])[:num_tech_context]
    ]
    return hard_skill_lst, tech_context_lst


def salvage_list(content):
    """Best-effort: pull a JSON array of strings out of messy model output.

    P6: the model occasionally emits a truncated or prose-wrapped list, which
    used to leave ~13% of subjects empty. Grab the bracketed part, and if even
    that won't parse, fall back to quoted strings.
    """
    match = re.search(r"\[.*?\]", content, re.DOTALL)
    candidate = match.group(0) if match else content
    try:
        value = json.loads(candidate)
        if isinstance(value, list):
            return value
    except json.JSONDecodeError:
        pass
    return re.findall(r'"([^"]+)"', candidate)


def parse_names(content, num_names):
    """Turn model output into a clean list of up to num_names strings."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = salvage_list(content)
    if isinstance(data, dict):
        # Sometimes models wrap the list in a key like {"classes": [...]}.
        values = list(data.values())
        if values and isinstance(values[0], list):
            data = values[0]
    if isinstance(data, list):
        return dictionary_utils.clean_course_names(data)[:num_names]
    return []


def ask_model(class_subject, num_names):
    """One LLM call; return the raw content string."""
    system_prompt = """
    You are a university professor producing class names based on a subject.
    Process the subject name and generate the requested number of class names.

    Output ONLY a raw JSON list of strings (e.g., ["Name1", "Name2"]).
    Do not include markdown formatting or extra text.
    """

    user_message = f"""
    Analyze the subject '{class_subject}' and produce {num_names} possible names for it.

    The context and meaning of the subject must be studied thoroughly, and the
    generated class names must relate to the subject. Example class names:
    - Principles of Database Systems
    - Advanced Data Analysis
    - Programming Language C
    - Design and Analysis of Algorithms
    - Applications of Deep Learning

    You can also produce your own class names relevant to the subject.
    """

    response = ollama.chat(
        model=model_name,
        messages=[{'role': 'system', 'content': system_prompt},
                  {'role': 'user', 'content': user_message}],
        format='json',
        think=False,  # course-name generation needs no long reasoning
        keep_alive='30m',  # keep the model resident between calls
        options={'num_predict': 600},  # bound the output length
    )
    return response['message']['content']


def llm_query(class_subject, num_names):
    """Generate class names for a subject, retrying once, then salvaging (P6)."""
    print(f"Generating class names for {class_subject.ljust(25)}... ", end='')
    total_start = time.time()

    for attempt in (1, 2):
        try:
            content = ask_model(class_subject, num_names)
            names = parse_names(content, num_names)
            if names:
                duration = time.time() - total_start
                log.info("gpu curriculum subject=%s names=%d attempt=%d %.0f ms",
                         class_subject, len(names), attempt, duration * 1000)
                print(f" Completed in {duration:.3f}s | Exp: {names[0]}")
                return names
            log.warning("gpu curriculum subject=%s empty output on attempt %d",
                        class_subject, attempt)
        except Exception as e:
            log.error("gpu curriculum subject=%s failed attempt %d: %s",
                      class_subject, attempt, e)

    print(" -> empty after retry")
    return []

def curriculum_gen():

    # 1. Load the gap report (plain dict; pandas mangles the nested structure).
    try:
        with open(gap_report_json_filepath, 'r') as f:
            gap_report = json.load(f)
        print(f"Loaded {gap_report_json_filepath} for analysis.")
    except Exception as e:
        print(f"Error loading source JSON: {e}")
        return

    # 2. Prepare Report Structure
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "countries": {}
    }

    # 3. Generate class names for each country's role categories.
    for country in config.COUNTRIES:
        code = country["code"]
        block = gap_report.get("countries", {}).get(code)
        if not block:
            continue
        categories = block.get("categories", {})
        print(f"\n===== {country['name']} ({code.upper()}) — {len(categories)} categories =====")
        report["countries"][code] = {"categories": {}}

        for i, (current_job_type, details) in enumerate(categories.items()):

            if current_job_type == 'Other':
                continue

            print(f"\nProcessing skills for {current_job_type} ===> ")

            # Get the top n hard skills and top m technical contexts.
            hard_skill_lst, tech_context_lst = extraction_of_skills(
                details=details,
                num_hard_skills=NUM_HARD_SKILLS,
                num_tech_context=NUM_TECH_CONTEXT,
            )

            # Generate possible class names for each subject.
            skill_dict = {}

            for subject in hard_skill_lst:
                skill_dict[subject] = llm_query(class_subject=subject,
                                                num_names=NUM_CLASS_NAMES)

            for subject in tech_context_lst:
                skill_dict[subject] = llm_query(class_subject=subject,
                                                num_names=NUM_CLASS_NAMES)

            # Save the nested class names to the main report.
            report['countries'][code]['categories'][current_job_type] = skill_dict

            # Save the report after each category in case of a crash.
            with open(skill_class_json_filepath, 'w') as f:
                json.dump(report, f, indent=4)

            print(f"[{code.upper()}] Checkpoint reached {i+1} / {len(categories)}")

    # 4. Save the final report.
    with open(skill_class_json_filepath, 'w') as f:
        json.dump(report, f, indent=4)

    print(f"\n✅ Analysis saved to {skill_class_json_filepath}")


def self_test():
    assert parse_names('["A", "B"]', 5) == ["A", "B"]
    assert parse_names('{"classes": ["A", "B"]}', 5) == ["A", "B"]
    assert parse_names("Here you go: [\"A\", \"B\"] done", 5) == ["A", "B"]
    assert parse_names('["A", "B"', 5) == ["A", "B"]   # truncated -> salvaged
    assert parse_names("no list here", 5) == []
    assert parse_names('["A", "B", "C"]', 2) == ["A", "B"]
    print("self-test OK")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate skill->course synonyms.")
    parser.add_argument("--self-test", action="store_true", help="Offline checks.")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        curriculum_gen()
