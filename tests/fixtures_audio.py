"""Test fixtures, mock devices, and comprehension data for Sprint 2 audio tests."""

from __future__ import annotations

import time
from collections.abc import Iterable
from dataclasses import dataclass

from voicecart.audio import (
    ArtifactMetadata,
    AudioChunk,
    AudioInputProtocol,
    AudioOutputProtocol,
    SpeechRecognizerProtocol,
    SpeechSynthesizerProtocol,
    Transcript,
    TranscriptKind,
    VADEvent,
    VADProtocol,
    VADState,
)


# Pinned reference artifact specifications
PINNED_WHISPER_BASE_EN = ArtifactMetadata(
    name="whisper.cpp-base.en",
    version="1.7.4",
    licence="MIT",
    language="en",
    sample_rate_hz=16000,
    is_commercial_eligible=True,
)

PINNED_PIPER_LJ_MEDIUM = ArtifactMetadata(
    name="piper-en_US-ljspeech-medium",
    version="1.2.0",
    licence="MIT",
    language="en_US",
    sample_rate_hz=22050,
    is_commercial_eligible=True,
)


@dataclass(frozen=True)
class AudioComprehensionTestCase:
    """Fixture to verify critical-slot preservation across ASR and template rendering."""

    description: str
    spoken_phrase: str
    expected_critical_tokens: tuple[str, ...]
    expected_rendered_template: str


COMPREHENSION_FIXTURES: tuple[AudioComprehensionTestCase, ...] = (
    AudioComprehensionTestCase(
        description="Rupee price bound with 'under' operator",
        spoken_phrase="find black backpack under 1500 rupees",
        expected_critical_tokens=("black", "backpack", "under", "1500", "rupees"),
        expected_rendered_template="Found black backpack under ₹1500.",
    ),
    AudioComprehensionTestCase(
        description="Rupee price bound with 'at most' operator",
        spoken_phrase="show blue shirt at most 2000 rupees",
        expected_critical_tokens=("blue", "shirt", "at most", "2000", "rupees"),
        expected_rendered_template="Found blue shirt at most ₹2000.",
    ),
    AudioComprehensionTestCase(
        description="Hyphenated SKU exact identification",
        spoken_phrase="add variant SKU-BLK-101 to cart",
        expected_critical_tokens=("add", "variant", "SKU-BLK-101", "cart"),
        expected_rendered_template="Added SKU-BLK-101 to your cart.",
    ),
    AudioComprehensionTestCase(
        description="Negation preservation (don't add)",
        spoken_phrase="search cheap shoes but don't add to cart",
        expected_critical_tokens=("search", "cheap", "shoes", "don't add"),
        expected_rendered_template="Found cheap shoes. Did not add to cart as requested.",
    ),
)


class MockVAD(VADProtocol):
    """Simulates speech activity detection with configurable silence/speech frames."""

    def __init__(self, speech_frames: int = 5, silence_frames_for_endpoint: int = 3) -> None:
        self.speech_frames = speech_frames
        self.silence_frames_for_endpoint = silence_frames_for_endpoint
        self._frames_seen = 0
        self._speech_detected = False

    def process_frame(self, chunk: AudioChunk) -> VADEvent:
        self._frames_seen += 1
        t = chunk.timestamp_s
        if self._frames_seen <= self.speech_frames:
            self._speech_detected = True
            return VADEvent(VADState.SPEECH, timestamp_s=t, speech_duration_s=0.1 * self._frames_seen)

        silence_count = self._frames_seen - self.speech_frames
        if silence_count >= self.silence_frames_for_endpoint:
            return VADEvent(
                VADState.ENDPOINT_DETECTED,
                timestamp_s=t,
                speech_duration_s=0.1 * self.speech_frames,
                silence_duration_s=0.1 * silence_count,
            )
        return VADEvent(VADState.SILENCE, timestamp_s=t, silence_duration_s=0.1 * silence_count)

    def reset(self) -> None:
        self._frames_seen = 0
        self._speech_detected = False


class MockSpeechRecognizer(SpeechRecognizerProtocol):
    """Simulates whisper.cpp ASR with programmable transcripts and latency."""

    def __init__(
        self,
        transcript_text: str = "find backpack under 2000 rupees",
        simulated_latency_s: float = 0.05,
        kind: TranscriptKind = TranscriptKind.FINAL,
        metadata: ArtifactMetadata = PINNED_WHISPER_BASE_EN,
    ) -> None:
        self._text = transcript_text
        self._latency_s = simulated_latency_s
        self._kind = kind
        self._metadata = metadata

    @property
    def metadata(self) -> ArtifactMetadata:
        return self._metadata

    def transcribe(self, audio_data: bytes, turn_id: str) -> Transcript:
        if self._latency_s > 0:
            time.sleep(self._latency_s)
        return Transcript(
            kind=self._kind,
            text=self._text,
            turn_id=turn_id,
            confidence=0.98,
        )


class MockSpeechSynthesizer(SpeechSynthesizerProtocol):
    """Simulates OHF Piper TTS with chunked synthesis and simulated failures."""

    def __init__(
        self,
        simulated_latency_s: float = 0.02,
        chunks_per_response: int = 3,
        should_fail: bool = False,
        metadata: ArtifactMetadata = PINNED_PIPER_LJ_MEDIUM,
    ) -> None:
        self._latency_s = simulated_latency_s
        self._chunks_count = chunks_per_response
        self._should_fail = should_fail
        self._metadata = metadata

    @property
    def metadata(self) -> ArtifactMetadata:
        return self._metadata

    def synthesize(self, text: str) -> Iterable[AudioChunk]:
        if self._should_fail:
            raise RuntimeError("Simulated neural TTS synthesis engine failure")

        if self._latency_s > 0:
            time.sleep(self._latency_s)

        for i in range(self._chunks_count):
            yield AudioChunk(
                pcm_data=f"PCM-DATA-{i}-{text}".encode(),
                sample_rate_hz=self._metadata.sample_rate_hz,
                channels=1,
            )


class MockAudioOutput(AudioOutputProtocol):
    """Simulates speakers with audible onset timing detection."""

    def __init__(self) -> None:
        self.played_chunks: list[AudioChunk] = []
        self._playing = False
        self.audible_onset_time: float = 0.0

    def play_chunk(self, chunk: AudioChunk) -> None:
        if not self.played_chunks:
            self.audible_onset_time = time.monotonic()
        self.played_chunks.append(chunk)
        self._playing = True

    def stop_playback(self) -> None:
        self._playing = False

    def is_playing(self) -> bool:
        return self._playing
