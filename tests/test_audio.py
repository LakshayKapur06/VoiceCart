"""Audio contract regressions. These do not establish real model/device quality."""

from __future__ import annotations

import io
import threading
import time
import unittest
import wave
from dataclasses import replace

from tests.fixtures_audio import (
    REFERENCE_LJ_VOICE,
    REFERENCE_PIPER_RUNTIME,
    REFERENCE_WHISPER_BASE_EN,
    SCRIPTED_TRANSCRIPTS,
    MockAudioInput,
    MockAudioOutput,
    MockSpeechRecognizer,
    MockSpeechSynthesizer,
    MockVAD,
)
from voicecart.audio import (
    ArtifactMetadata,
    AudioChunk,
    AudioPipelineSlice,
    CachedSpeechPrompt,
    HalfDuplexTurnController,
    LatencyBenchmarkRecorder,
    LatencyTrace,
    Transcript,
    TranscriptKind,
    TurnState,
    VADEvent,
    VADState,
)


def final(turn_id="t", text="find bag"):
    return Transcript(TranscriptKind.FINAL, text, turn_id)


def verified_template(text):
    # Echo for protocol preservation only, not NLU or a business-action handler.
    return f"Search request received: {text}"


class AudioTurnManagementTests(unittest.TestCase):
    def setUp(self):
        self.capture = MockAudioInput()
        self.output = MockAudioOutput()
        self.controller = HalfDuplexTurnController(audio_input=self.capture)
        self.controller.bind_output(self.output)

    def speaking(self, turn_id="t", response="Verified response"):
        self.controller.start_listening(turn_id)
        self.assertTrue(self.controller.process_transcript(final(turn_id)))
        self.assertTrue(self.controller.start_speaking(response, turn_id=turn_id))

    def test_initial_and_listening_states(self):
        self.assertEqual(self.controller.state, TurnState.IDLE)
        self.assertFalse(self.controller.is_capture_gated)
        self.controller.start_listening("t")
        self.assertTrue(self.capture.capturing)
        self.assertFalse(self.controller.is_capture_gated)

    def test_manual_and_vad_end_stop_capture_and_wait_for_final(self):
        for i, end in enumerate(
            (self.controller.end_turn_manually, self.controller.on_vad_endpoint)
        ):
            turn_id = str(i)
            self.controller.start_listening(turn_id)
            end(turn_id)
            self.assertFalse(self.capture.capturing)
            self.assertTrue(self.controller.is_capture_gated)
            self.assertTrue(self.controller.process_transcript(final(turn_id)))

    def test_partial_does_not_authorize_or_consume_final(self):
        self.controller.start_listening("t")
        partial = Transcript(TranscriptKind.PARTIAL, "find", "t")
        self.assertFalse(partial.can_authorize_action)
        self.assertFalse(self.controller.process_transcript(partial))
        self.assertTrue(self.controller.process_transcript(final()))
        self.assertFalse(self.controller.process_transcript(final()))

    def test_empty_and_nonfinal_terminal_events_retire_turn(self):
        for i, kind in enumerate(
            (
                TranscriptKind.FINAL,
                TranscriptKind.NO_SPEECH,
                TranscriptKind.SILENCE_TIMEOUT,
                TranscriptKind.ERROR,
            )
        ):
            with self.subTest(kind=kind):
                turn_id = str(i)
                self.controller.start_listening(turn_id)
                self.assertFalse(
                    self.controller.process_transcript(Transcript(kind, "  ", turn_id))
                )
                self.assertEqual(self.controller.state, TurnState.IDLE)
                self.assertIsNone(self.controller.current_turn_id)
                self.assertFalse(self.capture.capturing)
                self.assertFalse(self.controller.process_transcript(final(turn_id)))

    def test_stale_callbacks_have_no_effect(self):
        self.controller.start_listening("new")
        before = self.controller.status_messages
        self.assertFalse(self.controller.process_transcript(final("old")))
        self.controller.end_turn_manually("old")
        self.assertEqual(self.controller.finish_speaking("old"), (False, None))
        self.assertEqual(self.controller.status_messages, before)
        self.assertEqual(self.controller.state, TurnState.LISTENING)

    def test_stop_pause_and_dead_channels_reject_late_final(self):
        for action in ("stop", "pause", "fail"):
            with self.subTest(action=action):
                self.setUp()
                self.controller.start_listening("t")
                if action == "fail":
                    self.controller.set_channel_health(audio=False, assistive=False)
                else:
                    getattr(self.controller, action)()
                before = (self.controller.state, self.controller.status_messages)
                self.assertFalse(self.controller.process_transcript(final()))
                self.assertEqual(
                    (self.controller.state, self.controller.status_messages), before
                )
                self.assertFalse(self.capture.capturing)

    def test_speaking_gates_until_device_drain_completes(self):
        self.speaking()
        self.assertFalse(self.capture.capturing)
        self.output.on_drain = lambda: self.assertTrue(self.controller.is_capture_gated)
        self.controller.enqueue_audio("t", AudioChunk(b"\0\0" * 100, 16000))
        completed, onset = self.controller.finish_speaking("t")
        self.assertTrue(completed)
        self.assertIsNotNone(onset)
        self.assertEqual(self.controller.state, TurnState.IDLE)
        self.assertFalse(self.controller.is_capture_gated)
        self.assertFalse(self.output.is_playing())

    def test_stop_and_pause_flush_playback_and_never_undo_action(self):
        for action_name in ("stop", "pause"):
            self.setUp()
            self.speaking()
            self.controller.enqueue_audio("t", AudioChunk(b"\0\0", 16000))
            count = self.output.stop_calls
            result = getattr(self.controller, action_name)()
            self.assertEqual(self.output.stop_calls, count + 1)
            self.assertTrue(result.stopped_playback)
            self.assertFalse(result.action_undone)
            self.assertFalse(self.output.is_playing())
            self.assertEqual(self.controller.finish_speaking("t"), (False, None))
            self.assertIsNone(self.controller.repeat())

    def test_repeat_only_returns_completed_response(self):
        self.assertIsNone(self.controller.repeat())
        self.speaking(response="Found two options")
        self.assertIsNone(self.controller.repeat())
        self.controller.enqueue_audio("t", AudioChunk(b"\0\0", 16000))
        self.controller.finish_speaking("t")
        self.assertEqual(self.controller.repeat(), "Found two options")
        self.assertIsNone(self.controller.current_turn_id)

    def test_unique_ids_and_explicit_resume(self):
        self.controller.start_listening("t")
        self.controller.pause()
        with self.assertRaises(RuntimeError):
            self.controller.start_listening("new")
        self.controller.resume()
        with self.assertRaises(ValueError):
            self.controller.start_listening("t")
        self.controller.start_listening("new")

    def test_unusable_session_requires_health_recovery(self):
        self.controller.set_channel_health(audio=False, assistive=False)
        self.assertFalse(self.controller.resume().success)
        with self.assertRaises(RuntimeError):
            self.controller.start_listening("t")
        self.controller.set_channel_health(audio=False, assistive=True)
        self.controller.resume()
        self.controller.start_listening("t")

    def test_status_delivery_failure_and_audio_failure_fail_closed(self):
        def broken_sink(message):
            raise RuntimeError("Unavailable assistive host")

        controller = HalfDuplexTurnController(status_sink=broken_sink)
        controller.start_listening("t")
        self.assertTrue(controller.is_session_usable())
        controller.set_channel_health(audio=False, assistive=False)
        self.assertEqual(controller.state, TurnState.FAILED)
        self.assertIsNone(controller.current_turn_id)

    def test_failed_device_stop_reports_failure_and_keeps_capture_gated(self):
        self.speaking()
        self.controller.enqueue_audio("t", AudioChunk(b"\0\0", 16000))

        def broken_stop():
            raise OSError("Device did not stop")

        self.output.stop_playback = broken_stop
        outcome = self.controller.stop()
        self.assertFalse(outcome.success)
        self.assertFalse(outcome.stopped_playback)
        self.assertFalse(outcome.action_undone)
        self.assertEqual(self.controller.state, TurnState.FAILED)
        self.assertTrue(self.controller.is_capture_gated)
        self.assertFalse(self.controller.resume().success)
        with self.assertRaises(RuntimeError):
            self.controller.start_listening("next")

    def test_empty_playback_cannot_be_promoted_to_repeat(self):
        self.speaking()
        with self.assertRaises(RuntimeError):
            self.controller.finish_speaking("t")
        self.assertIsNone(self.controller.repeat())

    def test_capture_failure_retires_turn_and_emits_recovery(self):
        def broken_capture():
            raise OSError("Microphone unavailable")

        self.capture.start_capture = broken_capture
        self.controller.start_listening("t")
        self.assertIsNone(self.controller.current_turn_id)
        self.assertFalse(self.controller.process_transcript(final()))
        self.assertTrue(
            any(
                "capture unavailable" in m.text for m in self.controller.status_messages
            )
        )


