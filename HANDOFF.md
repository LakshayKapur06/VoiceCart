# VoiceCart engineering handoff — 2 November 2026

Version0.2.0 continuation of the existing project. Engineering implementation and the tests listed below are complete; product release acceptance is conditional on the explicit quality, environment, device, user and rights gates. This report supersedes the29 October operational summary; historical sprint/model evidence remains in Git and docs/evidence.

## 1. Executive summary

VoiceCart now has real customer/admin browser clients, a bounded authenticated HTTP API, historical Amazon metadata ingestion with provenance, optional lexical/exact-vector discovery, transactional cart quantity/removal/recovery, actual-event analytics and a shared local merchant adapter with a server-side JavaScript/TypeScript SDK. Existing PostgreSQL/pgvector, Ollama, Whisper/Piper and deterministic core were preserved. No checkout, live Amazon inventory, external platform adapter or operated cloud service is claimed.

Final verification: **193 source tests +193 fresh installed-wheel tests**, five Chromium browser tests, two actual local Node SDK tests and strict TS declaration checks passed. Measured Python statement coverage80.90%, branch coverage68.92%. Actual local speech HTTP, real historical catalogue browsing and semantic publication/query were exercised separately. Model quality and audible latency remain material limits.

## 2. Initial audit findings and resolution

The archive auditor's missing psycopg and global moviepy/Pillow conflict were environmental: a dedicated declared-dependency environment reproduced159+159 baseline tests, real isolated SQL, package/static/security/advisory checks. No global environment repair was needed. The absent .git in the archive was not a repository defect; this checkout has ordinary sprint history and the configured GitHub remote.

Confirmed gaps were unbroken59.17-second application timing, full-catalogue vocabulary hydration, unnecessary dense SQL ordering, no web/admin/merchant/Compose surfaces, increment-only cart and no historical source workflow. Added instrumentation and revision-keyed defensive vocabulary copies, retained complete dense score coverage, and delivered the missing boundaries. No pooling/model replacement was justified by the observations. Final review also fixed delayed final/cancel handling, stale browser response publication, schema readiness against all packaged migrations and recovery visibility for quantity operations. Full details: [audit](docs/ARCHITECTURE_AUDIT.md) and [performance](HANDOFF_PERFORMANCE.md).

## 3. Current architecture and decisions

One PostgreSQL snapshot/transaction boundary owns source publication, relational eligibility, FTS/pgvector, sessions/cart and immutable receipts. This reduces cross-store consistency/recovery work; it is not a measured speed victory over SQLite/Qdrant. Local models propose schema-constrained intent; independent literal/semantic validation and deterministic Python authorize actions. Unknown facts never become stock/current offers.

Customer/admin clients and merchant SDK delegate to the same local adapter/core. Registered final turns, session locks, canonical operation identities, fingerprint checks and fresh-connection receipt verification protect mutation/retry. Cancellation cannot roll back a committed write. Tenant configuration requires distinct physical databases and credentials. Historical discovery is separately labelled and never weakens commerce qualification. No major core replacement occurred. [Architecture](docs/ARCHITECTURE.md), [storage ADR](docs/decisions/0001-reference-storage.md), [historical ADR](docs/decisions/0002-historical-discovery.md).

## 4. Implementation inventory and status

| Component | Status and boundary |
|---|---|
| Domain/catalogue/ranking/search | Implemented and verified: integer constraints, complete structured minimum, separate relevance/price roles, exact vector coverage. Human relevance uncalibrated. |
| Database/ingestion/embeddings | Implemented and verified: six checksummed migrations, CAS full snapshots, provenance, import history, optional generation-pinned vectors. Maintained-server deployment still required. |
| NLU/local HTTP | Implemented but not fully verified: pinned Qwen, strict validation; actual holdout11/12, safe H05 rejection. |
| Sessions/application/cart/quantity | Implemented and verified: final-once turns, expiry, reference acknowledgement, atomic idempotency/receipts, target quantity0–99, recovery. Local cart only. |
| Native/browser audio | Implemented but not fully verified: actual Whisper/Piper file/HTTP inference and scripted capture/fault checks. Physical audio and users Not Run. |
| HTTP/customer/admin | Implemented and verified in tested native/Chromium states: roles/origins/limits, search/details/cart, CAS management and actual metrics. No certification/whole-browser guarantee. |
| Merchant adapter/JS/TS SDK | Implemented and verified actual local path; external platform adapters, webhooks and managed operation planned. |
| Compose | Implemented but not fully verified: configuration/static checks; runtime unavailable. |
| Telemetry/testing/docs | Implemented and verified to the recorded scope; source CFG/path analysis and coverage do not establish universal path coverage. |

## 5. Eight workstreams

