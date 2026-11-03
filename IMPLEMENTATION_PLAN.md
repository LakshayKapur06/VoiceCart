# VoiceCart execution plan

Updated 29 October 2026. The owner authorizes completion of all feasible engineering work, isolated test services, normal per-sprint commits/pushes and backed-up local history cleanup. Remote history rewriting required separate final approval; the owner gave it and the reviewed cleanup was pushed and verified at `201530a`. Normal product tables must remain empty until the owner supplies real catalogue data. No seeding, checkout, payment or merchant-cart claims.

## Execution sequence and gates

| Sprint | Goal / stories | Dependencies / ready | Engineering acceptance and tests | Deliverables / status |
|---|---|---|---|---|
| 1–2 existing | Preserve deterministic catalogue and audio contracts | Starting `f58709c`; 98 passing tests | Recheck baseline; existing cancellation, money, coverage and ranking invariants stay green | Existing implementation retained; actual voice acceptance open |
| 3 | Local NLU adapter and strict interpretation (N-01/02) | Typed contracts, loopback runtime API, explicit artifact identity | Unit critical evidence/negation/amount/operator tests; real HTTP protocol integration; malformed/truncated/time-out output cannot dispatch. Model quality acceptance requires provisioned artifacts and held-out language cases | Engineering verified/pushed `62f4a75`; model quality acceptance open |
| 4 | PostgreSQL/pgvector persistence, validated ingestion, lexical/dense/price search (R-01–04) | Validated plans; isolated PostgreSQL test service | Real migrations, no seeds, rollback/duplicate/stale publication, snapshot/conformance tests; scoped minimum separate from relevance; empty/unavailable/stale states distinct | Engineering verified/pushed `5b67ba2`; production/quality acceptance open |
| 5 | Session references and safe persistent cart (C-01–03) | Persistent facts and transactions | Real DB concurrency/idempotency/session/aggregate-stock/changed-offer/receipt/restart/uncertain-commit tests; success only after committed receipt lookup | Engineering verified/pushed `ef4acec`; release acceptance open |
| 6 | Runnable accessible text/voice integration (U-01/02, A-01–03 remediation) | Search, NLU and cart | System search/add/clarification/cancel/repeat/error paths; real adapter execution where artifacts/devices are available; never equate queued audio with heard speech | Engineering verified/pushed `233ad71`; hardware/quality acceptance open |
| 7 | Operational verification, docs, cleanup and handoff (E-01–03) | Integrated application | Full unit/integration/system/automatable acceptance gates, lint/format/type/security/compile/build/clean install; fresh app DB zero products; exact owner/model/device/manual gates documented | Engineering verified/pushed `67e526e`; 159 source/wheel tests; local history artifact recorded in HANDOFF; owner/device/quality gates remain explicit |

Each engineering sprint runs its applicable unit, real-boundary integration, system and automated story acceptance checks plus full regression, lint, type, security, compile and package checks before commit/push. Manual/hardware/quality gates unavailable in this environment remain explicitly open; an implementation checkpoint is not product release acceptance. No invented numerical relevance floors, multilingual guarantees or sub-1.5-second achievement.

Definition of ready: bounded story, existing dependencies, canonical inputs/outputs, isolated fixture/service plan and expected failures. Definition of engineering done: actual code integrated, meaningful automated checks pass, limitations recorded, diff/secret/product-data checks clear, commit pushed and remote verified. Definition of release done additionally requires real catalogue/source freshness, exact artifacts/terms, approved language/hardware and human accessibility/quality acceptance.

Security/privacy/reliability requirements for every sprint: loopback local inference; parameterized SQL; model output never authorizes facts or writes; no raw-content logs; no product fixtures outside tests; bounded operations and explicit errors; stable session and operation identity; accessible text equivalent and truthful audio delivery status.

## Evidence and remediation

Baseline and checklist: [AUDIT.md](docs/evidence/AUDIT.md). Current decisions are consolidated in docs/ARCHITECTURE.md; obsolete review-only restrictions are superseded by the current owner execution request.

## Release experiments and owner acceptance

Shared sprint definition of ready/done and the security/privacy/accessibility requirements above apply to every story. Unit/integration/system acceptance evidence for each delivered increment is linked in docs/evidence/SPRINT_3.md through SPRINT_7.md. Existing S1/S2 contracts remain historical evidence, not proof of present device usability.

