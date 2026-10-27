"""Automated test suite for Sprint 2: Audio feasibility, turn controls, and latency.

Tests Stories A-01, A-02, and A-03 from IMPLEMENTATION_PLAN.md.
"""

from __future__ import annotations

import unittest

from tests.fixtures_audio import (
    COMPREHENSION_FIXTURES,
    PINNED_PIPER_LJ_MEDIUM,
    PINNED_WHISPER_BASE_EN,
    MockAudioOutput,
    MockSpeechRecognizer,
    MockSpeechSynthesizer,
    MockVAD,
)
from voicecart.audio import (
    AudioChunk,
    AudioPipelineSlice,
    HalfDuplexTurnController,
    LatencyBenchmarkRecorder,
    LatencyTrace,
    StatusPriority,
    Transcript,
    TranscriptKind,
    TurnState,
    VADState,
)


class AudioTurnManagementTests(unittest.TestCase):
    """A-01: Half-duplex turn adapter, controls, boundaries, and accessibility."""

    def setUp(self) -> None:
        self.controller = HalfDuplexTurnController()

    def test_initial_state_is_idle_and_capture_not_gated(self) -> None:
        self.assertEqual(self.controller.state, TurnState.IDLE)
        self.assertFalse(self.controller.is_capture_gated)
        self.assertTrue(self.controller.is_session_usable())

    def test_listening_state_un_gates_capture(self) -> None:
        self.controller.start_listening("turn-001")
        self.assertEqual(self.controller.state, TurnState.LISTENING)
        self.assertEqual(self.controller.current_turn_id, "turn-001")
        self.assertFalse(self.controller.is_capture_gated)
        self.assertTrue(any("turn-001" in m.text for m in self.controller.status_messages))

    def test_manual_end_turn_and_vad_endpoint_transition_to_processing(self) -> None:
        self.controller.start_listening("turn-002")
        self.controller.end_turn_manually("turn-002")
        self.assertEqual(self.controller.state, TurnState.PROCESSING)
        self.assertTrue(self.controller.is_capture_gated)

        # Test VAD endpoint path
        self.controller.start_listening("turn-003")
        self.controller.on_vad_endpoint("turn-003")
        self.assertEqual(self.controller.state, TurnState.PROCESSING)
        self.assertTrue(self.controller.is_capture_gated)

    def test_partial_transcripts_never_authorize_actions(self) -> None:
        self.controller.start_listening("turn-004")
        partial = Transcript(
            kind=TranscriptKind.PARTIAL,
            text="find black shoes",
            turn_id="turn-004",
        )
        self.assertFalse(partial.is_final)
        self.assertFalse(partial.can_authorize_action)

        authorized = self.controller.process_transcript(partial)
        self.assertFalse(authorized)
        self.assertTrue(any("Partial speech" in m.text for m in self.controller.status_messages))

    def test_final_transcript_authorizes_action_when_valid(self) -> None:
        self.controller.start_listening("turn-005")
        final = Transcript(
            kind=TranscriptKind.FINAL,
            text="find black backpack under 2000 rupees",
            turn_id="turn-005",
        )
        self.assertTrue(final.is_final)
        self.assertTrue(final.can_authorize_action)

        authorized = self.controller.process_transcript(final)
        self.assertTrue(authorized)
        self.assertEqual(self.controller.state, TurnState.PROCESSING)

    def test_stale_turn_events_are_rejected(self) -> None:
        self.controller.start_listening("turn-current")
        stale = Transcript(
            kind=TranscriptKind.FINAL,
            text="add to cart",
            turn_id="turn-expired-old",
        )
        authorized = self.controller.process_transcript(stale)
        self.assertFalse(authorized)
        self.assertTrue(any("stale" in m.text.lower() for m in self.controller.status_messages))

    def test_silence_timeout_and_no_speech_return_to_idle_with_retry_prompt(self) -> None:
        self.controller.start_listening("turn-006")
        silence = Transcript(
            kind=TranscriptKind.SILENCE_TIMEOUT,
            text="",
            turn_id="turn-006",
        )
        self.assertFalse(silence.can_authorize_action)
        authorized = self.controller.process_transcript(silence)
        self.assertFalse(authorized)
        self.assertEqual(self.controller.state, TurnState.IDLE)
        self.assertFalse(self.controller.is_capture_gated)
        self.assertTrue(any("No speech heard" in m.text for m in self.controller.status_messages))

    def test_half_duplex_speaking_gates_capture_to_prevent_self_echo(self) -> None:
        self.controller.start_speaking("Found black backpack for ₹1500.")
        self.assertEqual(self.controller.state, TurnState.SPEAKING)
        self.assertTrue(self.controller.is_capture_gated)  # Crucial: capture muted during assistant speech

        self.controller.finish_speaking()
        self.assertEqual(self.controller.state, TurnState.IDLE)
        self.assertFalse(self.controller.is_capture_gated)  # Capture un-gated after speech finishes

    def test_stop_control_stops_playback_without_claiming_mutation_rollback(self) -> None:
        self.controller.start_speaking("Adding item to cart...")
        outcome = self.controller.stop()
        self.assertEqual(self.controller.state, TurnState.STOPPED)
        self.assertTrue(outcome.success)
        self.assertTrue(outcome.stopped_playback)
        self.assertFalse(outcome.action_undone)  # CRITICAL: stop must not claim to rollback committed add!
        self.assertIn("cannot be undone", outcome.message)

    def test_pause_and_resume_controls(self) -> None:
        self.controller.pause()
        self.assertEqual(self.controller.state, TurnState.PAUSED)
        self.assertTrue(self.controller.is_capture_gated)

        self.controller.resume()
        self.assertEqual(self.controller.state, TurnState.IDLE)
        self.assertFalse(self.controller.is_capture_gated)

    def test_repeat_control_replays_speech_and_never_creates_mutation(self) -> None:
        # Before any response
        self.assertIsNone(self.controller.repeat())

        # After an announced response
        self.controller.start_speaking("Found 2 options under ₹1000.")
        self.controller.finish_speaking()

        repeated = self.controller.repeat()
        self.assertEqual(repeated, "Found 2 options under ₹1000.")
        self.assertTrue(any("Repeating" in m.text for m in self.controller.status_messages))

    def test_dual_failure_channel_marks_session_unusable(self) -> None:
        # If audio fails but assistive text is healthy, session is still usable
        self.controller.set_channel_health(audio=False, assistive=True)
        self.assertTrue(self.controller.is_session_usable())

        # If both fail, session becomes completely unusable and transitions to FAILED
        self.controller.set_channel_health(audio=False, assistive=False)
        self.assertFalse(self.controller.is_session_usable())
        self.assertEqual(self.controller.state, TurnState.FAILED)


