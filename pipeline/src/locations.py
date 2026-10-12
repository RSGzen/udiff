"""Normalise a raw job location into a state/region.

Used by processor.py (per-posting) and analyzer.py (the `states` section), so
the two never drift apart. Hints are matched as whole words, which fixes the
old `'kl' in text` bug that also swallowed "Klang".
"""

import re

import pandas as pd

# Ordered: more specific hints first. Each entry is (state, [hints]).
MY_REGIONS = [
    ("Kuala Lumpur", ["kuala lumpur", "kl", "bangsar", "bukit jalil", "cheras",
                       "setapak", "wangsa maju", "mont kiara", "sri petaling"]),
    ("Selangor", ["selangor", "petaling jaya", "pj", "cyberjaya", "subang",
                  "puchong", "shah alam", "klang", "damansara", "bangi", "kajang",
                  "seri kembangan", "sepang", "rawang", "ampang", "gombak"]),
    ("Penang", ["penang", "pulau pinang", "georgetown", "bayan lepas",
                "butterworth", "bukit mertajam", "seberang"]),
    ("Johor", ["johor", "jb", "iskandar", "skudai", "kulai", "batu pahat",
               "muar", "senai"]),
    ("Melaka", ["melaka", "malacca", "ayer keroh", "alor gajah"]),
    ("Negeri Sembilan", ["negeri sembilan", "seremban", "nilai", "port dickson",
                          "senawang"]),
    ("Perak", ["perak", "ipoh", "taiping", "kampar", "manjung", "teluk intan"]),
    ("Kedah", ["kedah", "alor setar", "sungai petani", "kulim", "langkawi"]),
    ("Kelantan", ["kelantan", "kota bharu", "kubang kerian"]),
    ("Terengganu", ["terengganu", "kuala terengganu", "kemaman", "kerteh"]),
    ("Pahang", ["pahang", "kuantan", "temerloh", "bentong", "cameron highlands"]),
    ("Sabah", ["sabah", "kota kinabalu", "sandakan", "tawau"]),
    ("Sarawak", ["sarawak", "kuching", "miri", "sibu", "bintulu"]),
    ("Putrajaya", ["putrajaya"]),
    ("Labuan", ["labuan"]),
    ("Perlis", ["perlis", "kangar", "arau"]),
]


def _hits(text, hint):
    return re.search(r"\b" + re.escape(hint) + r"\b", text) is not None


# Coarse region for non-MY markets (no per-province map yet).
COUNTRY_NAMES = {"sg": "Singapore", "id": "Indonesia"}


def normalize_location(raw_location, country="my"):
    """Derive `{location_raw, state}` from a raw location string.

    For Malaysia the state comes from MY_REGIONS; other markets (M5.7) get a
    coarse country-level region until per-province maps are added.
    """
    if raw_location is None or (isinstance(raw_location, float) and pd.isna(raw_location)):
        return {"location_raw": "Unknown", "state": "Unknown"}

    text = str(raw_location).lower()

    if country == "my":
        for state, hints in MY_REGIONS:
            if any(_hits(text, hint) for hint in hints):
                return {"location_raw": raw_location, "state": state}
        if "malaysia" in text:
            return {"location_raw": raw_location, "state": "Malaysia (General)"}
    elif country in COUNTRY_NAMES:
        return {"location_raw": raw_location, "state": COUNTRY_NAMES[country]}

    return {"location_raw": raw_location, "state": "Other"}


def self_test():
    assert normalize_location("Bayan Lepas, Penang")["state"] == "Penang"
    assert normalize_location("Klang, Selangor")["state"] == "Selangor"
    assert normalize_location("Malacca")["state"] == "Melaka"
    assert normalize_location("Kota Kinabalu, Sabah")["state"] == "Sabah"
    assert normalize_location("Kuala Lumpur, Federal Territory")["state"] == "Kuala Lumpur"
    assert normalize_location("Malaysia")["state"] == "Malaysia (General)"
    assert normalize_location("Singapore", country="sg")["state"] == "Singapore"
    assert normalize_location("Jakarta", country="id")["state"] == "Indonesia"
    assert normalize_location(None)["state"] == "Unknown"
    print("self-test OK")


if __name__ == "__main__":
    self_test()
