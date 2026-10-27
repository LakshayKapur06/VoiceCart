"""Scripted protocol fixtures. Synthetic PCM is not speech or model evidence."""

from __future__ import annotations

import time
from collections.abc import Iterable

from voicecart.audio import (
    ArtifactMetadata,
    AudioChunk,
    Transcript,
    TranscriptKind,
    VADEvent,
    VADState,
)

# Candidates only: no downloaded artifact/hash, hardware test or clearance implied.
REFERENCE_WHISPER_BASE_EN = ArtifactMetadata(
    name="whisper.cpp-base.en",
    version="unverified",
    licence="MIT",
    language="en",
    sample_rate_hz=16000,
    artifact_kind="runtime/model candidate",
    source_url="https://github.com/ggml-org/whisper.cpp",
)
REFERENCE_PIPER_RUNTIME = ArtifactMetadata(
    name="OHF Piper",
    version="unverified",
    licence="GPL-3.0",
    language="voice-dependent",
    sample_rate_hz=None,
    artifact_kind="runtime candidate",
    source_url="https://github.com/OHF-Voice/piper1-gpl",
)
REFERENCE_LJ_VOICE = ArtifactMetadata(
    name="en_US-ljspeech-medium",
    version="unverified",
    licence="Dataset: public domain; voice distribution terms require verification",
    language="en_US",
    sample_rate_hz=22050,
    artifact_kind="voice candidate",
    source_url="https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/medium/MODEL_CARD",
)

# Lookup keys are synthetic PCM, not recordings. Transcripts and expected slot
# assertions are maintained separately so the integration actually invokes ASR.
SCRIPTED_TRANSCRIPTS = {
    b"\x01\x00" * 160: "find black backpack under 1500 rupees",
    b"\x02\x00" * 160: "show blue shirt at most 2000 rupees",
    b"\x03\x00" * 160: "find variant SKU-BLK-101",
    b"\x04\x00" * 160: "search cheap shoes but don't add to cart",
}


class MockSpeechRecognizer:
    def __init__(
        self,
        transcript_text="find backpack under 2000 rupees",
        *,
        kind=TranscriptKind.FINAL,
    ):
        self.text = transcript_text
        self.kind = kind
        self.calls = 0

    @property
    def metadata(self) -> ArtifactMetadata:
        return REFERENCE_WHISPER_BASE_EN

    def transcribe(self, audio_data: bytes, turn_id: str) -> Transcript:
        self.calls += 1
        text = self.text if self.text is not None else SCRIPTED_TRANSCRIPTS[audio_data]
        return Transcript(self.kind, text, turn_id, confidence=0.98)


class MockSpeechSynthesizer:
    def __init__(self, *, chunks_per_response=3, should_fail=False):
        self.chunks_count = chunks_per_response
        self.should_fail = should_fail
        self.spoken_texts: list[str] = []

    @property
    def metadata(self) -> ArtifactMetadata:
        return REFERENCE_LJ_VOICE

    def synthesize(self, text: str) -> Iterable[AudioChunk]:
        self.spoken_texts.append(text)
        if self.should_fail:
            raise RuntimeError("Simulated synthesis failure")
        for _ in range(self.chunks_count):
            yield AudioChunk(b"\x01\x00" * 220, 22050)


class MockAudioOutput:
    """Simulated onset only; no speaker/acoustic measurement occurs."""

    def __init__(self):
        self.played_chunks: list[AudioChunk] = []
        self._playing = False
        self.audible_onset_time: float | None = None
        self.stop_calls = 0
        self.begin_calls: list[str] = []
        self.generation: str | None = None
        self.on_play = None
        self.on_drain = None

    def begin_playback(self, turn_id: str) -> None:
        self.begin_calls.append(turn_id)
        self.generation = turn_id
        self.audible_onset_time = None

    def play_chunk(self, chunk: AudioChunk) -> None:
        if self.audible_onset_time is None:
            self.audible_onset_time = time.monotonic()
        self.played_chunks.append(chunk)
        self._playing = True
        if self.on_play:
            self.on_play()

    def drain(self, turn_id: str) -> float | None:
        onset = self.audible_onset_time
        if self.on_drain:
            self.on_drain()
        if self.generation == turn_id:
            self._playing = False
        return onset

    def stop_playback(self) -> None:
        self.stop_calls += 1
        self.generation = None
        self._playing = False

    def is_playing(self) -> bool:
        return self._playing


class MockAudioInput:
    def __init__(self):
        self.capturing = False

    def start_capture(self):
        self.capturing = True

    def stop_capture(self):
        self.capturing = False

    def read_chunk(self):
        return None


class MockVAD:
    def __init__(self, speech_frames=3, silence_frames_for_endpoint=2):
        self.speech_frames = speech_frames
        self.silence_frames_for_endpoint = silence_frames_for_endpoint
        self.reset()

    def process_frame(self, chunk: AudioChunk) -> VADEvent:
        self.frames_seen += 1
        if self.frames_seen <= self.speech_frames:
            state = VADState.SPEECH
        elif self.frames_seen - self.speech_frames >= self.silence_frames_for_endpoint:
            state = VADState.ENDPOINT_DETECTED
        else:
            state = VADState.SILENCE
        return VADEvent(state, chunk.timestamp_s)

    def reset(self):
        self.frames_seen = 0
