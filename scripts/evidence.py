"""Append-only run metadata; never capture environment values or owner data."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def run_directory() -> Path:
    return Path("docs/evidence") / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")


def identity() -> dict:
    def git(*args):
        return subprocess.check_output(["git", *args], text=True).strip()

    paths = sorted(
        [
            *Path("voicecart").rglob("*.py"),
            *Path("voicecart").rglob("*.sql"),
            *Path("voicecart/web").glob("*"),
            *Path("tests").rglob("*.py"),
            *Path("tests/browser").glob("*.mjs"),
            *Path("scripts").glob("*.py"),
            *Path("sdk").glob("*"),
            Path("pyproject.toml"),
            Path("package-lock.json"),
            Path("Dockerfile"),
            Path("compose.yaml"),
        ]
    )
    digest = hashlib.sha256()
    for path in paths:
        if path.is_file():
            digest.update(str(path).encode() + b"\0" + path.read_bytes())
    versions = {}
    for package in (
        "psycopg",
        "coverage",
        "ruff",
        "mypy",
        "bandit",
        "pip-audit",
        "pgserver",
        "pywhispercpp",
        "piper-tts",
    ):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed"
    for executable in ("node", "npm"):
        try:
            versions[executable] = subprocess.check_output(
                [executable, "--version"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            versions[executable] = "unavailable"
    return {
        "runtime_versions": versions,
        "commit_sha": git("rev-parse", "HEAD"),
        "working_tree_dirty": bool(git("status", "--porcelain")),
        "source_tree_sha256": digest.hexdigest(),
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
        "reproduction": "Fresh execution by the same coding agent; not an independent third-party audit.",
    }


def write_new(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as target:
        json.dump(data, target, indent=2)
        target.write("\n")