| Experiment | Automated/actual evidence now | Remaining release acceptance |
|---|---|---|
| E01 correctness | Full-source oracle, LT/LTE, unknown facts, real SQL publication/snapshot/rollback | Real-source completeness/freshness contract |
| E02 NLU | Strict critical-slot/action tests, real loopback HTTP, actual model smoke | Held-out English/profile cases and critical-error rates |
| E03 ASR | Real synthetic file speech/Whisper, scripted endpoint errors | Human microphone pauses/noise/amounts/negation by target language |
| E04 retrieval | Real FTS/pgvector and exhaustive composite counterexample | Owner relevance judgments, lexical/dense ablations, recall/nDCG |
| E05 TTS | Actual Piper synthesis, scripted drain/stop/failure | Device acoustic onset, rupee/SKU comprehension, approved voice terms |
| E06 state | Real concurrent/idempotent cart/receipt/restart/recovery tests | Representative operational recovery and user comprehension |
| E07 latency | Honest stage timings; native output returns no fabricated onset | End-of-utterance to meaningful audible output, cold/warm percentiles including failures/timeouts; 1.5s goal unverified |
| E08 accessibility | Keyboard controls/text equivalents and scripted failure paths | Representative blind/low-vision acceptance, screen reader/device testing |
| E09 recovery/privacy | Empty startup, packaged migrations, real logical dump/restore | Owner patched server/backups/retention, network-isolation and device-failure drill |
| E10 price/relevance | Separate minimum and overall role; full exact scoring regression | Freeze weights/placement using pilot, then held-out quality gates |
| E11 storage | Real one-store consistency/restore exercised | Equal-recall SQL/embedded/dedicated comparison at approved scale/device |

No thresholds or percentile success are invented without a meaningful sample. D01–D15 and ARCH-001–009 rationale are consolidated in [ARCHITECTURE.md](docs/ARCHITECTURE.md). Remaining requirements are owner data, hardware/user access and release decisions; no further source-only sprint is claimed to satisfy those gates.

## Continued development — 2 November 2026

The new mandate expands the delivered S1–S7 prototype. It supersedes the earlier empty-demo constraint by explicitly authorizing real Amazon Reviews 2023 historical metadata for a labelled demonstration catalogue. It does not authorize invented live offers, inventory or synthetic production data. Existing owner data remains protected. No history rewriting or force-push is permitted in this continuation.

| Sprint / stage | Goal, story and modules | Dependencies / acceptance / verification |
|---|---|---|
| S8 / 0–1 | Reproduce baseline; instrument and harden existing HTTP/NLU/database/search/application. As a maintainer I can identify stage delays and safely evaluate interpretations. | Ready: 159+159 fresh baseline; inspect current modules. Done: granular spans/counters, bounded caches never caching action facts, held-out protocol/evaluation harness, regression gates and performance handoff. Actual cold/warm model observations distinguished from historical evidence. |
| S9 / 2 | Import sourced Amazon historical metadata with provenance; browse missing-price/unknown-stock records without commerce claims. Modules ingestion/database + new dataset/browser boundary. | S8 stable. Validate terms/access, bounded real category extract, full source hash/revision/row provenance, repeatable CAS import, quality report and SQL/exact/lexical tests. No fabricated USD→INR conversion or stock. |
| S10 / 3 | Reproducible Compose/API foundation. | Catalogue contracts stable. Static configuration, health/migrations/secrets/volumes/networking, package installation; real container execution only if Docker available. Blocked runtime checks explicitly reported. |
| S11 / 4 | Accessible customer text/voice/search/details/cart UI and actual HTTP endpoints, transactional quantity/removal. | Reuse deterministic core. Browser/API system tests, auth/session/idempotency/cancel/error tests, keyboard/mobile/desktop; physical devices and human screen-reader acceptance separately recorded. |
| S12 / 5 | Admin catalogue publication/provenance/import history, actual events/health and access controls. | Real API and permissions. CAS-safe edit/deactivate/import, strict limits, auth and isolation tests, actual SQL aggregate metrics with no fake dashboard rows. |
| S13 / 6 | Common merchant contract, local adapter, TypeScript/JS SDK and self-hosted/managed topology. | Working local path. Contract/back-to-back, operation receipts, explicit tenant isolation/credential/rate-limit/webhook scope. No unsupported Shopify/WooCommerce/Magento claims. |
| S14 / 7 | Traceable testing syllabus: partitions/boundaries/tables/cause-effect, real CFGs/three complexity methods/basis paths, coverage/loops/interfaces/load/install/smoke/acceptance. | Integrated product. Executable tests plus generated source-linked analysis and measured coverage/load evidence; blocked hardware/runtime tests labelled Not Run. |
| S15 / 8 | Final integrated regression, security/package/browser checks, expanded professional README and final handoffs. | All independent stages verified. Accurate endpoints/commands/data/terms/status, no secrets/fixtures in production, reviewable ordinary sprint commits/pushes and exact remaining gates. |

