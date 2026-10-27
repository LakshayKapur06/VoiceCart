# VoiceCart implementation plan

Planning baseline: **27 October 2026**, repository commit `7b90f48`. Inspection found only README.md and Suggestions.md, a clean main branch, and no implementation, tests or AGENTS.md. This task authorizes documentation integration and **Sprint 1 only**. No commit, push, deployment, paid resource or external-service modification is authorized by this plan.

Use **one-week sprints provisionally**. Staffing, throughput, dates, story points and release dates are unknown; this is an ordering/acceptance plan, not a delivery promise. The owner accepts the reviewed architecture as the reference, while untested benefits and D01–D15 remain open. [Suggestions.md](Suggestions.md) is an unchanged historical review, not a delivery log. [README.md](README.md) describes current requirements and implemented status.

## Product goal and scope

Deliver a local, accessible voice-first shopping workflow that can search a catalogue, explain suitable options from actual evidence, identify the cheapest qualifying option and safely add an explicitly selected item to a **local session demonstration cart**. The LLM interprets; deterministic application logic owns eligibility, facts and mutations. Ordinary search balances query fit, supported preferences and price; it does not always sort by price. Cheapest and overall best-ranked matches remain distinct roles.

Preserve local inference, no paid inference APIs, templates for straightforward confirmations, retrieval before grounded explanation, nonvisual controls/recovery, session isolation and no persistent audio/transcript logs by default. PostgreSQL + pgvector is the reasoned storage reference, with exact vectors first and E11 validation still required. ASR, NLU, encoder and TTS candidates remain provisional.

The MVP excludes comprehensive cart editing/history, checkout, payment, merchant order placement, order tracking, a general autonomous-agent framework, extensive admin/analytics and shared multi-user deployment. A real merchant cart needs its own approved authoritative integration; a local receipt must never imply it happened.

Sprint 1 deliberately delivers only a pure deterministic foundation. It does not deliver a voice application, semantic search, database service or cart mutation.

## Working assumptions

- Use Python >=3.11 for development; this is not an approved minimum end-user device specification (D01).
- Use one process and immutable synthetic catalogue snapshots. Coverage and price freshness are explicit assertions on a fixture; nothing imports or verifies real merchant data yet (D03).
- Use canonical case-sensitive IDs/attributes, INR examples and explicitly typed price operators. No natural-language parser, fuzzy matching, currency conversion or multilingual claim is included (D02/D09).
- Unknown coverage is the default. Unknown/missing facts never become matches. A known contradiction can exclude a record even if another unrelated fact is missing; only potentially qualifying unknowns block a complete claim.
- D14’s separate cheapest-role presentation is a working proposal only. The backend result-role distinction can be built now; owner/user presentation acceptance is a later gate.
- Ranking has a versioned interface/evaluation seam; no production relevance formula/weights are invented in Sprint 1.

## Product backlog

P0 means required correctness, accessibility or feasibility work. P1 means the next required integration/evaluation work after its dependencies; it does not mean optional product safety. Experiments/optimizations are P2 and enter a sprint only for a demonstrated problem. IDs below are local backlog identifiers, not newly created external issues.

| Epic | Outcome | Review changes |
|---|---|---|
| F — deterministic foundation | Validated money/identity/constraints and complete structured selection | ARCH-001/002; contracts for ARCH-009 |
| A — early audio feasibility | Observable local turns, ASR/TTS and actual audible timing | ARCH-006/007/008 |
| N — interpretation | Bounded schema NLU with independent semantic checks | ARCH-004 |
| R — catalogue and discovery | SQL authority, atomic publication, hybrid retrieval and evaluated ranking | ARCH-002/003/009 |
| C — safe local action | Session/reference identity and transactional idempotent cart increments | ARCH-005 |
| U — usable integrated workflow | Nonvisual interaction, grounded responses and recovery | ARCH-006/007 |
| E — evidence and release | Combined quality/resource/storage/accessibility gates | ARCH-008; all changes |