class AudioPipelineSliceTests(unittest.TestCase):
    def setUp(self):
        self.controller = HalfDuplexTurnController()
        self.output = MockAudioOutput()
        self.asr = MockSpeechRecognizer()
        self.tts = MockSpeechSynthesizer()
        self.trace = LatencyTrace("t", t_speech_end=time.monotonic())
        self.controller.start_listening("t")

    def run_slice(
        self, *, asr=None, tts=None, template=verified_template, fallback=None
    ):
        pipeline = AudioPipelineSlice(
            asr or self.asr,
            tts or self.tts,
            self.controller,
            self.output,
            fallback=fallback,
        )
        return pipeline.execute_slice(b"\0\0", "t", template, self.trace)

    def test_success_plays_output_and_records_simulated_onset(self):
        transcript, response, chunks = self.run_slice()
        self.assertEqual(transcript.text, self.asr.text)
        self.assertEqual(response, verified_template(self.asr.text))
        self.assertEqual(chunks, self.output.played_chunks)
        self.assertEqual(self.trace.t_audible_onset, self.output.audible_onset_time)
        self.assertTrue(self.trace.is_successful)
        self.assertFalse(self.output.is_playing())
        self.assertEqual(self.controller.state, TurnState.IDLE)

    def test_scripted_pcm_runs_through_asr_template_tts_and_output(self):
        expected_slots = (
            ("under", "1500", "rupees"),
            ("at most", "2000", "rupees"),
            ("SKU-BLK-101",),
            ("don't add",),
        )
        responses = []
        for i, (pcm, slots) in enumerate(
            zip(SCRIPTED_TRANSCRIPTS, expected_slots, strict=True)
        ):
            controller = HalfDuplexTurnController()
            controller.start_listening(str(i))
            asr = MockSpeechRecognizer(None)
            tts, output = MockSpeechSynthesizer(), MockAudioOutput()
            pipeline = AudioPipelineSlice(asr, tts, controller, output)
            transcript, response, chunks = pipeline.execute_slice(
                pcm, str(i), verified_template
            )
            self.assertEqual(asr.calls, 1)
            self.assertEqual(tts.spoken_texts, [response])
            for slot in slots:
                self.assertIn(slot, transcript.text)
                self.assertIn(slot, response)
            self.assertEqual(chunks, output.played_chunks)
            responses.append(response)
        self.assertEqual(len(set(responses)), 4)

    def test_stop_during_synthesis_fences_remaining_chunks(self):
        controller = self.controller

        class InterruptedTTS(MockSpeechSynthesizer):
            def synthesize(self, text):
                yield AudioChunk(b"\0\0", 16000)
                controller.stop()
                yield AudioChunk(b"\1\0", 16000)

        _, response, chunks = self.run_slice(tts=InterruptedTTS())
        self.assertEqual(response, "")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(self.output.played_chunks), 1)
        self.assertTrue(self.trace.cancelled)
        self.assertEqual(self.controller.state, TurnState.STOPPED)

    def test_pause_inside_enqueue_cancels_without_finishing(self):
        self.output.on_play = self.controller.pause
        self.run_slice()
        self.assertEqual(len(self.output.played_chunks), 1)
        self.assertEqual(self.controller.state, TurnState.PAUSED)
        self.assertTrue(self.trace.cancelled)
        self.assertIsNone(self.controller.repeat())

    def test_stop_during_drain_allows_concurrent_control_and_fences_completion(self):
        entered, release = threading.Event(), threading.Event()

        def drain():
            entered.set()
            if not release.wait(3):
                raise RuntimeError("Test drain timed out")

        self.output.on_drain = drain
        results = []
        worker = threading.Thread(target=lambda: results.append(self.run_slice()))
        worker.start()
        try:
            self.assertTrue(entered.wait(3))
            self.controller.stop()
            self.controller.start_listening("new")
        finally:
            release.set()
            worker.join(3)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(results), 1)
        self.assertEqual(self.controller.current_turn_id, "new")
        self.assertEqual(self.controller.state, TurnState.LISTENING)
        self.assertTrue(self.trace.cancelled)
        self.assertIsNone(self.trace.t_audible_onset)

    def test_stop_during_asr_does_not_render_template(self):
        controller = self.controller

        class StoppedASR(MockSpeechRecognizer):
            def transcribe(self, audio_data, turn_id):
                controller.stop()
                return final(turn_id)

        def forbidden(text):
            self.fail("Cancelled ASR must not invoke template")

        self.run_slice(asr=StoppedASR(), template=forbidden)
        self.assertTrue(self.trace.cancelled)
        self.assertEqual(self.output.played_chunks, [])

    def test_template_failure_and_asr_failure_recover_with_status(self):
        def broken_template(text):
            raise RuntimeError("private input must not enter failure telemetry")

        self.run_slice(template=broken_template)
        self.assertEqual(self.trace.failure_reason, "template_error")
        self.assertEqual(self.controller.state, TurnState.IDLE)
        self.assertTrue(
            any("unavailable" in m.text for m in self.controller.status_messages)
        )
        self.setUp()

        class BrokenASR(MockSpeechRecognizer):
            def transcribe(self, audio_data, turn_id):
                raise RuntimeError("backend failure")

        self.run_slice(asr=BrokenASR())
        self.assertEqual(self.trace.failure_reason, "asr_error")
        self.assertEqual(self.output.played_chunks, [])

    def test_partial_and_invalid_final_never_render(self):
        for kind, text in (
            (TranscriptKind.PARTIAL, "add"),
            (TranscriptKind.FINAL, " "),
            (TranscriptKind.NO_SPEECH, ""),
            (TranscriptKind.ERROR, "error"),
        ):
            self.setUp()

            def forbidden(text):
                self.fail("Non-authorizing event reached template")

            self.run_slice(
                asr=MockSpeechRecognizer(text, kind=kind), template=forbidden
            )
            self.assertEqual(self.output.played_chunks, [])
            if kind is TranscriptKind.PARTIAL:
                self.assertEqual(self.controller.state, TurnState.PROCESSING)
            else:
                self.assertTrue(self.trace.failed)
                self.assertEqual(self.controller.state, TurnState.IDLE)

    def test_tts_failure_and_empty_stream_have_explicit_recovery_without_fake_audio(
        self,
    ):
        for tts in (
            MockSpeechSynthesizer(should_fail=True),
            MockSpeechSynthesizer(chunks_per_response=0),
        ):
            self.setUp()
            _, response, chunks = self.run_slice(tts=tts)
            self.assertEqual(response, AudioPipelineSlice.ERROR_RESPONSE)
            self.assertEqual(chunks, [])
            self.assertTrue(self.trace.failed)
            self.assertFalse(self.trace.meets_1500ms_target)
            self.assertTrue(
                any("unavailable" in m.text for m in self.controller.status_messages)
            )
            self.assertEqual(self.controller.state, TurnState.IDLE)

    def test_cached_asset_is_injected_and_failure_does_not_claim_original_success(self):
        # Synthetic PCM tests the transport only; it is NOT an emergency recording.
        fallback = CachedSpeechPrompt(
            "Speech unavailable. Try again.", AudioChunk(b"\0\0" * 160, 16000)
        )
        _, response, chunks = self.run_slice(
            tts=MockSpeechSynthesizer(should_fail=True), fallback=fallback
        )
        self.assertEqual(response, fallback.text)
        self.assertEqual(chunks, [fallback.chunk])
        self.assertTrue(self.trace.failed)
        self.assertFalse(self.trace.meets_1500ms_target)
        self.assertEqual(self.controller.repeat(), fallback.text)
        self.assertTrue(
            any(fallback.text in m.text for m in self.controller.status_messages)
        )

    def test_output_failure_and_dead_assistive_channel_mark_session_unusable(self):
        def broken_play(chunk):
            raise OSError("Device missing")

        self.output.play_chunk = broken_play
        self.controller.set_channel_health(audio=True, assistive=False)
        self.run_slice()
        self.assertEqual(self.trace.failure_reason, "output_error")
        self.assertFalse(self.controller.is_session_usable())
        self.assertEqual(self.controller.state, TurnState.FAILED)

    def test_no_device_onset_is_not_a_successful_benchmark(self):
        self.output.drain = lambda turn_id: None
        # Adapter contract still requires drain to finish playback.
        self.output.on_play = self.output.stop_playback
        self.run_slice()
        self.assertFalse(self.trace.is_successful)
        recorder = LatencyBenchmarkRecorder()
        recorder.record(self.trace)
        self.assertEqual(recorder.summarize().failed_turns, 1)

    def test_wrong_trace_rejected_before_asr(self):
        self.trace.turn_id = "other"
        with self.assertRaises(ValueError):
            self.run_slice()
        self.assertEqual(self.asr.calls, 0)

    def test_late_old_drain_cannot_finish_new_playback(self):
        entered, release = threading.Event(), threading.Event()

        def wait_for_cancel():
            entered.set()
            if not release.wait(3):
                raise RuntimeError("Test drain timed out")

        self.output.on_drain = wait_for_cancel
        worker = threading.Thread(target=self.run_slice)
        worker.start()
        try:
            self.assertTrue(entered.wait(3))
            self.controller.stop()
            self.controller.start_listening("new")
            self.controller.process_transcript(final("new"))
            self.controller.start_speaking("New response", turn_id="new")
            self.controller.enqueue_audio("new", AudioChunk(b"\1\0", 16000))
        finally:
            release.set()
            worker.join(3)
        self.assertFalse(worker.is_alive())
        self.assertTrue(self.output.is_playing())
        self.assertEqual(self.controller.state, TurnState.SPEAKING)
        self.assertEqual(self.controller.current_turn_id, "new")
        self.assertTrue(self.trace.cancelled)
        self.output.on_drain = None
        self.assertTrue(self.controller.finish_speaking("new")[0])

    def test_pipeline_ends_capture_before_asr_and_rejects_consumed_turn(self):
        capture = MockAudioInput()
        controller = HalfDuplexTurnController(audio_input=capture)
        controller.start_listening("capture")

        class CaptureCheckingASR(MockSpeechRecognizer):
            def transcribe(inner_self, audio_data, turn_id):
                self.assertFalse(capture.capturing)
                return super().transcribe(audio_data, turn_id)

        asr = CaptureCheckingASR()
        pipeline = AudioPipelineSlice(asr, self.tts, controller, self.output)
        pipeline.execute_slice(b"\0\0", "capture", verified_template)
        pipeline.execute_slice(b"\0\0", "capture", verified_template)
        self.assertEqual(asr.calls, 1)

    def test_output_begin_and_drain_failures_recover(self):
        def broken(*args):
            raise OSError("Output failure")

        for method in ("begin_playback", "drain"):
            self.setUp()
            setattr(self.output, method, broken)
            _, response, chunks = self.run_slice()
            self.assertEqual(response, AudioPipelineSlice.ERROR_RESPONSE)
            self.assertEqual(chunks, [])
            self.assertEqual(self.trace.failure_reason, "output_error")
            self.assertEqual(self.controller.state, TurnState.IDLE)

    def test_deadline_and_missing_output_remain_in_denominator(self):
        class TimedOutASR(MockSpeechRecognizer):
            def transcribe(self, audio_data, turn_id):
                raise TimeoutError("Adapter deadline exceeded")

        self.run_slice(asr=TimedOutASR())
        self.assertTrue(self.trace.timed_out)
        recorder = LatencyBenchmarkRecorder()
        recorder.record(self.trace)
        self.assertEqual(recorder.summarize().timeout_turns, 1)
        self.assertEqual(recorder.summarize().target_1500ms_pass_rate, 0)

    def test_stop_followed_by_asr_error_is_cancellation(self):
        controller = self.controller

        class CancelledASR(MockSpeechRecognizer):
            def transcribe(self, audio_data, turn_id):
                controller.stop()
                raise RuntimeError("Late worker error")

        _, response, _ = self.run_slice(asr=CancelledASR())
        self.assertEqual(response, "")
        self.assertTrue(self.trace.cancelled)
        self.assertFalse(self.trace.failed)
        self.assertEqual(self.controller.state, TurnState.STOPPED)

    def test_tts_fails_after_partial_stream_flushes_before_cached_prompt(self):
        fallback = CachedSpeechPrompt("Please retry", AudioChunk(b"\2\0" * 160, 16000))

        class PartialFailure(MockSpeechSynthesizer):
            def synthesize(self, text):
                yield AudioChunk(b"\1\0", 16000)
                raise RuntimeError("Synthesis interrupted")

        count = self.output.stop_calls
        _, response, chunks = self.run_slice(tts=PartialFailure(), fallback=fallback)
        self.assertEqual(response, fallback.text)
        self.assertEqual(chunks, [fallback.chunk])
        self.assertEqual(self.output.begin_calls, ["t", "t"])
        self.assertGreater(self.output.stop_calls, count)
        self.assertTrue(self.trace.failed)
        self.assertFalse(self.trace.is_successful)

    def test_status_sink_failure_then_output_failure_disables_session(self):
        def broken_sink(message):
            raise OSError("Assistive channel unavailable")

        self.controller = HalfDuplexTurnController(status_sink=broken_sink)
        self.controller.start_listening("t")

        def broken_play(chunk):
            raise OSError("Output unavailable")

        self.output.play_chunk = broken_play
        self.run_slice()
        self.assertFalse(self.controller.is_session_usable())
        self.assertEqual(self.controller.state, TurnState.FAILED)

    def test_asr_wrong_turn_and_unknown_fixture_cannot_reach_template(self):
        class WrongTurnASR(MockSpeechRecognizer):
            def transcribe(self, audio_data, turn_id):
                return final("old")

        self.run_slice(asr=WrongTurnASR())
        self.assertEqual(self.trace.failure_reason, "asr_turn_mismatch")
        self.assertEqual(self.tts.spoken_texts, [])
        self.setUp()
        self.run_slice(asr=MockSpeechRecognizer(None))
        self.assertEqual(self.trace.failure_reason, "asr_error")
        self.assertEqual(self.tts.spoken_texts, [])


