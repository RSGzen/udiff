"""Copy the pipeline's output JSON into the Next.js app's data folder (M7)."""

import shutil

import config

OUTPUTS = [config.GAP_REPORT_JSON, config.SKILL_CLASS_JSON]


def main():
    config.ensure_utf8_stdout()
    config.WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for source in OUTPUTS:
        if not source.is_file():
            raise SystemExit(f"Missing pipeline output: {source}")
        target = config.WEB_DATA_DIR / source.name
        shutil.copyfile(source, target)
        print(f"synced {source.name} -> {target}")
    print(f"Web data up to date in {config.WEB_DATA_DIR}")


if __name__ == "__main__":
    main()
