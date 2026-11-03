# Human involvement and external-dependency register — 3 November 2026

This register separates completed engineering from real-world acceptance. No human feedback, device result, deployment success or legal approval is invented. Copy `docs/templates/ACCEPTANCE_RESULTS.csv` to a private run directory; keep consent/identity/credentials separate. Record UTC time, SHA, device/profile, expected/actual outcome, status and redacted evidence path. After actual execution update this register with the evidence link, reviewer and date; elapsed time is not approval.

Allowed statuses: CODEX_COMPLETED, CODEX_PARTIALLY_COMPLETED, HUMAN_REQUIRED, BLOCKED_EXTERNAL_DEPENDENCY, NOT_APPLICABLE. Tasks below are grouped by their principal dependency; a procedure may require more than one category.

## Completed available preparation

**Task ID:** CODEX-ENGINEERING. **Related sprint:**16–21. **Status:** CODEX_COMPLETED for source/SQL/browser/SDK/frozen text measurement tools and procedures only. **Validation:** exact per-sprint records and ADDITIVE_EXECUTION_REPORT. **Why limited:** automated evidence cannot witness people/physical devices/rights. **Human involvement/prerequisites:** developer with declared environment may reproduce. **Procedure:** run scripts/record_run.py around the commands in the practical pack. **Expected result/pass criterion:** measured outcomes match assertions or failures are retained. **Evidence:** timestamped RUN/coverage/cases/model records. **Precautions:** guarded fixtures only, preserve owner data. This does not close any acceptance task below.

## ENV-DOCKER — Clean Compose boot, migrations, health, private secret mounts and durable restart

1. **Task ID:** ENV-DOCKER
2. **Related sprint:** 18
3. **What to validate:** Clean Compose boot, migrations, health, private secret mounts and durable restart
4. **Why Codex cannot fully validate:** No Docker executable/daemon is present; static and native checks cannot prove container behavior.
5. **Exact human involvement / dependency category:** Unavailable execution environment; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Operator with Docker on the intended supported host, disposable directory/volume, maintained image review and private secret storage.

7. **Execution procedure:**

   - [ ] Clone into a new lowercase voicecart directory; create a dedicated git worktree/clone for this drill.
   - [ ] Choose a unique COMPOSE_PROJECT_NAME and free loopback port; do not reuse an owner volume.
   - [ ] Run python scripts/init_secrets.py, docker compose config --quiet and docker compose up --build -d.
   - [ ] Check docker compose ps and logs, GET http://localhost:8080/health, open customer/admin and log in with the private admin file.
   - [ ] Import a licensed/current test source with the documented full snapshot contract or run labelled test fixtures only in a marked disposable drill database.
   - [ ] Perform search/add/quantity/retry; note revision and receipt.
   - [ ] Run docker compose restart backend db; recheck health, catalogue/session/cart/receipt.
   - [ ] Stop with docker compose down; preserve the volume until evidence is reviewed..

8. **Expected result:** Healthy migrations-before-backend, no unexpected503/403 probe failures, same committed receipt/cart after restart, no secrets in logs.
9. **Evidence to collect:** Compose version/config, image digests, ps/logs with credentials redacted, health/status/screenshots, before/after revision/cart/operation IDs.
10. **Pass/fail criteria:** Pass only if all actual boot/import/cart/restart/secret-mount checks succeed; otherwise fail with logs. Static probe alone is not Pass.
11. **Risks/precautions:** Never use down --volumes or overwrite existing secrets/data. Test credentials/offers stay in disposable labelled infrastructure.
12. **Current status:** `BLOCKED_EXTERNAL_DEPENDENCY` — no human result recorded.

## ENV-RECOVERY — Maintained deployment database outage, migration failure, backup/restore and committed-response-loss recovery