| Workstream | Delivered / remaining |
|---|---|
| Audit/performance/hardening | Fresh baseline, structured numeric spans, actual Qwen/resource/load observations, safe optimizations; audio target not met/accepted. |
| Comprehensive documentation | Expanded README, actual API, architecture/ADRs, security/licensing/data/deployment/SDK/testing and this handoff. |
| Amazon historical metadata | Reproducible pinned extract, normalization/provenance/quality, actual SQL/vector/browser path; redistribution terms unresolved. |
| Compose/environment | Nonroot/read-only backend, private PG volume/secrets, health/migrate dependency and host inference; container/runtime/platform acceptance Not Run. |
| Customer frontend | Desktop/mobile text/search/details, voice review/cancel, cart/quantity/remove/reload/retry, keyboard/status controls; users/devices pending. |
| Admin frontend | Authenticated real catalogue/variants/import/deactivate/history/provenance, actual analytics/health; full JSON snapshots, no CSV promise. |
| Merchant integration | Shared protocol/local adapter, server-side typed SDK, actual end-to-end and tenant isolation; external adapters planned. |
| Comprehensive testing | Executable partitions/boundaries/tables, cause-effect mapping, real CFG/three complexity methods/basis paths, coverage, loops/interfaces/integration/load/install/smoke; manual gates explicitly Not Run. |

## 6. Catalogue: source, results and integrity

Official McAuley-Lab Amazon Reviews2023 Appliances metadata revision `2b6d039ed471f2ba5fd2acb718bf33b0a7e5598e`, first300 rows, extract SHA256 `a3b27ecae6fa5c498860b7ea9dbd706fbe7906eed0c03d7d22e965cbdeb4809b`. Actual normalization admitted298, rejected2, duplicated0;169 known historical USD prices, zero known current-stock records. Title/features/known brand/attributes/images/raw facts/original price/provenance are preserved locally. Parent metadata is an explicitly unspecified discovery representation, not an invented purchasable variant. No USD→INR conversion or stock fabrication occurs.

Raw/normalized data and models are ignored private assets; committed evidence contains counts/hashes, not redistributed records. Historical prices remain stale and stock unknown, so preview add buttons are disabled. Repeating an unchanged import conflicts rather than duplicating records. [Workflow/quality/terms](docs/DATASET_AND_CATALOGUE.md), [quality evidence](docs/evidence/DATA_QUALITY_20261102.json), [actual semantic evidence](docs/evidence/DATA_SEMANTIC_20261102.json). Normal initialization/startup was separately checked to contain zero products. No owner DSN/data was used.

## 7. Install, configure, start and operate

Clone explicitly into lowercase `voicecart`; this checkout's original case was corrected with owner-delegated judgment and all history/files preserved.

```sh
git clone https://github.com/LakshayKapur06/VoiceCart.git voicecart
cd voicecart
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,voice]'
cp .env.example .env
chmod 600 .env
# Configure a dedicated maintained PostgreSQL+pgvector DB and explicit model/file pins.
set -a; source .env; set +a
voicecart init-db
voicecart db-status
# Import actual owner facts using the documented schema; no seed step exists.
voicecart import-catalogue /absolute/path/to/owner-snapshot.json
python scripts/init_secrets.py
# Set HTTP_SECRET_FILE, ADMIN_TOKEN_FILE and PUBLIC_ORIGIN using .env.example names.
python -m voicecart.server
```

Use README for complete configuration names/artifact pins and the [actual API](docs/API.md). The text-only default needs no models; optional voice/NLU require explicitly verified local assets. For a disposable real historical preview, run the download/normalization workflow then `PYTHONPATH=. python scripts/preview.py`; it owns an ephemeral private DB and serves loopback8080. Credential path is `.local/preview-secrets/admin_token`; never print/commit its value. Ctrl+C discards only that preview DB. This helper uses legacy bundled PG16.2 for local development, not production hosting.

Compose: `python scripts/init_secrets.py`, `docker compose config --quiet`, `docker compose up --build`. DB is private, web loopback8080, migrations explicit before backend, large models outside images. Secrets have0700 parent and read-only files for the unprivileged mount. **Docker executable/daemon absent: actual container boot, restart persistence, secret mounts, GPU/platform and clean Compose installation Not Run.** [DOCKER_SETUP.md](docs/DOCKER_SETUP.md) is the operating/checklist authority.

CLI remains `voicecart run` or `voicecart run --voice --speak`; /listen,/end,/stop,/repeat,/ack,/retry ID,/cart,/quit. Retain original operation IDs after uncertainty. Back up into private storage and restore a separate DB before a real switch; guarded logical dump/restore passed, owner deployment drills remain necessary. Session/event retention is configured, not a promise that WAL/backups are erased immediately. Never reset needed volumes.

