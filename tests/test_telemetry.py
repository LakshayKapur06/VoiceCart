"""Timing is opt-in, context-isolated and never captures raw content."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from voicecart.telemetry import inference_metrics, measurements, span, timed


class TelemetryTests(unittest.TestCase):
    def test_nested_failure_numeric_metrics_and_context_cleanup(self):
        @timed("failure")
        def fail(secret):
            raise ValueError(secret)

        with measurements() as trace:
            with self.assertRaises(ValueError):
                fail("PRIVATE TRANSCRIPT")
            inference_metrics({"load_duration": 2_000_000_000, "eval_duration": True})
        self.assertEqual(trace.spans[0]["outcome"], "error")
        self.assertEqual(trace.spans[1]["seconds"], 2)
        self.assertNotIn("PRIVATE", str(trace.spans))
        with span("outside"):
            pass
        self.assertEqual(len(trace.spans), 2)

    def test_concurrent_traces_do_not_mix(self):
        def record(value):
            with measurements() as trace:
                with span(str(value)):
                    pass
            return trace.spans[0]["stage"]

        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(
                list(pool.map(record, range(20))), list(map(str, range(20)))
            )
