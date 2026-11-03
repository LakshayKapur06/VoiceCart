"""Evaluation integrity: transport outages must never become successful rejections."""

import unittest
from unittest.mock import Mock

from scripts.nlu_evaluation import evaluate, summarize
from tests.test_nlu import VOCAB, extraction
from voicecart.local_http import LocalServiceError
from voicecart.nlu import Intent, InterpretationError, validate_interpretation


class EvaluationIntegrityTests(unittest.TestCase):
    def test_reject_label_distinguishes_validation_service_and_unknown_errors(self):
        case = {
            "id": "TEST-EVAL",
            "text": "unsupported",
            "expected": {"reject": True},
            "action_allowed": False,
        }
        for failure, correct, outcome in [
            (InterpretationError("ambiguous"), True, "semantic_rejection"),
            (LocalServiceError("offline"), False, "service_error"),
            (TimeoutError(), False, "service_error"),
            (RuntimeError("defect"), False, "unexpected_error:RuntimeError"),
        ]:
            with self.subTest(outcome=outcome):
                interpreter = Mock()
                interpreter.interpret.side_effect = failure
                row = evaluate(case, interpreter)
                self.assertEqual(row["correct"], correct)
                self.assertEqual(row["outcome"], outcome)

    def test_false_action_proposal_is_counted_without_dispatch(self):
        interpreter = Mock()
        interpreter.interpret.return_value = Intent("add", explicit_add=True)
        row = evaluate(
            {
                "id": "TEST-ACTION",
                "text": "find only",
                "expected": {"kind": "search"},
                "action_allowed": False,
            },
            interpreter,
        )
        metrics = summarize([row])
        self.assertEqual(metrics["false_action_authorization_count"], 1)
        self.assertEqual(metrics["false_action_authorization_rate"], 1)
        self.assertEqual(metrics["exact_expectation_matches"], 0)

    def test_slot_micro_counts_missing_wrong_extra_and_correct(self):
        metrics = summarize(
            [
                {
                    "expected": {
                        "kind": "search",
                        "category": "backpack",
                        "colour": "blue",
                        "size": "medium",
                        "ordinal": None,
                    },
                    "observed": {
                        "kind": "search",
                        "category": "backpack",
                        "colour": "black",
                        "ordinal": 2,
                    },
                    "outcome": "accepted",
                    "correct": False,
                    "action_allowed": False,
                    "false_action_authorization": False,
                    "seconds": 1,
                }
            ]
        )
        self.assertEqual(
            (metrics["slot_tp"], metrics["slot_fp"], metrics["slot_fn"]), (1, 2, 2)
        )
        self.assertAlmostEqual(metrics["slot_micro_f1"], 1 / 3)
        self.assertIsNone(metrics["p95_seconds"])

    def test_malformed_shape_and_unsafe_action_outputs_are_independently_rejected(self):
        for raw in [
            {},
            {"intent": "add"},
            extraction(quantity={"value": True, "evidence": "one"}),
            extraction(intent="search_and_add", add_evidence="add"),
        ]:
            with self.subTest(raw=raw), self.assertRaises(InterpretationError):
                validate_interpretation(raw, "Find backpack; do not add", VOCAB)

    def test_frozen_bank_ids_unique_and_explicit_action_labels(self):
        import json
        from pathlib import Path

        bank = json.loads(Path(__file__).with_name("nlu_eval_v2.json").read_text())[
            "cases"
        ]
        self.assertEqual(len({r["id"] for r in bank}), len(bank))
        self.assertTrue(
            all(type(r["action_allowed"]) is bool and r["expected"] for r in bank)
        )
