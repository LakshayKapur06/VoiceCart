"""Executable partitions, boundaries, decision rules and loop designs (test-only data)."""

import hashlib
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from tests.database_support import fabricated_document, isolated_database
from tests.test_persistence import FixtureEncoder
from voicecart.domain import MAX_MINOR_UNITS, Money, PriceLimit, PriceOperator
from voicecart.ingestion import ImportValidationError, load_import, parse_import
from voicecart.nlu import InterpretationError, whole_number
from voicecart.sessions import SessionError, SessionStore
from voicecart.voice import FileArtifact, VoiceError


class SyllabusPartitions(unittest.TestCase):
    def test_money_min_max_bool_float_and_lt_lte_decision_table(self):
        for price in (0, 1, MAX_MINOR_UNITS):
            self.assertEqual(Money(price, "INR").minor_units, price)
        for price in (-1, MAX_MINOR_UNITS + 1, True, 1.0):
            with self.subTest(price=price), self.assertRaises((TypeError, ValueError)):
                Money(price, "INR")
        for operator, price, expected in [
            (PriceOperator.LT, 99, True),
            (PriceOperator.LT, 100, False),
            (PriceOperator.LT, 101, False),
            (PriceOperator.LTE, 99, True),
            (PriceOperator.LTE, 100, True),
            (PriceOperator.LTE, 101, False),
        ]:
            self.assertEqual(
                PriceLimit(Money(100, "INR"), operator).permits(Money(price, "INR")),
                expected,
            )

    def test_number_loop_zero_one_two_typical_scales_and_early_failure(self):
        for text, expected in [
            ("0", 0),
            ("one", 1),
            ("twenty one", 21),
            ("one hundred and five", 105),
            ("two thousand three hundred forty five", 2345),
            ("one lakh twenty thousand", 120000),
        ]:
            self.assertEqual(whole_number(text), expected)
        for text in (
            "",
            "and one",
            "one one",
            "hundred",
            "one thousand thousand",
            "one and one",
            "twenty twenty",
        ):
            with self.subTest(text=text), self.assertRaises(InterpretationError):
                whole_number(text)

    def test_import_file_boundary_and_oversized_manifest_without_huge_allocation(self):
        source = Mock()
        source.stat.return_value.st_size = 128 * 1024 * 1024
        source.read_text.return_value = __import__("json").dumps(fabricated_document())
        self.assertEqual(load_import(source).revision, "fixture-1")
        source.reset_mock()
        source.stat.return_value.st_size = 128 * 1024 * 1024 + 1
        with self.assertRaises(ImportValidationError):
            load_import(source)
        source.read_text.assert_not_called()

        class TooMany(list):
            def __len__(self):
                return 100001

        document = fabricated_document()
        document["products"] = TooMany()
        with self.assertRaises(ImportValidationError):
            parse_import(document)

    def test_secret_provisioning_private_parent_and_container_readable_files(self):
        import stat
        import subprocess
        import sys

        script = Path(__file__).resolve().parents[1] / "scripts/init_secrets.py"
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=folder,
                capture_output=True,
                text=True,
                check=True,
            )
            parent = Path(folder) / ".secrets"
            self.assertEqual(stat.S_IMODE(parent.stat().st_mode), 0o700)
            for path in parent.iterdir():
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o444)
                self.assertNotIn(path.read_text().strip(), result.stdout)
            again = subprocess.run(
                [sys.executable, str(script)],
                cwd=folder,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(again.returncode, 0)

    def test_artifact_hash_zero_one_two_chunks_and_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "TEST-ONLY.bin"
            for size in (0, 1, 1024 * 1024, 1024 * 1024 + 1):
                data = b"x" * size
                path.write_bytes(data)
                self.assertEqual(
                    FileArtifact(path, hashlib.sha256(data).hexdigest()).verify(), path
                )
            with self.assertRaises(VoiceError):
                FileArtifact(path, "a" * 64).verify()
            with self.assertRaises(VoiceError):
                FileArtifact(path, "bad").verify()


class SyllabusSQLLoops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = isolated_database()
        cls.database.migrate()

    def setUp(self):
        with self.database.connect() as connection:
            connection.execute(
                "TRUNCATE sessions,variant_search,variants,products CASCADE"
            )
            connection.execute(
                "UPDATE catalogue_state SET revision='unpopulated',populated=false"
            )

    def test_session_min_max_and_exact_expiry_boundary(self):
        store = SessionStore(self.database)
        for ttl in (0, 59, 86401):
            with self.assertRaises((ValueError, SessionError)):
                store.create(ttl_seconds=ttl)
        for ttl in (60, 86400):
            self.assertIsInstance(store.create(ttl_seconds=ttl), str)
        session = store.create()
        fixed = datetime(2030, 1, 1, tzinfo=UTC)
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE sessions SET expires_at=%s WHERE session_id=%s",
                (fixed, session),
            )
            with patch("voicecart.sessions.datetime") as clock:
                clock.now.return_value = fixed - timedelta(microseconds=1)
                self.assertEqual(
                    str(store.require(connection, session)["session_id"]), session
                )
                for now in (fixed, fixed + timedelta(microseconds=1)):
                    clock.now.return_value = now
                    with self.assertRaises(SessionError):
                        store.require(connection, session)

    def test_publication_batch_zero_one_two_32_33_and_early_encoder_failure(self):
        for count in (0, 1, 2, 32, 33):
            with self.subTest(count=count):
                raw = fabricated_document(
                    "batch-" + str(count), self.database.inspect()["revision"]
                )
                base = raw["variants"][0]
                raw["variants"] = [
                    {**base, "variant_id": f"TEST-V-{i}", "sku": None}
                    for i in range(count)
                ]
                encoder = FixtureEncoder()
                self.database.publish(parse_import(raw), encoder=encoder)
                self.assertEqual(self.database.inspect()["variant_count"], count)

        class FailingEncoder(FixtureEncoder):
            def __init__(self):
                super().__init__()
                self.calls = 0

            def encode(self, texts, *, query=False):
                self.calls += 1
                if self.calls == 2:
                    raise RuntimeError("TEST ONLY second batch failure")
                return super().encode(texts, query=query)

        before = self.database.inspect()["revision"]
        raw = fabricated_document("batch-failure", before)
        raw["variants"] = [
            {**raw["variants"][0], "variant_id": f"TEST-FAIL-{i}", "sku": None}
            for i in range(33)
        ]
        with self.assertRaises(RuntimeError):
            self.database.publish(parse_import(raw), encoder=FailingEncoder())
        self.assertEqual(self.database.inspect()["revision"], before)