class AudibleLatencyTelemetryTests(unittest.TestCase):
    def test_intervals_and_zero_clock_are_valid(self):
        trace = LatencyTrace(
            "t",
            t_speech_end=0,
            t_endpoint_detected=0.1,
            t_asr_start=0.1,
            t_asr_end=0.4,
            t_tts_start=0.5,
            t_first_pcm_chunk=0.8,
            t_audible_onset=1.0,
        )
        self.assertAlmostEqual(trace.endpoint_delay_s, 0.1)
        self.assertAlmostEqual(trace.asr_latency_s, 0.3)
        self.assertAlmostEqual(trace.tts_to_first_audio_s, 0.3)
        self.assertEqual(trace.audible_onset_latency_s, 1)
        self.assertTrue(trace.meets_1500ms_target)

    def test_missing_reversed_nonfinite_and_bool_times_never_pass(self):
        invalid = (
            LatencyTrace("missing"),
            LatencyTrace("end", t_audible_onset=11),
            LatencyTrace("reverse", t_speech_end=10, t_audible_onset=9),
            LatencyTrace("nan", t_speech_end=float("nan"), t_audible_onset=11),
            LatencyTrace("inf", t_speech_end=10, t_audible_onset=float("inf")),
            LatencyTrace("bool", t_speech_end=False, t_audible_onset=1),
            LatencyTrace(
                "stage",
                t_speech_end=10,
                t_asr_start=12,
                t_asr_end=11,
                t_audible_onset=13,
            ),
        )
        recorder = LatencyBenchmarkRecorder()
        for trace in invalid:
            self.assertFalse(trace.meets_1500ms_target, trace.turn_id)
            recorder.record(trace)
        summary = recorder.summarize()
        self.assertEqual(summary.successful_turns, 0)
        self.assertEqual(summary.failed_turns, len(invalid))
        self.assertIsNone(summary.p50_audible_onset_s)
        self.assertEqual(summary.target_1500ms_pass_rate, 0)

    def test_full_denominator_disjoint_outcomes_and_percentiles(self):
        recorder = LatencyBenchmarkRecorder()
        for i, latency in enumerate((1.0, 1.2, 1.5, 2.0)):
            recorder.record(
                LatencyTrace(str(i), t_speech_end=10, t_audible_onset=10 + latency)
            )
        recorder.record(LatencyTrace("failed", failed=True, is_warm=False))
        recorder.record(LatencyTrace("timeout", failed=True, timed_out=True))
        recorder.record(LatencyTrace("cancelled", cancelled=True, timed_out=True))
        summary = recorder.summarize()
        self.assertEqual(summary.total_turns, 7)
        self.assertEqual(summary.successful_turns, 4)
        self.assertEqual(summary.failed_turns, 1)
        self.assertEqual(summary.timeout_turns, 1)
        self.assertEqual(summary.cancelled_turns, 1)
        self.assertEqual(summary.cold_turns, 1)
        self.assertAlmostEqual(summary.target_1500ms_pass_rate, 2 / 7)
        self.assertAlmostEqual(summary.p50_audible_onset_s, 1.35)
        self.assertEqual(summary.p95_audible_onset_s, 2.0)

    def test_recorder_freezes_snapshots_and_rejects_duplicate_ids(self):
        trace = LatencyTrace("t", t_speech_end=10, t_audible_onset=11)
        recorder = LatencyBenchmarkRecorder()
        recorder.record(trace)
        trace.failed = True
        recorder.traces[0].failed = True
        self.assertEqual(recorder.summarize().successful_turns, 1)
        with self.assertRaises(ValueError):
            recorder.record(trace)
        self.assertIsNone(LatencyBenchmarkRecorder().summarize().max_audible_onset_s)


