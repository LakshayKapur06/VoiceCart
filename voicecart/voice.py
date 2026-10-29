"""Real optional local speech/device adapters; no implicit downloads or recordings."""

from __future__ import annotations

import hashlib
import queue
import threading
import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from importlib.metadata import version
from pathlib import Path
from typing import Any

from voicecart.application import Response
from voicecart.audio import (
    ArtifactMetadata,
    AudioChunk,
    CachedSpeechPrompt,
    HalfDuplexTurnController,
    Transcript,
    TranscriptKind,
    TurnState,
)


class VoiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class FileArtifact:
    path: Path
    sha256: str
    source_url: str | None = None
    licence: str = "unverified"

    def verify(self) -> Path:
        if len(self.sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.sha256
        ):
            raise VoiceError("A lowercase SHA-256 artifact digest is required")
        digest = hashlib.sha256()
        with self.path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
        if digest.hexdigest() != self.sha256:
            raise VoiceError("Local artifact integrity check failed")
        return self.path


class WhisperRecognizer:
    def __init__(self, artifact: FileArtifact):
        from pywhispercpp.model import ContextParams, Model

        path = artifact.verify()
        self.runtime_version = version("pywhispercpp")
        self._metadata = ArtifactMetadata(
            path.name,
            artifact.sha256,
            artifact.licence,
            "en",
            16000,
            artifact_kind="ASR model",
            source_url=artifact.source_url,
            sha256=artifact.sha256,
        )
        self._model = Model(
            str(path),
            models_dir=str(path.parent),
            context_params=ContextParams(use_gpu=False),
            print_progress=False,
            print_realtime=False,
            print_timestamps=False,
            language="en",
            no_context=True,
        )
        self._lock = threading.Lock()

    @property
    def metadata(self) -> ArtifactMetadata:
        return self._metadata

    def transcribe(
        self,
        audio_data: bytes,
        turn_id: str,
        *,
        cancelled: threading.Event | None = None,
    ) -> Transcript:
        import numpy as np

        if not audio_data or len(audio_data) % 2 or len(audio_data) > 16000 * 2 * 60:
            raise VoiceError(
                "ASR requires nonempty mono signed 16-bit PCM at 16 kHz, at most 60 seconds"
            )
        with self._lock:
            samples = (
                np.frombuffer(audio_data, dtype="<i2").astype(np.float32) / 32768.0
            )
            segments = self._model.transcribe(
                samples,
                abort_callback=cancelled.is_set if cancelled is not None else None,
            )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return Transcript(
            TranscriptKind.FINAL if text else TranscriptKind.NO_SPEECH, text, turn_id
        )


class PiperSynthesizer:
    def __init__(self, voice: FileArtifact, config: FileArtifact):
        import onnxruntime

        onnxruntime.disable_telemetry_events()
        from piper import PiperVoice

        voice_path, config_path = voice.verify(), config.verify()
        self.runtime_version = version("piper-tts")
        self._voice = PiperVoice.load(voice_path, config_path=config_path)
        self._metadata = ArtifactMetadata(
            voice_path.name,
            voice.sha256,
            voice.licence,
            "en_US",
            self._voice.config.sample_rate,
            artifact_kind="voice model",
            source_url=voice.source_url,
            sha256=voice.sha256,
        )
        self._lock = threading.Lock()

    @property
    def metadata(self) -> ArtifactMetadata:
        return self._metadata

    def synthesize(self, text: str) -> Iterable[AudioChunk]:
        if not text.strip() or len(text) > 3000:
            raise VoiceError("Response text must be nonempty and bounded")
        with self._lock:
            for chunk in self._voice.synthesize(text):
                if chunk.sample_width != 2:
                    raise VoiceError("Piper returned an unsupported PCM width")
                yield AudioChunk(
                    chunk.audio_int16_bytes, chunk.sample_rate, chunk.sample_channels
                )


