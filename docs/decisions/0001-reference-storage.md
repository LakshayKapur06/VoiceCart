# ADR-001: PostgreSQL + pgvector as the reference store

Date: 27 October 2026. Status: **accepted implementation reference, performance/resource fit provisional** (D15). Scope: later catalogue/retrieval/session-cart adapters; Sprint 1 implements an in-memory domain contract only.

## Context and decision

The owner’s integration task accepts Suggestions.md’s verdict. VoiceCart needs relational eligibility/price ordering, lexical/vector discovery, completeness metadata and minimal safe cart/operation receipts. Use one local PostgreSQL database with pgvector and built-in text search. Start with exact vectors; add ANN only after measured need and recall gates. The LLM remains outside authority.

One transaction/snapshot boundary removes the former proposal’s SQLite/Qdrant publication and recovery coordination. Prepare embeddings outside transactions, publish matching content/search revisions atomically, validate generation fingerprints and take consistent multi-branch snapshots. Revalidate action facts in short guarded transactions; preserve operation identity and immutable receipts. Sharing a database does not automatically make default multi-statement reads consistent or asynchronous embeddings current.

## Alternatives and consequences

- SQLite plus an in-process exact scan or embedded engine can suit a real no-daemon/device constraint. It remains a conditional E11 alternative.
- SQLite + Qdrant Server or PostgreSQL + Qdrant may fit a demonstrated dedicated-vector need, but reintroduce coordination/recovery work.
- Qdrant also has a client local mode and an embedded Edge option. Do not generalize server-count comparisons to all modes; assess their actual packaging, stability and resource costs.
- Qdrant alone does not establish the required relational action/receipt contract. More services/frameworks are not justified now.

PostgreSQL needs installation, extension/client compatibility, maintenance, local access control, backups and resource tuning. Built-in text ranking differs from FTS5 BM25; filtered ANN can underfill/miss candidates. No speed/relevance benefit or 1.5-second success is claimed. The same encoder/scorer does not become more relevant merely because it moves databases.

## Validation and revisit gate

Sprint 4 ports the Sprint 1 conformance/oracle tests, adds E01 publication/snapshot/crash tests, and records an initial E09/E11 resource/restore baseline. Sprint 7 completes E11 at equivalent recall/quality and on the approved hardware/scale, including exact/ANN and dedicated/embedded alternatives plus full-turn latency. If correctness, resource or agreed latency gates fail, document the measured bottleneck and select the smallest justified alternative; do not retain PostgreSQL out of habit.

The original evidence and source URLs remain in [Suggestions.md §§3–4](../../Suggestions.md); this ADR records integration, not new database research or benchmarks. D01/D03/D07/D15 remain unresolved. No PostgreSQL service, schema or vector index is installed by Sprint 1.
