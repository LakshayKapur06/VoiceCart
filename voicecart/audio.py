"""Sprint 2 audio contracts and simulated integration, not device feasibility proof."""

from __future__ import annotations

import io
import math
import time
import wave
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field, replace
from enum import StrEnum
from statistics import median
from threading import RLock
from typing import Protocol, TypeGuard

from voicecart.domain import require_integer, require_text


def _finite_time(value: object) -> TypeGuard[float]:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def _interval(start: float | None, end: float | None) -> float | None:
    if not _finite_time(start) or not _finite_time(end) or end < start:
        return None
    return end - start


class TurnState(StrEnum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"


class TranscriptKind(StrEnum):
    PARTIAL = "partial"
    FINAL = "final"
    SILENCE_TIMEOUT = "silence_timeout"
    NO_SPEECH = "no_speech"
    ERROR = "error"


class VADState(StrEnum):
    SILENCE = "silence"
    SPEECH = "speech"
    ENDPOINT_DETECTED = "endpoint_detected"


class StatusPriority(StrEnum):
    POLITE = "polite"
    ASSERTIVE = "assertive"


@dataclass(frozen=True)
class AudioChunk:
    """PCM audio buffer chunk with explicit audio format and timing."""

    pcm_data: bytes
    sample_rate_hz: int
    channels: int = 1
    timestamp_s: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        if not isinstance(self.pcm_data, bytes):
            raise TypeError("pcm_data must be bytes")
        require_integer(self.sample_rate_hz, "sample_rate_hz", minimum=8000)
        require_integer(self.channels, "channels", minimum=1)
        if not self.pcm_data or len(self.pcm_data) % (2 * self.channels):
            raise ValueError("PCM must contain complete, nonempty signed 16-bit frames")
        if not _finite_time(self.timestamp_s):
            raise ValueError("timestamp_s must be finite and nonnegative")

    @property
    def duration_s(self) -> float:
        bytes_per_sample = 2  # 16-bit PCM reference
        total_samples = len(self.pcm_data) / (bytes_per_sample * self.channels)
        return total_samples / self.sample_rate_hz


@dataclass(frozen=True)
class VADEvent:
    state: VADState
    timestamp_s: float
    speech_duration_s: float = 0.0
    silence_duration_s: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.state, VADState):
            raise TypeError("state must be VADState")
        if not all(
            _finite_time(t)
            for t in (self.timestamp_s, self.speech_duration_s, self.silence_duration_s)
        ):
            raise ValueError("VAD times must be finite and nonnegative")


@dataclass(frozen=True)
class Transcript:
    """Spoken transcript event.

    CRITICAL INVARIANT: Only FINAL transcripts with matching turn ID
    can authorize application actions. Partial transcripts never authorize actions.
    """

    kind: TranscriptKind
    text: str
    turn_id: str
    confidence: float | None = None
    timestamp_s: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, TranscriptKind):
            raise TypeError("kind must be TranscriptKind")
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        require_text(self.turn_id, "turn_id")
        if not _finite_time(self.timestamp_s):
            raise ValueError("timestamp_s must be finite and nonnegative")
        if self.confidence is not None and (
            not _finite_time(self.confidence) or self.confidence > 1
        ):
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def is_final(self) -> bool:
        return self.kind is TranscriptKind.FINAL

    @property
    def can_authorize_action(self) -> bool:
        """Partial, silence, error, or empty transcripts can NEVER authorize actions."""
        return self.is_final and bool(self.text.strip())


@dataclass(frozen=True)
class AssistiveStatusMessage:
    """Screen-reader and assistive technology status channel message."""

    text: str
    priority: StatusPriority = StatusPriority.POLITE
    timestamp_s: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        require_text(self.text, "text")
        if not isinstance(self.priority, StatusPriority):
            raise TypeError("priority must be StatusPriority")


@dataclass(frozen=True)
class TurnControlOutcome:
    """Result of an explicit control action (e.g. stop, repeat)."""

    action_name: str
    success: bool
    stopped_playback: bool
    action_undone: bool
    message: str


