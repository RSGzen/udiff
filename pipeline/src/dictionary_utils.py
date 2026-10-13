"""Clean the LLM-generated skill -> course-name dictionary.

The curriculum generator occasionally emits junk course names (empty strings,
punctuation like ``","``, numbers-only, or duplicates). Left in, an entry such as
``","`` normalises to an empty string and then matches *everything* in the web
checker. This module drops that junk.

Used two ways:
  * imported by ``curriculum_generation.py`` so NEW runs are clean, and
  * runnable on its own to clean files produced before this fix::

        python pipeline/src/dictionary_utils.py            # default: output + web copy
        python pipeline/src/dictionary_utils.py <path…>    # explicit files
"""

import json
import re
from pathlib import Path


def clean_course_names(names) -> list:
    """Return only usable course names: >=3 chars, contains a letter, de-duplicated."""
    cleaned = []
    seen = set()
    for item in names or []:
        text = re.sub(r"\s+", " ", str(item)).strip().strip('"').strip()
        text = text.strip(" .,;:|/-_*()")
        if len(text) < 3 or not re.search(r"[A-Za-z]", text):
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return cleaned


def sanitize_skill_class(path) -> int:
    """Clean every skill's course list in a skill_class.json file. Returns lists changed."""
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    changed = 0
    for block in (data.get("countries") or {}).values():
        for skills in (block.get("categories") or {}).values():
            for skill, names in list(skills.items()):
                cleaned = clean_course_names(names)
                if cleaned != names:
                    skills[skill] = cleaned
                    changed += 1

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return changed


def self_test():
    assert clean_course_names([",", "  ", "42", "A", "Databases"]) == ["Databases"]
    assert clean_course_names(["Intro to Java", "intro to java", "Intro to Java"]) == ["Intro to Java"]
    assert clean_course_names([]) == []
    assert clean_course_names(None) == []
    print("self-test OK")


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv:
        self_test()
    else:
        targets = sys.argv[1:]
        if not targets:
            import config

            targets = [config.SKILL_CLASS_JSON, config.WEB_DATA_DIR / "skill_class.json"]
        for target in targets:
            target = Path(target)
            if not target.is_file():
                print(f"skip (missing): {target}")
                continue
            print(f"{target}: cleaned {sanitize_skill_class(target)} skill lists")