class AudioValueContractTests(unittest.TestCase):
    def test_pcm_and_timestamp_validation(self):
        self.assertEqual(AudioChunk(b"\0\0" * 160, 16000).duration_s, 0.01)
        for pcm in (b"", b"odd"):
            with self.assertRaises(ValueError):
                AudioChunk(pcm, 16000)
        for value in (-1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                AudioChunk(b"\0\0", 16000, timestamp_s=value)
            with self.assertRaises(ValueError):
                Transcript(TranscriptKind.FINAL, "find", "t", confidence=value)
            with self.assertRaises(ValueError):
                VADEvent(VADState.SPEECH, value)

    def test_wav_fallback_rejects_fake_and_truncated_recordings(self):
        for data in (b"RIFF-MOCK-CACHED-AUDIO-FALLBACK-PROMPT", b"", b"invalid"):
            with self.assertRaises(ValueError):
                CachedSpeechPrompt.from_wav("Please retry", data)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(16000)
            writer.writeframes(b"\0\0" * 160)
        asset = CachedSpeechPrompt.from_wav("Synthetic fixture only", buffer.getvalue())
        self.assertEqual(asset.chunk.duration_s, 0.01)
        with self.assertRaises(ValueError):
            CachedSpeechPrompt.from_wav("Please retry", buffer.getvalue()[:-2])

    def test_candidate_runtime_and_voice_metadata_are_distinct_and_unpinned(self):
        self.assertEqual(REFERENCE_WHISPER_BASE_EN.licence, "MIT")
        self.assertEqual(REFERENCE_PIPER_RUNTIME.licence, "GPL-3.0")
        self.assertIsNone(REFERENCE_PIPER_RUNTIME.sample_rate_hz)
        self.assertEqual(REFERENCE_LJ_VOICE.sample_rate_hz, 22050)
        for metadata in (
            REFERENCE_WHISPER_BASE_EN,
            REFERENCE_PIPER_RUNTIME,
            REFERENCE_LJ_VOICE,
        ):
            self.assertFalse(metadata.is_pinned)
            self.assertIsNone(metadata.is_commercial_eligible)
        self.assertTrue(replace(REFERENCE_LJ_VOICE, sha256="a" * 64).is_pinned)
        with self.assertRaises(ValueError):
            replace(REFERENCE_LJ_VOICE, sha256="fake")
        self.assertIsNone(
            ArtifactMetadata(
                "test", "test", "unknown", "en", None
            ).is_commercial_eligible
        )

    def test_vad_fixture_and_reset(self):
        vad = MockVAD(speech_frames=1, silence_frames_for_endpoint=2)
        chunk = AudioChunk(b"\0\0", 16000)
        self.assertEqual(
            [vad.process_frame(chunk).state for _ in range(3)],
            [VADState.SPEECH, VADState.SILENCE, VADState.ENDPOINT_DETECTED],
        )
        vad.reset()
        self.assertEqual(vad.process_frame(chunk).state, VADState.SPEECH)


if __name__ == "__main__":
    unittest.main()
