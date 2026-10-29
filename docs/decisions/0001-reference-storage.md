# ADR-001: PostgreSQL + pgvector reference store

Accepted implementation reference, 29 October 2026; performance/resource fit provisional.

Use one local PostgreSQL database for authoritative catalogue, full-text search, exact vectors, sessions, local carts and operation receipts. A single publication and transaction boundary reduces the cross-store consistency/recovery coordination required by SQLite plus Qdrant. Explicit repeatable-read snapshots, atomic publication and guarded mutation are still necessary.

SQLite plus in-process vectors remains an alternative for a strict no-daemon requirement. Dedicated or embedded Qdrant remains a workload-driven challenger. No comparative speed/relevance win has been measured. Revisit on approved hardware and representative real catalogue at equal recall/quality, including updates, resource cost and backup/restore. See the consolidated [architecture rationale and decision register](../ARCHITECTURE.md).