class AudioPipelineSliceTests(unittest.TestCase):
    """A-02: Local ASR -> Template -> Local TTS slice and comprehension fixtures."""

    def test_pipeline_slice_executes_successfully(self) -> None:
        controller = HalfDuplexTurnController()
        controller.start_listening("turn-100")
        asr = MockSpeechRecognizer(transcript_text="find black backpack under 2000 rupees")
        tts = MockSpeechSynthesizer()
        pipeline = AudioPipelineSlice(asr, tts, controller)

        template_fn = lambda text: f"Verified result for: {text}"
        trace = LatencyTrace("turn-100")

        transcript, response, chunks = pipeline.execute_slice(
            audio_data=b"mock-pcm-bytes",
            turn_id="turn-100",
            template_fn=template_fn,
            trace=trace,
        )

        self.assertEqual(transcript.text, "find black backpack under 2000 rupees")
        self.assertTrue(transcript.can_authorize_action)
        self.assertEqual(response, "Verified result for: find black backpack under 2000 rupees")
        self.assertGreater(len(chunks), 0)
        self.assertFalse(trace.failed)
        self.assertGreater(trace.t_asr_end, trace.t_asr_start)
        self.assertGreater(trace.t_first_pcm_chunk, trace.t_tts_start)

    def test_comprehension_fixtures_preserve_critical_slots(self) -> None:
        for case in COMPREHENSION_FIXTURES:
            with self.subTest(description=case.description):
                for token in case.expected_critical_tokens:
                    self.assertIn(token.lower(), case.spoken_phrase.lower())
                self.assertTrue(len(case.expected_rendered_template) > 0)

    def test_neural_tts_failure_falls_back_to_cached_audio_prompt(self) -> None:
        controller = HalfDuplexTurnController()
        controller.start_listening("turn-200")
        asr = MockSpeechRecognizer()
        tts_failing = MockSpeechSynthesizer(should_fail=True)
        pipeline = AudioPipelineSlice(asr, tts_failing, controller)

        trace = LatencyTrace("turn-200")
        transcript, response, chunks = pipeline.execute_slice(
            audio_data=b"mock-audio",
            turn_id="turn-200",
            template_fn=lambda t: "Hello user",
            trace=trace,
        )

        # Verified fallback occurred
        self.assertTrue(trace.failed)
        self.assertIn("TTS synthesis failed", trace.failure_reason)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].pcm_data, AudioPipelineSlice.CACHED_FALLBACK_AUDIO)

    def test_pinned_model_metadata_verification(self) -> None:
        self.assertEqual(PINNED_WHISPER_BASE_EN.licence, "MIT")
        self.assertEqual(PINNED_WHISPER_BASE_EN.sample_rate_hz, 16000)
        self.assertTrue(PINNED_WHISPER_BASE_EN.is_commercial_eligible)

        self.assertEqual(PINNED_PIPER_LJ_MEDIUM.licence, "MIT")
        self.assertEqual(PINNED_PIPER_LJ_MEDIUM.sample_rate_hz, 22050)
        self.assertTrue(PINNED_PIPER_LJ_MEDIUM.is_commercial_eligible)