## 8. Customer frontend and accessibility

Actual customer flow covers search/filter/pagination, historical labels, details/provenance, opt-in images, explicit add for current offers, quantity/removal/subtotals, recent operation verification and reload recovery. Audio is half duplex with explicit start/end, final transcript review/discard and text fallback; stop fences late speech/search/query work. Five Chromium tests cover functional cart/reload, keyboard/dialog/axe/mobile states, scripted ASR review/late cancellation and cancelled delayed search responses. Real historical browser evidence confirmed298 records and zero actionable historical buttons. Automated axe and scripted capture are not physical microphone, screen reader or target-user acceptance.

## 9. Admin frontend

Scoped authentication, catalogue/provenance views, create/edit/variant/deactivate through validated full-snapshot CAS publication, JSON import/export, actual import history, health and numeric event aggregates work. Invalid or stale imports fail atomically. Metrics distinguish test/development/merchant environment; no fake popular searches, checkout revenue or conversion exists. Browser edit/auth and SQL/API isolation tests passed. Admin credentials remain server-side/HttpOnly; no unrestricted storefront admin key.

## 10. Merchant adapter and SDK

`MerchantAdapter`/`LocalMerchantAdapter` expose discovery, lookup, synchronization, offer refresh, sessions/cart/add/target quantity and operation reconciliation. Actual JS SDK→HTTP→PostgreSQL create/search/add/replay/receipt/refresh/lookup/remove passed; strict TS checks enforce required identities. The SDK refuses insecure remote origins/redirect credential forwarding and does not auto-retry writes. Local refresh only rereads local facts. A merchant BFF must authenticate end customers and retain operation IDs. Self-hosted and dedicated-database-per-tenant managed topology are documented; Shopify/WooCommerce/Magento, external stock/cart webhooks, a published npm package and operated hosting remain planned. [Contract](docs/MERCHANT_SDK.md).

## 11. Performance investigation and results

The historical59.1698s combined stage cannot be retrospectively split. Current actual12-case Qwen holdout had32.063s first request,18.953s mean and18.721s median. First runtime counters:2.812s load,8.541s prompt,20.621s generation; warm cases remained slow. These different profiles are not a controlled speedup comparison. Safe vocabulary/query optimizations reduce avoidable work without weakening exact coverage/transactions; model replacement/pooling/async mutation was not justified.

Actual2000-variant,128-query/eight-worker isolated SQL load: zero failures, mean0.189s, exploratory empiricalP95 0.221s, P99 unestimated. Real298-record MiniLM publication2.904s/query0.0393s used the explicit compact derived profile. Actual final HTTP ASR0.6415s/TTS1.2488s measured separate stages with synthetic spoken input and real local inference, not human audible turnaround. [Performance report](HANDOFF_PERFORMANCE.md) records reproduction, resources, measurement limits and inference bottleneck. Sub-1.5s is unachieved/unverified.

## 12. Testing and reproduction

```sh
python scripts/verify.py --postgres --package --audit --coverage
PYTHONPATH=. python scripts/test_report.py
python scripts/cfg_analysis.py
PYTHONPATH=. python scripts/stress.py
npm ci
npx playwright install chromium
PYTHONPATH=. python scripts/browser_test_server.py
# Separate terminal while that guarded fixture driver is active:
npm run test:browser
npm run test:sdk
npx tsc --strict --noEmit --module nodenext --target es2022 sdk/typecheck.mts
```

Final source193/193 and isolated installed-wheel193/193 passed without service skips; Ruff lint/format, compilation, production mypy, Bandit, pip check, diff and Python/npm advisory checks passed. Five browser and two Node SDK tests passed. Coverage3210/3968 statements (80.90%),918/1332 branches (68.92%),62 excluded lines visible. Thirteen actual-source CFGs verify E−N+2P, predicate+1 and actual planar regions; GF2 structural basis independence does not establish feasibility/execution of every path. Tests exercise boundaries/partitions/tables/cause-effect mappings, loops, interfaces, stubs/drivers, top-down/bottom-up/back-to-back/system/install/smoke/load cases. [Testing guide](docs/TESTING_GUIDE.md), [complete case records](docs/TEST_CASES.md), [CFG analysis](docs/CFG_ANALYSIS.md).

Seven manual/external acceptance records are Not Run; the actual NLU H05 quality expectation is separately **Fail**, safely rejected without dispatch. Physical mic/speaker/noise/acoustic onset, VoiceOver/target users, real deployment/container/platform/GPU/owner recovery and rights gates are not converted into passes. Frozen holdout11/12 is a small bank, not general accuracy. [Final evidence](docs/evidence/SPRINT_15.md).

