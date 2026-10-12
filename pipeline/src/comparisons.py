"""Cross-country comparisons (M5.7): every market vs Malaysia.

Reads the gap report (with salary estimates) and the per-posting analysis, then
writes a `comparisons` block into gap_report.json:

    comparisons["my-vs-sg"] = {
        "skill_gaps": [{skill, my_pct, peer_pct, delta}, ...],
        "salary_delta_nominal": [{role, level, my, peer, delta}, ...],
        "salary_delta_ppp":     [{role, level, my, peer, delta}, ...],
    }
"""

import argparse
import json

import pandas as pd

import config

HOME = "my"
TOP_SKILL_GAPS = 25


def country_skill_pct(df):
    """{country: {hard_skill: % of that country's jobs mentioning it}}."""
    out = {}
    for code, sub in df.groupby("country"):
        total = max(len(sub), 1)
        exploded = sub["hard_skills"].explode().dropna()
        counts = exploded.value_counts()
        out[code] = {k: round(v / total * 100, 1) for k, v in counts.items()}
    return out


def skill_gaps(my_pct, peer_pct):
    rows = []
    for skill in set(my_pct) | set(peer_pct):
        mp, pp = my_pct.get(skill, 0.0), peer_pct.get(skill, 0.0)
        rows.append({"skill": skill, "my_pct": mp, "peer_pct": pp,
                     "delta": round(mp - pp, 1)})
    rows.sort(key=lambda r: (-abs(r["delta"]), r["skill"]))
    return rows[:TOP_SKILL_GAPS]


def salary_deltas(my_block, peer_block, view):
    """Per role x level, the MY value vs the peer value for one currency view."""
    rows = []
    for role, levels in my_block["categories"].items():
        peer_levels = peer_block["categories"].get(role, {})
        for level, entry in levels.items():
            if not isinstance(entry, dict):
                continue
            peer_entry = peer_levels.get(level)
            if not isinstance(peer_entry, dict):
                continue
            mine = entry.get("salary_estimate", {}).get(view)
            theirs = peer_entry.get("salary_estimate", {}).get(view)
            if mine and theirs:
                rows.append({"role": role, "level": level,
                             "my": mine["median"], "peer": theirs["median"],
                             "delta": round(mine["median"] - theirs["median"], 2)})
    return rows


def build(report, jobs_df):
    """Return the comparisons block for every peer market present."""
    skills = country_skill_pct(jobs_df) if not jobs_df.empty else {}
    my_skills = skills.get(HOME, {})
    comparisons = {}
    for code, block in report.get("countries", {}).items():
        if code == HOME:
            continue
        peer_skills = skills.get(code, {})
        comparisons[f"{HOME}-vs-{code}"] = {
            "skill_gaps": skill_gaps(my_skills, peer_skills),
            "salary_delta_nominal": salary_deltas(report["countries"][HOME], block, "nominal_myr"),
            "salary_delta_ppp": salary_deltas(report["countries"][HOME], block, "ppp_myr"),
        }
    return comparisons


def load_report():
    with open(config.GAP_REPORT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_report(report):
    with open(config.GAP_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Build cross-country comparisons.")
    parser.add_argument("--self-test", action="store_true", help="Offline checks.")
    args = parser.parse_args()
    config.ensure_utf8_stdout()
    if args.self_test:
        self_test()
        return

    report = load_report()
    with open(config.JOB_ANALYSIS_JSON, "r", encoding="utf-8") as f:
        jobs_df = pd.DataFrame(json.load(f))
    if "country" not in jobs_df.columns:
        jobs_df["country"] = "my"

    report["comparisons"] = build(report, jobs_df)
    save_report(report)
    print(f"Wrote {len(report['comparisons'])} comparison(s) to {config.GAP_REPORT_JSON}")


def self_test():
    df = pd.DataFrame({
        "country": ["my", "my", "sg", "sg"],
        "hard_skills": [["Python"], ["Python", "Java"], ["Python"], ["Go"]],
    })
    pct = country_skill_pct(df)
    assert pct["my"]["Python"] == 100.0
    assert pct["sg"]["Go"] == 50.0
    gaps = skill_gaps(pct["my"], pct["sg"])
    java = next(g for g in gaps if g["skill"] == "Java")
    assert java == {"skill": "Java", "my_pct": 50.0, "peer_pct": 0.0, "delta": 50.0}
    assert all(abs(gaps[i]["delta"]) >= abs(gaps[i + 1]["delta"]) for i in range(len(gaps) - 1))

    def block(nom, ppp):
        return {"categories": {"Backend": {"All": {"salary_estimate": {
            "nominal_myr": {"median": nom}, "ppp_myr": {"median": ppp}}}}}}
    rows = salary_deltas(block(8000, 7000), block(20000, 11000), "ppp_myr")
    assert rows[0] == {"role": "Backend", "level": "All", "my": 7000, "peer": 11000, "delta": -4000}
    print("self-test OK")


if __name__ == "__main__":
    main()
