# Baseline audit — 29 October 2026

Starting commit: `f58709c45bcbc0ed99e166d16fd2b50b294ffdb9`, clean `main`, existing origin `https://github.com/LakshayKapur06/VoiceCart.git`. `git pull --ff-only origin main` reported already up to date. Eight commits, one local branch, no tags, no AI co-author trailers found in the existing messages. No applicable AGENTS.md was found. User's new full-implementation request supersedes the old README's review-only and Sprint-1-only restrictions.

Inspected tracked source, tests/fixtures, package/configuration, README, Suggestions, plan, sprint records and ADR. Existing generated build, egg-info, bytecode, Ruff cache and virtual environment are ignored. There is no application entry point, real inference adapter, persistence schema/importer, semantic discovery, application orchestration or cart. No normal application database or real catalogue is configured. Synthetic records exist only in tests.

| Baseline command | Actual outcome |
|---|---|
| `.venv/bin/python -m unittest discover -s tests -q` | 98 passed |
| `.venv/bin/python -S -m unittest discover -s tests -q` | 98 passed |
| `.venv/bin/python -m doctest docs/SPRINT_1.md docs/SPRINT_2.md` | passed |
| `.venv/bin/python -m compileall -q voicecart tests` | passed |
| `.venv/bin/ruff check .` | passed |
| `.venv/bin/ruff format --check .` | 12 files formatted |
| `.venv/bin/python -m pip check` | no broken requirements |
| bundled Python `setuptools.build_meta.build_wheel(tempdir)` | built wheel containing all five package modules |
| `.venv/bin/python -m mypy voicecart` | initially unavailable; after installing mypy, 19 type errors in domain/catalogue/audio |
| `.venv/bin/python -m bandit -r voicecart -q` | initially unavailable; after installing Bandit, passed |
| `.venv/bin/python -m pip_audit` | initially unavailable; 12 advisory entries (including duplicate identifiers) for development pip 25.0.1; upgraded local pip to 26.2.2; recheck recorded below |

Confirmed: old audio slice ASR/template failures emit assistive text and return a string; no caller turns those strings into speech. This is not audible recovery. Existing fake-fallback/cancellation/latency regressions are fixed at the starting commit, but actual device/model and human accessibility acceptance remain unverified. README still contains obsolete review instructions and conflicting implementation status.

Remediation checklist:

- [x] Correct source type errors and configure reproducible type/security checks.
- [x] Add bounded local NLU transport and independent critical-field validation.
- [x] Add real PostgreSQL/pgvector migrations, atomic validated ingestion, consistent search and empty-catalogue outcomes.
- [x] Add transaction-safe session cart, stable result references, immutable receipts and idempotent recovery.
- [x] Add runnable application and real local speech adapters; make all response/error paths explicit.
- [ ] Exercise isolated real-service integration, system/acceptance scenarios, package installation and failure cases.
- [ ] Consolidate durable architecture knowledge, catalogue/model setup and owner decisions; remove obsolete Suggestions requirement/file.
- [ ] Push verified engineering increments normally; preserve human author metadata and add no AI trailers.
- [ ] Back up and verify local history cleanup separately; do not overwrite GitHub history without final approval.
