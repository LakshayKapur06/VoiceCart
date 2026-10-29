# VoiceCart execution plan

Updated 29 October 2026. The owner authorizes completion of all feasible engineering work, isolated test services, normal per-sprint commits/pushes and backed-up local history cleanup. Remote history rewriting requires separate final approval. Normal product tables must remain empty until the owner supplies real catalogue data. No seeding, checkout, payment or merchant-cart claims.

## Execution sequence and gates

| Sprint | Goal / stories | Dependencies / ready | Engineering acceptance and tests | Deliverables / status |
|---|---|---|---|---|
| 1–2 existing | Preserve deterministic catalogue and audio contracts | Starting `f58709c`; 98 passing tests | Recheck baseline; existing cancellation, money, coverage and ranking invariants stay green | Existing implementation retained; actual voice acceptance open |
| 3 | Local NLU adapter and strict interpretation (N-01/02) | Typed contracts, loopback runtime API, explicit artifact identity | Unit critical evidence/negation/amount/operator tests; real HTTP protocol integration; malformed/truncated/time-out output cannot dispatch. Model quality acceptance requires provisioned artifacts and held-out language cases | Engineering verified/pushed `62f4a75`; model quality acceptance open |
| 4 | PostgreSQL/pgvector persistence, validated ingestion, lexical/dense/price search (R-01–04) | Validated plans; isolated PostgreSQL test service | Real migrations, no seeds, rollback/duplicate/stale publication, snapshot/conformance tests; scoped minimum separate from relevance; empty/unavailable/stale states distinct | Engineering verified/pushed `5b67ba2`; production/quality acceptance open |
| 5 | Session references and safe persistent cart (C-01–03) | Persistent facts and transactions | Real DB concurrency/idempotency/session/aggregate-stock/changed-offer/receipt/restart/uncertain-commit tests; success only after committed receipt lookup | In progress |
| 6 | Runnable accessible text/voice integration (U-01/02, A-01–03 remediation) | Search, NLU and cart | System search/add/clarification/cancel/repeat/error paths; real adapter execution where artifacts/devices are available; never equate queued audio with heard speech | Pending |
| 7 | Operational verification, docs, cleanup and handoff (E-01–03) | Integrated application | Full unit/integration/system/automatable acceptance gates, lint/format/type/security/compile/build/clean install; fresh app DB zero products; exact owner/model/device/manual gates documented | Pending |

Each engineering sprint runs its applicable unit, real-boundary integration, system and automated story acceptance checks plus full regression, lint, type, security, compile and package checks before commit/push. Manual/hardware/quality gates unavailable in this environment remain explicitly open; an implementation checkpoint is not product release acceptance. No invented numerical relevance floors, multilingual guarantees or sub-1.5-second achievement.

Definition of ready: bounded story, existing dependencies, canonical inputs/outputs, isolated fixture/service plan and expected failures. Definition of engineering done: actual code integrated, meaningful automated checks pass, limitations recorded, diff/secret/product-data checks clear, commit pushed and remote verified. Definition of release done additionally requires real catalogue/source freshness, exact artifacts/terms, approved language/hardware and human accessibility/quality acceptance.

Security/privacy/reliability requirements for every sprint: loopback local inference; parameterized SQL; model output never authorizes facts or writes; no raw-content logs; no product fixtures outside tests; bounded operations and explicit errors; stable session and operation identity; accessible text equivalent and truthful audio delivery status.

## Evidence and remediation

Baseline and checklist: [AUDIT.md](docs/evidence/AUDIT.md). Existing experiment/decision register below remains relevant until consolidated into final README/HANDOFF. Superseded instructions limiting this task to Sprint 1, retaining Suggestions.md forever, or prohibiting authorized commit/push do not apply to the current owner request.

## Existing decision and experiment reference

## Testing and evaluation strategy