## 13. Security, privacy and licensing

Enforced: parameterized SQL, bounded workers/body/timeouts/ratelimiter, fixed Host/Origin/no wildcard CORS, signed role/tenant/expiry capabilities, constant-time hashed admin credentials, separate tenant databases, private configuration, no model authority over facts/writes, no raw queries/audio/IP/token event storage. Numeric telemetry failures do not change transaction outcomes. Remote hosting requires HTTPS/TLS, secret rotation, maintained server, operator backups/retention/monitoring and a deployment review. No vulnerability scan proves absence of flaws.

Pinned runtime/voice/data inventories and exact terms are in [LICENSING.md](docs/LICENSING.md). Piper1.8.0 is GPL3-or-later; the selected LJ card declares dataset public-domain facts, which do not settle every distribution obligation. No explicit Amazon dataset-wide redistribution grant was located; raw data/models were not shipped. Project LICENSE is owner-undecided. Do not infer commercial clearance from public downloads or install success. [Security/privacy](docs/SECURITY_AND_PRIVACY.md).

## 14. Documentation inventory

Expanded README is the primary professional project overview/setup/architecture/trade-off/testing/showcase entry point. Current supporting files: ARCHITECTURE_AUDIT, ARCHITECTURE and ADRs, API, DATASET_AND_CATALOGUE, DOCKER_SETUP, MERCHANT_SDK, SECURITY_AND_PRIVACY, LICENSING, TESTING_GUIDE, TEST_CASES, CFG_ANALYSIS, IMPLEMENTATION_PLAN, HANDOFF_PERFORMANCE and dated sprint/evidence JSON. Earlier useful sprint/model evidence is preserved; no historical benchmark was relabelled as fresh. Generated caches/build/browser reports are ignored and removable; source, evidence, private models/data and environment must not be confused during cleanup.

## 15. Git and sprint delivery

Remote: https://github.com/LakshayKapur06/VoiceCart.git; branch main. Ordinary sequential continuation commits:

| Commit | Delivery |
|---|---|
| 8cb367e | Fresh baseline/audit and continuation plan |
| 685f5c3 | S8 instrumentation and safe performance hardening |
| e4e4204 | S9 real historical metadata/provenance/discovery |
| 22b5a5f | S10 HTTP/security/Compose foundation |
| 9b8fe51 | S11 customer/cart flows |
| 2ea2ab4 | S12 admin/actual events |
| 2493342 | S13 shared adapter and actual typed SDK path |
| 4a4fed6 | S14 testing syllabus/CFG/coverage/load and discovery hardening |
| Final sprint commit containing this handoff | S15 integrated193+193 checks, final race/readiness/recovery fixes, actual HTTP voice and documentation |

Use `git log -10 --oneline` and `git rev-parse HEAD` for the exact self-containing final commit, then `git ls-remote origin refs/heads/main` and `git status --short` to verify push/cleanliness. Prior separately approved history cleanup is historical; **no force-push or history rewrite was performed in this continuation**. Local ignored data/models/secrets are intentionally not Git deliverables.

## 16. Known limitations and impact

NLU H05 safe false rejection and slow actual inference limit convenience/latency. Relevance weights and optional dense ordering lack representative human judgments; no universal best-product guarantee. Partial historical catalogue lacks live stock/current offers and cannot support real checkout/cart adds. English/INR interpretation and tested English CPU voice do not establish Hindi/Hinglish acceptance. Physical audio/accessibility, container/platform/GPU, maintained deployment and production capacity remain unverified. Licensed distribution and owner current-source policy are unresolved. Local carts are not reservations; expired sessions/unknown outcomes require explicit recovery. Dedicated per-tenant DBs simplify isolation but impose operational overhead.

## 17. Prioritized next work

1. Obtain authoritative current merchant facts/coverage/update SLA and license/distribution decisions; historical metadata cannot safely substitute for inventory.
2. Correct NLU quantity failures using separate development cases, then freeze a new holdout; preserve critical-slot/action guards. Profile pinned inference with controlled cold/warm/residency/concurrency conditions before changing model architecture.
3. Run actual maintained PostgreSQL/Compose clean boot/restart/volume/secret/TLS/backup drills and platform/GPU checks; native/test success cannot prove container operation.
4. Measure end-of-user-speech to meaningful audible output with approved devices/languages, failures and adequate samples; test prices/negation/noise/interruption with real people.
5. Evaluate VoiceOver and representative blind/low-vision users; collect judged product relevance/task success before tuning weights or selecting rerankers/ANN.
6. Add one external merchant adapter only with its real authentication, stock/cart authority, refresh/webhook/idempotency/reconciliation contract and conformance tests.