@dataclass(frozen=True)
class ArtifactMetadata:
    """Declared runtime/voice identity; the host must verify actual artifact bytes."""

    name: str
    version: str
    licence: str
    language: str
    sample_rate_hz: int | None
    is_commercial_eligible: bool | None = None
    artifact_kind: str = "candidate"
    source_url: str | None = None
    sha256: str | None = None

    def __post_init__(self) -> None:
        require_text(self.name, "name")
        require_text(self.version, "version")
        require_text(self.licence, "licence")
        require_text(self.language, "language")
        require_text(self.artifact_kind, "artifact_kind")
        if self.source_url is not None:
            require_text(self.source_url, "source_url")
        if self.sample_rate_hz is not None:
            require_integer(self.sample_rate_hz, "sample_rate_hz", minimum=8000)
        if (
            self.is_commercial_eligible is not None
            and type(self.is_commercial_eligible) is not bool
        ):
            raise TypeError("is_commercial_eligible must be bool or None")
        if self.sha256 is not None and (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(c not in "0123456789abcdef" for c in self.sha256)
        ):
            raise ValueError("sha256 must be a lowercase hexadecimal digest")

    @property
    def is_pinned(self) -> bool:
        return bool(self.source_url and self.sha256)


@dataclass
class LatencyTrace:
    """Optional monotonic timestamps. Missing/invalid timings never count as zero."""

    turn_id: str
    is_warm: bool = True
    t_turn_start: float | None = None
    t_speech_start: float | None = None
    t_speech_end: float | None = None
    t_endpoint_detected: float | None = None
    t_asr_start: float | None = None
    t_asr_end: float | None = None
    t_template_start: float | None = None
    t_template_end: float | None = None
    t_tts_start: float | None = None
    t_first_pcm_chunk: float | None = None
    t_audible_onset: float | None = None
    failed: bool = False
    failure_reason: str | None = None
    timed_out: bool = False
    cancelled: bool = False

    def __post_init__(self) -> None:
        require_text(self.turn_id, "turn_id")
        for flag in (self.is_warm, self.failed, self.timed_out, self.cancelled):
            if type(flag) is not bool:
                raise TypeError("Trace flags must be bool")

    @property
    def endpoint_delay_s(self) -> float | None:
        return _interval(self.t_speech_end, self.t_endpoint_detected)

    @property
    def asr_latency_s(self) -> float | None:
        return _interval(self.t_asr_start, self.t_asr_end)

    @property
    def tts_to_first_audio_s(self) -> float | None:
        return _interval(self.t_tts_start, self.t_first_pcm_chunk)

    @property
    def audible_onset_latency_s(self) -> float | None:
        return _interval(self.t_speech_end, self.t_audible_onset)

    @property
    def has_valid_timing(self) -> bool:
        ordered = (
            self.t_turn_start,
            self.t_speech_start,
            self.t_speech_end,
            self.t_endpoint_detected,
            self.t_asr_start,
            self.t_asr_end,
            self.t_template_start,
            self.t_template_end,
            self.t_tts_start,
            self.t_first_pcm_chunk,
            self.t_audible_onset,
        )
        present = [t for t in ordered if t is not None]
        return (
            self.audible_onset_latency_s is not None
            and all(_finite_time(t) for t in present)
            and all(a <= b for a, b in zip(present, present[1:], strict=False))
        )

    @property
    def is_successful(self) -> bool:
        return self.has_valid_timing and not (
            self.failed or self.timed_out or self.cancelled
        )

    @property
    def meets_1500ms_target(self) -> bool:
        latency = self.audible_onset_latency_s
        return self.is_successful and latency is not None and latency < 1.5


@dataclass(frozen=True)
class LatencyBenchmarkSummary:
    """Disjoint outcome counts; every recorded turn stays in the denominator."""

    total_turns: int
    successful_turns: int
    failed_turns: int
    timeout_turns: int
    cancelled_turns: int
    cold_turns: int
    warm_turns: int
    p50_audible_onset_s: float | None
    p95_audible_onset_s: float | None
    max_audible_onset_s: float | None
    target_1500ms_pass_rate: float


class AudioInputProtocol(Protocol):
    def start_capture(self) -> None: ...
    def read_chunk(self) -> AudioChunk | None: ...
    def stop_capture(self) -> None: ...