| Story | Priority | User story / engineering outcome | Dependencies | Testable acceptance criteria | Risks / decisions |
|---|---|---|---|---|---|
| F-01 | P0 | Establish a small Python package and reproducible local tests. | None | Python requirement and dependencies declared; stdlib test command runs without models/services; package/lint commands documented. | D01; avoid framework scaffolding. |
| F-02 | P0 | Represent canonical products/variants, integer money and typed requests/results. | F-01 | Reject floats/bools as money, invalid identifiers/operators and contradictory construction; unknowns remain explicit; no currency conversion. | D03; future PostgreSQL bigint compatibility. |
| F-03 | P0 | Find the cheapest supported structured match across a whole snapshot. | F-02 | Full-set independent oracle agrees on price/ID ties; strict/inclusive bounds differ; missing/stale required facts or unknown/partial coverage prevent complete minimum/no-match claims. | D03; three-valued logic and scope. |
| F-04 | P0 | Resolve an explicit typed identifier without fuzzy substitution. | F-02 | Variant ID/SKU/product ID/model lookup uses exact equality; variants stay separate; unknown IDs and ambiguous multi-variant identity are exposed; invalid/duplicate records fail snapshot creation. | D03; model number need not identify one variant. |
| F-05 | P0 | Keep ranking and minimum roles independent with a versioned evaluation seam. | F-03/F-04 | Only qualified records reach a supplied ranking policy; invalid output is rejected; overall match can differ from cheapest; absent policy means unevaluated relevance; discovery explicitly unsupported. | D09/D13/D14; no default weights. |
| F-06 | P0 | Publish coherent architecture, tests and domain limitations. | F-01–05 | All required Sprint 1 edge cases pass; README/ADR/plan distinguish planned code from measured behaviour; Suggestions.md unchanged. | Historical review restrictions must stay scoped. |
| A-01 | P0 | End/stop/repeat and partial/final boundaries are discoverable. | F-01 | Half-duplex turn adapter tests pauses, stop, silence and stale events; partials never authorize actions; explicit keyboard/assistive controls usable. | D01/D02/D11. |
| A-02 | P0 | Run a local ASR → fixed verified template → local TTS slice. | A-01 | Pin tested artifacts/backends; critical-word and rupee/SKU comprehension fixtures; TTS/playback failure exposes cached speech/assistive status. | D02/D05/D11; voice terms before distribution. |
| A-03 | P0 | Measure actual audio onset with visible failure accounting. | A-02 | Record annotated utterance end, VAD, remaining inference, PCM and audible onset; cold/warm/resources and timeout/no-audio samples retained; no target-achieved claim without data. | D01/D06/D13. |
| N-01 | P0 | Extract bounded schema interpretations with reference Qwen/Ollama. | F-02, A-03 timing seam | Pin digest/template/runtime; strict schema, token/time bounds and bounded repair; malformed/truncated/extra-field output cannot dispatch actions. | D08; grammar is not semantic proof. |
| N-02 | P0 | Independently validate numbers, intent, negation and supported constraints. | N-01/F-03 | “Under”/“at most,” quantity/budget basis, “don’t add,” unknown taxonomy and corrections match held-out expected plans or clarify. | D02/D03/D13. |
| N-03 | P1 | Compare small-model challengers only under controlled gates. | N-01/N-02/A-03 | Same schema/data/quantization controls; critical regressions block promotion; record latency/resources and reasoned model decision. | D08; no automatic newer-model switch. |
| R-01 | P0 | Port deterministic authority to PostgreSQL through the catalogue contract. | F-01–06 | Pin compatible server/extension/driver; enforce schema constraints; run adapter conformance/oracle tests; local access, timeouts and clean-host backup/restore tested. | D01/D03/D07/D15. |
| R-02 | P0 | Publish facts and matching search data consistently. | R-01 | Reject stale embedding jobs; atomic content/coverage publication and generation switches; concurrent readers see one snapshot; pending semantics never becomes no-match. | D03; crash/rebuild windows. |
| R-03 | P1 | Retrieve exact lexical+dense+qualifying low-price candidates. | R-01/R-02/N-02 | Exact BGE/pgvector baseline, explicit text config, safe query construction, Recall/Precision/nDCG by query/filter strata; exact IDs remain binding. | D02/D09/D10; filtered ANN not yet enabled. |
| R-04 | P1 | Evaluate a versioned query-fit/preference/price scorer. | F-05/R-03 | Hard eligibility first; equal-fit cheaper and higher-price better-fit pairs; human judgments plus candidate-union/exhaustive composite-score comparison; scoped cheapest retrieval for every supported search. | D13/D14; tune on development labels, freeze held-out policy. |
| C-01 | P0 | Bind turns and spoken references to stable session/list IDs. | N-02/R-03 | New/refined/partly spoken lists and late callbacks cannot redirect “second”; session isolation and documented expiry tests. | D11/D12. |
| C-02 | P0 | Apply authorized local cart increments once per operation identity. | C-01/R-01/F-03 | Same ID/fingerprint retries replay immutable receipt; new intentional adds get new IDs; aggregate quantities, selected revisions and scoped minimum rechecked transactionally. | D04/D12; no inventory reservation/merchant claim. |
| C-03 | P0 | Reconcile cancellation, concurrent writes and uncertain commits. | C-02 | Serialization/deadlock/unique-key/connection-loss faults preserve correct quantity and receipt; no blind retry or success guess; repeat only replays audio. | D07/D12; external semantics still unapproved. |
| U-01 | P0 | Integrate nonvisual search, clarification, selection and safe local add. | A/N/R/C slices | All critical paths work with keyboard/screen reader and speech; templates use verified facts; optional explanation cannot invent claims or mutate. | D02/D05/D11. |
| U-02 | P0 | Present overall-ranked and cheapest roles understandably. | R-04/C-01/U-01 | Deduplicate roles, preserve announced order for ordinals, test misunderstanding and interruption; document provisional D14 until owner/user acceptance. | D14; do not ship a silently chosen presentation. |
| E-01 | P0 | Run combined quality/latency/resource/offline gates. | Integrated Sprint 6 slice | Frozen data/profiles/threshold decisions; publish failures/timeouts and cold/warm distributions; all required invariants pass; unmeasured strata clearly excluded. | D01/D02/D06/D07/D13. |
| E-02 | P1 | Validate storage fit with an equivalent-quality comparison. | R-01–04, A-03 | E11 compares exact/ANN, split and embedded modes at equal recall/quality; updates/restore/setup/resource/latency results justify retention or a scoped alternative. | D15; no universal database winner. |
| E-03 | P0 | Review readiness with representative users and exact shipped artifacts. | U-01/U-02/E-01/E-02 | Critical accessibility defects resolved; voice/runtime licences recorded; retained data/network reviewed; residual risks/unsupported profiles and owner decisions recorded. | D01–D15; release only after actual gates. |
| O-01 | P2 | Optimize a measured bottleneck without weakening correctness. | A failed metric with baseline | One justified change (ANN/reranker/model/runtime/store) passes paired task/resource tests and rollback drill. | D08–D10/D15; outside this task. |

