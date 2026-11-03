"""Frozen text holdout and numeric timings; opt-in actual local inference."""

import argparse
import json
import platform
import resource
import statistics
import time
from pathlib import Path

from voicecart.local_http import LocalJSONClient
from voicecart.nlu import PROMPT_VERSION, InterpretationError, OllamaInterpreter
from voicecart.telemetry import measurements


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:11439")
    parser.add_argument("--model", default="qwen3:4b-instruct-2507-q4_K_M")
    parser.add_argument(
        "--digest",
        default="0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = json.loads(Path("tests/nlu_holdout.json").read_text())
    client = LocalJSONClient(args.url, timeout=120)
    model = OllamaInterpreter(client, args.model, args.digest)
    vocab = {
        "category": {
            "backpacks": "backpack",
            "backpack": "backpack",
            "shirts": "shirt",
        },
        "colour": {"black": "black", "blue": "blue"},
        "size": {},
    }
    rows = []
    for index, case in enumerate(cases):
        start = time.perf_counter()
        with measurements() as trace:
            try:
                intent = model.interpret(case["text"], vocab)
                correct = not case.get("reject") and intent.kind == case["kind"]
                if "price_minor" in case:
                    limit = (
                        intent.constraints.price_limit if intent.constraints else None
                    )
                    correct = (
                        correct
                        and limit is not None
                        and limit.amount.minor_units == case["price_minor"]
                        and limit.operator.value == case["operator"]
                    )
                for key in ("quantity", "ordinal"):
                    if key in case:
                        correct = correct and getattr(intent, key) == case[key]
                if "route" in case:
                    correct = (
                        correct
                        and intent.search is not None
                        and intent.search.route.value == case["route"]
                    )
                outcome = intent.kind
            except InterpretationError as error:
                correct = bool(case.get("reject"))
                outcome = type(error).__name__
            except Exception as error:
                correct = False
                outcome = "service_or_unexpected_error:" + type(error).__name__
        row = {
            "id": case["id"],
            "correct": bool(correct),
            "outcome": outcome,
            "seconds": time.perf_counter() - start,
            "condition": "first/cold-or-model-switch"
            if index == 0
            else "subsequent/warm-request",
            "spans": trace.spans,
        }
        rows.append(row)
        print(case["id"], outcome, correct, round(row["seconds"], 3), flush=True)
    times = [row["seconds"] for row in rows]
    with args.output.open("x") as target:
        target.write(
            json.dumps(
                {
                    "method": "Frozen continuation holdout, one pass, no prompt tuning on these results. Text-only; no audio/commerce writes. First request and subsequent requests reported separately; no p95/p99 estimate from 12 observations. Nested spans overlap and must not be summed. Runtime load/prompt/eval counters are service-reported.",
                    "prompt_version": PROMPT_VERSION,
                    "model": args.model,
                    "digest": args.digest,
                    "platform": platform.platform(),
                    "python": platform.python_version(),
                    "client_peak_rss_native_units": resource.getrusage(
                        resource.RUSAGE_SELF
                    ).ru_maxrss,
                    "client_cpu_seconds": resource.getrusage(
                        resource.RUSAGE_SELF
                    ).ru_utime,
                    "count": len(rows),
                    "correct": sum(row["correct"] for row in rows),
                    "mean_seconds": statistics.mean(times),
                    "median_seconds": statistics.median(times),
                    "results": rows,
                },
                indent=2,
            )
            + "\n"
        )


if __name__ == "__main__":
    main()