class AudioOutputProtocol(Protocol):
    """Single-owner output. Begin/enqueue/stop must be short and nonblocking.

    drain waits for completion (or stop) and returns device-measured onset in the
    trace's monotonic clock, or None if unavailable. Enqueue time is not onset.
    Adapters must flush pending buffers on stop, including during drain.
    Each drain is scoped to its turn and must never alter a newer stream.
    """

    def begin_playback(self, turn_id: str) -> None: ...
    def play_chunk(self, chunk: AudioChunk) -> None: ...
    def drain(self, turn_id: str) -> float | None: ...
    def stop_playback(self) -> None: ...
    def is_playing(self) -> bool: ...


class VADProtocol(Protocol):
    def process_frame(self, chunk: AudioChunk) -> VADEvent: ...
    def reset(self) -> None: ...


class SpeechRecognizerProtocol(Protocol):
    @property
    def metadata(self) -> ArtifactMetadata: ...
    def transcribe(self, audio_data: bytes, turn_id: str) -> Transcript: ...


class SpeechSynthesizerProtocol(Protocol):
    @property
    def metadata(self) -> ArtifactMetadata: ...
    def synthesize(self, text: str) -> Iterable[AudioChunk]: ...


@dataclass(frozen=True)
class CachedSpeechPrompt:
    """Host-provisioned speech asset. Format checks do not prove intelligibility.

    The host must verify spoken text, provenance and distribution terms before
    supplying this asset. There is deliberately no fabricated default recording.
    """

    text: str
    chunk: AudioChunk

    def __post_init__(self) -> None:
        require_text(self.text, "text")
        if not isinstance(self.chunk, AudioChunk):
            raise TypeError("chunk must be AudioChunk")

    @classmethod
    def from_wav(cls, text: str, wav_data: bytes) -> CachedSpeechPrompt:
        try:
            with wave.open(io.BytesIO(wav_data), "rb") as recording:
                if recording.getsampwidth() != 2 or recording.getcomptype() != "NONE":
                    raise ValueError(
                        "Fallback WAV must be uncompressed signed 16-bit PCM"
                    )
                frames = recording.readframes(recording.getnframes())
                if len(frames) != recording.getnframes() * recording.getnchannels() * 2:
                    raise ValueError("Truncated fallback WAV")
                chunk = AudioChunk(
                    frames, recording.getframerate(), recording.getnchannels()
                )
        except (wave.Error, EOFError) as exc:
            raise ValueError("Invalid fallback WAV") from exc
        return cls(text, chunk)


