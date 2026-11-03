# VoiceCart additive engineering execution report

3 November 2026, continuing S1–S15 on main. Starting commit9973045 matched fetched GitHub; no user-owned changes were present. Ordinary commits only, existing architecture and historical November2 JSON preserved. Current project remains an engineering demonstration with explicit release gates.

## A. Executive summary

Reviewed all production/test/script/component inventories and current README/handoffs/plan/architecture/audits/testing/sprint evidence; reproduced the existing193+193 source/wheel baseline and browser/SDK/type/static/advisory/CFG/load checks. Delivered append-only run evidence, meaningful price/eligibility/output/loop tests, frozen NLU metrics/comparison, HTTP/deployment/input/authorization fixes, voice/focus/error-recovery tests, transaction expiry/uncertainty/concurrency tests and an executable professor/human handoff.

No core storage/model/framework replacement occurred. New authored32-case bank measured4B26/32 versus0.6B21/32, with lower smaller-model slot recall;4B reference retained. No unsafe validated add proposal observed on either small27-case nonaction subset; this is not a population safety guarantee. Actual synthetic speech smoke failed once; one diagnostic run with better observability passed. Both observations are retained. Eight browser checked states and actual local SDK passed; no physical device/user result is invented.

Final engineering verification:218 distinct Python methods, run against source and a freshly installed wheel; current per-method record and measured Python coverage linked below. Three final evidence-integrity tests ensure failure/skip/error summaries are not counted as passes and old evidence cannot be overwritten. Actual SQL includes controlled commit-loss/expiry/rollback and concurrent carts; optional model benchmarks do not perform commerce writes. Production deployment, current-source/external-platform rights/access, full acoustic latency, real assistive technology/users and legal/owner decisions remain incomplete.

## B. Sprint-wise completion

| Sprint / task | Status | Changes and verification | Evidence / remaining human work |
|---|---|---|---|
|16 baseline/audit/reproducibility | COMPLETED for available engineering | Fresh193+193, then four meaningful practical contracts and197+197; browser5/SDK2/TS; timestamped logs/SHA/source hash/coverage/CFG/load, gap classification | [S16](evidence/SPRINT_16.md), [audit](CONTINUATION_AUDIT_20261103.md); same-agent fresh run is not independent certification |
|17 NLU evaluation | PARTIALLY_COMPLETED | Frozen32 authored cases; intent/slots/quantity/bounds/negation/control/ambiguity/adversarial probes, explicit transport versus semantic rejection; actual same-bank two-model comparison | [S17](evidence/SPRINT_17.md), [method/results](NLU_EVALUATION_20261103.md); representative language/audio/quality and development fixes still needed |
|18 deployment/security/recovery | PARTIALLY_COMPLETED | Compose Host fix, nested input400, expired auth403, framing/config bounds; protected-route matrix and real HTTP regression;208+208 combined pass | [S18](evidence/SPRINT_18.md), [matrix](ROUTE_AUTHORIZATION_MATRIX.md); Docker/TLS/secret platform/independent security BLOCKED or HUMAN_REQUIRED |
|19 voice/accessibility | PARTIALLY_COMPLETED | Browser8pass, permission/correction/speech/timeout/expiry/focus/reflow/axe; source208pass; actual speech failure and diagnostic stage pass retained, human protocols/CSV | [S19](evidence/SPRINT_19.md), [voice report](VOICE_ACCESSIBILITY_20261103.md); physical audio/AT/users/acoustic latency HUMAN_REQUIRED |
|20 transactions/catalogue/merchant/scale | PARTIALLY_COMPLETED | Seven new controlled real-SQL cases, late expiry and uncertain receipt fixes;25targeted,215+215 full;128searches/eight workers plus16 concurrent cart workflows zero failures; real local adapter retained | [S20](evidence/SPRINT_20.md), [transactions](TRANSACTION_AND_SCALE_20261103.md), [external specification](MERCHANT_INTEGRATION_SPEC.md); current-source rights/external sandbox BLOCKED |
|21 release/docs/licensing/practical | COMPLETED for available engineering; release HUMAN_REQUIRED | Fresh final218+218, browser8/SDK2/TS/audits, append-only case/coverage/CFG, professor pack/checklist, human register/release/rights decision records; direct-script portability repaired | [S21](evidence/SPRINT_21.md), [release checklist](RELEASE_READINESS_CHECKLIST.md), [license decisions](LICENSING_DECISIONS.md); no license/signoff/production readiness fabricated |