Shared Definition of Ready: inspected source, explicit story and bounded contract, dependency availability, isolated fixture plan, failure expectations and data/permission scope. Shared Definition of Done: meaningful unit, integration, system and automatable acceptance tests plus full applicable regressions; lint/format/types/security/package checks; reviewed changes; documented evidence and limits; normal commit/push verified. No sprint is a release acceptance substitute. Privacy/security: local model authority boundary, parameterized SQL, authenticated admin, scoped sessions, no raw-content analytics, bounded requests and explicit errors. Accessibility: semantic controls/text equivalent, keyboard/focus/status tests, honest device/user gaps. New evidence is dated separately from S1–S7.

## Continuation completion record

| Increment | Ordinary pushed commit | Verified delivery / remaining gate |
|---|---|---|
| Baseline | 8cb367e | Fresh159+159 reproduction and bounded audit/plan |
| S8 | 685f5c3 | Instrumentation/caches/frozen NLU protocol; actual11/12 quality, latency target open |
| S9 | e4e4204 | Real historical provenance/ingestion/read-only discovery; no live stock |
| S10 | 22b5a5f | HTTP/security/Compose configuration; Docker runtime Not Run |
| S11 | 9b8fe51 | Customer UI, safe cart quantity/remove; device/user gates open |
| S12 | 2ea2ab4 | Admin CAS edits/import/history and actual analytics |
| S13 | 2493342 | Shared adapter, actual local JS/TS SDK path and tenant guards; external adapters planned |
| S14 | 4a4fed6 | Syllabus/CFG/coverage/load evidence;191+191 checkpoint preserved in sprint record |
| S15 | See final sprint commit in Git log | Final193+193 regression, browser/SDK, HTTP real voice, readiness/delayed-turn fixes, comprehensive README/API/handoff. Five browser/two SDK checks; unavailable release tests explicitly Not Run. |

All feasible source engineering is delivered; release acceptance remains conditional on the explicit environmental/quality/rights gates in HANDOFF.md. Normal product startup still seeds zero records; the separate historical preview imports actual approved research metadata. Earlier empty-demo/history-cleanup instructions remain historical and are superseded only as stated by the continuation.

## Additive S16–S21 execution — 3 November 2026

Preserve S1–S15 and all November2 evidence. Each new run records SHA, dirty source fingerprint, UTC time, command, environment, outcome and limitations in a new evidence directory. Same-agent reproduction is never called independent security/human certification. No user changes at start; ordinary commits/pushes only.

| Sprint | Bounded increment / acceptance |
|---|---|
| S16 | Fresh193+193 baseline, browser/SDK/types/static/audits/CFG/load, evidence integrity tooling, coverage triage and meaningful practical contracts. |
| S17 | Frozen authored NLU dataset, intent/slot/action/rejection scorer, actual pinned-model comparison where local assets permit; no validator weakening or retuning on holdout. |
| S18 | Correct deployment defects, route authorization/security/recovery checks and exact missing runtime/TLS requirements. |
| S19 | Automated device-failure/review/focus/accessibility checks; available actual speech-stage evidence; explicit device/human protocols. |
| S20 | Cart concurrency/expiry/deactivation/uncertainty and original-ID recovery; actual local merchant path and external integration specification. |
| S21 | Final regression/evidence/rights/release audit, actionable human register, self-contained professor practical pack/checklist and additive report. |

All feasible engineering is attempted. Each partial sprint retains its explicit external/device/user/legal gates. A plan/document is not execution evidence.

### S16–S21 delivered engineering / remaining acceptance

| Sprint | Commit | Actual outcome |
|---|---|---|
|16 |4d58aa1 |Fresh193+193 baseline, four practical methods,197+197 regression, append-only evidence/triage; available engineering complete |
|17 |6fa10f3 |32frozen authored cases, two actual pinned models, scorer integrity; quality/representativeness partial |
|18 |eecc35a |Host/authorization/import/framing fixes, route matrix,208+208 regression; actual Docker/TLS/independent review blocked/human |
|19 |1fc1780 |8browser checks, source208pass, actual speech fail plus diagnostic pass, detailed human register; physical/users/acoustics pending |
|20 |8477528 |Late expiry/unknown receipt fixes,25targeted/215+215 full, actual bounded concurrent cart/search workloads; real source/external authorization missing |
|21 |Final commit containing report |Final218+218,8browser/2SDK/TS/audits/current coverage/cases/CFG, professor pack/checklist, human/release/license/additive report and compatibility/evidence tests |

All feasible requested engineering tasks attempted; unresolved quality/environment/device/participant/credential/rights gates have exact human actions. See ADDITIVE_EXECUTION_REPORT and HUMAN_INVOLVEMENT_REQUIRED. No force-push/history rewrite; all November2 JSON preserved.