class HalfDuplexTurnController:
    """Turn tokens fence transcript acceptance, output and late completion callbacks.

    Ports are single-owner. Blocking inference/drain runs outside the state lock
    so explicit stop can invalidate the turn and flush playback concurrently.
    The optional status sink must enqueue quickly; its buffer is not a UI itself.
    """

    def __init__(
        self,
        *,
        audio_input: AudioInputProtocol | None = None,
        status_sink: Callable[[AssistiveStatusMessage], None] | None = None,
    ) -> None:
        self._lock = RLock()
        self._state = TurnState.IDLE
        self._current_turn_id: str | None = None
        self._used_turn_ids: set[str] = set()
        self._consumed = False
        self._last_verified_response: str | None = None
        self._pending_response: str | None = None
        self._audio_enqueued = False
        self._status_messages: list[AssistiveStatusMessage] = []
        self._audio_channel_healthy = True
        self._assistive_channel_healthy = True
        self._input = audio_input
        self._output: AudioOutputProtocol | None = None
        self._status_sink = status_sink

    @property
    def state(self) -> TurnState:
        with self._lock:
            return self._state

    @property
    def current_turn_id(self) -> str | None:
        with self._lock:
            return self._current_turn_id

    @property
    def is_capture_gated(self) -> bool:
        with self._lock:
            return self._state not in (
                TurnState.IDLE,
                TurnState.LISTENING,
                TurnState.STOPPED,
            )

    @property
    def status_messages(self) -> tuple[AssistiveStatusMessage, ...]:
        with self._lock:
            return tuple(self._status_messages)

    def bind_output(self, output: AudioOutputProtocol) -> None:
        with self._lock:
            if self._output is not None and self._output is not output:
                raise ValueError("Controller already owns an output")
            self._output = output

    def is_active(self, turn_id: str, state: TurnState | None = None) -> bool:
        with self._lock:
            return (
                turn_id == self._current_turn_id
                and self.is_session_usable()
                and (state is None or self._state is state)
            )

    def can_receive_transcript(self, turn_id: str) -> bool:
        with self._lock:
            return (
                self.is_active(turn_id)
                and not self._consumed
                and self._state in (TurnState.LISTENING, TurnState.PROCESSING)
            )

    def is_session_usable(self) -> bool:
        with self._lock:
            return self._audio_channel_healthy or self._assistive_channel_healthy

    def _halt_ports(self) -> bool:
        stopped = True
        if self._input is not None:
            try:
                self._input.stop_capture()
            except Exception:
                stopped = False
                self._audio_channel_healthy = False
        if self._output is not None:
            try:
                self._output.stop_playback()
            except Exception:
                stopped = False
                self._audio_channel_healthy = False
        return stopped

    def _retire(self, state: TurnState) -> None:
        self._current_turn_id = None
        self._pending_response = None
        self._audio_enqueued = False
        self._state = state

    def _check_health(self) -> None:
        if not self.is_session_usable():
            self._retire(TurnState.FAILED)
            self._halt_ports()

    def set_channel_health(self, *, audio: bool, assistive: bool) -> None:
        if type(audio) is not bool or type(assistive) is not bool:
            raise TypeError("Channel health must be bool")
        with self._lock:
            self._audio_channel_healthy = audio
            self._assistive_channel_healthy = assistive
            self._check_health()

    def _emit_status(
        self, text: str, priority: StatusPriority = StatusPriority.POLITE
    ) -> None:
        if self._assistive_channel_healthy:
            message = AssistiveStatusMessage(text, priority)
            self._status_messages.append(message)
            if self._status_sink is not None:
                try:
                    self._status_sink(message)
                except Exception:
                    self._assistive_channel_healthy = False
                    self._check_health()

    def start_listening(self, turn_id: str) -> None:
        require_text(turn_id, "turn_id")
        with self._lock:
            if not self.is_session_usable() or self._state in (
                TurnState.PAUSED,
                TurnState.SPEAKING,
                TurnState.FAILED,
            ):
                raise RuntimeError("Session must be usable and ready before listening")
            if turn_id in self._used_turn_ids:
                raise ValueError("Turn IDs must be unique within a session")
            self._retire(TurnState.IDLE)
            if not self._halt_ports():
                self._retire(TurnState.FAILED)
                self._emit_status(
                    "Audio device could not stop. Recovery required.",
                    StatusPriority.ASSERTIVE,
                )
                raise RuntimeError("Audio device recovery required before listening")
            self._check_health()
            if not self.is_session_usable():
                raise RuntimeError(
                    "Audio capture failed and no assistive channel is available"
                )
            self._used_turn_ids.add(turn_id)
            self._current_turn_id = turn_id
            self._consumed = False
            self._state = TurnState.LISTENING
            if self._input is not None:
                try:
                    self._input.start_capture()
                except Exception:
                    self.fail_turn(
                        turn_id, "Audio capture unavailable.", audio_failed=True
                    )
                    return
            self._emit_status(f"Listening for turn {turn_id}")

    def end_turn_manually(self, turn_id: str) -> None:
        with self._lock:
            if not self.is_active(turn_id, TurnState.LISTENING):
                return
            self._state = TurnState.PROCESSING
            if self._input is not None:
                try:
                    self._input.stop_capture()
                except Exception:
                    self.fail_turn(
                        turn_id, "Audio capture unavailable.", audio_failed=True
                    )
                    return
            self._emit_status("Speech input ended. Processing request...")

    def on_vad_endpoint(self, turn_id: str) -> None:
        self.end_turn_manually(turn_id)

    def process_transcript(self, transcript: Transcript) -> bool:
        with self._lock:
            if not self.can_receive_transcript(transcript.turn_id):
                return False
            if transcript.kind is TranscriptKind.PARTIAL:
                self._emit_status(f"Partial speech: {transcript.text}")
                return False
            self.end_turn_manually(transcript.turn_id)
            if not self.is_active(transcript.turn_id):
                return False
            self._consumed = True
            if not transcript.can_authorize_action:
                self.fail_turn(
                    transcript.turn_id, "No usable speech heard. Please try again."
                )
                return False
            self._emit_status(f"Heard: {transcript.text}")
            return self.is_active(transcript.turn_id, TurnState.PROCESSING)

    def start_speaking(self, response_text: str, *, turn_id: str) -> bool:
        require_text(response_text, "response_text")
        with self._lock:
            if not self.is_active(turn_id, TurnState.PROCESSING) or not self._consumed:
                return False
            if self._output is None:
                raise RuntimeError("An audio output is required for playback")
            self._state = TurnState.SPEAKING
            self._pending_response = response_text
            self._audio_enqueued = False
            self._output.begin_playback(turn_id)
            if not self.is_active(turn_id, TurnState.SPEAKING):
                return False
            self._emit_status(f"Assistant speaking: {response_text}")
            return self.is_active(turn_id, TurnState.SPEAKING)

    def enqueue_audio(self, turn_id: str, chunk: AudioChunk) -> bool:
        if not isinstance(chunk, AudioChunk):
            raise TypeError("Synthesizer must yield AudioChunk")
        with self._lock:
            if not self.is_active(turn_id, TurnState.SPEAKING):
                return False
            self._audio_enqueued = True
            if self._output is None:
                raise RuntimeError("Playback output is not bound")
            self._output.play_chunk(chunk)
            return True

    def finish_speaking(self, turn_id: str) -> tuple[bool, float | None]:
        with self._lock:
            if not self.is_active(turn_id, TurnState.SPEAKING):
                return False, None
            if not self._audio_enqueued:
                raise RuntimeError("Cannot finish an empty playback")
            output = self._output
            if output is None:
                raise RuntimeError("Playback output is not bound")
        onset = output.drain(turn_id)  # Stop can run while this stream drains.
        with self._lock:
            if not self.is_active(turn_id, TurnState.SPEAKING):
                return False, None
            if output.is_playing():
                raise RuntimeError("Output drain returned before playback completed")
            self._last_verified_response = self._pending_response
            self._retire(TurnState.IDLE)
            self._emit_status("Playback finished. Assistant ready.")
            return True, onset

    def fail_turn(
        self, turn_id: str, message: str, *, audio_failed: bool = False
    ) -> None:
        with self._lock:
            if not self.is_active(turn_id):
                return
            self._retire(TurnState.IDLE)
            if not self._halt_ports():
                self._state = TurnState.FAILED
            if audio_failed:
                self._audio_channel_healthy = False
            self._emit_status(message, StatusPriority.ASSERTIVE)
            self._check_health()

    def restart_fallback(self, turn_id: str, text: str) -> bool:
        with self._lock:
            if not self.is_active(turn_id, TurnState.SPEAKING):
                return False
            if self._output is None:
                raise RuntimeError("Playback output is not bound")
            self._output.stop_playback()
            if not self.is_active(turn_id, TurnState.SPEAKING):
                return False
            self._state = TurnState.PROCESSING
            return self.start_speaking(text, turn_id=turn_id)

    def _cancel(
        self, action: str, state: TurnState, message: str
    ) -> TurnControlOutcome:
        with self._lock:
            was_speaking = self._state is TurnState.SPEAKING
            self._retire(state)
            stopped = self._halt_ports()
            if not stopped:
                self._state = TurnState.FAILED
                message = "Audio device could not stop. Recovery required; committed operations cannot be undone by stop."
            self._emit_status(message, StatusPriority.ASSERTIVE)
            self._check_health()
            return TurnControlOutcome(
                action,
                self._state is not TurnState.FAILED,
                was_speaking and stopped,
                False,
                message,
            )

    def stop(self) -> TurnControlOutcome:
        return self._cancel(
            "stop",
            TurnState.STOPPED,
            "Speech stopped. Already committed operations cannot be undone by stop.",
        )

    def pause(self) -> TurnControlOutcome:
        return self._cancel(
            "pause", TurnState.PAUSED, "Session paused; current turn cancelled."
        )

    def resume(self) -> TurnControlOutcome:
        with self._lock:
            usable = self.is_session_usable()
            if usable and self._state in (TurnState.PAUSED, TurnState.FAILED):
                usable = self._halt_ports()
                if not usable:
                    self._state = TurnState.FAILED
                    return TurnControlOutcome(
                        "resume", False, False, False, "Audio device recovery required."
                    )
                self._retire(TurnState.IDLE)
                self._emit_status("Session resumed.")
            usable = self.is_session_usable() and self._state is not TurnState.FAILED
            return TurnControlOutcome(
                "resume",
                usable,
                False,
                False,
                "Session ready." if usable else "No available response channel.",
            )

    def repeat(self) -> str | None:
        """Return completed response text for host playback; never dispatch an action."""
        with self._lock:
            text = self._last_verified_response
            self._emit_status(
                f"Repeating: {text}" if text else "No prior response to repeat."
            )
            return text