1. **Task ID:** ENV-RECOVERY
2. **Related sprint:** 18/20/21
3. **What to validate:** Maintained deployment database outage, migration failure, backup/restore and committed-response-loss recovery
4. **Why Codex cannot fully validate:** Guarded development faults/dump-restore are automated; no owner maintained deployment/backup storage or approved outage window is available.
5. **Exact human involvement / dependency category:** Unavailable deployment access; a responsible human must execute and review the following procedure.
6. **Prerequisites:** DB/operator authorization, isolated staging copy, backup encryption/storage policy and tested restore tooling.

7. **Execution procedure:**

   - [ ] Record healthy source revision/session/cart/operation.
   - [ ] Back up staging using the maintained PostgreSQL pg_dump tool into a private destination; restore into a separate empty staging DB and compare counts/revision/receipt.
   - [ ] Stop only staging DB and check startup/health/action failure, then restart.
   - [ ] Test an invalid NEW migration in a separate clone/empty DB; record rollback, never edit an applied migration.
   - [ ] Use a test proxy to cut the add HTTP response after committed receipt; reconcile original operation ID and verify quantity once.
   - [ ] Record incident/recovery times and sanitize logs..

8. **Expected result:** Explicit unavailable/unknown outcomes, no guessed success/new-ID duplicate, same receipt after restore/restart.
9. **Evidence to collect:** Commands/tool versions, encrypted backup metadata, restore comparison, fault timeline and original-ID reconciliation.
10. **Pass/fail criteria:** Pass only if restore comparison and recovery/idempotency assertions hold; stale/missing receipt or duplicate increment fails.
11. **Risks/precautions:** Never fault a production DB, delete a needed backup or disclose credentials. Agree RPO/RTO before release; code tests do not choose them.
12. **Current status:** `BLOCKED_EXTERNAL_DEPENDENCY` — no human result recorded.

## ACCESS-ANDROID — Android TalkBack and browser microphone lifecycle

1. **Task ID:** ACCESS-ANDROID
2. **Related sprint:** 19
3. **What to validate:** Android TalkBack and browser microphone lifecycle
4. **Why Codex cannot fully validate:** Browser automation cannot hear TalkBack, operate a physical Android permission workflow or assess touch exploration.
5. **Exact human involvement / dependency category:** Physical device; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Android device/version, current supported browser, TalkBack enabled, HTTPS staging origin, approved voice models and headphones if appropriate.

7. **Execution procedure:**

   - [ ] Record OS/browser/TalkBack versions.
   - [ ] Navigate with swipe/touch exploration through search, filters, product details, current-offer add, quantity/remove and help.
   - [ ] Deny microphone once, confirm text fallback, then grant and record/end/review/correct/discard.
   - [ ] Background/resume and revoke permission mid-recording.
   - [ ] Stop/repeat during processing and reconcile uncertain cart using the same ID..

8. **Expected result:** Meaningful labels/order/status/error announcements, no focus trap or unexpected write, correct recoverable lifecycle.
9. **Evidence to collect:** Pseudonymous task sheet, device versions, announcement/focus notes, consented screen recording/screenshots and receipts.
10. **Pass/fail criteria:** Pass each task only when it can be completed with TalkBack and correct cart outcome; inaccessible blocking controls or incorrect mutation fails.
11. **Risks/precautions:** Use staging and non-purchase tasks; obtain consent before recording voices or assistive speech.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## ACCESS-IOS — iOS VoiceOver/Safari input, focus and background resume

1. **Task ID:** ACCESS-IOS
2. **Related sprint:** 19
3. **What to validate:** iOS VoiceOver/Safari input, focus and background resume
4. **Why Codex cannot fully validate:** No physical iOS/VoiceOver session or trusted microphone interaction is available.
5. **Exact human involvement / dependency category:** Physical device; a responsible human must execute and review the following procedure.
6. **Prerequisites:** iPhone/iOS/Safari/VoiceOver versions, HTTPS staging, configured local inference reachable on the protected deployment.

7. **Execution procedure:**

   - [ ] Enable VoiceOver and navigate search/details/cart/admin where authorized.
   - [ ] Test rotor/heading navigation, dialog open/close and focus restoration.
   - [ ] Deny then allow microphone; record/review/edit/discard, background Safari mid-recording, resume, stop and repeat.
   - [ ] Check zoom/magnification and orientation without hidden actions..