## C. Defect and limitation register

| ID / severity | Component and reproducible trigger | Impact / fix / regression | Remaining risk |
|---|---|---|---|
|DEP-01 High deployment blocker | Compose PUBLIC_ORIGIN localhost while healthcheck requested127.0.0.1; strict Host returns403 | Probe now localhost; actual native Host plus static probe regression `ExtendedSecurityTests.test_compose_probe_matches_strict_host_policy` | Actual Docker execution unavailable |
|AUTH-01 Medium | Expired signed customer's DB session reaches auth helper before local catch | Was400 ambiguous input; now403 at auth boundary. Cookie/origin/expiry/key-rotation regression | Copied admin tokens not centrally revoked by logout; rotate signing key/credential per documented policy |
|HTTP-01 Medium | Transfer-Encoding or ambiguous Content-Length supplied to JSON endpoint | Explicit framing rejection before read; `test_body_limits_duplicate_json_and_framing_rejected` | Actual proxy/TLS deployment still needs review |
|API-01 Low | Authenticated import with variants=None/nonobject row/nonobject price | Was503; strict nested types now400, no publication; `test_malformed_nested_admin_import_is_400_without_publication` | Other invalid source cases retained; data authority/rights external |
|CONFIG-01 Low | Admin file token longer than login's256limit | Startup now validates same32–256 range rather than silently creating unusable UI credential | Operator still needs private storage/rotation |
|TX-01 High correctness | Session valid at initial lock, expires while catalogue/eligibility work proceeds | Added session recheck immediately before add/target write; controlled clock+actual SQL rollback tests assert no mutation | Not a promise to undo a completed commit or every possible timing schedule |
|TX-02 Medium | Quantity commit succeeds but fresh receipt read is unavailable | Now explicitOutcomeUnknown, original-ID reconcile/replay; precommit rollback/postcommit loss/fresh-read-outage regressions | Staging actual network recovery remains necessary |
|EV-01 Medium evidence integrity | Verification/CFG/report/load hardcodedNovember2 filenames | New timestamp/exclusive paths, exact command/SHA/dirty source fingerprint/environment/result/logs; overwrite-protection tests | Source/wheel execution totals are not distinct-method or user-task totals |
|EV-02 Medium | NLU reject-labelled case raises transport/unexpected exception | Previously could count as correct; new and legacy scorers distinguish semantic/service/unexpected outcomes; evaluator tests | Small authored bank still not representative quality |
|TOOL-01 Low | New helper imports with `env -u PYTHONPATH python scripts/verify.py` or CFG script | Direct invocation failed ModuleNotFoundError scripts; conditional sibling imports plus known checkout root for test driver restore direct/module compatibility | Run from repo root, declared dev dependencies still required |
|TEST-01 Low test tooling | New evaluation fixture relative to CWD, then YAML import in core-only wheel tests | Source-relative path and no unnecessary YAML test dependency; initial failed wheel records retained, final wheel passes | Optional dev-only standalone inventory/probe still requires dev extras |
|TEST-02 Low test tooling | Newly authored browser selector “Use reviewed transcript”, actual button “Use this search”; wrong expiry exception expectations | Inspected actual source/public error contract, corrected exact selector/code; original failures retained, assertions not weakened | Selector drift requires future maintenance |
|NLU-Q High release quality | Actual authored bank quantity/control/identifier/negation/unsupported requests |4B26/32,0.6B21/32; failures/slots/timings retained, no prompt tuning/label changes or smaller-model promotion | Separate development improvement and newly frozen representative evaluation needed |
|VOICE-Q Medium acceptance | Fresh synthetic-input smoke fails strict speech-identity assertion | Failure retained; helper records transcript/input hash before assertion; one diagnostic pass, no weakening | Initial transcript/hash not captured, cause not reconstructible; acoustic/user quality pending |
|DOC-01 Low documentation drift | Current193-count/fixed design dates and statements implied all routes require numeric stock count | Current versus historical reports distinguished; exact source contract documented: explicit availability can assert one in core, multiunit requires count; discovery UI conservative | Do not infer current offers from historical unknown availability |

