# Sprint 2: early audio feasibility

This increment implements **A-01–A-03** from [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md). It delivers the half-duplex turn controller, audio event contracts, ASR → verified template → TTS slice, pinned speech artifact metadata, critical-word comprehension fixtures, and audible onset latency telemetry with visible failure accounting.

## Implemented surface

| File | Responsibility |
|---|---|
| `voicecart/audio.py` | Turn state machine, half-duplex microphone gating, accessible nonvisual controls (`stop`, `repeat`, `end_turn`, `pause`, `resume`), partial/final transcript authorization boundaries, assistive status messages, ASR/TTS protocols, pipeline slice with cached audio fallback, and audible onset latency telemetry. |
| `tests/fixtures_audio.py` | Pinned model metadata (`whisper.cpp`, `OHF Piper`), comprehension fixtures for rupee amounts, SKUs, and negation, and mock ASR/TTS/VAD devices. |
| `tests/test_audio.py` | Unit tests for turn boundaries, half-duplex gating, partial transcript non-authorization, stop/repeat controls, cached fallback on TTS failure, dual-channel failure, critical-word comprehension, and full-denominator latency benchmarks. |

## Supported contracts and assumptions

- **Half-Duplex Microphone Gating:** To avoid the assistant's own speech confirmation being recorded and transcribed as a new user command, the controller enters `SPEAKING` state and gates (mutes) microphone capture during playback. When playback concludes or is stopped, capture is un-gated and the session returns to `IDLE`.
- **Transcript Authorization Invariant:** A transcript object exposes `can_authorize_action`. This property is strictly `False` for `PARTIAL`, `SILENCE_TIMEOUT`, `NO_SPEECH`, `ERROR`, or empty transcripts. Downstream mutation layers must reject any transcript where `can_authorize_action` is false.
- **Stale Event Isolation:** Every turn generates a unique `turn_id`. Any speech event or late callback bearing an expired or mismatched turn ID is rejected immediately without changing turn state or authorizing actions.
- **Accessible Stop Control:** The `stop()` control halts speech playback immediately and transitions to `STOPPED`. It explicitly reports `action_undone=False`: stopping playback does not and cannot retroactively roll back an already committed cart transaction.
- **Repeat Control:** `repeat()` replays the last verified response text or audio. It never triggers or re-executes an action or transaction.
- **Dual-Channel Accessibility & Failure:** If neural TTS fails, the pipeline immediately falls back to a cached emergency audio prompt (`CACHED_FALLBACK_AUDIO`) alongside an assistive status text message. If both audio and assistive channels fail, the session explicitly reports `is_session_usable() == False` and transitions to `FAILED`.
- **Audible Onset Latency:** Latency is measured from physical utterance end (`t_speech_end`) to audible playback onset (`t_audible_onset`), accounting for VAD endpoint silence delay, ASR transcription, template rendering, and TTS first-chunk generation.
- **Full-Denominator Failure Accounting:** The benchmark recorder retains failed turns and timeouts in the denominator when calculating the `<1.5s` target pass rate. Failures are never silently omitted to inflate performance.

## Executable example

This doctest demonstrates turn state progression, half-duplex capture gating, and safe stop controls:

    >>> from voicecart.audio import HalfDuplexTurnController, Transcript, TranscriptKind, TurnState
    >>> controller = HalfDuplexTurnController()
    >>> controller.state == TurnState.IDLE
    True
    >>> controller.is_capture_gated
    False
    >>> controller.start_listening("turn-example-1")
    >>> controller.state == TurnState.LISTENING
    True
    >>> partial = Transcript(TranscriptKind.PARTIAL, "find bag", "turn-example-1")
    >>> partial.can_authorize_action
    False
    >>> controller.process_transcript(partial)
    False
    >>> final = Transcript(TranscriptKind.FINAL, "find black backpack under 2000 rupees", "turn-example-1")
    >>> final.can_authorize_action
    True
    >>> controller.process_transcript(final)
    True
    >>> controller.start_speaking("Found black backpack for ₹1500.")
    >>> controller.state == TurnState.SPEAKING
    True
    >>> controller.is_capture_gated
    True
    >>> outcome = controller.stop()
    >>> outcome.stopped_playback
    True
    >>> outcome.action_undone
    False
    >>> controller.state == TurnState.STOPPED
    True
    >>> controller.is_capture_gated
    False

## Development and verification

All Sprint 1 and Sprint 2 tests run without third-party runtime dependencies using Python stdlib:

```sh
python -m unittest discover -s tests -v
python -S -m unittest discover -s tests -q
python -m doctest docs/SPRINT_2.md
python -m compileall -q voicecart tests
```