8. **Expected result:** All required actions reachable/announced, transcript explicit before submission, no stale result or duplicate cart action.
9. **Evidence to collect:** Versions, announcement transcript notes without private shopping text, screenshots/video only with consent, task/operation outcomes.
10. **Pass/fail criteria:** Pass only for the actual tested iOS/browser/AT combination and all prescribed tasks; log each fail rather than extrapolate.
11. **Risks/precautions:** No real purchases; protect tokens, voices and participant identity.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## ACCESS-NVDA — Windows NVDA with supported browser, keyboard and magnification

1. **Task ID:** ACCESS-NVDA
2. **Related sprint:** 19
3. **What to validate:** Windows NVDA with supported browser, keyboard and magnification
4. **Why Codex cannot fully validate:** Chromium axe/focus assertions do not run NVDA speech or actual Windows zoom/high contrast.
5. **Exact human involvement / dependency category:** Physical/assistive technology; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Windows host, NVDA/version, supported browser/version, keyboard-only user, optional magnifier.

7. **Execution procedure:**

   - [ ] Enable NVDA; use headings/forms/list navigation and Tab/Shift+Tab for search/filter/details/cart/help.
   - [ ] Close dialogs with Escape, verify focus returns to opener and statuses/errors are announced once.
   - [ ] Disable optional shortcuts, test200%/400% browser zoom, high contrast and horizontal layout.
   - [ ] Repeat denial/timeout/empty-state recovery with text only..

8. **Expected result:** No keyboard trap, logical reading order, accessible names/status and usable reflow at tested zoom.
9. **Evidence to collect:** AT/browser versions, focus/announcement notes, task sheet, screenshots and exceptions.
10. **Pass/fail criteria:** Pass per tested configuration only when all required tasks work; any blocked essential action fails.
11. **Risks/precautions:** Do not call automated axe success WCAG certification or simulate a blind participant.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## ACCESS-USERS — Representative blind/low-vision usability and recovery task completion

1. **Task ID:** ACCESS-USERS
2. **Related sprint:** 19/21
3. **What to validate:** Representative blind/low-vision usability and recovery task completion
4. **Why Codex cannot fully validate:** No consented participants are available; modelled or invented feedback would not be evidence.
5. **Exact human involvement / dependency category:** Human participants/judgment; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Project-approved protocol/consent, representative participants, accessible instructions, staging and trained facilitator.

7. **Execution procedure:**

   - [ ] Recruit with voluntary informed consent and pseudonyms; collect only needed access needs.
   - [ ] Pilot instructions.
   - [ ] Give unassisted tasks: find a constrained product, identify cheapest scope, inspect variant, correct transcript, explicitly add/change/remove, recover an error/uncertain operation.
   - [ ] Record start/end, completion, wrong selection/mutation, assistance, recovery, issue severity and optional comments.
   - [ ] Ask neutral follow-ups; permit withdrawal.
   - [ ] Review results with participants before decisions..

8. **Expected result:** Users understand current versus historical facts and can safely complete/recover supported tasks.
9. **Evidence to collect:** ACCEPTANCE_RESULTS.csv, consent stored separately, pseudonymous observations and task/issue summaries.
10. **Pass/fail criteria:** Record measured rates/counts; owner must predeclare acceptance floors before main study. Any unintended mutation is a release blocker requiring investigation.
11. **Risks/precautions:** Do not fabricate feedback, collect diagnoses or publish identifiable voice/video; compensate/obtain ethics approval where applicable.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## VOICE-ACOUSTIC — Complete speech-to-first-meaningful-audible latency, pauses/noise/stop and output comprehension

