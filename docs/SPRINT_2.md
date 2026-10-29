> Historical sprint contract/evidence. Current runnable behavior and release limitations are in README and HANDOFF.

# Sprint 2: audio contracts and simulated integration

The audit of `83ea1bb` found that the original 20 audio tests passed despite broken cancellation, premature playback completion, fake fallback bytes and invalid latency samples passing the target. The corrected increment provides a tested protocol foundation for **A-01–A-03**. **Sprint 2 device feasibility is not yet signed off.** Actual ASR/TTS adapters, microphone/speaker measurements and accessible host controls remain unverified.

## Corrected behavior

| Area | Enforced behavior |
|---|---|
| Turn boundaries | Accept a nonblank final once, only for a live listening/processing turn. Partial events cannot authorize actions. Stop, pause, terminal recognition events and completion retire the turn. IDs cannot be reused within a controller session. Stale callbacks leave state/status untouched. |
| Capture | With an input port bound, listening starts capture; manual/VAD endpoint and pipeline execution stop it before ASR. Capture is gated during processing, speaking, pause and failure. IDLE/STOPPED do not automatically restart physical capture: a new explicit turn does. |
| Playback | The pipeline requires an output port, streams chunks to it and stays SPEAKING until that turn's drain completes. Returned chunks are diagnostics of audio already submitted, not instructions to play it a second time. |
| Cancellation | Stop/pause invalidate the active turn and call device stop/flush. Late ASR/TTS results and drain completions cannot resume cancelled work or finish a newer turn. A device stop exception is reported as failure, keeps capture gated and requires recovery. Stop always reports `action_undone=False`. |
| Repeat | Returns only the last completed response string for host playback. Interrupted/empty responses are not promoted. Repeat never invokes ASR, search or mutations. Host replay must also gate capture and honor stop. |
| Recovery | ASR, template, empty/failed TTS and output errors produce explicit assistive recovery and failure telemetry. A fast optional status sink connects the status channel to a host; delivery errors update channel health. Losing both response channels retires the turn and marks FAILED. The in-memory status buffer alone is not a screen reader. |
| Fallback | The fake `RIFF-MOCK...` constant is removed. A host may inject a verified spoken prompt through `CachedSpeechPrompt`; the WAV loader requires complete, nonempty 16-bit PCM. TTS failure flushes its pending stream before this prompt. It returns the recovery text, never the original success text. Without an asset, recovery is assistive-only. A broken output device cannot be repaired by playing another asset on it. |
| Latency | Missing timestamps are `None`. Missing, nonfinite, boolean, negative or reversed timing never becomes a successful zero-latency sample. Only an output adapter's measured onset is used; the pipeline never substitutes enqueue time. All provided stages must be ordered in the same monotonic clock. |
| Benchmark | Record one snapshot per turn ID, insulated from subsequent caller mutation. Success requires valid utterance-end/onset timing and no failure/timeout/cancellation. Cancellation, timeout and other failure counts are disjoint (in that precedence); missing audio is failure. All turns remain in the target denominator; median and nearest-rank P95 use successful samples only, and are `None` when none exist. |

`Transcript.can_authorize_action` describes the event's final/nonblank shape. Callers must also use the controller's turn acceptance result. This is not cart authorization or transactional idempotency; those belong to future stories. `template_fn` only renders already verified facts and must not perform business mutations. No cart/payment behavior is implemented here.

## Adapter contract and migration

The prior mock-only playback API could not enforce its own guarantees. Integrations must now:

- Pass an `AudioOutputProtocol` into `AudioPipelineSlice(asr, tts, controller, output)`; a controller owns one output. Optionally bind `audio_input` and `status_sink` when constructing the controller.
- Implement short, nonblocking `begin_playback(turn_id)`, `play_chunk`, and `stop_playback` calls. Input start/stop and status delivery must likewise enqueue quickly. Backend buffering must be bounded by the adapter.
- Implement interruptible `drain(turn_id)` that waits for playback completion/stop and returns measured audible onset in the trace clock, or `None` if unavailable. A cancelled old drain must never alter a newer stream. Real acoustic calibration is an outstanding device test.
- Supply `turn_id` to `start_speaking` and `finish_speaking`. The latter returns `(completed, onset)`; stale completion returns `(False, None)`. Completion requires at least one submitted chunk and a drained output.
- Use unique turn IDs, resume explicitly after pause/failure recovery, and supply explicit ASR/TTS/drain deadlines. Pipeline cancellation fences downstream output, but cannot forcibly interrupt a backend's blocking inference call. Adapter `TimeoutError` becomes a timed-out trace.
- Supply a fresh trace for each turn and annotate actual physical `t_speech_end` using the same monotonic clock. No physical utterance-end detector is implemented by the pipeline.
- Inject any fallback speech asset after checking its text, intelligibility and distribution terms. PCM/WAV format validation does not prove that a recording contains speech.

