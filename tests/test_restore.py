"""Real logical backup/restore drill confined to the runner-owned test server."""

import os
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from tests.database_support import fabricated_document, isolated_database
from voicecart.database import Database
from voicecart.ingestion import parse_import


class RestoreTests(unittest.TestCase):
    def test_real_dump_restores_schema_catalogue_and_metadata(self):
        database = isolated_database()  # validates ownership BEFORE create/drop/dump
        database.migrate()
        with database.connect() as connection:
            connection.execute("TRUNCATE variant_search,variants,products CASCADE")
            connection.execute(
                "UPDATE catalogue_state SET revision='unpopulated',populated=false"
            )
        database.publish(parse_import(fabricated_document()))
        original = os.environ["VOICECART_TEST_DSN"]
        config = conninfo_to_dict(original)
        name = "vc_restore_" + uuid.uuid4().hex
        target = make_conninfo(original, dbname=name)
        binaries = Path(os.environ["VOICECART_TEST_PG_BIN"])
        with psycopg.connect(original, autocommit=True) as admin:
            admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            try:
                with tempfile.TemporaryDirectory(prefix="vc-restore-") as folder:
                    dump = Path(folder) / "backup.sql"
                    subprocess.run(
                        [
                            str(binaries / "pg_dump"),
                            "--dbname",
                            original,
                            "--file",
                            str(dump),
                        ],
                        check=True,
                        capture_output=True,
                        timeout=30,
                    )
                    subprocess.run(
                        [
                            str(binaries / "psql"),
                            "-v",
                            "ON_ERROR_STOP=1",
                            "--dbname",
                            target,
                            "--file",
                            str(dump),
                        ],
                        check=True,
                        capture_output=True,
                        timeout=30,
                    )
                restored = Database(target)
                restored.check_ready()
                self.assertEqual(restored.inspect(), database.inspect())
                self.assertEqual(config["host"], conninfo_to_dict(target)["host"])
            finally:
                admin.execute(
                    sql.SQL("DROP DATABASE {} WITH (FORCE)").format(
                        sql.Identifier(name)
                    )
                )
