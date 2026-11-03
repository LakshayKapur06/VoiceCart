# S16 additive audit and coverage review — 3 November 2026

Baseline main `9973045`, clean checkout, fetched remote0 ahead/0 behind. No AGENTS.md or user changes. This is a fresh same-agent reproduction, not an independent third-party certification. All30 production Python modules,23 existing test modules, entry points, packaged web assets, six migrations, SDK,14 current scripts, Compose/Dockerfile/configuration and documentation/evidence inventory were reviewed structurally and at the relevant authority boundaries. Existing modules remain the baseline; no rewrite or new runtime framework is justified.

## Fresh reproduction and historical comparison

[Baseline RUN](evidence/20261103_S16_baseline/RUN.json) records193 source+193 fresh-wheel passes, no failures/errors/skips, actual guarded PostgreSQL/pgvector/empty-startup/restore, compile/Ruff/mypy/Bandit/pip/advisory checks. November2 coverage JSON is preserved byte-for-byte. New baseline coverage is separately recorded beside RUN. [Browser](evidence/20261103_S16_browser/RUN.json):5 passes; [SDK](evidence/20261103_S16_sdk/RUN.json):2 passes; [TS](evidence/20261103_S16_typescript/RUN.json):exit0. [Load](evidence/20261103_S16_load/LOAD.json):128 searches/eight workers/2000 synthetic TEST-only variants, zero failures, mean0.1915s, exploratory empiricalP95 0.2379s; no P99/production inference. [CFG](evidence/20261103_S16_cfg/CFG.json):13 actual-source functions, three calculations agree. The old NLU11/12 and real-data browser evidence remain historical, not automatically reproduced by these unit/load runs. Separate S17/S19 runs address available model/browser boundaries.

Installed-wheel warning that a source distribution cannot be uninstalled outside the temporary environment is retained; the explicit imported-path assertion still proves the tested wheel was installed in the fresh environment. pip-audit cannot audit this unpublished local package against PyPI; source analysis and upstream installed dependencies are separate checks. Legacy bundled PG16.2/pgvector is disposable test infrastructure only. Docker is unavailable. No owner DB was used.

## Confirmed findings and disposition

| ID | Severity / finding | Disposition |
|---|---|---|
| EV-01 | Medium: verify/test-report/CFG/load scripts hardcoded November2 evidence paths, so a fresh invocation could rewrite historical evidence | FixedS16: timestamped default directories, explicit output directory, exclusive JSON writes, run SHA/source fingerprint/command/result/log metadata. Existing dated JSON retained. |
| EV-02 | Medium: NLU benchmark counts any exception as correct for reject cases; service outages could masquerade as safe semantic rejection | S17 fixes scorer/transport distinction and expanded frozen labels; no production validator relaxation. |
| DEP-01 | High deployment blocker: Compose health probe uses127.0.0.1 Host while configured PUBLIC_ORIGIN requireslocalhost; strict Host check rejects it | S18 fixes probe origin and adds real boundary/static regression. Container boot still needs Docker. |
| API-01 | Low: admin import preprocessing assumes every variants element/price is an object; malformed nested types can return503 instead of input400 | S18 adds shape validation and regression. No partial publication occurs. |
| OPS-01 | Medium: quantity adjustment fresh receipt lookup after commit can leak a raw DB error instead of explicit OutcomeUnknown | S20 covers commit-response interruption and standardizes uncertainty. Existing add path already reconciles. |
| DOC-01 | Low: test-report generated design date/failure pointer fixed toNovember2; current run record lacks structured browser/SDK counts | S16–21 evidence/report corrections; historical design/outcome still explicitly dated. |

No demonstrably unused production dependency was found: psycopg is runtime; speech extras optional; Node, graph, coverage and YAML tools are development-only. Similar core/cart-adjustment code reflects distinct increment versus target-state receipt contracts; unifying them without preserving retry identity/lock order would add risk. Historical model-smoke and contract stubs are labelled, useful, and retained. Full historical tests remain. No authoritative facts are cached or invented. stdout request logging is intentionally disabled; actual numeric events are environment-scoped.

## Coverage triage

November2 statements3210/3968 (80.90%), branches918/1332 (68.92%),62 exclusions. Percentages do not decide test priority. Fresh reports retain missing lines/arcs for exact follow-up.

| Gap class | Representative source branches | Action / remaining evidence |
|---|---|---|
| Important behavior | price strict/inclusive plus missing/invalid values; rejected facts dominate unknown; money_text INR-with/without-paise/nonINR | Four named practical contract tests addedS16 and freshly executed. These are observable contracts, not implementation mirrors. |
| Error handling | quantity receipt verification after commit; malformed admin nested input; startup/migration/model outage | S18/S20 targeted real-boundary and controlled failure tests; controlled faults distinguished from actual outage acceptance. |
| Defensive validation | capability scope/expiry/malformed token, content-type/oversize/duplicate JSON, invalid config | S18 route/security matrix and negative HTTP tests. |
| Legitimate business scenarios | concurrent target quantities, deactivation/revision after search, expired sessions, stock limits and same-ID changed payload | Existing cart tests plus S20 additions under guarded SQL. |
| Environment dependent | actual TLS/proxy secret mounts, audio-device drain/onset, container/GPU paths | Not inferred from coverage; human/environment register provides procedures. |
| Explicit exclusions / implicit paths |62 coverage exclusions, arbitrary external-call exceptions, nested CFG comprehension/callable frames | Exclusions remain visible; no assertion of unreachable code or complete path coverage. Implicit fault models are outside CFG convention. |

Money_text's three feasible returns receive exact assertion tests. Parser loops cover numeric bypass, pre-loop empty failure, one/two/typical/large words and early invalid sequence; every structural basis is not asserted executable. Coverage improvements after new behavior tests are measurements, never a completion target. See the final practical pack for exact inputs, source paths, commands and path limits.

## Final closure / remaining gates

S16–S21 records and the additive report supersede planned dispositions above with actual results. Final218 source+218 fresh wheel,8 browser/2SDK, strictTS/static/security/advisory, per-method cases/CFG and controlled load pass. Important error/expiry/framing/import/uncertain-outcome gaps receive meaningful regressions. Model/speech quality failures remain explicitly reported. Direct-script import compatibility found late in documentation review was restored and tested without PYTHONPATH; evidence summary counts/overwrite protection have executable tests. Existing single-unit qualification accepts affirmative available=true with unknown numeric count (asserts at least one); multiunit requires known enough count and discovery UI is conservative. Historical source availability remains unknown, so this is not fabricated inventory. No production/user/legal acceptance inferred.