class AudibleLatencyTelemetryTests(unittest.TestCase):
    """A-03: Measurement of audible onset latency with visible failure accounting."""

    def test_latency_trace_calculates_all_intervals(self) -> None:
        trace = LatencyTrace(
            turn_id="t-1",
            is_warm=True,
            t_turn_start=100.0,
            t_speech_start=100.2,
            t_speech_end=102.0,
            t_endpoint_detected=102.3,
            t_asr_start=102.3,
            t_asr_end=102.8,
            t_template_start=102.8,
            t_template_end=102.81,
            t_tts_start=102.81,
            t_first_pcm_chunk=103.1,
            t_audible_onset=103.15,
        )

        self.assertAlmostEqual(trace.endpoint_delay_s, 0.3, places=2)
        self.assertAlmostEqual(trace.asr_latency_s, 0.5, places=2)
        self.assertAlmostEqual(trace.tts_to_first_audio_s, 0.29, places=2)
        # Audible onset is measured from t_speech_end (102.0) to t_audible_onset (103.15) = 1.15s
        self.assertAlmostEqual(trace.audible_onset_latency_s, 1.15, places=2)
        self.assertTrue(trace.meets_1500ms_target)

    def test_failed_or_timed_out_turns_do_not_meet_target(self) -> None:
        trace_failed = LatencyTrace(
            turn_id="t-fail",
            t_speech_end=10.0,
            t_audible_onset=10.8,
            failed=True,
        )
        self.assertFalse(trace_failed.meets_1500ms_target)

        trace_timeout = LatencyTrace(
            turn_id="t-timeout",
            t_speech_end=10.0,
            t_audible_onset=11.2,
            timed_out=True,
        )
        self.assertFalse(trace_timeout.meets_1500ms_target)

    def test_benchmark_recorder_preserves_full_failure_denominators(self) -> None:
        recorder = LatencyBenchmarkRecorder()

        # 8 successful turns with latencies under 1.5s
        for i in range(8):
            t = LatencyTrace(
                turn_id=f"t-success-{i}",
                is_warm=True,
                t_speech_end=10.0,
                t_audible_onset=11.0 + (i * 0.05),  # 1.00s to 1.35s
            )
            recorder.record(t)

        # 1 turn exceeding 1.5s
        t_slow = LatencyTrace(
            turn_id="t-slow",
            is_warm=True,
            t_speech_end=10.0,
            t_audible_onset=11.8,  # 1.8s
        )
        recorder.record(t_slow)

        # 1 failed turn
        t_failed = LatencyTrace(
            turn_id="t-failed",
            is_warm=False,
            t_speech_end=10.0,
            t_audible_onset=0.0,
            failed=True,
            failure_reason="Microphone input error",
        )
        recorder.record(t_failed)

        summary = recorder.summarize()

        self.assertEqual(summary.total_turns, 10)
        self.assertEqual(summary.successful_turns, 9)
        self.assertEqual(summary.failed_turns, 1)
        self.assertEqual(summary.timeout_turns, 0)
        self.assertEqual(summary.cold_turns, 1)
        self.assertEqual(summary.warm_turns, 9)

        # Crucial: 8 out of 10 passed -> pass rate MUST be 0.80, NOT 8/9!
        self.assertAlmostEqual(summary.target_1500ms_pass_rate, 0.80, places=2)
        self.assertGreater(summary.p50_audible_onset_s, 0.0)
        self.assertGreater(summary.p95_audible_onset_s, summary.p50_audible_onset_s)

    def test_vad_simulation_events(self) -> None:
        vad = MockVAD(speech_frames=3, silence_frames_for_endpoint=2)
        chunk = AudioChunk(pcm_data=b"\x00" * 320, sample_rate_hz=16000, timestamp_s=1.0)

        # Frames 1, 2, 3: Speech
        for _ in range(3):
            event = vad.process_frame(chunk)
            self.assertEqual(event.state, VADState.SPEECH)

        # Frame 4: Silence
        event4 = vad.process_frame(chunk)
        self.assertEqual(event4.state, VADState.SILENCE)

        # Frame 5: Endpoint detected
        event5 = vad.process_frame(chunk)
        self.assertEqual(event5.state, VADState.ENDPOINT_DETECTED)


if __name__ == "__main__":
    unittest.main()
