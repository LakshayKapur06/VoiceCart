"""Reproducible measured load using fabricated fixtures ONLY in guarded test SQL."""

import argparse
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
    from scripts.evidence import identity, run_directory, write_new

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--cart-users", type=int, default=0)
    args = parser.parse_args()
    output = args.output_dir or run_directory()
    if not 0 <= args.cart_users <= 64:
        parser.error("cart-users must be0–64")
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
        if args.cart_users:
            import uuid

            from voicecart.cart import AddCommand, CartService
            from voicecart.cart_management import CartManagement
            from voicecart.sessions import SessionStore

            def cart_user(index):
                begin = time.perf_counter()
                try:
                    sessions = SessionStore(database)
                    session = sessions.create()
                    turn = sessions.begin_turn(session)
                    command = AddCommand(
                        session,
                        turn,
                        str(uuid.uuid4()),
                        "exact",
                        SearchRequest(HardConstraints("INR")),
                        "TEST-LOAD-0",
                    )
                    service = CartService(database)
                    first = service.add(command)
                    replay = service.add(command)
                    management = CartManagement(database)
                    operation = str(uuid.uuid4())
                    changed = management.set_quantity(
                        session, operation, "TEST-LOAD-0", 2, "INR"
                    )
                    duplicate = management.set_quantity(
                        session, operation, "TEST-LOAD-0", 2, "INR"
                    )
                    persisted = CartManagement(database).overview(session)
                    search = catalogue.search(
                        SearchRequest(HardConstraints("INR", category="backpack"))
                    )
                    ok = (
                        first == replay
                        and changed == duplicate
                        and persisted["items"][0]["quantity"] == 2
                        and len(search.matches) == 2000
                    )
                    return {"ok": ok, "seconds": time.perf_counter() - begin}
                except Exception as error:
                    return {
                        "ok": False,
                        "seconds": time.perf_counter() - begin,
                        "error_type": type(error).__name__,
                    }

            begin = time.perf_counter()
            cpu_start = time.process_time()
            with ThreadPoolExecutor(max_workers=8) as pool:
                carts = list(pool.map(cart_user, range(args.cart_users)))
            report["cart_workload"] = {
                "method": "Concurrent independent local sessions, actual SQL add/replay/target-quantity/replay/new-service persisted read and complete2000-record search. No stock reservation or production users.",
                "users": args.cart_users,
                "workers": 8,
                "elapsed_seconds": time.perf_counter() - begin,
                "client_cpu_seconds": time.process_time() - cpu_start,
                "failures": sum(not row["ok"] for row in carts),
                "rows": carts,
                "p95": None,
                "p99": None,
            }
        write_new(output / "LOAD.json", {**identity(), **report})
        print(json.dumps(report))
        if report["failures"] or report.get("cart_workload", {}).get("failures"):
            raise RuntimeError("Load correctness gate failed")


if __name__ == "__main__":
    main()
