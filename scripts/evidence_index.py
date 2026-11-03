"""New derived index over immutable run logs, including failed and skipped results."""

import argparse
import json
from pathlib import Path

if __package__:
    from scripts.evidence import identity, run_directory, test_counts, write_new
else:
    from evidence import identity, run_directory, test_counts, write_new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    rows = []
    for path in sorted(Path("docs/evidence").glob("20261103*/RUN.json")):
        data = json.loads(path.read_text())
        log = path.parent / "command.log"
        rows.append(
            {
                "record": str(path),
                "label": data["label"],
                "commit_sha": data["commit_sha"],
                "command": data["command"],
                "exit_code": data["exit_code"],
                "reported_test_counts": test_counts(log.read_text(errors="replace")),
                "warnings": data["warnings"],
                "historical_record_unchanged": True,
            }
        )
    write_new(
        (args.output_dir or run_directory()) / "EVIDENCE_INDEX.json",
        {
            **identity(),
            "method": "New derived summary from already recorded immutable logs, not a rerun or replacement. Nonzero measurement/probe outcomes remain visible. A completed model process is not quality acceptance. Static tools have no invented test count.",
            "runs": rows,
        },
    )
    print("Indexed actual run records:", len(rows))


if __name__ == "__main__":
    main()
