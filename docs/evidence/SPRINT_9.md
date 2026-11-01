# Sprint 9 — sourced historical catalogue

2026-11-02. Added bounded pinned-source download, hash-checked normalization, preserved raw/provenance/brand/attributes/images/original historical USD representation, atomic metadata publication/import history and separate read-only metadata discovery. Commerce qualification remains strict.

Actual official Appliances extract: 300 source rows, 298 admitted, 2 indexed validation rejections, 169 known historical USD prices, no known current inventory. Actual isolated PostgreSQL publication/exact read/browser queries returned all 298, including missing-price records under their known source currency; zero page records authorize a cart add. DATA_QUALITY_20261102.json and DATA_SQL_20261102.json contain exact evidence. No raw source records are committed or bundled.

165 source and 165 fresh-wheel tests pass with real PostgreSQL/pgvector, migrations/provenance/browser, malformed/duplicate/missing-price/amount boundaries, compilation, Ruff lint/format, mypy, Bandit, package assets, dependency/diff checks and advisory audit. No known advisories in audited dependencies. Normal empty-startup probe remains empty. Log /tmp/voicecart-s9.log.

Dataset-wide redistribution terms were not found in the official card/site; private owner-requested development ingestion is distinct from redistribution/commercial clearance. No live Amazon integration, fabricated stock/rupee conversion, globally cheapest real offer, production capacity or semantic quality improvement is claimed. README/supporting final documentation will consolidate the new read-only workflow and release gates.
