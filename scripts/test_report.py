"""Execute real isolated tests and generate source-linked lab test case records."""

import argparse
import ast
import hashlib
import time
import unittest
from datetime import UTC, datetime
from pathlib import Path

if __package__:
    from scripts.verify import isolated_postgres
else:
    from verify import isolated_postgres


class Results(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.started = time.perf_counter()
        self.rows = getattr(self, "rows", {})
        self.rows[test.id()] = {
            "status": "Not Run",
            "started_at": datetime.now(UTC).isoformat(),
        }

    def stopTest(self, test):
        self.rows[test.id()]["seconds"] = time.perf_counter() - self.started
        super().stopTest(test)

    def addSuccess(self, test):
        self.rows[test.id()]["status"] = "Pass"
        super().addSuccess(test)

    def addFailure(self, test, error):
        self.rows[test.id()]["status"] = "Fail"
        super().addFailure(test, error)

    def addError(self, test, error):
        self.rows[test.id()]["status"] = "Fail"
        super().addError(test, error)

    def addSkip(self, test, reason):
        self.rows[test.id()].update(status="Not Run", reason=reason)
        super().addSkip(test, reason)

    def addSubTest(self, test, subtest, error):
        if error:
            self.rows[test.id()]["status"] = "Fail"
        super().addSubTest(test, subtest, error)


def manual_cases():
    cases = [
        (
            "DEVICE",
            "Physical microphone/speaker and noise/pauses/interruptions",
            "Provision exact English voice models and consented physical devices; record several prices/SKUs with silence/noise and stop/repeat.",
            "Correct reviewed transcripts/negation, no partial mutation, stopped audio, understood prices and recovery.",
            "Headless host capture returned NotSupportedError; browser capture/ASR fault tests are explicitly scripted. Physical device/user test Not Run.",
        ),
        (
            "A11Y",
            "Representative blind/low-vision screen-reader acceptance",
            "Use actual VoiceOver/screen reader and keyboard on desktop/mobile; search, review, select, change cart and recover from error.",
            "Correct focus/order/status announcements, intelligible amounts/SKUs and independent completion without a mouse.",
            "Automated keyboard/axe checks passed checked states; representative-user/screen-reader speech acceptance Not Run.",
        ),
        (
            "DOCKER",
            "Clean container installation and persistent restart",
            "Install Docker; provision private secrets; compose config/up; migrate/import; stop/start and restore into a separate destination.",
            "Healthy actual services, readable scoped secrets, persisted revision/cart/receipts, correct migration/recovery and no seed fixtures.",
            "Docker is unavailable; static configuration only. Clean container/restart acceptance Not Run.",
        ),
        (
            "MERCHANT",
            "External merchant platform conformance",
            "Implement an approved adapter with real merchant credentials/current source and authoritative idempotency/outcome lookup.",
            "Fresh merchant facts and platform receipt own every confirmed mutation; tenant/auth/retry/failure contracts hold.",
            "Only the actual local adapter is implemented; external Shopify/WooCommerce/Magento integration Not Run/unsupported.",
        ),
        (
            "RIGHTS",
            "Distribution and data/voice rights review",
            "Owner specifies project/license/deployment intent and obtains dataset/voice/dependency distribution clearance.",
            "Exact notices, source obligations and permitted data/voice use documented for the actual shipped artifacts.",
            "Inventory/declared terms inspected; no dataset-wide redistribution grant or owner project license selected. Commercial redistribution acceptance Not Run.",
        ),
        (
            "AUDIBLE",
            "Calibrated full audible latency acceptance",
            "Measure actual end of user speech to meaningful verified audible response, cold/warm, failures and sufficient samples on approved hardware/language.",
            "Report sample sizes/percentiles/timeouts and compare the unchanged 1.5s goal without substituting enqueue or synthesis time.",
            "Stage/file timings exist; calibrated acoustic/human full-turn acceptance Not Run.",
        ),
        (
            "PLATFORM",
            "Windows/Linux/GPU/mobile hardware acceptance",
            "Run documented clean setup and real devices on each supported candidate platform, including network/permissions and model resources.",
            "Platform-specific setup, recovery, input/output and resource observations recorded without assuming parity.",
            "Native macOS source/wheel/Chromium checks completed; other physical platform/GPU acceptance Not Run.",
        ),
    ]
    rows = ["\n# Manual and external acceptance records"]
    for identifier, name, steps, expected, reason in cases:
        rows.append(
            f"\n## VC-MAN-{identifier} — {name}\n\n**Test Case ID:** VC-MAN-{identifier}\n\n**Test Case Name:** {name}\n\n**System/Sub-system:** Release acceptance\n\n**Designed By:** VoiceCart engineering test automation\n\n**Design Date:** 2026-11-02\n\n**Executed By:** Not Run\n\n**Execution Date:** Not Run\n\n**Description:** Required acceptance beyond automated source/browser contracts.\n\n**Preconditions:** Owner-approved real environment/users/rights and isolated recovery plan.\n\n**Test Steps / Step Number / Action:** 1. {steps} 2. Record observations, failures and evidence. 3. Restore/stop the test resources.\n\n**Expected Result:** {expected}\n\n**Actual Result:** {reason}\n\n**Pass/Fail/Not Run:** Not Run\n\n**Comments:** No automated fixture/model/protocol result is substituted for this acceptance.\n\n**Postconditions:** Protect owner data; stop capture and remove unnecessary diagnostics.\n\n**Defect Reference:** OPEN-{identifier}."
        )
    rows.append(
        "\n## VC-ML-H05 — held-out quantity interpretation\n\n**Test Case ID:** VC-ML-H05\n\n**Test Case Name:** Two-item explicit search-and-add\n\n**System/Sub-system:** Actual pinned local NLU\n\n**Designed By:** VoiceCart frozen holdout design\n\n**Design Date:** 2026-11-02\n\n**Executed By:** scripts/benchmark_nlu.py against actual Qwen\n\n**Execution Date:** 2026-11-02\n\n**Description:** H05 in tests/nlu_holdout.json; no prompt tuning on this evaluation.\n\n**Preconditions:** Pinned local Qwen model and canonical fixture vocabulary, no writes.\n\n**Test Steps / Step Number / Action:** 1. Submit the exact H05 text. 2. Apply strict independent validation. 3. Compare against search_and_add quantity 2 expectation.\n\n**Expected Result:** Valid explicit intent with quantity 2.\n\n**Actual Result:** InterpretationError (safe rejection), recorded 21.882 seconds; no commerce dispatch.\n\n**Pass/Fail/Not Run:** Fail (quality expectation; safety preserved).\n\n**Comments:** Eleven other declared holdout expectations passed; this is not population accuracy.\n\n**Postconditions:** No cart/database mutation.\n\n**Defect Reference:** OPEN-NLU-H05; improve on development data and reevaluate on a new frozen holdout."
    )
    return rows


def main():
    if __package__:
        from scripts.evidence import identity, run_directory, write_new
    else:
        from evidence import identity, run_directory, write_new

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    evidence = args.output_dir or run_directory()
    with isolated_postgres():
        suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
        result = unittest.TextTestRunner(verbosity=1, resultclass=Results).run(suite)
    report = {
        "method": "New execution of actual unittest methods and their subtests in guarded disposable PostgreSQL. Browser/SDK/model/manual acceptance evidence is separate.",
        "executed_at": datetime.now(UTC).isoformat(),
        "test_count": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "cases": result.rows,
    }
    write_new(evidence / "TEST_EXECUTION.json", {**identity(), **report})
    text = [
        "# VoiceCart test case records",
        f"Current execution: {report['executed_at']}. Evidence: [{evidence.name}/TEST_EXECUTION.json](../{evidence}/TEST_EXECUTION.json). Source design dates are historical where known; current mappings were reviewed on {datetime.now(UTC).date()}.",
        "Generated from actual source tests and a new recorded execution. Source methods contain exact fixture arrangements, inputs and expected assertions. A case is Pass only when that method actually completed successfully; skipped/unexecuted cases are Not Run. Test data is fabricated only in explicitly guarded test files/databases. This record does not mark real-device, Docker or human acceptance as passed.",
        "Design technique mapping and concrete decision/partition/loop scenarios are in [TESTING_GUIDE.md](TESTING_GUIDE.md); white-box graphs and independent-path designs are in [CFG_ANALYSIS.md](CFG_ANALYSIS.md).",
    ]
    for name, row in sorted(report["cases"].items()):
        module, cls, method = name.rsplit(".", 2)
        path = Path(module.replace(".", "/") + ".py")
        tree = ast.parse(path.read_text())
        classnode = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == cls
        )
        node = next(
            node
            for node in classnode.body
            if isinstance(node, ast.FunctionDef) and node.name == method
        )
        assertions = [
            ast.unparse(child)
            for child in ast.walk(node)
            if isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr.startswith("assert")
        ]
        inputs = [
            ast.unparse(child)
            for child in node.body
            if isinstance(child, (ast.Assign, ast.AnnAssign))
        ][:3]
        identifier = "VC-" + hashlib.sha256(name.encode()).hexdigest()[:8].upper()
        expected = (
            "; ".join(assertions)
            if assertions
            else "The complete source method finishes without an unhandled error; inspect any helper assertions at the linked source."
        )
        actual = (
            "All method assertions completed without a failure."
            if row["status"] == "Pass"
            else row.get("reason", "See execution report; not passed.")
        )
        text += [
            f"\n## {identifier} — {method.removeprefix('test_').replace('_', ' ')}",
            f"**Test Case ID:** {identifier}\n\n**Test Case Name:** {cls}.{method}\n\n**System/Sub-system:** {module}\n\n**Designed By:** VoiceCart engineering test automation\n\n**Design Date:** {datetime.now(UTC).date()} (current mapping review; see Git source history for original design)\n\n**Executed By:** Python unittest runner\n\n**Execution Date:** {row['started_at']}",
            f"**Description:** Executable contract [{name}](../{path}#L{node.lineno}), lines {node.lineno}–{node.end_lineno}.\n\n**Preconditions:** Dedicated declared Python dependencies; scripts/test_report.py owns the temporary PostgreSQL server. Module-specific setup/fixtures are at the source link. No owner DB is used.\n\n**Concrete input arrangement:** `{('; '.join(inputs) or 'See the source method and class setUp fixture.').replace('`', chr(39))[:1200]}`",
            f"**Test Steps / Step Number / Action:**\n\n1. Arrange the exact source fixture and input cases linked above.\n2. Execute `python -m scripts.run_tests {name}` using the guarded runner (or execute `python -m scripts.test_report` for the complete safe driver).\n3. Evaluate the following exact source assertions and restore owned temporary state.\n\n**Expected Result:**\n\n```python\n{expected}\n```",
            f"**Actual Result:** {actual} Duration {row['seconds']:.4f} seconds.\n\n**Pass/Fail/Not Run:** {row['status']}\n\n**Comments:** Subtest inputs/expected values are part of the exact source method. This outcome is not an inference/device/human-accessibility result.\n\n**Postconditions:** Per-test/class cleanup and the runner-owned service teardown preserve normal owner data.\n\n**Defect Reference:** None observed in this execution."
            if row["status"] == "Pass"
            else f"**Defect Reference:** See {evidence}/TEST_EXECUTION.json and the failed/skipped source test; unresolved status is not Pass.",
        ]
    text += manual_cases()
    Path("docs/TEST_CASES.md").write_text("\n\n".join(text) + "\n")
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
