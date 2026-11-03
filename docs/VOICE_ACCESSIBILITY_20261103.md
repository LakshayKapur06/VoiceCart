# Voice and accessibility validation — 3 November 2026

Actual browser suite now has8 passing tests: existing customer/admin/cart/reload/keyboard/dialog/mobile/axe/review/cancel plus new permission-denial/text-fallback/focus-return, transcript-correction/submitted-text, speech-failure/status, expiry and interpreter-timeout recovery. Tests run the actual native backend; permission/audio/service faults are explicitly scripted or intercepted to reach exact UI branches, not hardware/model-quality evidence. axe found zero violations in the checked states; this is not WCAG/AT/user acceptance.320px reflow and focus return are checked; real browser200%/400% zoom, magnification and screen-reader speech remain manual.

[Eight-test run](evidence/20261103_S19_browser/RUN.json) follows an initial seven-pass/one-fail run caused by a newly authored test's incorrect button label; selector corrected to actual “Use this search”, assertions preserved and initial failure retained. Browser fake media/ASR never becomes an unlabelled production model adapter.

## Actual speech-stage observations

A fresh actual Piper synthetic-input→CPU Whisper HTTP smoke failed its strict expected-word check before any cart selection. [Failure](evidence/20261103_S19_voice/RUN.json) retained; the old helper did not persist that failed transcript, so its exact recognition error cannot be reconstructed. The helper now writes observed transcript/input PCM SHA256/time before asserting identity, and uses new evidence paths instead of overwriting November2.

One diagnostic run with that observability passed: actual transcript “backpack.”; ASR HTTP0.50193s, TTS HTTP1.26128s,184320 frames at22050Hz, duplicate same-ID add did not increment twice. [Observation](evidence/20261103_S19_voice_diagnostic/ASR_OBSERVATION.json), [complete boundary](evidence/20261103_S19_voice_diagnostic/VOICE_HTTP.json). Synthetic PCM can differ between synthesis runs and the first hash was not preserved; no causal diagnosis or stable acoustic-quality conclusion follows from one failure/one pass. No assertion was weakened and no repeated search-for-green campaign was used.

The successful path uses an explicit deterministic selection after reviewed ASR, then authoritative SQL receipt and actual Piper WAV; it does not include NLU or physical capture/playback. Individual stages cannot substitute for end-of-speech→first meaningful audible response. No total acoustic latency, human comprehension or1.5s success is claimed. Separate actual text NLU observations are in NLU_EVALUATION_20261103.md.

## Execution and human evidence

`PYTHONPATH=. python tests/manual_voice_http.py --output-dir NEW_DIRECTORY` requires the exact privately provisioned artifacts/verified-hashes.json and voice extras; it owns guarded SQL and refuses fabricated source outcomes. Failure is meaningful and should remain in evidence. Full source/static/security regression passed separately.

[Human register](HUMAN_INVOLVEMENT_REQUIRED.md) provides separate Android/TalkBack, iOS/VoiceOver, NVDA/keyboard/zoom, real acoustic/noise/accent/language, representative blind/low-vision usability and relevance protocols. Each includes prerequisites, steps, observations, criteria and precautions; no results/signoff are simulated. Use the private-copy [CSV template](templates/ACCEPTANCE_RESULTS.csv) to retain attempts, failures, selection/mutation errors, recovery, assistance, task time and actual acoustic onset. Owner must predeclare acceptance thresholds/profile before user trials.
