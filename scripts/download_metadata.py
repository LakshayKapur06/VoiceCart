"""Explicit bounded download from the pinned official metadata repository."""

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

REVISION = "2b6d039ed471f2ba5fd2acb718bf33b0a7e5598e"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(".local/datasets"))
    parser.add_argument("--rows", type=int, default=300)
    args = parser.parse_args()
    if not 1 <= args.rows <= 1000:
        raise ValueError("Choose 1–1000 bounded development rows")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    url = f"https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/{REVISION}/raw/meta_categories/meta_Appliances.jsonl"
    target = args.output_dir / f"appliances-first{args.rows}.jsonl"
    if target.exists():
        raise FileExistsError("Source exists; preserve it or select a new directory")
    count = 0
    with (
        urllib.request.urlopen(url, timeout=45) as response,
        target.open("wb") as output,
    ):
        for _ in range(args.rows):
            line = response.readline(2 * 1024 * 1024 + 1)
            if not line:
                break
            if len(line) > 2 * 1024 * 1024:
                raise ValueError("Oversized source row")
            json.loads(line)
            output.write(line)
            count += 1
    manifest = {
        "dataset": "McAuley-Lab/Amazon-Reviews-2023",
        "revision": REVISION,
        "url": url,
        "category": "Appliances",
        "rows": count,
        "selection": f"first {args.rows} rows, partial historical source",
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "terms": "No explicit dataset redistribution license found in official dataset card/site; private owner-requested research extract only, not redistribution clearance.",
    }
    (args.output_dir / "appliances-source.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
