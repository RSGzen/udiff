"""Generate course-name synonyms for each role's top skills via the LLM."""

import pandas as pd
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
NUM_CLASS_NAMES = 25

model_name = config.MODEL_NAME
# ---------------------

def extraction_of_skills(df, num_hard_skills, num_tech_context):

    # Obtain list that contains n required hard skill
    hard_skill_lst = []

    hard_skill_df = df['All']['top_hard_skills']

    if len(hard_skill_df) < num_hard_skills:
        raise ValueError(f"Number of hard skill queried is more than available of {len(hard_skill_df)}")

    for n in range(0, num_hard_skills):
        hard_skill_lst.append(hard_skill_df[n]['name'])

    # Obtain list that contains n required technical context
    tech_context_lst = []

    tech_context_df = df['All']['top_technical_context']

    if len(tech_context_df) < num_tech_context:
        raise ValueError(f"Number of tech context queried is more than available of {len(tech_context_df)}")

    for n in range(0, num_tech_context):
        tech_context_lst.append(tech_context_df[n]['name'])

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

    # 1. Load Data
    try:
        with open(gap_report_json_filepath, 'r') as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        print(f"Loaded {gap_report_json_filepath} for analysis.")

    except Exception as e:
        print(f"Error loading source JSON: {e}")
        return

    # 2. Prepare Report Structure
    report = {
        "generated at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "categories": {}
    }

    # 3. Generate class names for each role category.

    job_types_list = list(df['categories'].keys())

    for i in range(0, len(job_types_list)):

        current_job_type = job_types_list[i]

        if current_job_type == 'Other':
            continue

        print(f"\nProcessing skills for {current_job_type} ===> ")

        current_job_details = df['categories'][current_job_type]

        hard_skill_lst = []
        tech_context_lst = []

        # Get the top n hard skills and top m technical contexts.
        try:
            hard_skill_lst, tech_context_lst = extraction_of_skills(df=current_job_details,
                                                                    num_hard_skills=NUM_HARD_SKILLS,
                                                                    num_tech_context=NUM_TECH_CONTEXT)
        except ValueError as e:
            print(f"Error caught: {e}")

        # Generate possible class names for each subject.
        skill_dict = {}

        for subject in hard_skill_lst:
            data = llm_query(class_subject=subject,
                             num_names=NUM_CLASS_NAMES)

            skill_dict[subject] = data

        for subject in tech_context_lst:
            data = llm_query(class_subject=subject,
                             num_names=NUM_CLASS_NAMES)

            skill_dict[subject] = data

        # Save the nested class names to the main report.
        report['categories'][current_job_type] = skill_dict

        # Save the report after each category in case of a crash.
        with open(skill_class_json_filepath, 'w') as f:
            json.dump(report, f, indent=4)

        print(f"Checkpoint reached {i+1} / {len(job_types_list)}")

    # 4. Save the final report.
    with open(skill_class_json_filepath, 'w') as f:
        json.dump(report, f, indent=4)

    print(f"\n✅ Analysis saved to {skill_class_json_filepath}")

if __name__ == "__main__":
    curriculum_gen()
