"""Fabricated extraction fixtures and a real loopback HTTP boundary, not model quality evidence."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from voicecart.domain import PriceOperator, RetrievalRoute
from voicecart.local_http import LocalJSONClient, LocalServiceError, strict_json
from voicecart.nlu import (
    InterpretationError,
    OllamaInterpreter,
    rupees_to_minor,
    validate_interpretation,
)

VOCAB = {
    "category": {"backpack": "backpack", "backpacks": "backpack"},
    "colour": {"black": "black", "blue": "blue"},
    "size": {"medium": "medium"},
}


def extraction(**changes):
    fields = dict(
        intent="search",
        query="backpack",
        category={"value": "backpack", "evidence": "backpack"},
        colour=None,
        size=None,
        price=None,
        quantity=None,
        identifier=None,
        ordinal=None,
        objective="best_match",
        add_evidence=None,
        unresolved=[],
    )
    fields.update(changes)
    return fields


class InterpretationTests(unittest.TestCase):
    def test_structured_and_discovery_scopes_remain_distinct(self):
        result = validate_interpretation(extraction(), "find backpack", VOCAB)
        self.assertEqual(result.search.route, RetrievalRoute.STRUCTURED)
        result = validate_interpretation(
            extraction(query="backpack for college"), "find backpack for college", VOCAB
        )
        self.assertEqual(result.search.route, RetrievalRoute.DISCOVERY)
        # The extractor cannot drop an unsupported adjective and upgrade scope.
        result = validate_interpretation(
            extraction(), "find waterproof backpack", VOCAB
        )
        self.assertEqual(result.search.route, RetrievalRoute.DISCOVERY)
        self.assertIn("waterproof", result.search.semantic_query)

    def test_integer_money_and_strict_inclusive_bounds(self):
        for phrase, amount, operator in (
            ("under 2,000", "2000", "lt"),
            ("at most two thousand", "two thousand", "lte"),
        ):
            raw = extraction(
                price={"amount": amount, "operator": operator, "evidence": phrase}
            )
            result = validate_interpretation(
                raw, f"find backpack {phrase} rupees", VOCAB
            )
            self.assertEqual(
                result.search.constraints.price_limit.amount.minor_units, 200000
            )
            self.assertEqual(
                result.search.constraints.price_limit.operator, PriceOperator(operator)
            )
        self.assertEqual(rupees_to_minor("1,50,000.25"), 15000025)
        for invalid in (
            "12,34",
            "1.001",
            "NaN",
            "-1",
            "one million",
            "one two",
            "one hundred hundred",
            "two thousand one lakh",
        ):
            with (
                self.subTest(invalid=invalid),
                self.assertRaises((ValueError, TypeError)),
            ):
                rupees_to_minor(invalid)

    def test_critical_field_loss_and_operator_drift_are_rejected(self):
        price = {"amount": "2000", "operator": "lt", "evidence": "under 2000"}
        for changed in (
            None,
            {**price, "operator": "lte"},
            {**price, "amount": "20000"},
        ):
            with self.subTest(changed=changed), self.assertRaises(InterpretationError):
                validate_interpretation(
                    extraction(price=changed), "backpack under 2000", VOCAB
                )
        with self.assertRaises(InterpretationError):
            validate_interpretation(extraction(), "cheapest backpack", VOCAB)
        with self.assertRaises(InterpretationError):
            validate_interpretation(extraction(), "black backpack", VOCAB)

    def test_negation_cannot_authorize_add_or_invert_colour(self):
        raw = extraction(intent="search_and_add", add_evidence="add")
        for text in (
            "find backpack but don't add",
            "never add backpack",
            "find backpack without adding to cart",
        ):
            with self.subTest(text=text), self.assertRaises(InterpretationError):
                validate_interpretation(raw, text, VOCAB)
        raw = extraction(colour={"value": "blue", "evidence": "blue"})
        with self.assertRaises(InterpretationError):
            validate_interpretation(raw, "backpack not blue", VOCAB)

    def test_bool_extra_keys_and_fabricated_evidence_are_rejected(self):
        for raw in (
            extraction(extra="execute sql"),
            extraction(quantity={"value": True, "evidence": "one"}),
            extraction(category={"value": "backpack", "evidence": "shirt"}),
            extraction(unresolved=["size"]),
        ):
            with self.subTest(raw=raw), self.assertRaises(InterpretationError):
                validate_interpretation(raw, "find backpack", VOCAB)

    def test_quantity_and_total_budget_semantics(self):
        raw = extraction(
            intent="search_and_add",
            add_evidence="add",
            quantity={"value": 2, "evidence": "two"},
            price={"amount": "100.01", "operator": "lt", "evidence": "under 100.01"},
        )
        result = validate_interpretation(
            raw, "add two backpack under 100.01 total", VOCAB
        )
        self.assertEqual(result.search.constraints.price_limit.amount.minor_units, 5001)
        with self.assertRaises(InterpretationError):
            validate_interpretation(raw, "add two backpack under 100.01", VOCAB)
        raw["quantity"] = None
        with self.assertRaises(InterpretationError):
            validate_interpretation(raw, "add two backpack under 100.01 each", VOCAB)

    def test_exact_identifier_and_ordinal_require_literal_evidence(self):
        raw = extraction(
            intent="add",
            query=None,
            category=None,
            add_evidence="add",
            identifier={
                "kind": "sku",
                "value": "SKU-BLK-101",
                "evidence": "SKU-BLK-101",
            },
        )
        result = validate_interpretation(raw, "add SKU-BLK-101", VOCAB)
        self.assertEqual(result.search.identifier.value, "SKU-BLK-101")
        raw["identifier"]["value"] = "SKU-BLK-10"
        with self.assertRaises(InterpretationError):
            validate_interpretation(raw, "add SKU-BLK-101", VOCAB)
        raw = extraction(
            intent="add",
            query=None,
            category=None,
            add_evidence="add",
            ordinal={"value": 2, "evidence": "second"},
        )
        result = validate_interpretation(raw, "add second", VOCAB)
        self.assertEqual(result.ordinal, 2)
        self.assertIsNone(result.search)

    def test_unknown_currency_and_ambiguous_bounds_need_clarification(self):
        for text in (
            "backpack under 20 dollars",
            "backpack under 1000 at most 1500",
            "backpack budget 1500",
        ):
            with self.subTest(text=text), self.assertRaises(InterpretationError):
                validate_interpretation(extraction(), text, VOCAB)

    def test_control_requests_are_narrow_and_do_not_reuse_search_state(self):
        result = validate_interpretation(extraction(intent="cancel"), "cancel", VOCAB)
        self.assertEqual(result.kind, "cancel")
        self.assertIsNone(result.search)
        with self.assertRaises(InterpretationError):
            validate_interpretation(
                extraction(intent="repeat"), "repeat add backpack", VOCAB
            )


class LocalTransportTests(unittest.TestCase):
    def test_external_url_credentials_paths_and_nonfinite_timeouts_rejected(self):
        for url in (
            "https://example.com",
            "http://192.168.1.1:11434",
            "http://user:pass@localhost",
            "http://localhost/api",
            "http://localhost?x=1",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                LocalJSONClient(url)
        with self.assertRaises(ValueError):
            LocalJSONClient(timeout=float("nan"))
        for data in ('{"x":1,"x":2}', '{"x":NaN}'):
            with self.assertRaises(ValueError):
                strict_json(data)


class OllamaProtocolIntegrationTests(unittest.TestCase):
    """Actual HTTP requests to a scripted server; no actual neural model runs."""

    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                data = {"models": [{"name": "fixture-model", "digest": "a" * 64}]}
                self.reply(data)

            def do_POST(self):
                self.server.payload = json.loads(
                    self.rfile.read(int(self.headers["Content-Length"]))
                )
                self.reply(self.server.result)

            def reply(self, data):
                body = json.dumps(data).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.client = LocalJSONClient(
            f"http://127.0.0.1:{cls.server.server_port}", timeout=2
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(2)

    def setUp(self):
        self.server.result = {
            "done": True,
            "done_reason": "stop",
            "response": json.dumps(extraction()),
        }

    def test_actual_transport_schema_and_independent_validation(self):
        interpreter = OllamaInterpreter(self.client, "fixture-model", "a" * 64)
        self.assertEqual(interpreter.interpret("find backpack", VOCAB).kind, "search")
        self.assertFalse(self.server.payload["stream"])
        self.assertFalse(self.server.payload["format"]["additionalProperties"])
        self.assertEqual(self.server.payload["options"]["num_predict"], 768)

    def test_embedding_http_shape_and_generation_are_checked(self):
        from voicecart.embeddings import EncoderSpec, OllamaEncoder

        self.server.result = {"embeddings": [[3, 4]]}
        spec = EncoderSpec("fixture-model", "a" * 64, 2)
        encoder = OllamaEncoder(self.client, spec)
        self.assertEqual(encoder.encode(["college backpack"]), [(0.6, 0.8)])
        self.assertFalse(self.server.payload["truncate"])
        self.server.result = {"embeddings": [[1]]}
        with self.assertRaises(LocalServiceError):
            encoder.encode(["backpack"])

    def test_wrong_digest_or_truncated_generation_never_returns_plan(self):
        with self.assertRaises(LocalServiceError):
            OllamaInterpreter(self.client, "fixture-model", "b" * 64).interpret(
                "find backpack", VOCAB
            )
        for result in (
            {"done": False},
            {"done": True, "done_reason": "length", "response": "{}"},
        ):
            self.server.result = result
            with self.assertRaises(LocalServiceError):
                OllamaInterpreter(self.client, "fixture-model", "a" * 64).interpret(
                    "find backpack", VOCAB
                )

    def test_malformed_model_json_and_extra_fields_never_returns_plan(self):
        for response in (
            "not json",
            json.dumps(extraction(extra="SQL")),
            '{"intent":"search","intent":"add"}',
        ):
            self.server.result["response"] = response
            with self.assertRaises(InterpretationError):
                OllamaInterpreter(self.client, "fixture-model", "a" * 64).interpret(
                    "find backpack", VOCAB
                )