No unresolved critical code defect is asserted from these checks; that is not proof of defect absence. High release gates remain open and no production certification is issued.

## D. Verification summary and reproducibility

| Fresh command / scope | Actual outcome / durable evidence |
|---|---|
| `python scripts/verify.py --postgres --package --audit --coverage --output-dir NEW_DIR` | Final218 source+218 fresh wheel, no service skips; compile/Ruff lint+format/mypy/Bandit/pip/diff/package/audit. [Final RUN](evidence/20261103_S21_engineering/RUN.json), [coverage](evidence/20261103_S21_engineering/COVERAGE.json) |
| `python scripts/test_report.py --output-dir NEW_DIR` | Current218 methods/outcomes/source arrangements/assertions; [record](evidence/20261103_S21_final_cases/TEST_EXECUTION.json), [case document](TEST_CASES.md) |
| `python scripts/cfg_analysis.py --output-dir NEW_DIR` |13 actual-source graphs, three calculations and structural basis rank verified; [CFG](evidence/20261103_S21_cfg/CFG.json), [analysis](CFG_ANALYSIS.md) |
| `python -m unittest tests.test_practical_contracts -v` |4methodsPass, all black-box/path/loop subcase assertions; [run](evidence/20261103_S21_practical/RUN.json) |
| Exact five-case `python -m scripts.run_tests ...` in professor pack |5Pass against owned PostgreSQL; [run](evidence/20261103_S21_professor_ce/RUN.json) |
| `npm run test:browser` against restarted current source fixture server |8Pass; actual UI/backend plus clearly scripted voice/service faults; [run](evidence/20261103_S21_browser/RUN.json) |
| `node tests/manual_historical_browser.mjs http://127.0.0.1:8082 NEW_DIR` after `python scripts/preview.py --port 8082` | Current actual historical-data preview:298 records,11microwave matches,zero known stock/enabled adds,details/admin actual metrics; [real-data run](evidence/20261103_S21_real_catalogue_repro/RUN.json) |
| `npm run test:sdk` |2Pass, actual local SDK→HTTP→SQL; [run](evidence/20261103_S21_sdk/RUN.json) |
| Strict TS command in practical pack |Exit0; static type check, no invented test count; [run](evidence/20261103_S21_ts/RUN.json) |
| `npm audit --omit=optional` |No known vulnerabilities observed; [run](evidence/20261103_S21_node_audit/RUN.json) |
| `python scripts/stress.py --cart-users 16` |Zero failures:128 complete structured searches/eight workers/2000 synthetic variants plus16 concurrent idempotent cart workflows; [load](evidence/20261103_S20_load/LOAD.json) |
| New frozen model evaluator with pinned model/digest |4B26/32,0.6B21/32 quality expectations, no service errors; [reference](evidence/20261103_S17_qwen4b/NLU.json), [challenger](evidence/20261103_S17_qwen06b/NLU.json). Process completion is not qualityPass |
| `PYTHONPATH=. python tests/manual_voice_http.py --output-dir NEW_DIR` |First strict ASR identityFail; diagnostic onePass with actual stages/receipt, both retained; see S19 report |
| `python scripts/deployment_probe.py` |Static config/Host checks; actual Docker absent, container boot NOT RUN; [probe](evidence/20261103_S18_deployment/DEPLOYMENT.json) |

New run records contain exact actual commands, UTC timestamps, base SHA, dirty flag/source fingerprint, platform/Python/runtime versions, outputs/outcomes/warnings. Derived [evidence index](evidence/20261103_S21_complete_index/EVIDENCE_INDEX.json) adds structured counts for earlier browser/SDK logs without rewriting original records. Same-agent reproduction is labelled; no independent assessor was invented. The initial local license-inventory attempt hit sandbox network restrictions; the separate permitted loopback rerun succeeded, and both records remain. Advisory warnings about editable/unpublished local package are retained: it is not PyPI-auditable and is separately source analyzed. Legacy PG test service is not production deployment. Log CPU/RSS scope excludes other processes where stated; neither structured search nor synthetic speech stages are full audible latency.