## Sprint plan

| Sprint | Goal and deliverables | Dependencies | Exit criteria |
|---|---|---|---|
| **1 — deterministic foundation** | F-01–06: package, contracts, immutable in-memory authority, exact lookup, complete structured selection, ranking protocol, tests and documentation. | Review verdict plus explicit synthetic assumptions; no services/models. | Required counterexamples/boundaries/unknowns/identity/ties/coverage tests pass; independent full-fixture oracle agrees; no inferred completeness; declared checks pass and limitations are documented. |
| **2 — early audio feasibility** | A-01–03: local audio/VAD/ASR/TTS adapters, half-duplex controls, failure/status path and actual playback timing. | Sprint 1 contracts; provisional test device/language/eligible artifacts. | Actual device audio slice and critical slots tested; accessibility controls/failures demonstrable; timings/resources and unsupported profiles recorded, not fabricated. |
| **3 — constrained interpretation** | N-01–03: pinned reference NLU, strict output contract, independent semantic validation and controlled challenger experiment. | Typed domain plus audio/timing seams. | Critical intent/slot/operator/negation fixtures pass; repair/time limits enforced; model/runtime choice traceable to task evidence. |
| **4 — data and hybrid retrieval** | R-01–04: PostgreSQL/pgvector exact adapter, text search, publication snapshots/generations, low-price branch and experimental scorer. | Deterministic conformance suite and validated plans; representative catalogue. | SQL oracle/consistency/fault tests pass; exact-search baseline and initial E11 resource/restore results; relevance and candidate recall evaluated; no unsupported global/semantic claim. |
| **5 — safe local action** | C-01–03: state/list identity, transactional local cart, idempotency/receipts and recovery. | Database authority, result roles and validated add plans. | No duplicate, redirected, cross-session or invalid-quantity effect in challenge tests; uncertain outcomes reconcile; no unconfirmed merchant claim. |
| **6 — accessible integration** | U-01/02: full voice loop, templates/optional grounded explanation, recovery, user-tested result roles. | Audio, NLU, retrieval and safe action slices. | Critical workflow/failure/control paths usable without sight; result references accurate; D14 resolved for release or presentation explicitly experimental/unreleased. |
| **7 — evidence/readiness** | E-01–03: combined evaluation, E11 storage comparison, offline/resource/recovery and readiness review. | Integrated workflow and pre-registered profile/quality decisions. | Published actual results plus denominators/uncertainty; invariants pass; D01–D15 disposition recorded. Failed gates yield backlog changes, not a claim of completion. |

