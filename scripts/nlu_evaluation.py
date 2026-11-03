"""Frozen authored text evaluation; rejected syntax is separate from unavailable service."""

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path

if __package__:
    from scripts.evidence import identity, run_directory, write_new
else:
    from evidence import identity, run_directory, write_new
from voicecart.local_http import LocalJSONClient, LocalServiceError
from voicecart.nlu import PROMPT_VERSION, InterpretationError, OllamaInterpreter
from voicecart.telemetry import measurements

VOCAB = {
    "category": {
        "backpack": "backpack",
        "backpacks": "backpack",
        "shirt": "shirt",
        "shirts": "shirt",
    },
    "colour": {"black": "black", "blue": "blue"},
    "size": {"medium": "medium"},
}


def flatten(intent):
    constraint = intent.constraints
    limit = constraint.price_limit if constraint else None
    identifier = intent.search.identifier if intent.search else None
    return {
        "kind": intent.kind,
        "category": constraint.category if constraint else None,
        "colour": constraint.colour if constraint else None,
        "size": constraint.size if constraint else None,
        "quantity": intent.quantity,
        "price_minor": limit.amount.minor_units if limit else None,
        "operator": limit.operator.value if limit else None,
        "ordinal": intent.ordinal,
        "objective": intent.objective,
        "explicit_add": intent.explicit_add,
        "route": intent.search.route.value if intent.search else None,
        "identifier": identifier.value if identifier else None,
    }


def evaluate(case, interpreter):
    start = time.perf_counter()
    with measurements() as trace:
        try:
            intent = interpreter.interpret(case["text"], VOCAB)
            observed = flatten(intent)
            outcome = "accepted"
        except InterpretationError:
            observed, outcome = {}, "semantic_rejection"
        except (LocalServiceError, TimeoutError, OSError):
            observed, outcome = {}, "service_error"
        except Exception as error:
            observed, outcome = {}, "unexpected_error:" + type(error).__name__
    expected = case["expected"]
    correct = (
        outcome == "semantic_rejection"
        if expected.get("reject")
        else outcome == "accepted"
        and all(observed.get(key) == value for key, value in expected.items())
    )
    return {
        "id": case["id"],
        "outcome": outcome,
        "correct": correct,
        "observed": observed,
        "expected": expected,
        "action_allowed": case["action_allowed"],
        "false_action_authorization": bool(observed.get("explicit_add"))
        and not case["action_allowed"],
        "seconds": time.perf_counter() - start,
        "spans": trace.spans,
    }


def summarize(rows):
    tp = fp = fn = 0
    slots = {}
    for row in rows:
        if row["expected"].get("reject"):
            continue
        for key, value in row["expected"].items():
            if key == "kind":
                continue
            predicted = row["observed"].get(key)
            counts = slots.setdefault(
                key, {"correct": 0, "annotated": 0, "tp": 0, "fp": 0, "fn": 0}
            )
            counts["annotated"] += 1
            counts["correct"] += row["outcome"] == "accepted" and predicted == value
            # A rejected output supplies no slots; defaults on accepted output are evaluated too.
            present = row["outcome"] == "accepted" and predicted is not None
            if value is not None and present and predicted == value:
                counts["tp"] += 1
                tp += 1
            else:
                if present:
                    counts["fp"] += 1
                    fp += 1
                if value is not None:
                    counts["fn"] += 1
                    fn += 1
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    accepted = sum(r["outcome"] == "accepted" for r in rows)
    forbidden = sum(not r["action_allowed"] for r in rows)
    rejecting = sum(r["outcome"] == "semantic_rejection" for r in rows)
    times = [r["seconds"] for r in rows]
    return {
        "count": len(rows),
        "exact_expectation_matches": sum(r["correct"] for r in rows),
        "intent_exact_matches": sum(
            (r["expected"].get("reject") and r["outcome"] == "semantic_rejection")
            or (
                r["outcome"] == "accepted"
                and r["observed"].get("kind") == r["expected"].get("kind")
            )
            for r in rows
        ),
        "accepted": accepted,
        "semantic_rejections": rejecting,
        "service_errors": sum(r["outcome"] == "service_error" for r in rows),
        "unexpected_errors": sum(
            r["outcome"].startswith("unexpected_error") for r in rows
        ),
        "slot_tp": tp,
        "slot_fp": fp,
        "slot_fn": fn,
        "slot_micro_precision": precision,
        "slot_micro_recall": recall,
        "slot_micro_f1": f1,
        "slots": slots,
        "safe_rejection_rate": rejecting / len(rows) if rows else None,
        "false_action_authorization_count": sum(
            r["false_action_authorization"] for r in rows
        ),
        "nonaction_cases": forbidden,
        "false_action_authorization_rate": sum(
            r["false_action_authorization"] for r in rows
        )
        / forbidden
        if forbidden
        else None,
        "mean_seconds": statistics.mean(times) if times else None,
        "p50_seconds": statistics.median(times) if times else None,
        "p95_seconds": None,
        "p99_seconds": None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path("tests/nlu_eval_v2.json"))
    parser.add_argument("--model", required=True)
    parser.add_argument("--digest", required=True)
    parser.add_argument("--url", default="http://127.0.0.1:11439")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--unload-first", action="store_true")
    args = parser.parse_args()
    data = args.cases.read_bytes()
    bank = json.loads(data)
    client = LocalJSONClient(args.url, timeout=120)
    model = OllamaInterpreter(client, args.model, args.digest)
    metadata = identity()
    if args.unload_first:
        client.request("/api/generate", {"model": args.model, "keep_alive": 0})
    rows = []
    for index, case in enumerate(bank["cases"]):
        row = evaluate(case, model)
        row["condition"] = (
            "first after explicit model eviction; OS caches uncontrolled"
            if index == 0 and args.unload_first
            else "subsequent request; residency measured by runtime spans"
        )
        rows.append(row)
        print(
            case["id"],
            row["outcome"],
            row["correct"],
            round(row["seconds"], 3),
            flush=True,
        )
    if args.cases.read_bytes() != data:
        raise RuntimeError("Frozen case bank changed during evaluation")
    write_new(
        (args.output_dir or run_directory()) / "NLU.json",
        {
            **metadata,
            "model": args.model,
            "digest": args.digest,
            "prompt_version": PROMPT_VERSION,
            "dataset_sha256": hashlib.sha256(data).hexdigest(),
            "dataset": str(args.cases),
            "method": "One sequential frozen authored English text pass; same hardware and validation/prompt for comparisons; no cart/DB writes. Semantic rejection is distinct from service failure. Slot metrics cover annotated canonical slots only, not free-form query semantic equivalence. False action authorization means validated intent proposal, not a commerce commit. p95/p99 withheld for small sample. OS caches/thermal state/order uncontrolled. Nested spans overlap.",
            "summary": summarize(rows),
            "results": rows,
        },
    )


if __name__ == "__main__":
    main()
