"""Opt-in real local NLU smoke; no catalogue writes or device playback."""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

from voicecart.local_http import LocalJSONClient
from voicecart.nlu import PROMPT_VERSION, OllamaInterpreter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    client = LocalJSONClient(args.url, timeout=120)
    tags = client.request("/api/tags")["models"]
    vocabulary = {
        "category": {"backpack": "backpack", "shirts": "shirt"},
        "colour": {"black": "black", "blue": "blue"},
        "size": {},
    }
    cases = [
        ("Find a black backpack under 2,000 rupees.", "search", "best_match"),
        (
            "Find the cheapest black backpack under 2000 rupees and add it to my cart.",
            "search_and_add",
            "cheapest",
        ),
        (
            "Search for blue shirts. Do not add anything to the cart.",
            "search",
            "best_match",
        ),
    ]
    results = []
    for model in args.model:
        digest = next(x["digest"] for x in tags if x["name"] == model)
        for request, expected_kind, expected_objective in cases:
            start = time.monotonic()
            row = {"model": model, "digest": digest, "synthetic_test_request": request}
            try:
                intent = OllamaInterpreter(client, model, digest).interpret(
                    request, vocabulary
                )
                row.update(
                    outcome="accepted",
                    intent=intent.kind,
                    objective=intent.objective,
                    correct=intent.kind == expected_kind
                    and intent.objective == expected_objective,
                    route=intent.search.route.value if intent.search else None,
                )
            except Exception as exc:
                row.update(
                    outcome="rejected", correct=False, cause=str(exc.__cause__ or exc)
                )
            row["seconds"] = round(time.monotonic() - start, 4)
            results.append(row)
            print(json.dumps(row), flush=True)
    args.output.write_text(
        json.dumps(
            {
                "recorded_at": datetime.now(UTC).isoformat(),
                "prompt_version": PROMPT_VERSION,
                "method": "Real local models; three development smoke cases per model; no held-out accuracy claim. No device playback or product writes.",
                "results": results,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
