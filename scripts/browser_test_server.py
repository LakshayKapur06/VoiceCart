"""Disposable browser driver: FABRICATED fixtures only in guarded test database."""

import hashlib
import os

from scripts.verify import isolated_postgres
from tests.database_support import fabricated_document, isolated_database
from voicecart.ingestion import parse_import
from voicecart.server import Merchant, Server, WebApplication
from voicecart.settings import Settings

with isolated_postgres():
    database = isolated_database()
    database.migrate()
    database.publish(parse_import(fabricated_document()))
    app = WebApplication(
        {
            "local": Merchant(
                Settings(os.environ["VOICECART_TEST_DSN"]),
                hashlib.sha256(
                    b"TEST-ONLY-ADMIN-KEY-DO-NOT-USE-OUTSIDE-TESTS"
                ).hexdigest(),
            )
        },
        b"TEST-ONLY-CAPABILITY-SECRET-32-BYTES",
        environment="test",
    )
    with Server(("127.0.0.1", 8089), app) as server:
        print("Disposable fixture browser server ready at 8089", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
