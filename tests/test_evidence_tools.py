"""Evidence integrity contracts: failures/skips retained and prior records immutable."""

import tempfile
import unittest
from pathlib import Path

from scripts.evidence import test_counts, write_new


class EvidenceIntegrityTests(unittest.TestCase):
    def test_source_wheel_counts_are_executions_with_failure_skip_and_error(self):
        output = "Ran 5 tests in 1.0s\n\nFAILED (failures=1, errors=1, skipped=1)\nRan 5 tests in 1.1s\n\nOK\n"
        self.assertEqual(
            test_counts(output),
            {
                "framework": "unittest",
                "scope": "execution totals, not distinct methods across source/wheel runs",
                "executed": 10,
                "passed": 7,
                "failed": 1,
                "errored": 1,
                "skipped": 1,
            },
        )

    def test_browser_node_and_static_summaries_preserve_scope(self):
        result = test_counts("  1 failed\n  7 passed (36.2s)\n")
        self.assertEqual(
            (result["executed"], result["passed"], result["failed"]), (8, 7, 1)
        )
        self.assertIsNone(result["errored"])
        self.assertEqual(
            test_counts("ℹ tests 2\nℹ pass 1\nℹ fail 1\nℹ skipped 0\n")["failed"], 1
        )
        self.assertIsNone(test_counts("Success: no issues found in 30 source files"))

    def test_evidence_write_refuses_overwrite_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            write_new(path, {"status": "FAIL"})
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                write_new(path, {"status": "PASS"})
            self.assertEqual(path.read_bytes(), original)