1. **Task ID:** VOICE-ACOUSTIC
2. **Related sprint:** 19/17
3. **What to validate:** Complete speech-to-first-meaningful-audible latency, pauses/noise/stop and output comprehension
4. **Why Codex cannot fully validate:** Actual synthetic-file ASR/TTS stages are measured; microphone endpoint and acoustic output/onset are not observed.
5. **Exact human involvement / dependency category:** Physical devices; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Calibrated audio loopback/recording setup, agreed microphone/speaker/device, exact pinned models, quiet/noise profiles and consented speech.

7. **Execution procedure:**

   - [ ] Define end-of-utterance and first meaningful response onset before trials; record shared monotonic trace IDs plus consented acoustic reference.
   - [ ] Run separate cold-after-eviction and warm blocks, including failed/time-out trials.
   - [ ] Speak price LT/LTE, quantities, product IDs, negation and pauses; inject reproducible background noise.
   - [ ] End/review/correct, stop during each stage, listen to price/cart confirmation and repeat.
   - [ ] Record ASR/NLU/search/cart/response/onset/full-output timestamps without summing overlapping spans..

8. **Expected result:** Correct transcript/action or safe clarification, intelligible price/ID speech, stop works, truthful full-turn latency.
9. **Evidence to collect:** Device/profile/artifact hashes, complete trial denominator/timestamps, stage spans, consented acoustic traces, failures and comprehension answers.
10. **Pass/fail criteria:** No1.5s pass unless predeclared workload/percentile and meaningful audible onset meet it with sufficient samples; missing onset/timeouts count as failures.
11. **Risks/precautions:** Keep audio private/delete per consent; avoid loud noise, echo/barge-in assumptions and real purchases.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## VOICE-LANGUAGE — Accent, speaking speed, noisy requests and requested Hindi/Hinglish scope

1. **Task ID:** VOICE-LANGUAGE
2. **Related sprint:** 17/19
3. **What to validate:** Accent, speaking speed, noisy requests and requested Hindi/Hinglish scope
4. **Why Codex cannot fully validate:** Authored English text and synthetic English speech do not establish real accent/language quality.
5. **Exact human involvement / dependency category:** Human speech/judgment; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Owner-selected language/script/device/voice profiles, licensed artifacts, consented representative speakers and independently annotated development/evaluation banks.

7. **Execution procedure:**

   - [ ] Freeze a new held-out bank before tuning.
   - [ ] Collect consented natural price/quantity/variant/negation/correction/control requests at normal/slow/fast rates and defined noise.
   - [ ] Independently annotate intent/slots/action permission; resolve ambiguity before running.
   - [ ] Run ASR plus NLU with unchanged safety validation; compare extraction, false proposals and task outcomes.
   - [ ] Keep development data separate and do not relabel after model failures..

8. **Expected result:** Accurate critical slots or safe clarification; no unsupported multilingual claim.
9. **Evidence to collect:** Consent/pseudonym ledger separated from audio, frozen hashes/labels, per-case outcomes/latency/errors and adjudication notes.
10. **Pass/fail criteria:** Owner predeclares critical-error/quality floors; no acceptance from small authored English examples. Any unsafe action proposal investigated.
11. **Risks/precautions:** Verify voice/model terms per language; no silent remote/cloud speech fallback.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## MERCHANT-SANDBOX — One actual external merchant platform product/stock/cart integration

1. **Task ID:** MERCHANT-SANDBOX
2. **Related sprint:** 20
3. **What to validate:** One actual external merchant platform product/stock/cart integration
4. **Why Codex cannot fully validate:** Only local PostgreSQL adapter is implemented; no authorized external test account/token exists.
5. **Exact human involvement / dependency category:** Credentials/external authorization; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Merchant owner consent, supported platform sandbox, scoped product/inventory/cart credentials and rate/webhook documentation.

7. **Execution procedure:**

   - [ ] Follow MERCHANT_INTEGRATION_SPEC.md: record API/version/scopes, map actual product/variant/currency/price/stock/source timestamps, import a bounded sandbox source, refresh changed stock/price, obtain explicit customer authorization, add using platform-supported idempotency, reconcile same ID after forced response loss, verify cancellation/deactivation/webhook ordering and tenant isolation..