Historical November2 TEST_EXECUTION/COVERAGE/NLU_HOLDOUT/LOAD/REAL_BROWSER_FINAL JSON is byte-preserved. New baseline reproduces same193 method count and separately measures coverage/load; new32 case NLU bank is not compared as if it were the old12 case distribution. Original model/live-data observations remain dated historical unless explicitly rerun. S21 independently reran the actual298-record historical preview on current code and verified the same counts/details/admin metrics; this remains historical-source metadata, not live inventory. Device/AT/users/Docker/TLS/external platform/source rights/legal acceptance NOT RUN here. Initial failed verification records are linked, not removed.

## E. Human involvement and immediate priorities

[HUMAN_INVOLVEMENT_REQUIRED.md](HUMAN_INVOLVEMENT_REQUIRED.md) has task IDs, sprint, exact limitation/category, prerequisite, human action checklist, expected result, evidence, criteria, risks and status. [CSV template](templates/ACCEPTANCE_RESULTS.csv) supports pseudonymous observations and complete failure/assistance/latency denominators. Protocol preparation is not completed human validation.

Immediate: prepare the professor demo from the pack/checklist, review release scope, install/provide an actual disposable Docker environment and run ENV-DOCKER. Provide authoritative current catalogue access/coverage/SLA plus data/media permission and a sanctioned merchant sandbox before external implementation. Physical Android/iOS/NVDA/microphone/speaker and representative blind/low-vision/voice-language participants must execute the detailed tasks. Appoint staging TLS/secret/backup/monitoring operator and independent security reviewer as needed. Owner/counsel must decide project/voice/runtime/data distribution rights; no convenient license added.

## F. Professor practical pack

[PROFESSOR_PRACTICAL_PACK.md](PROFESSOR_PRACTICAL_PACK.md) is self-contained with project explanation, price partitions/LT-LTE boundaries/three-valued table/cart cause-effect, exact named source tests/commands/fresh outcomes, real money_text/rupees_to_minor graphs, node/edge/decision/region calculations, basis inputs and explicitly NOT RUN handler paths, actual number-word loop cases, current coverage interpretation, fifteen screen-sharing steps, viva bank, complete command prerequisites and What This Demonstration Does Not Prove. [One-page checklist](PROFESSOR_DEMO_CHECKLIST.md) supports live use. Actual professor/participant signoff, acoustic/device/external demonstrations remain unverified; structurally enumerated Decimal exception basis candidates are not claimed naturally executable or run.

## G. Next actions by responsibility

1. **Immediate owner/professor:** reproduce prepared practical commands, record witnessed outcomes/scope, review all open release gates; no production-ready claim.
2. **External access/credentials:** Docker/maintained staging, authorized current-source permissions, real merchant sandbox, DNS/TLS/secret manager and monitoring/backup ownership.
3. **Devices/people:** actual TalkBack/VoiceOver/NVDA/zoom, microphone/noise/accent/onset/comprehension and consented user/relevance trials; record failed attempts and assistance too.
4. **Legal/project owner:** exact distribution/BOM/source ownership and project-license/data/media/Piper/voice notices decision; technical declarations are not legal conclusions.
5. **Further Codex engineering when dependencies arrive:** integrate one sanctioned real external adapter, instrument real acoustic trials with approved hardware, improve NLU only on separate development cases then newly frozen evaluation, tune retrieval only with independent judgments, rerun maintained container/platform/recovery/security tests. No extra source-only test can replace unavailable human/rights/deployment acceptance.

## Git delivery

Ordinary commits: S16 `4d58aa1`, S17 `6fa10f3`, S18 `eecc35a`, S19 `1fc1780`, S20 `8477528`; S21 is the final commit containing this report. Use `git log -7 --oneline` for its exact self-containing SHA. Final remote comparison/push status is reported after the normal push; no force-push/history rewrite. Private datasets/models/environments/secrets remain ignored. A clean tracked worktree does not mean those required private assets are shipped in Git.
