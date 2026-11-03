"""Record an actual command, result and log in a new timestamped directory."""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

from scripts.evidence import identity, run_directory, write_new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("Supply -- COMMAND ARGUMENTS")
    root = args.output_dir or run_directory()
    root.mkdir(parents=True, exist_ok=True)
    # One command per directory prevents evidence from being overwritten.
    log = root / "command.log"
    metadata = identity()
    start = time.perf_counter()
    with log.open("x") as target:
        result = subprocess.run(command, stdout=target, stderr=subprocess.STDOUT)
    output = log.read_text(errors="replace")
    runs = []
    for match in re.finditer(
        r"Ran (\d+) tests? in ([\d.]+)s\s+\n\s*(OK[^\n]*|FAILED[^\n]*)", output
    ):
        count, seconds, status = match.groups()
        fields = {
            key: int(value)
            for key, value in re.findall(r"(failures|errors|skipped)=(\d+)", status)
        }
        failures, errors, skipped = (
            fields.get(x, 0) for x in ("failures", "errors", "skipped")
        )
        runs.append(
            {
                "count": int(count),
                "passed": int(count) - failures - errors - skipped,
                "failed": failures,
                "errored": errors,
                "skipped": skipped,
                "seconds": float(seconds),
                "status": status,
            }
        )
    write_new(
        root / "RUN.json",
        {
            **metadata,
            "label": args.label,
            "command": command,
            "exit_code": result.returncode,
            "elapsed_seconds": time.perf_counter() - start,
            "unittest_runs": runs,
            "log": str(log),
            "limitations": [
                "Local disposable PostgreSQL is legacy development tooling, not a production deployment.",
                "Model, physical-device, human, external-platform and legal acceptance are separate.",
                "Tests that were not invoked are not passes.",
            ],
            "warnings": [
                line
                for line in output.splitlines()
                if any(
                    key in line.lower() for key in ("warning:", "not run", "skipped")
                )
            ],
        },
    )
    print(output, end="")
    print("Evidence:", root / "RUN.json")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
