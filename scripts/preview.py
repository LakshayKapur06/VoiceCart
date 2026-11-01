"""Private disposable real-metadata preview, never an owner/production database.

The bundled PG 16.2 is legacy development tooling. Use maintained PostgreSQL /
Compose for a deployment; this helper binds HTTP only to loopback and PG to its
private Unix socket on supported local Unix hosts. It imports no fake products.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import secrets
import tempfile
from pathlib import Path


def private_value(path):
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(path.parent, 0o700)
    if not path.exists():
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as target:
            target.write(secrets.token_urlsafe(48) + "\n")
    result = path.read_bytes().strip()
    if len(result) < 32:
        raise ValueError("Private preview credential is too short")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Loopback-only disposable historical metadata preview. Not production hosting."
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=Path(".local/datasets/appliances-normalized.json"),
    )
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    from voicecart.ingestion import load_import

    bundle = load_import(args.snapshot)
    if (
        not bundle.metadata
        or len(bundle.products) > 1000
        or any(not row.get("historical") for row in bundle.metadata.values())
    ):
        raise ValueError("Use a bounded explicitly historical real-metadata snapshot")
    import fasteners
    import pgserver
    import psycopg
    from pgserver.postgres_server import PostgresServer

    from voicecart.server import Merchant, Server, WebApplication
    from voicecart.settings import Settings

    secret_root = Path(".local/preview-secrets")
    admin = private_value(secret_root / "admin_token")
    key = private_value(secret_root / "http_secret")
    with tempfile.TemporaryDirectory(prefix="vc-preview-", dir="/tmp") as directory:
        root = Path(directory)
        PostgresServer.runtime_path = root
        PostgresServer._lock = fasteners.InterProcessLock(root / "lock")
        postgres = pgserver.get_server(root / "data", cleanup_mode="delete")
        try:
            with psycopg.connect(postgres.get_uri(), autocommit=True) as connection:
                connection.execute("CREATE DATABASE voicecart_preview")
            dsn = postgres.get_uri(database="voicecart_preview")
            old_dsn = os.environ.get("VOICECART_DATABASE_URL")
            os.environ["VOICECART_DATABASE_URL"] = dsn
            try:
                settings = Settings.from_env()
            finally:
                if old_dsn is None:
                    os.environ.pop("VOICECART_DATABASE_URL", None)
                else:
                    os.environ["VOICECART_DATABASE_URL"] = old_dsn
            from voicecart.cli import components

            database, encoder, _ = components(settings)
            database.migrate()
            database.publish(bundle, encoder=encoder)
            application = WebApplication(
                {
                    "local": Merchant(
                        Settings(dsn), hashlib.sha256(admin).hexdigest(), "USD"
                    )
                },
                key,
                environment="development",
            )
            with Server(("127.0.0.1", args.port), application) as server:
                print(
                    f"Real historical metadata preview: http://127.0.0.1:{args.port}",
                    flush=True,
                )
                print(
                    f"Private admin credential file: {secret_root / 'admin_token'}",
                    flush=True,
                )
                print(
                    "Disposable local DB; no owner DB/fixtures. Legacy bundled PostgreSQL is development-only. Ctrl+C removes preview DB.",
                    flush=True,
                )
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    return
        finally:
            postgres.cleanup()


if __name__ == "__main__":
    main()
