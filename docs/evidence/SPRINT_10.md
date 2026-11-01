# Sprint 10 — deployment and HTTP/security foundation

2026-11-02. Added digest-pinned Python/pgvector Docker images, private explicit secrets provisioning, volume persistence, health/migration dependencies, unprivileged read-only backend and external inference configuration. Static YAML parsed and service/port/dependency structure checked. **Docker boot/restart/clean-container/GPU checks Not Run: Docker is absent.** Digest metadata was checked against Docker Hub; no platform support guarantee follows from configuration.

Added bounded HTTP threads/body/timeouts, sanitized failures, numeric rate limiting, role/tenant/expiry-scoped signed capabilities, strict Host/Origin checks and explicit administrator-controlled service-host allowlists. Default local-client network restrictions remain unchanged. Per-merchant databases are validated as distinct; no silently shared catalogue/session/cart database. No customer/admin endpoint is claimed before subsequent implementation.

170 source and 170 fresh installed-wheel tests pass with real isolated PostgreSQL and loopback HTTP, plus compile/Ruff lint/format/mypy/Bandit/package/pip/diff/advisory checks (no known advisories in audited installed dependencies). Tests caught an initially ineffective Host check; fixed to compare the actual configured/listening origin, then full regressions passed. Auth tamper/role/tenant/expiry boundaries, rate-window/storage bounds, explicit service hosts and duplicate merchant DB rejection are covered. /tmp/voicecart-s10.log.

This extends transport/deployment around the existing core; PostgreSQL/Ollama/voice/cart architecture is retained. Public managed deployment still needs TLS, maintained infrastructure, secrets/retention operations and owner acceptance; no live managed service is claimed.
