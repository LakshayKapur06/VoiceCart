"""Repeatable automated engineering gates; never connects to an owner database."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager, nullcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(arguments: list[str], **kwargs) -> None:
    print("CHECK:", " ".join(arguments), flush=True)
    subprocess.run(arguments, cwd=ROOT, check=True, **kwargs)


def package_check() -> None:
    with tempfile.TemporaryDirectory(prefix="vc-package-") as directory:
        temp = Path(directory)
        run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--no-isolation",
                "--outdir",
                str(temp),
            ]
        )
        wheel = next(temp.glob("*.whl"))
        env = temp / "env"
        run([sys.executable, "-m", "venv", "--without-pip", str(env)])
        python = env / (
            "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
        )
        run(
            [
                sys.executable,
                "-m",
                "pip",
                "--python",
                str(python),
                "install",
                "--no-cache-dir",
                str(wheel),
            ]
        )
        code = f"""import unittest, voicecart
from pathlib import Path
assert Path(voicecart.__file__).is_relative_to({str(env)!r}), voicecart.__file__
suite=unittest.defaultTestLoader.discover({str(ROOT / "tests")!r}, top_level_dir={str(ROOT)!r})
result=unittest.TextTestRunner(verbosity=0).run(suite)
raise SystemExit(not result.wasSuccessful())
"""
        subprocess.run([str(python), "-I", "-c", code], cwd=temp, check=True)


@contextmanager
def isolated_postgres():
    import fasteners
    import pgserver
    import psycopg
    from pgserver.postgres_server import PostgresServer
    from psycopg import sql

    from voicecart.database import Database

    # Own all files, sockets and databases. Never read VOICECART_DATABASE_URL.
    with tempfile.TemporaryDirectory(prefix="vcpg-", dir="/tmp") as directory:
        root = Path(directory)
        PostgresServer.runtime_path = root
        PostgresServer._lock = fasteners.InterProcessLock(root / "lock")
        server = pgserver.get_server(root / "data", cleanup_mode="delete")
        try:
            suffix = uuid.uuid4().hex[:16]
            test_name, empty_name = "vc_test_" + suffix, "vc_empty_" + suffix
            with psycopg.connect(server.get_uri(), autocommit=True) as connection:
                for name in (test_name, empty_name):
                    connection.execute(
                        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name))
                    )
                print(
                    "REAL SERVICE:",
                    connection.execute("select version()").fetchone()[0],
                    flush=True,
                )
            (root / ".voicecart-test-owner").write_text(test_name)
            old = {
                name: os.environ.get(name)
                for name in ("VOICECART_TEST_ROOT", "VOICECART_TEST_DSN")
            }
            os.environ["VOICECART_TEST_ROOT"] = str(root)
            os.environ["VOICECART_TEST_DSN"] = server.get_uri(database=test_name)
            empty = Database(server.get_uri(database=empty_name))
            empty.migrate()
            empty.check_ready()
            if empty.inspect()["product_count"] != 0:
                raise RuntimeError("Fresh application schema contains products")
            try:
                yield
                empty.check_ready()
                state = empty.inspect()
                if state["product_count"] != 0 or state["variant_count"] != 0:
                    raise RuntimeError("Application probe database was populated")
                print(
                    "EMPTY DATABASE: fresh initialization and startup contain zero products/variants",
                    flush=True,
                )
            finally:
                for name, value in old.items():
                    if value is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = value
        finally:
            server.cleanup()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--postgres", action="store_true")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    with isolated_postgres() if args.postgres else nullcontext():
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"])
        run([sys.executable, "-m", "compileall", "-q", "voicecart", "tests", "scripts"])
        run([sys.executable, "-m", "ruff", "check", "."])
        run([sys.executable, "-m", "ruff", "format", "--check", "."])
        run([sys.executable, "-m", "mypy", "voicecart"])
        run([sys.executable, "-m", "bandit", "-r", "voicecart", "-q"])
        run([sys.executable, "-m", "pip", "check"])
        run(["git", "diff", "--check"])
        if args.package:
            package_check()
        if args.audit:
            with tempfile.TemporaryDirectory(prefix="vc-advisories-") as cache:
                run(
                    [
                        sys.executable,
                        "-m",
                        "pip_audit",
                        "--skip-editable",
                        "--progress-spinner",
                        "off",
                        "--cache-dir",
                        cache,
                    ]
                )
        print(
            "Automated gates passed. Device/model/human acceptance is a separate gate."
        )


if __name__ == "__main__":
    main()
