"""Read-only deployment availability/static probe; never pretends to boot containers."""

import argparse
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from scripts.evidence import identity, run_directory, write_new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    config = yaml.safe_load(Path("compose.yaml").read_text())
    backend = config["services"]["backend"]
    origin = backend["environment"]["VOICECART_PUBLIC_ORIGIN"]
    check = backend["healthcheck"]["test"][-1]
    if urlsplit(origin).netloc not in check:
        raise RuntimeError("Health probe and strict public Host are inconsistent")
    docker = shutil.which("docker")
    version = None
    daemon = None
    if docker:
        version = subprocess.run(
            [docker, "--version"], capture_output=True, text=True
        ).stdout.strip()
        daemon = (
            subprocess.run([docker, "info"], capture_output=True, text=True).returncode
            == 0
        )
    result = {
        **identity(),
        "docker_executable": docker,
        "docker_version": version,
        "daemon_available": daemon,
        "static_checks": {
            "probe_origin_matches": True,
            "private_db_port": "ports" not in config["services"]["db"],
            "backend_read_only": backend["read_only"],
            "migration_dependency": backend["depends_on"]["migrate"]["condition"],
            "persistent_volume": config["services"]["db"]["volumes"],
        },
        "container_boot": "NOT RUN; use the isolated deployment protocol, even if executable exists",
        "reason": "Docker executable absent"
        if not docker
        else "Read-only discovery only; container acceptance separately required",
    }
    write_new((args.output_dir or run_directory()) / "DEPLOYMENT.json", result)
    print(result["reason"])


if __name__ == "__main__":
    main()