| Review experiment | Stories / sprint | Evidence required and current coverage |
|---|---|---|
| **E01 catalogue correctness/consistency** | F-02–06 (S1); R-01/02 (S4); C-02/03 (S5) | S1 covers complete-fixture oracle, top-K counterexample, LT/LE, unknown/missing/stale facts, variants, ties, unknown/partial coverage and no-match scope. SQL publication/concurrency/crashes are later, not proven by S1. |
| **E02 NLU** | N-01–03 (S3), E-01 (S7) | Schema versus semantic correctness; critical slots/negation/actions; audio repeats after text tests. No model call in S1. |
| **E03 ASR/endpoint** | A-01–03 (S2), E-01 (S7) | WER plus prices/amounts/colour/quantity/negation accuracy; pauses, silence, echo, early endpoints and code switching only if in profile. |
| **E04 retrieval/rerank** | R-03/04 (S4), E-01 (S7) | Lexical/dense/hybrid ablations, identity, recall/precision/nDCG, selective filters and safe query construction; rerank only if recall is adequate. |
| **E05 TTS/playback** | A-02/03 (S2), U-01 (S6), E-03 (S7) | Actual audible onset, rupee/SKU comprehension, failed synthesis/playback, cached/assistive recovery and exact artifact terms. |
| **E06 action/state** | C-01–03 (S5), U-01 (S6), E-01 (S7) | Idempotency, stable lists, quantity aggregates, concurrent mutation, late callbacks, cancel/commit and receipt replay after later adds. No cart implementation in S1. |
| **E07 combined latency** | A-03 baseline (S2), N/R/C/U instrumentation, E-01 (S7) | Actual utterance end → meaningful audible response; verified outcomes separately; failures/timeouts retained, cold/warm/device/language strata and resources. Under 1.5 seconds is unverified. |
| **E08 accessibility** | A-01 (S2), U-01/02 (S6), E-03 (S7) | Representative blind/low-vision user tasks across controls, ambiguity, no-match, interrupted lists and audio failure. Unit tests alone cannot establish usability. |
| **E09 offline/recovery** | F-01 (offline pure tests, S1); A-02 (S2); R-01/02 (S4); E-01/03 (S7) | S1 has no inference/network/service dependency. Later measure actual network after provisioning, missing artifacts, contention, clean restore, model/index/audio failure and retained data. |
| **E10 relevance/price** | F-05 interface/role tests (S1); R-04 (S4); U-02 (S6); E-01 (S7) | S1 fixture ranking can choose a better-fit higher-priced qualified item while keeping the minimum separate; no learned relevance claim. Later tune/freeze features/weights on judgments and compare exhaustive composite-score recall. |
| **E11 storage fit** | R-01–04 initial (S4), E-02 (S7) | Same snapshot/embeddings/predicates/scorer/device, equal recall/quality, exact versus ANN/selectivity, SQL+dedicated/embedded alternatives, memory/disk/build/update cost, recovery/setup and full-turn latency. Not run in S1. |

For hard invariants require exact agreement/no violations on the declared fixtures; finite tests do not prove arbitrary real-world correctness. Noncritical quality/resource headroom and minimum usable sample sizes require pilot evidence and D13 before held-out acceptance. Preserve D06’s original target; a warm P95 interpretation is still a proposal. Store experiment manifests/results by code revision, dataset/profile/configuration and failure denominators once actual experiments exist; do not fabricate populated benchmark files now.

## Risks and open decisions

| Decision | Remaining question / risk | Unblocking assumption now | Gate / evidence needed |
|---|---|---|---|
| **D01** | Target hardware/OS and Python/audio/model fit unknown. | Local Python >=3.11 development only. | Device inventory, A-03/E07/E09 before support/latency claims. |
| **D02** | Required English/Hindi/Hinglish/scripts unconfirmed. | Canonical synthetic fields; no language capability claimed. | Owner profile plus NLU/ASR/retrieval/TTS tests by language. |
| **D03** | Catalogue source/size/coverage/update SLA and freshness unknown. | Complete/incomplete synthetic snapshots with explicit assertions. | Representative records, taxonomy, source contract and publication/freshness tests. |
| **D04** | Local demo versus real merchant cart. | Local demonstration only; no cart mutation in S1. | Authoritative API/auth/idempotency/outcome lookup before any merchant claim. |
| **D05** | Distribution/project/runtime/voice licences unresolved. | No model/voice bundled; no project licence invented. | Exact shipped artifact inventory and intended-use decision before distribution. |
| **D06** | Under-1.5-second workload/percentile/profile acceptance unknown. | Retain target; measure actual meaningful audio with failures. | Owner acceptance and E07 evidence; no hidden relaxation. |
| **D07** | Catalogue scale/update concurrency and model contention unknown. | Immutable single-process fixtures. | Representative load and E06/E07/E11; shared deployment not in MVP. |
| **D08** | Best extraction model/runtime configuration unmeasured. | Keep pinned 2507 reference direction; no model loaded in S1. | E02/E07 controlled task/device comparison. |
| **D09** | English BGE adequacy/language coverage and encoder migration. | No embeddings in S1. | E04 approved-language judgments and versioned re-embedding tests. |
| **D10** | Whether a neural reranker solves a real ordering problem. | No reranker/default weights. | Adequate candidate recall but poor order plus paired E04/E07/E10 benefit. |
| **D11** | Accepted controls/voice/accessibility in actual failure paths. | Define controls now; no usability claim. | A/U slices and E05/E08 representative-user acceptance. |
| **D12** | Session expiry, retained content and restart semantics unresolved. | No audio/transcript/cart storage; immutable fixture memory. | Explicit policy, E06/E09; do not promise cross-session recovery. |
| **D13** | Noncritical quality thresholds/sample sizes not justified. | Deterministic fixture invariants; no invented relevance weights/floors. | Pilot judgments/error costs, pre-register gates before held-out comparisons. |
| **D14** | How cheapest appears alongside relevance-ranked matches. | Distinct backend roles; separate presentation is provisional. | Owner/user decision and U-02/E10 inclusion/order/comprehension tests before release. |
| **D15** | PostgreSQL/pgvector device/workload fit unmeasured. | Accepted reference; in-memory contract now, exact vectors later. | E11 including split/embedded alternatives and resource/restore costs; change only for evidence/requirements. |
