"""Repeatable automated engineering gates; never connects to an owner database."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", action="store_true")
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
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
    print("Automated gates passed. Device/model/human acceptance is a separate gate.")


if __name__ == "__main__":
    main()
