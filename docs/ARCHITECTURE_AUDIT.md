# Continued-development audit — 2 November 2026

Baseline: a8d7d31, existing main/origin aligned, clean tracked tree. The existing checkout was named VoiceCart; owner delegated the naming decision, so it was case-renamed to voicecart while retaining every file and Git history. Package name was already voicecart. No AGENTS.md applies.

Fresh reproduction: `.venv/bin/python scripts/verify.py --postgres --package --audit` passed 159 source tests and 159 fresh installed-wheel tests, real isolated PostgreSQL/pgvector, zero-product startup probe, compile, Ruff lint/format, mypy, Bandit, pip check and advisory scan (no known advisories). Python 3.12.14, macOS Apple Silicon. Missing psycopg/global moviepy conflicts in the archive audit were environmental; the dedicated environment has the declared runtime dependencies. New log: /tmp/voicecart-stage0-20261102.log. Historical S7 results remain separately dated evidence.

## Inventory and gaps

Existing domain/catalogue/ranking, NLU/local HTTP, ingestion/embeddings/database, sessions/cart, application/audio/voice/settings/CLI and migrations are retained. No HTTP server, customer/admin assets, Docker setup, merchant SDK or historical metadata ingestion existed. No normal owner database is configured. Large verified speech/model files are ignored local assets. No live Amazon/merchant integration exists.

Confirmed gaps: 59.17-second combined stage has no operation breakdown or runtime inference counters; vocabulary hydrates the entire catalogue; metadata/show calls repeat; each SQL connection is new; dense search explicitly sorts all vectors despite needing all scores; strict commerce qualification correctly excludes historical unknown-stock metadata, so a separately labelled read-only discovery surface is required. Adding historical records must never relax current-offer eligibility. Cart supports increment only; target quantity/removal need distinct idempotent receipts. No frontend/authentication/tenant/analytics interfaces exist. Existing weights are explicitly experimental and must not be presented as tuned.

Docker executable/daemon is unavailable on this host. Compose can be authored, statically validated and documented, but container boot/restart/GPU acceptance cannot be claimed without a real runtime. Human screen-reader, physical microphone/speaker and representative-user acceptance require access to those users/devices. All independent engineering proceeds; those release gates remain explicit.

## Incremental decisions

Keep PostgreSQL/pgvector, Ollama extraction, Whisper/Piper, deterministic eligibility and immutable cart receipts. Add timing spans and bounded revision-keyed vocabulary/model metadata caches without caching action facts. Add provenance metadata alongside existing tables and a read-only historical discovery route. Add a small HTTP boundary and semantic HTML/JS clients using the same application/cart services. Whole-database-per-merchant deployment isolation avoids silently altering every existing consistency key. Customer capabilities and admin credentials are enforced server-side. The local merchant adapter is the first real contract implementation; external platforms remain unsupported until integrated.

No core replacement is proposed or approved. Container networking requires explicitly configured trusted service hostnames; loopback remains the default. Public managed hosting, TLS termination, distribution rights and real merchant credentials are deployment decisions, not features to pretend are live.
