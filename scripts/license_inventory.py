"""Installed declarations and local model license identities, not legal clearance."""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

if __package__:
    from scripts.evidence import identity, run_directory, write_new
else:
    from evidence import identity, run_directory, write_new
from voicecart.local_http import LocalJSONClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    rows = []
    for dist in importlib.metadata.distributions():
        notices = []
        for item in dist.files or []:
            if any(
                name in str(item).lower() for name in ("license", "copying", "notice")
            ) and ".dist-info/" in str(item):
                path = dist.locate_file(item)
                if path.is_file():
                    notices.append(
                        {
                            "path": str(item),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        }
                    )
        rows.append(
            {
                "name": dist.metadata["Name"],
                "version": dist.version,
                "license_expression": dist.metadata.get("License-Expression"),
                "license_classifiers": [
                    v
                    for v in dist.metadata.get_all("Classifier", [])
                    if v.startswith("License ::")
                ],
                "notice_files": notices,
            }
        )
    node = []
    for name in [
        "@playwright/test",
        "playwright",
        "@axe-core/playwright",
        "axe-core",
        "typescript",
    ]:
        data = json.loads((Path("node_modules") / name / "package.json").read_text())
        node.append(
            {"name": name, "version": data["version"], "license": data.get("license")}
        )
    client = LocalJSONClient("http://127.0.0.1:11439", timeout=5)
    models = []
    for item in client.request("/api/tags")["models"]:
        data = client.request("/api/show", {"model": item["name"]})
        text = data.get("license", "")
        models.append(
            {
                "model": item["name"],
                "digest": item["digest"],
                "details": data.get("details", {}),
                "license_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "license_declared_first_line": text.strip().splitlines()[0]
                if text.strip()
                else "not declared",
            }
        )
    write_new(
        (args.output_dir or run_directory()) / "LICENSE_INVENTORY.json",
        {
            **identity(),
            "method": "Actual installed declarations/notice hashes and local /api/show metadata. No OS/native/container exhaustive BOM or legal interpretation. Model weights, raw source data, voices and notices are not redistributed by this inventory.",
            "python": sorted(rows, key=lambda r: r["name"].lower()),
            "node": node,
            "models": models,
            "ollama_version": client.request("/api/version"),
        },
    )
    print(
        "Recorded Python/Node/local-model declarations:",
        len(rows),
        len(node),
        len(models),
    )


if __name__ == "__main__":
    main()