8. **Expected result:** Upstream sandbox owns external offers/cart receipts; duplicate/retry cannot double mutate; stale facts cannot authorize add.
9. **Evidence to collect:** Redacted configuration/scopes/API version, actual mappings, source revisions, request/receipt IDs, sandbox conformance results.
10. **Pass/fail criteria:** Pass only a working supported sandbox adapter with authoritative receipt and all conformance checks; fake/local adapter is not external integration.
11. **Risks/precautions:** Least privilege, secrets server-side, no production purchases/webhook exposure without review.
12. **Current status:** `BLOCKED_EXTERNAL_DEPENDENCY` — no human result recorded.

## CATALOGUE-RIGHTS — Current merchant catalogue authority, completeness, freshness and data/media rights

1. **Task ID:** CATALOGUE-RIGHTS
2. **Related sprint:** 20/21
3. **What to validate:** Current merchant catalogue authority, completeness, freshness and data/media rights
4. **Why Codex cannot fully validate:** Historical Amazon metadata supplies neither live inventory nor a documented commercial redistribution grant; no current source authorization is available.
5. **Exact human involvement / dependency category:** Source access/commercial decision; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Owner/merchant data permission, current API/export contract, taxonomy/variant identifiers, currency and price/stock SLA.

7. **Execution procedure:**

   - [ ] Obtain written source/use/distribution permission.
   - [ ] Record source owner, supported fields/variants/currencies, completeness and refresh/expiry SLA.
   - [ ] Validate real prices in original currency, current stock and source revisions against authority; preserve unknown facts.
   - [ ] Import via full-snapshot CAS; demonstrate changed offer blocks stale add, missing stock blocks action and partial coverage limits minimum..

8. **Expected result:** Factual current actionable offers only when independently supported; no fabricated INR conversion/stock.
9. **Evidence to collect:** Written permission stored privately, schema mapping, source timestamps/hashes, validation/quality report and stale/retry outcomes.
10. **Pass/fail criteria:** Pass only when rights and current facts/coverage are documented; unknown rights/freshness remain blocked.
11. **Risks/precautions:** Do not redistribute raw Amazon records/media or assert live Amazon integration.
12. **Current status:** `BLOCKED_EXTERNAL_DEPENDENCY` — no human result recorded.

## DEPLOY-TLS — Production DNS/TLS reverse proxy, Secure cookies, secret manager and private inference/DB

1. **Task ID:** DEPLOY-TLS
2. **Related sprint:** 18/21
3. **What to validate:** Production DNS/TLS reverse proxy, Secure cookies, secret manager and private inference/DB
4. **Why Codex cannot fully validate:** No authorized domain/certificate/cloud account/secret manager is provided.
5. **Exact human involvement / dependency category:** Credentials/operator authorization; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Operator-owned staging domain/hosting/certificates, fixed public origin, private network, backup/monitoring ownership.

7. **Execution procedure:**

   - [ ] Deploy reviewed maintained images on staging.
   - [ ] Configure TLS termination/fixed PUBLIC_ORIGIN and private database/inference routes; verify no wildcard CORS or forwarded-host trust.
   - [ ] Check secure cookie behavior in actual browser, cross-origin/Host denial, body/time/rate limits, secret manager mounts/rotation and no tokens in logs/browser bundles.
   - [ ] Run restore/health/restart drill before exposure..

8. **Expected result:** HTTPS-only remote access, correct capability scope, protected services and operable recovery.
9. **Evidence to collect:** TLS chain/config scans, redacted proxy/network config, cookie/network checks, secret rotation/restore record and accountable operator.
10. **Pass/fail criteria:** Pass only actual staging network/TLS/security behavior; static headers or local HTTP tests are insufficient.
11. **Risks/precautions:** Never publish inference/database ports or put admin keys in storefront JS; no production changes without owner authorization.
12. **Current status:** `BLOCKED_EXTERNAL_DEPENDENCY` — no human result recorded.

