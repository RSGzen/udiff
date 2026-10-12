"""Generate course-name synonyms for each role's top skills via the LLM."""

import json
import ollama
import time
import config

config.ensure_utf8_stdout()

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

def llm_query(class_subject, num_names):
    # System prompt: ask for a raw JSON list of course names.
    system_prompt = """
    You are a university professor producing class names based on a subject.
    Process the subject name and generate the requested number of class names.

    Output ONLY a raw JSON list of strings (e.g., ["Name1", "Name2"]).
    Do not include markdown formatting or extra text.
    """

    # User prompt: the generation instructions.
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

    # Start timer
    total_start = time.time()
    print(f"Generating class names for {class_subject.ljust(25)}... ", end='')

    try:
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'system',
                       'content': system_prompt},
                      {'role': 'user',
                       'content': user_message}],
            format='json',
            think=False,  # course-name generation needs no long reasoning
            keep_alive='30m',  # keep the model resident between calls
            options={'num_predict': 600},  # bound the output length
        )

        content = response['message']['content']

        class_list = json.loads(content)

        if isinstance(class_list, dict):
            # Sometimes models wrap the list in a key like {"classes": [...]}. Handle that edge case.
            values = list(class_list.values())
            if values and isinstance(values[0], list):
                class_list = values[0]

        if isinstance(class_list, list):
            total_duration = time.time() - total_start
            print(f" Completed in {total_duration:.3f}s | Exp: {class_list[0]}")

            return class_list[:num_names]  # keep at most num_names items
        else:
            raise ValueError("Model did not return a list.")

    except json.JSONDecodeError:
        print("Error: Failed to parse model output as JSON.")
        return []

    except Exception as e:
        print(f"An error occurred: {e}")
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
        "categories": {}
    }

    # 3. Generate class names for each role category.
    categories = gap_report.get("categories", {})

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
        report['categories'][current_job_type] = skill_dict

        # Save the report after each category in case of a crash.
        with open(skill_class_json_filepath, 'w') as f:
            json.dump(report, f, indent=4)

        print(f"Checkpoint reached {i+1} / {len(categories)}")

    # 4. Save the final report.
    with open(skill_class_json_filepath, 'w') as f:
        json.dump(report, f, indent=4)

    print(f"\n✅ Analysis saved to {skill_class_json_filepath}")

if __name__ == "__main__":
    curriculum_gen()
