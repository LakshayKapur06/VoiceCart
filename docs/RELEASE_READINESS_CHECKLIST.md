# Release readiness checklist — 3 November 2026

Engineering demonstration is verifiable; **production release is not accepted**. Checked source/configuration is different from an actual deployed service or stakeholder signoff. Scope/version/profile and reviewer/date must accompany every decision. Human register has the exact procedures and evidence template.

| Gate | Current status / evidence | Required next owner action |
|---|---|---|
| Dedicated reproducible installation | COMPLETED for source/fresh installed wheel + exact imported-location assertion; S21 final RUN | Reproduce on intended supported platform with maintained DB/runtime |
| Unit/integration/system regression | COMPLETED for recorded218 Python methods and scoped browser/SDK paths; no service skips | Preserve meaningful failures/regressions; do not infer defect absence |
| Clean container deployment | BLOCKED: Docker executable absent; static probe/Host fix verified | ENV-DOCKER: actual build/boot/health/migrate/import/cart/restart/volume/secret check |
| Migrations | COMPLETED on owned real PostgreSQL/pgvector; checksummed readiness/rollback; no owner seeds | Maintained deployment migration-failure/restore drill; never edit applied SQL |
| Security/authorization | PARTIALLY_COMPLETED: route matrix, negative HTTP/types/origin/cookie/tenant/framing/rates, static/advisory checks | DEPLOY-TLS + SECURITY-REVIEW: actual proxy/private networks/secret rotation and authorized independent assessment |
| Privacy/retention | PARTIALLY_COMPLETED: no raw query/audio/IP/token events, scoped numeric analytics, cleanup tests | OPS-MONITOR: approve data/backup/WAL retention and incident handling; logical deletion is not secure erasure |
| Voice/accessibility | HUMAN_REQUIRED:8 Chromium checked states/axe and actual synthetic-file stages; one strict ASR failure retained | ACCESS-ANDROID/IOS/NVDA/USERS, VOICE-ACOUSTIC/LANGUAGE; actual devices/participants/onset/comprehension |
| NLU quality | PARTIALLY_COMPLETED: frozen32 authored cases,4B26/32,0.6B21/32; reference retained | Separate development fixes and new frozen representative language/audio evaluation; do not tune labels to outcomes |
| Audible latency | HUMAN_REQUIRED: actual individual ASR/TTS/text/SQL observations only | Define full utterance→meaningful acoustic output/profile/percentile and record complete denominators; no1.5s success yet |
| Product relevance | HUMAN_REQUIRED: exact/lexical/vector mechanisms/minimum oracles; no universal relevance guarantee | RELEVANCE-JUDGMENT: independent relevance/variant/price-scope tasks before tuning |
| Current catalogue correctness | BLOCKED for operational source: historical provenance works, no fake live facts | CATALOGUE-RIGHTS: authorize source/variants/currency/coverage/freshness SLA and actual data rights |
| External merchant | BLOCKED: local adapter/SDK tested, external platforms unimplemented | MERCHANT-SANDBOX: real scope/account/authority/idempotency/receipt conformance |
| Backup/restore/recovery | PARTIALLY_COMPLETED: guarded dump/restore, commit-loss/original-ID/expiry/concurrency tests | ENV-RECOVERY: staging backup/restore/fault drill, agreed RPO/RTO and operator |
| Documentation/practical | COMPLETED for current source-linked pack/checklist/cases/evidence/commands; no simulated signoff | OWNER-ACCEPTANCE: professor witnesses actual demo and scope/deferrals |
| Licensing/distribution | HUMAN_REQUIRED: installed/model declarations/notice hashes and primary-source review; no project license invented | LEGAL-DISTRIBUTION: owner/counsel decision, source/media permission, intended bundle/native/container notices |
| Monitoring/ownership | HUMAN_REQUIRED: actual event/health mechanisms only | Name operator/alert policy/authorized destination and perform staging incident/retention drill |

Do not release against needed data by resetting volumes or bypassing unknown outcomes. No critical real-world gate becomes complete because a document exists. Attach actual human/device/deployment/legal evidence, responsible reviewer/date and accepted residual risk before changing statuses.