class AudioPipelineSlice:
    """Synchronous protocol integration; chunks returned are already sent to output.

    template_fn must only render verified text, with no business mutations.
    Cancellation fences output; it cannot forcibly interrupt a blocking ASR/TTS
    backend call. Those adapters must impose their own deadlines/cancellation.
    """

    ERROR_RESPONSE = "Speech response unavailable. Please try again."

    def __init__(
        self,
        asr: SpeechRecognizerProtocol,
        tts: SpeechSynthesizerProtocol,
        controller: HalfDuplexTurnController,
        output: AudioOutputProtocol,
        *,
        fallback: CachedSpeechPrompt | None = None,
    ) -> None:
        self.asr = asr
        self.tts = tts
        self.controller = controller
        self.fallback = fallback
        controller.bind_output(output)

    def execute_slice(
        self,
        audio_data: bytes,
        turn_id: str,
        template_fn: Callable[[str], str],
        trace: LatencyTrace | None = None,
    ) -> tuple[Transcript, str, list[AudioChunk]]:
        if trace is not None and trace.turn_id != turn_id:
            raise ValueError("Trace must belong to the active turn")
        transcript = Transcript(TranscriptKind.ERROR, "", turn_id)
        chunks: list[AudioChunk] = []

        def failed(reason: str, error: Exception | None = None) -> None:
            if trace is not None:
                trace.failed = True
                trace.failure_reason = reason
                trace.timed_out = trace.timed_out or isinstance(error, TimeoutError)

        def cancelled() -> tuple[Transcript, str, list[AudioChunk]]:
            if trace is not None:
                if self.controller.state is TurnState.FAILED:
                    trace.failed = True
                    trace.failure_reason = trace.failure_reason or "session_unavailable"
                else:
                    trace.cancelled = True
            return transcript, "", chunks

        if not self.controller.can_receive_transcript(turn_id):
            return cancelled()
        self.controller.end_turn_manually(turn_id)
        if not self.controller.is_active(turn_id):
            return cancelled()
        try:
            if trace is not None:
                trace.t_asr_start = time.monotonic()
            transcript = self.asr.transcribe(audio_data, turn_id)
            if not isinstance(transcript, Transcript):
                raise TypeError("ASR must return Transcript")
            if trace is not None:
                trace.t_asr_end = time.monotonic()
        except Exception as exc:
            if not self.controller.is_active(turn_id):
                return cancelled()
            failed("asr_error", exc)
            self.controller.fail_turn(turn_id, self.ERROR_RESPONSE)
            return transcript, self.ERROR_RESPONSE, chunks
        if not self.controller.is_active(turn_id):
            return cancelled()
        if transcript.turn_id != turn_id:
            failed("asr_turn_mismatch")
            self.controller.fail_turn(turn_id, self.ERROR_RESPONSE)
            return transcript, self.ERROR_RESPONSE, chunks
        if not self.controller.process_transcript(transcript):
            if transcript.kind is TranscriptKind.PARTIAL:
                return transcript, "", chunks
            failed("unusable_transcript")
            return transcript, self.ERROR_RESPONSE, chunks
        try:
            if trace is not None:
                trace.t_template_start = time.monotonic()
            response = template_fn(transcript.text)
            require_text(response, "response_text")
            if trace is not None:
                trace.t_template_end = time.monotonic()
        except Exception as exc:
            if not self.controller.is_active(turn_id):
                return cancelled()
            failed("template_error", exc)
            self.controller.fail_turn(turn_id, self.ERROR_RESPONSE)
            return transcript, self.ERROR_RESPONSE, chunks
        if not self.controller.is_active(turn_id):
            return cancelled()
        phase = "output_error"
        try:
            if not self.controller.start_speaking(response, turn_id=turn_id):
                return cancelled()
            if trace is not None:
                trace.t_tts_start = time.monotonic()
            phase = "tts_error"
            for chunk in self.tts.synthesize(response):
                if not self.controller.is_active(turn_id, TurnState.SPEAKING):
                    return cancelled()
                if not isinstance(chunk, AudioChunk):
                    raise TypeError("Synthesizer must yield AudioChunk")
                if trace is not None and trace.t_first_pcm_chunk is None:
                    trace.t_first_pcm_chunk = time.monotonic()
                phase = "output_error"
                if not self.controller.enqueue_audio(turn_id, chunk):
                    return cancelled()
                chunks.append(chunk)
                phase = "tts_error"
            if not self.controller.is_active(turn_id, TurnState.SPEAKING):
                return cancelled()
            if not chunks:
                raise RuntimeError("TTS produced no audio")
            phase = "output_error"
            completed, onset = self.controller.finish_speaking(turn_id)
            if not completed:
                return cancelled()
            if trace is not None:
                trace.t_audible_onset = onset
            return transcript, response, chunks
        except Exception as exc:
            if not self.controller.is_active(turn_id):
                return cancelled()
            failed(phase, exc)
            if phase == "tts_error" and self.fallback is not None:
                try:
                    if not self.controller.restart_fallback(
                        turn_id, self.fallback.text
                    ):
                        return cancelled()
                    if not self.controller.enqueue_audio(turn_id, self.fallback.chunk):
                        return cancelled()
                    completed, onset = self.controller.finish_speaking(turn_id)
                    if not completed:
                        return cancelled()
                    if trace is not None:
                        trace.t_audible_onset = onset
                    return transcript, self.fallback.text, [self.fallback.chunk]
                except Exception as exc:
                    if not self.controller.is_active(turn_id):
                        return cancelled()
                    failed("fallback_output_error", exc)
            self.controller.fail_turn(turn_id, self.ERROR_RESPONSE, audio_failed=True)
            return transcript, self.ERROR_RESPONSE, []


