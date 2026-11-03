"""Targeted lab/engineering runner with an owned disposable PostgreSQL service."""

import argparse
import unittest

from scripts.verify import isolated_postgres


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "tests", nargs="+", help="Exact unittest module/class/method names"
    )
    args = parser.parse_args()
    with isolated_postgres():
        suite = unittest.defaultTestLoader.loadTestsFromNames(args.tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