Sequence rationale: prove cheapest selection without retrieval/model confounders first; test defining audio feasibility in Sprint 2 rather than the old README’s Sprint 4; integrate NLU only after clear typed seams. The review’s early database recommendation is moved to Sprint 4 to honour this task’s domain-only Sprint 1, retaining the conformance suite for the later adapter. Database performance is consequently unverified until that slice; a source or device limitation can reorder later stories after documenting why. Do not implement future sprint placeholders as fake adapters now.

## Definition of Ready

A story is ready when its ID, owner-selected priority, bounded outcome, dependencies, canonical inputs/outputs, relevant D decisions and testable acceptance cases are recorded. Its fixtures must distinguish known facts, unknowns and scope. Provisional assumptions may unblock a fixture/prototype; a release-only decision does not block all coding. A story touching a real model/device/data source must identify the exact experiment and eligible artifacts before running it. Mutation stories need authorization, identity, rollback/recovery and no-match/ambiguity cases defined before coding.

## Definition of Done

- The agreed scoped behaviour exists, including failure/unknown paths, with meaningful automated tests against explicit expected outcomes.
- The full available suite and configured lint/format/syntax checks pass; unrun/blocked checks and environment limits are reported, never relabelled successful.
- Documentation distinguishes implemented/tested code, unverified integration, future work, provisional references and unresolved owner decisions.
- No hard constraint is overridden by ranking; no catalogue-wide claim follows from unknown coverage, stale/missing required facts or candidate-only scope.
- No unsupported model quality, universal correctness, latency, accessibility-conformance, external exactly-once or merchant-action claim is introduced.
- Privacy/accessibility/scope impacts are reviewed; no unrelated changes, sensitive logs or hidden external resources are added.
- Suggestions.md remains the original review record. Commit/push/deploy are separate user actions, not automatic sprint completion.

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

## Agile operating procedure

Track story IDs here using **Ready → In progress → Review → Done**; keep blocked items with the missing dependency/decision rather than blocking unrelated work. At each sprint boundary choose the smallest ready set that achieves its goal; do not assume every listed story fits one person/week. Before coding, identify acceptance fixtures. During work, record material assumptions and scope changes. Tests/review/Definition of Done gate the state transition; a planning document or green mock alone is insufficient.

At sprint end demonstrate the actual increment, review failures and user feedback, and update the next backlog/sprint order with evidence. Use a short written planning/review note, not mandatory meetings or a heavyweight process. Experiments can reject a model/store choice; preserve the previous reproducible configuration and explain the change. Resolve release decisions with owners/users when needed while continuing independent ready stories. External issues, messages, releases and resources require separate authorization.

## Sprint 1 delivery record

F-01–06 are the only stories implemented by this task. The initial 53-test suite passed; the owner then requested immediate commit/push and explicitly skipped remaining final checks. The code is implemented and initially tested, with final verification/review pending rather than every Definition of Done gate closed. See [docs/SPRINT_1.md](docs/SPRINT_1.md) for exact commands/outcomes and limits. E01’s domain subset and E10’s interface/role checks are covered; no full E01 database/publication experiment or E02–E11 runtime/quality benchmark is implied. Sprints 2–7 remain planned.