## OPS-MONITOR — Monitoring, incident response, retention and backup ownership

1. **Task ID:** OPS-MONITOR
2. **Related sprint:** 18/21
3. **What to validate:** Monitoring, incident response, retention and backup ownership
4. **Why Codex cannot fully validate:** Local event/health tests cannot appoint operators or verify their ongoing alert response.
5. **Exact human involvement / dependency category:** External operational ownership; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Named owner/on-call route, staging alert destination explicitly authorized, retention/backup and recovery objectives.

7. **Execution procedure:**

   - [ ] Choose thresholds/workload/RPO/RTO with owner.
   - [ ] Configure minimal aggregate health/errors/latency alerts without raw query/audio/token capture.
   - [ ] Trigger a staging incident and confirm operator receives/acknowledges it; reconcile committed operations.
   - [ ] Run retention cleanup and inspect app records plus backup/WAL retention policy.
   - [ ] Record restart/restore times and incident runbook..

8. **Expected result:** Actionable alerts and accountable recovery without private-content leakage.
9. **Evidence to collect:** Owner signoff, authorized alert drill/timeline, retention configuration and backup restore/incident logs.
10. **Pass/fail criteria:** Pass only when a responsible operator demonstrates response and approved retention/recovery objectives; thresholds are not invented by Codex.
11. **Risks/precautions:** No unsolicited external notifications; use authorized destinations and protect backups/diagnostics.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## SECURITY-REVIEW — Independent threat modelling/penetration assessment of intended deployment

1. **Task ID:** SECURITY-REVIEW
2. **Related sprint:** 18/21
3. **What to validate:** Independent threat modelling/penetration assessment of intended deployment
4. **Why Codex cannot fully validate:** Same-agent tests/scans are not an independent assessor and cannot certify actual remote infrastructure.
5. **Exact human involvement / dependency category:** Independent assessment; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Authorized qualified reviewer, written scope/staging targets, test credentials/roles, incident contacts and non-destructive rules.

7. **Execution procedure:**

   - [ ] Review route matrix/tenant/BFF boundaries and code; test same-origin/CSRF/Host/cookie/session/revocation, admin import, limits, proxies, secrets, dependencies and uncertain outcomes on scoped staging.
   - [ ] Record reproducible findings with severity; fix/retest before acceptance..

8. **Expected result:** No unresolved critical/high findings; residual risks and scope explicitly accepted by owner.
9. **Evidence to collect:** Signed scope, redacted findings/reproductions, remediation/test evidence and reviewer signoff.
10. **Pass/fail criteria:** Reviewer-defined tests pass and material findings resolved/accepted; automated green suite is not certification.
11. **Risks/precautions:** No unsanctioned scanning, production faults or secret disclosure.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## LEGAL-DISTRIBUTION — Project license, Piper GPL, model/voice/native notices, dataset/media distribution and intended use

1. **Task ID:** LEGAL-DISTRIBUTION
2. **Related sprint:** 21
3. **What to validate:** Project license, Piper GPL, model/voice/native notices, dataset/media distribution and intended use
4. **Why Codex cannot fully validate:** Technical license declarations cannot establish legal advice, source ownership or commercial permission.
5. **Exact human involvement / dependency category:** Legal/commercial/owner decision; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Project owner and qualified counsel where needed, intended distribution/use/bundling model and exact bill of materials.

7. **Execution procedure:**

   - [ ] Read LICENSING_DECISIONS.md and installed/pinned license texts.
   - [ ] Inventory actually distributed core/optional/runtime/native/container/model/voice/data assets.
   - [ ] Resolve Amazon/third-party media permission and Piper/GPL source/notice/distribution approach for the intended delivery.
   - [ ] Check contributors/source ownership; choose project license only by explicit owner decision.
   - [ ] Record artifact/version/text/hash, obligations, approvals and blocked uses..

