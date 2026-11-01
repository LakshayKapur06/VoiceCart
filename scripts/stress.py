"""Reproducible measured load using fabricated fixtures ONLY in guarded test SQL."""

import json
import platform
import resource
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from scripts.verify import isolated_postgres
from tests.database_support import fabricated_document, isolated_database
from voicecart.domain import HardConstraints, SearchRequest
from voicecart.ingestion import parse_import
from voicecart.search import PostgresCatalogue


def main():
    with isolated_postgres():
        database = isolated_database()
        database.migrate()
        source = fabricated_document()
        source["products"] = source["products"][:1]
        source["variants"] = [
            {
                **source["variants"][0],
                "variant_id": f"TEST-LOAD-{i}",
                "sku": None,
                "price": {"minor_units": 100000 + i, "currency": "INR"},
            }
            for i in range(2000)
        ]
        start = time.perf_counter()
        database.publish(parse_import(source))
        publication = time.perf_counter() - start
        catalogue = PostgresCatalogue(database)

        def request(index):
            start = time.perf_counter()
            try:
                result = catalogue.search(
                    SearchRequest(HardConstraints("INR", category="backpack"))
                )
                correct = (
                    len(result.matches) == 2000
                    and result.cheapest_qualifying_match.variant.variant_id
                    == "TEST-LOAD-0"
                )
                return {"seconds": time.perf_counter() - start, "ok": correct}
            except Exception:
                return {"seconds": time.perf_counter() - start, "ok": False}

        start = time.perf_counter()
        cpu = time.process_time()
        with ThreadPoolExecutor(max_workers=8) as pool:
            rows = list(pool.map(request, range(128)))
        elapsed = time.perf_counter() - start
        cpu = time.process_time() - cpu
        times = sorted(row["seconds"] for row in rows)
        report = {
            "method": "Actual isolated PostgreSQL load, fabricated TEST-ONLY catalogue. No inference/audio/owner data or merchant analytics. One 2000-variant publication followed by 128 complete structured searches over 8 workers. Empirical P95 only; P99 not estimated from this sample. Client CPU/RSS excludes the separate PostgreSQL/model processes.",
            "hardware_os": platform.platform(),
            "python": platform.python_version(),
            "variants": 2000,
            "concurrency": 8,
            "requests": 128,
            "failures": sum(not row["ok"] for row in rows),
            "publication_seconds": publication,
            "elapsed_seconds": elapsed,
            "mean_seconds": statistics.mean(times),
            "median_seconds": statistics.median(times),
            "p95_seconds": times[int(0.95 * (len(times) - 1))],
            "p99_seconds": None,
            "client_cpu_seconds": cpu,
            "client_peak_rss_native_units": resource.getrusage(
                resource.RUSAGE_SELF
            ).ru_maxrss,
        }
        Path("docs/evidence/LOAD_20261102.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
        print(json.dumps(report))
        if report["failures"]:
            raise RuntimeError("Load correctness gate failed")


if __name__ == "__main__":
    main()