class MicrophoneInput:
    """Explicit bounded capture; no continuous ambient listening or file logging."""

    def __init__(self, *, max_seconds: int = 30):
        if type(max_seconds) is not int or not 1 <= max_seconds <= 60:
            raise ValueError("Capture duration must be 1–60 seconds")
        self.max_bytes = max_seconds * 16000 * 2
        self._stream: Any = None
        self._chunks: list[AudioChunk] = []
        self._bytes = 0
        self._lock = threading.Lock()
        self.overflow = False

    def start_capture(self) -> None:
        import sounddevice as sd

        self.stop_capture()
        with self._lock:
            self._chunks.clear()
            self._bytes = 0
            self.overflow = False

        def callback(data, frames, timing, status):
            pcm = bytes(data)
            with self._lock:
                if status or self._bytes + len(pcm) > self.max_bytes:
                    self.overflow = True
                    raise sd.CallbackStop
                self._chunks.append(AudioChunk(pcm, 16000))
                self._bytes += len(pcm)

        self._stream = sd.RawInputStream(
            samplerate=16000,
            channels=1,
            dtype="int16",
            blocksize=320,
            callback=callback,
        )
        self._stream.start()

    def stop_capture(self) -> None:
        stream, self._stream = self._stream, None
        if stream is not None:
            try:
                stream.stop()
            finally:
                stream.close()

    def read_chunk(self) -> AudioChunk | None:
        with self._lock:
            return self._chunks.pop(0) if self._chunks else None

    def take_pcm(self) -> bytes:
        self.stop_capture()
        with self._lock:
            data = b"".join(chunk.pcm_data for chunk in self._chunks)
            self._chunks.clear()
            self._bytes = 0
            if self.overflow:
                raise VoiceError(
                    "Capture overflowed or the device dropped audio; repeat a shorter request"
                )
            return data


@dataclass
class _OutputJob:
    turn_id: str
    chunks: queue.Queue = field(default_factory=lambda: queue.Queue(maxsize=32))
    cancelled: threading.Event = field(default_factory=threading.Event)
    finished: threading.Event = field(default_factory=threading.Event)
    stream: Any = None
    error: Exception | None = None
    enqueued: bool = False
    worker: threading.Thread | None = None


