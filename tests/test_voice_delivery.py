"""Adapter regressions with synthetic PCM/scripted devices; not acoustic acceptance."""

import hashlib
import tempfile
import unittest
from pathlib import Path

from tests.fixtures_audio import MockAudioOutput, MockSpeechSynthesizer
from voicecart.application import Response
from voicecart.audio import (
    AudioChunk,
    CachedSpeechPrompt,
    HalfDuplexTurnController,
    Transcript,
    TranscriptKind,
)
from voicecart.voice import FileArtifact, ResponseSpeaker, SoundDeviceOutput, VoiceError


class DeliveryTests(unittest.TestCase):
    def test_all_response_codes_share_verified_output_path(self):
        for code in (
            "results",
            "clarify",
            "asr_error",
            "response_error",
            "added",
            "no_match",
            "incomplete",
        ):
            with self.subTest(code=code):
                controller = HalfDuplexTurnController()
                output = MockAudioOutput()
                speaker = ResponseSpeaker(controller, MockSpeechSynthesizer(), output)
                result = speaker.deliver(
                    Response(
                        code,
                        "Verified response or explicit recovery.",
                        "session",
                        "turn",
                    )
                )
                self.assertEqual(result.kind, "response_completed")
                self.assertGreater(len(output.played_chunks), 0)
                self.assertFalse(controller.is_capture_gated)
                self.assertFalse(
                    controller.process_transcript(
                        Transcript(
                            TranscriptKind.FINAL,
                            "add",
                            controller.current_turn_id or "expired",
                        )
                    )
                )

    def test_tts_fallback_is_not_a_completed_product_list(self):
        controller = HalfDuplexTurnController()
        output = MockAudioOutput()
        fallback = CachedSpeechPrompt(
            "Please use text or retry.", AudioChunk(b"\0\0" * 100, 16000)
        )
        speaker = ResponseSpeaker(
            controller,
            MockSpeechSynthesizer(should_fail=True),
            output,
            fallback=fallback,
        )
        result = speaker.deliver(
            Response("results", "The original product list.", "session", "turn")
        )
        self.assertEqual(result.kind, "fallback_completed")
        self.assertEqual(output.played_chunks, [fallback.chunk])

    def test_playback_failure_uses_assistive_channel_and_never_claims_audible_delivery(
        self,
    ):
        output = MockAudioOutput()

        def broken(chunk):
            raise OSError("Injected missing device")

        output.play_chunk = broken
        controller = HalfDuplexTurnController()
        speaker = ResponseSpeaker(controller, MockSpeechSynthesizer(), output)
        delivery = speaker.deliver(
            Response("added", "Committed local add.", "session", "turn")
        )
        self.assertEqual(delivery.kind, "assistive_only")
        self.assertIsNone(delivery.audible_onset)
        self.assertTrue(
            any(
                "Speech unavailable" in status.text
                for status in controller.status_messages
            )
        )

    def test_artifact_integrity_and_resource_cleanup_without_fake_onset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture"
            path.write_bytes(b"test fixture only")
            artifact = FileArtifact(path, hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(artifact.verify(), path)
            with self.assertRaises(VoiceError):
                FileArtifact(path, "a" * 64).verify()

        class Stream:
            closed = False

            def __init__(self, **kwargs):
                pass

            def start(self):
                pass

            def write(self, data):
                pass

            def stop(self):
                pass

            def abort(self):
                pass

            def close(self):
                Stream.closed = True

        class Driver:
            RawOutputStream = Stream

        output = SoundDeviceOutput(driver=Driver())
        output.begin_playback("t")
        output.play_chunk(AudioChunk(b"\0\0" * 100, 16000))
        self.assertIsNone(output.drain("t"))
        self.assertTrue(Stream.closed)
        self.assertFalse(output.is_playing())