The diagnostic status/transcript data remains in session memory; this module creates no persistent audio or transcript logs. The host still owns session lifetime and its retention policy (D12).

## Artifact provenance

The old `PINNED_*` fixtures were unverified candidate descriptions and conflated runtime and voice licenses. They are now separate `REFERENCE_*` candidates with unverified versions, no fabricated digest and unknown commercial eligibility. `ArtifactMetadata.is_pinned` only checks that a URL and SHA-256 were declared; an adapter must actually verify downloaded bytes before use.

Primary sources checked on 2026-10-27:

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp) declares MIT. Its runtime and a selected model file must each be identified and tested before promotion.
- [OHF Piper](https://github.com/OHF-Voice/piper1-gpl) declares GPL-3.0; it must not be labeled MIT simply because a voice repository has that label.
- The [LJ medium voice card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/medium/MODEL_CARD) specifies 22,050 Hz and a public-domain dataset. The dataset statement does not establish terms for the runtime or every distributed artifact.

No runtime/model/voice is bundled or commercially cleared by these fixture records. Exact versions, configuration, source revisions, hashes and applicable terms must be recorded with real adapter results before distribution (D02/D05).

## Executable example

This example demonstrates contract gating without claiming device playback:

    >>> from voicecart.audio import HalfDuplexTurnController, Transcript, TranscriptKind, TurnState
    >>> controller = HalfDuplexTurnController()
    >>> controller.state == TurnState.IDLE
    True
    >>> controller.start_listening("turn-example-1")
    >>> controller.is_capture_gated
    False
    >>> controller.process_transcript(Transcript(TranscriptKind.PARTIAL, "find bag", "turn-example-1"))
    False
    >>> controller.process_transcript(Transcript(TranscriptKind.FINAL, "find bag under 2000 rupees", "turn-example-1"))
    True
    >>> controller.is_capture_gated
    True
    >>> controller.process_transcript(Transcript(TranscriptKind.FINAL, "find bag", "turn-example-1"))
    False
    >>> outcome = controller.stop()
    >>> outcome.action_undone
    False
    >>> outcome.stopped_playback  # No output port was playing in this example.
    False
    >>> controller.state == TurnState.STOPPED
    True
    >>> controller.current_turn_id is None
    True
    >>> controller.process_transcript(Transcript(TranscriptKind.FINAL, "add bag", "turn-example-1"))
    False

## Verification and readiness

On CPython 3.12.14 the corrected suite contains **44 audio tests and 98 total tests**. Coverage includes final/partial/blank/stale events, cancellation during ASR/synthesis/enqueue/drain, an old drain returning during a newer playback, failed device stop, capture failure, assistive delivery failure, partial-stream fallback, output failure, missing onset, malformed WAV and full-denominator latency statistics. Scripted PCM keys now run through ASR → template → TTS → output, checking preservation of price operators, rupee values, SKU and negation. These are protocol regressions with synthetic PCM, **not a speech-comprehension benchmark**.

Verification on 2026-10-27 passed for the source suite, the site-packages-disabled suite, both sprint doctests, compilation, Ruff lint/format and diff checks. A fresh wheel was built with setuptools 84.1.0, checked for the current audio source and zero mandatory runtime dependencies, installed without network/dependencies into a clean Python 3.12 environment, and passed the same 98-test suite. Relative documentation links are valid; `ARCHITECTURE.md` and the Sprint 1 implementation remain unchanged. Python 3.11 and a static type checker were not exercised.

Run from the repository root using supported Python >=3.11:

```sh
python -m unittest tests/test_audio.py -v
python -m unittest discover -s tests -v
python -S -m unittest discover -s tests -q
python -m doctest docs/SPRINT_1.md docs/SPRINT_2.md
python -m compileall -q voicecart tests
ruff check .
ruff format --check .
```

Readiness verdict: the audited logic defects are fixed and the protocol foundation is suitable for continued development. **A-01–A-03 remain in progress**, with these acceptance gates outstanding:

| Gate | Evidence still needed |
|---|---|
| A-01 / D11 | Real keyboard/assistive controls and screen-reader status delivery, echo/capture behavior, and representative blind/low-vision user recovery tasks. |
| A-02 / D01/D02/D05 | Real local ASR/TTS/VAD adapters; identified artifacts and terms; recorded utterances testing critical words, pauses, prices, SKUs and negation; an intelligible emergency speech asset; actual missing-device and offline recovery. |
| A-03 / D06/D13 | Annotated physical utterance end and measured meaningful audible onset, including calibration, cold/warm runs, resources, timeout/no-audio counts and device/language profiles. No under-1.5-second result is claimed. |

A text-only Sprint 3 experiment may use these typed seams independently. Full voice integration and an unconditional Sprint 2 completion claim require the gates above. No Sprint 3 implementation is included in this fix.