class LatencyBenchmarkRecorder:
    """Snapshot each unique turn, keeping invalid/no-audio samples as failures."""

    def __init__(self) -> None:
        self._traces: dict[str, LatencyTrace] = {}

    def record(self, trace: LatencyTrace) -> None:
        if trace.turn_id in self._traces:
            raise ValueError("Duplicate benchmark turn ID")
        self._traces[trace.turn_id] = replace(trace)

    @property
    def traces(self) -> tuple[LatencyTrace, ...]:
        return tuple(replace(t) for t in self._traces.values())

    def summarize(self) -> LatencyBenchmarkSummary:
        traces = self.traces
        total = len(traces)
        successful = [t for t in traces if t.is_successful]
        latencies = sorted(
            latency
            for t in successful
            if (latency := t.audible_onset_latency_s) is not None
        )
        # Outcomes are disjoint: cancellation, then timeout, then other failure.
        cancelled = sum(t.cancelled for t in traces)
        timeouts = sum(t.timed_out and not t.cancelled for t in traces)
        return LatencyBenchmarkSummary(
            total_turns=total,
            successful_turns=len(successful),
            failed_turns=total - len(successful) - cancelled - timeouts,
            timeout_turns=timeouts,
            cancelled_turns=cancelled,
            cold_turns=sum(not t.is_warm for t in traces),
            warm_turns=sum(t.is_warm for t in traces),
            p50_audible_onset_s=median(latencies) if latencies else None,
            p95_audible_onset_s=latencies[math.ceil(len(latencies) * 0.95) - 1]
            if latencies
            else None,
            max_audible_onset_s=latencies[-1] if latencies else None,
            target_1500ms_pass_rate=sum(t.meets_1500ms_target for t in traces) / total
            if total
            else 0.0,
        )