class SoundDeviceOutput:
    """Blocking device writes run in a worker; controller enqueue stays bounded.

    Completion is device drain, not enqueue. PortAudio is not acoustic loopback
    calibration: drain deliberately returns None for actual audible onset.
    """

    def __init__(self, *, driver=None):
        if driver is None:
            import sounddevice

            driver = sounddevice
        self._driver = driver
        self._job: _OutputJob | None = None
        self._lock = threading.RLock()

    def _play(self, job: _OutputJob) -> None:
        sd = self._driver
        stream = None
        audio_format = None
        try:
            while not job.cancelled.is_set():
                try:
                    chunk = job.chunks.get(timeout=0.1)
                except queue.Empty:
                    continue
                if chunk is None or job.cancelled.is_set():
                    break
                if stream is None:
                    audio_format = chunk.sample_rate_hz, chunk.channels
                    stream = sd.RawOutputStream(
                        samplerate=chunk.sample_rate_hz,
                        channels=chunk.channels,
                        dtype="int16",
                    )
                    job.stream = stream
                    if job.cancelled.is_set():
                        break
                    stream.start()
                if audio_format != (chunk.sample_rate_hz, chunk.channels):
                    raise VoiceError("PCM format changed during a response")
                if job.cancelled.is_set():
                    stream.abort()
                    break
                stream.write(chunk.pcm_data)
            if stream is not None:
                stream.abort() if job.cancelled.is_set() else stream.stop()
        except Exception as exc:
            if not job.cancelled.is_set():
                job.error = exc
        finally:
            try:
                if stream is not None:
                    stream.close()
            except Exception as exc:
                job.error = exc
            finally:
                job.stream = None
                job.finished.set()

    def begin_playback(self, turn_id: str) -> None:
        with self._lock:
            if self._job is not None and not self._job.finished.is_set():
                raise VoiceError("An output stream is already active")
            job = _OutputJob(turn_id)
            job.worker = threading.Thread(target=self._play, args=(job,), daemon=True)
            self._job = job
            job.worker.start()

    def play_chunk(self, chunk: AudioChunk) -> None:
        with self._lock:
            job = self._job
            if (
                job is None
                or job.cancelled.is_set()
                or job.error is not None
                or job.finished.is_set()
            ):
                raise VoiceError("Audio output unavailable")
            if len(chunk.pcm_data) > 2 * 1024 * 1024:
                raise VoiceError("PCM chunk exceeds the output bound")
            try:
                job.chunks.put_nowait(chunk)
            except queue.Full as exc:
                raise VoiceError("Audio output queue is full") from exc
            job.enqueued = True

    def drain(self, turn_id: str) -> None:
        with self._lock:
            job = self._job
            if job is None or job.turn_id != turn_id:
                return None
            try:
                job.chunks.put_nowait(None)
            except queue.Full as exc:
                raise VoiceError("Audio drain queue is full") from exc
        if not job.finished.wait(120):
            self.stop_playback()
            raise TimeoutError("Playback exceeded its deadline")
        if job.error is not None:
            raise VoiceError("Playback device failed") from job.error
        with self._lock:
            if self._job is job:
                self._job = None
        return None

    def stop_playback(self) -> None:
        with self._lock:
            job = self._job
            if job is None:
                return
            job.cancelled.set()
            while True:
                try:
                    job.chunks.get_nowait()
                except queue.Empty:
                    break
            if job.stream is not None:
                stream = job.stream

                def abort():
                    try:
                        stream.abort()
                    except Exception as exc:
                        job.error = exc  # Drain reports failed native cancellation.

                threading.Thread(target=abort, daemon=True).start()
        if not job.finished.wait(0.5):
            raise VoiceError("Device did not acknowledge stop; recovery required")
        with self._lock:
            if self._job is job:
                self._job = None

    def is_playing(self) -> bool:
        with self._lock:
            return (
                self._job is not None
                and self._job.enqueued
                and not self._job.finished.is_set()
            )


@dataclass(frozen=True)
class Delivery:
    kind: str
    audible_onset: float | None = None


class ResponseSpeaker:
    """All app success/error/clarification responses use this same output path."""

    def __init__(
        self,
        controller: HalfDuplexTurnController,
        synthesizer,
        output,
        *,
        fallback: CachedSpeechPrompt | None = None,
    ):
        self.controller, self.synthesizer, self.fallback = (
            controller,
            synthesizer,
            fallback,
        )
        controller.bind_output(output)

    def deliver(self, response: Response) -> Delivery:
        if not response.text:
            return Delivery("cancelled")
        token = str(uuid.uuid4())
        try:
            if not self.controller.start_system_response(response.text, turn_id=token):
                return Delivery("assistive_only")
            count = 0
            phase = "tts"
            try:
                for chunk in self.synthesizer.synthesize(response.text):
                    phase = "output"
                    if not self.controller.enqueue_audio(token, chunk):
                        return Delivery("cancelled")
                    count += 1
                    phase = "tts"
                if not count:
                    raise VoiceError("TTS produced no audio")
            except Exception:
                if not self.controller.is_active(token, TurnState.SPEAKING):
                    return Delivery("cancelled")
                if phase != "tts" or self.fallback is None:
                    raise
                if not self.controller.restart_fallback(token, self.fallback.text):
                    return Delivery("cancelled")
                self.controller.enqueue_audio(token, self.fallback.chunk)
                completed, onset = self.controller.finish_speaking(token)
                return Delivery(
                    "fallback_completed" if completed else "cancelled", onset
                )
            completed, onset = self.controller.finish_speaking(token)
            return Delivery("response_completed" if completed else "cancelled", onset)
        except Exception:
            self.controller.fail_turn(
                token,
                "Speech unavailable. Read the accessible text response or retry; this does not repeat the cart operation.",
                audio_failed=True,
            )
            return Delivery(
                "assistive_only" if self.controller.is_session_usable() else "unusable"
            )
