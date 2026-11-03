# VoiceCart practical — quick checklist

Use with PROFESSOR_PRACTICAL_PACK.md, from lowercase repo root/activated declared venv. Date/SHA:________ Professor/witness:________ Actual outcome/evidence:________

- [ ] README introduction: speech/text search→reviewed selection→verified local cart. Historical metadata is not live inventory.
- [ ] `git rev-parse HEAD`; show current evidence/known limitations and human register.
- [ ] Open tests/test_practical_contracts.py and run `python -m unittest tests.test_practical_contracts -v` (four methods).
- [ ] Explain partitions: valid below/equal/above, invalid negative/float/bool, legitimate unknown price.
- [ ] Explain9999/10000/10001 with LT versus LTE, integer minor units.
- [ ] Explain qualify decision table: known rejection dominates unknown; no invented facts.
- [ ] Show cause-effect graph: session/final intent/eligible offer/ID/turn plus committed receipt.
- [ ] Run named cause-effect methods with `python -m scripts.run_tests ...` from pack; guard owns SQL, never owner data.
- [ ] Open application.py:money_text and nlu.py:rupees_to_minor, verify current lines.
- [ ] `python scripts/cfg_analysis.py`; show actual nodes/edges/decisions.
- [ ] Money graph:N9,E10,P1,D2,V3. Parser:N14,E18,P1,D5,V6. Explain counting convention and actual planar faces.
- [ ] Map concrete basis inputs; explicitly identify two Decimal handler paths NOT RUN/natural feasibility unestablished.
- [ ] Show number-loop bypass/empty guard/one/two/typical/large/invalid cases.
- [ ] `python scripts/verify.py --postgres --package --audit --coverage`; open `python -m coverage report` and missing arcs/exclusions. A full run needs time/local services/network dependencies.
- [ ] Explain what coverage/tests do not prove; do not certify devices/users/security/rights/production/1.5s.

Optional prior setup: `npm ci`, `npx playwright install chromium`; `python scripts/browser_test_server.py` in a separate terminal; then browser/SDK/TS commands from pack. Stop only the fixture server with Ctrl+C. Real voice needs separately verified assets and may fail; retain actual observations. Use a new output directory for recorded reruns, never rewrite November2 evidence.

Final decision/failed steps/action owners:________________________________________________
