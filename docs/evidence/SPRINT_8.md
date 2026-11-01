# Sprint 8 — fresh baseline, observability and hardening

2026-11-02. Baseline 159+159 source/wheel tests was freshly reproduced, not inferred from historical evidence. The continuation now passes 162 source and 162 fresh-wheel tests plus real isolated PostgreSQL/pgvector, compile, Ruff lint/format, mypy, Bandit, package/SQL assets, pip check and advisory audit. No known advisories in audited dependencies. Normal startup remains zero-product. Source log /tmp/voicecart-s8.log.

Implemented bounded context-isolated numeric timings, actual runtime inference counters, publication-aware distinct-attribute vocabulary caching with defensive copies, removal of unnecessary full dense ordering (all candidate scores retained), and forced fresh-wheel installation. Existing session/cart/receipt safety and architecture are unchanged. Tests verify trace isolation/failures/privacy and cache mutation/publication invalidation.

The frozen twelve-case actual pinned-Qwen holdout is recorded separately in NLU_HOLDOUT_20261102.json; it was not used to tune this prompt. Eleven expectations passed, one quantity/search-and-add case safely rejected. This is not a held-out population accuracy guarantee. It is an explicit release-quality gap; direct structured controls and strict independent validation remain available. HANDOFF_PERFORMANCE.md records stage definitions, observations and remaining audible-device/model-contention acceptance.

No major component replacement, invented performance result or normal database fixture import occurred. Docker is unavailable; actual container acceptance remains blocked while independent stages proceed. Root folder case was corrected to voicecart per the prompt after the owner delegated the naming decision; files/history were preserved.