8. **Expected result:** Documented lawful intended-use/distribution decision with required notices/source and no unsupported rights claim.
9. **Evidence to collect:** Owner/counsel decision record, notices/source offer where applicable, written source permissions and exact artifact inventory.
10. **Pass/fail criteria:** No commercial/redistribution release while material rights/obligations are unresolved; installed/public-download status is not permission.
11. **Risks/precautions:** Do not invent MIT/project license or blanket commercial clearance; keep legal correspondence private.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## RELEVANCE-JUDGMENT — Representative relevance/cheapest-scope ranking quality and presentation comprehension

1. **Task ID:** RELEVANCE-JUDGMENT
2. **Related sprint:** 17/20/21
3. **What to validate:** Representative relevance/cheapest-scope ranking quality and presentation comprehension
4. **Why Codex cannot fully validate:** Exact scoring/minimum mechanisms cannot prove universally best human product relevance; no judged representative queries supplied.
5. **Exact human involvement / dependency category:** Human product judgment; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Owner-approved real catalogue/query tasks, independent judges/participants, separate development/holdout partitions and error-cost priorities.

7. **Execution procedure:**

   - [ ] Freeze query/constraint/price-scope tasks and candidate judgments before tuning.
   - [ ] Have judges label variant relevance/hard constraints and understand minimum claims; adjudicate disagreements.
   - [ ] Evaluate recall/nDCG/task completion and price-role comprehension, retaining no-match/unknown/partial cases.
   - [ ] Tune only on development; test a new holdout with full latency/candidate coverage..

8. **Expected result:** Relevant results respect hard constraints; cheap accessories do not become an unsupported global answer.
9. **Evidence to collect:** Frozen query/source hashes, anonymized judgments/adjudication, metric definition/results and failed cases.
10. **Pass/fail criteria:** Owner defines quality floors before evaluation; mechanism tests or32 authored NLU cases do not satisfy this gate.
11. **Risks/precautions:** Avoid leaking raw personal searches or optimizing labels to match existing ranking.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## OWNER-ACCEPTANCE — Practical examination and engineering/release acceptance signoff

1. **Task ID:** OWNER-ACCEPTANCE
2. **Related sprint:** 21
3. **What to validate:** Practical examination and engineering/release acceptance signoff
4. **Why Codex cannot fully validate:** Codex can prepare/run the pack but cannot act as the professor, project owner or actual users.
5. **Exact human involvement / dependency category:** Project/professor decision; a responsible human must execute and review the following procedure.
6. **Prerequisites:** Current checkout/environment, PROFESSOR_PRACTICAL_PACK, checklist and reviewed evidence/human register.

7. **Execution procedure:**

   - [ ] Follow the fifteen-step professor sequence, rerun named tests/CFG/coverage safely, challenge expected outcomes/path feasibility and inspect failed historical runs.
   - [ ] Review each unresolved register/release-checklist item, record accepted scope and explicit deferrals.
   - [ ] Sign only the exact engineering demonstration/profile actually observed..

8. **Expected result:** Accurate demonstration without production/accessibility/latency/license overclaim.
9. **Evidence to collect:** Completed checklist, questions/answers, witnessed commands/results, signed scope/deferrals and date/SHA.
10. **Pass/fail criteria:** Pass professor demonstration only on actual witnessed correct explanations/runs; production acceptance remains conditional on critical gates.
11. **Risks/precautions:** Do not present prepared text as human signoff or delete negative evidence.
12. **Current status:** `HUMAN_REQUIRED` — no human result recorded.

## Result calculations and submission

Per defined task/profile, task completion=completed/attempted; wrong selection and wrong mutation each retain numerator/denominator; recovery success=recovered/recovery attempts. Record assistance and task time per attempt, including failures/timeouts; missing acoustic onset is not a fast successful sample. Do not pool different language/device/catalogue profiles. Predeclare acceptance floors with owner/professor and investigate any unintended mutation. Return redacted CSV and evidence to the repository only with participant/privacy approval; raw recordings, secrets, legal letters and identifying consent stay private. No human task becomes CODEX_COMPLETED merely because its protocol was written.
