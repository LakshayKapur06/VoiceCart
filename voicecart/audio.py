"""Audio turn management, half-duplex control, ASR/TTS contracts, and latency telemetry.

Sprint 2 deliverables: A-01 (Turn management & accessible controls),
A-02 (ASR -> Template -> TTS slice & comprehension),
A-03 (Audible latency measurement & failure accounting).
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from voicecart.domain import require_integer, require_text


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
        if not isinstance(self.timestamp_s, (int, float)):
            raise TypeError("timestamp_s must be numeric")

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
        if not isinstance(self.timestamp_s, (int, float)):
            raise TypeError("timestamp_s must be numeric")


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
        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
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
    """Licence and technical specifications of pinned local speech models."""

    name: str
    version: str
    licence: str
    language: str
    sample_rate_hz: int
    is_commercial_eligible: bool = True

    def __post_init__(self) -> None:
        require_text(self.name, "name")
        require_text(self.version, "version")
        require_text(self.licence, "licence")
        require_text(self.language, "language")
        require_integer(self.sample_rate_hz, "sample_rate_hz", minimum=8000)
        if type(self.is_commercial_eligible) is not bool:
            raise TypeError("is_commercial_eligible must be bool")


@dataclass
class LatencyTrace:
    """Detailed timestamp breakdown for a single interaction turn.

    Records the progression from speech onset through actual audible response.
    """

    turn_id: str
    is_warm: bool = True
    t_turn_start: float = 0.0
    t_speech_start: float = 0.0
    t_speech_end: float = 0.0
    t_endpoint_detected: float = 0.0
    t_asr_start: float = 0.0
    t_asr_end: float = 0.0
    t_template_start: float = 0.0
    t_template_end: float = 0.0
    t_tts_start: float = 0.0
    t_first_pcm_chunk: float = 0.0
    t_audible_onset: float = 0.0
    failed: bool = False
    failure_reason: str | None = None
    timed_out: bool = False

    @property
    def endpoint_delay_s(self) -> float:
        """VAD silence duration before finalizing endpoint."""
        if self.t_endpoint_detected > 0 and self.t_speech_end > 0:
            return max(0.0, self.t_endpoint_detected - self.t_speech_end)
        return 0.0

    @property
    def asr_latency_s(self) -> float:
        if self.t_asr_end > 0 and self.t_asr_start > 0:
            return max(0.0, self.t_asr_end - self.t_asr_start)
        return 0.0

    @property
    def tts_to_first_audio_s(self) -> float:
        if self.t_first_pcm_chunk > 0 and self.t_tts_start > 0:
            return max(0.0, self.t_first_pcm_chunk - self.t_tts_start)
        return 0.0

    @property
    def audible_onset_latency_s(self) -> float:
        """Utterance end to meaningful audible playback onset."""
        if self.t_audible_onset > 0 and self.t_speech_end > 0:
            return max(0.0, self.t_audible_onset - self.t_speech_end)
        return 0.0

    @property
    def meets_1500ms_target(self) -> bool:
        """Check against the <1.5s (1500ms) audible onset target."""
        if self.failed or self.timed_out or self.t_audible_onset == 0.0:
            return False
        return self.audible_onset_latency_s < 1.5


@dataclass(frozen=True)
class LatencyBenchmarkSummary:
    """Summary of benchmarked turns with explicit failure accounting.

    Crucial principle: Failures and timeouts must NEVER be silently omitted
    from denominator calculations.
    """

    total_turns: int
    successful_turns: int
    failed_turns: int
    timeout_turns: int
    cold_turns: int
    warm_turns: int
    p50_audible_onset_s: float
    p95_audible_onset_s: float
    max_audible_onset_s: float
    target_1500ms_pass_rate: float


class AudioInputProtocol(Protocol):
    def start_capture(self) -> None: ...
    def read_chunk(self) -> AudioChunk | None: ...
    def stop_capture(self) -> None: ...


class AudioOutputProtocol(Protocol):
    def play_chunk(self, chunk: AudioChunk) -> None: ...
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


class HalfDuplexTurnController:
    """Half-duplex turn adapter ensuring strict turn boundaries, playback cancellation,

    assistive-technology status, and safe action gating.

    Rules:
    1. Half-duplex: When speaking, microphone capture is gated (muted) to prevent self-echo.
    2. Partial transcripts NEVER authorize mutations or actions.
    3. 'stop()' stops speech immediately, but explicitly notes that committed actions cannot be undone.
    4. 'repeat()' replays response text/audio; never re-executes mutations.
    5. Stale turn events from expired or superseded turn IDs are rejected.
    6. Dual-failure: If both audio and assistive channels fail, session is flagged unusable.
    """

    def __init__(self) -> None:
        self._state: TurnState = TurnState.IDLE
        self._current_turn_id: str | None = None
        self._is_capture_gated: bool = False
        self._last_verified_response: str | None = None
        self._last_final_transcript: Transcript | None = None
        self._status_messages: list[AssistiveStatusMessage] = []
        self._audio_channel_healthy: bool = True
        self._assistive_channel_healthy: bool = True

    @property
    def state(self) -> TurnState:
        return self._state

    @property
    def current_turn_id(self) -> str | None:
        return self._current_turn_id

    @property
    def is_capture_gated(self) -> bool:
        """True when capture is inhibited (e.g. while speaking or stopped)."""
        return self._is_capture_gated

    @property
    def status_messages(self) -> tuple[AssistiveStatusMessage, ...]:
        return tuple(self._status_messages)

    def set_channel_health(self, *, audio: bool, assistive: bool) -> None:
        self._audio_channel_healthy = audio
        self._assistive_channel_healthy = assistive
        if not audio and not assistive:
            self._state = TurnState.FAILED
            self._emit_status("CRITICAL: Both audio and assistive channels unavailable", StatusPriority.ASSERTIVE)

    def is_session_usable(self) -> bool:
        return self._audio_channel_healthy or self._assistive_channel_healthy

    def _emit_status(self, text: str, priority: StatusPriority = StatusPriority.POLITE) -> None:
        if self._assistive_channel_healthy:
            self._status_messages.append(AssistiveStatusMessage(text=text, priority=priority))

    def start_listening(self, turn_id: str) -> None:
        require_text(turn_id, "turn_id")
        self._current_turn_id = turn_id
        self._state = TurnState.LISTENING
        self._is_capture_gated = False
        self._emit_status(f"Listening for turn {turn_id}")

    def end_turn_manually(self, turn_id: str) -> None:
        """Manual accessible end-turn control without waiting for VAD silence timeout."""
        if turn_id != self._current_turn_id:
            return
        self._state = TurnState.PROCESSING
        self._is_capture_gated = True
        self._emit_status("Speech input ended. Processing request...")

    def on_vad_endpoint(self, turn_id: str) -> None:
        if turn_id != self._current_turn_id:
            return
        self._state = TurnState.PROCESSING
        self._is_capture_gated = True
        self._emit_status("Endpoint detected. Processing...")

    def process_transcript(self, transcript: Transcript) -> bool:
        """Process incoming transcript.

        Returns True if transcript is valid and final for the active turn.
        Rejects stale events or partial transcripts from authorizing actions.
        """
        if transcript.turn_id != self._current_turn_id:
            # Stale turn event from past turn, drop immediately
            self._emit_status("Ignored stale turn event", StatusPriority.POLITE)
            return False

        if transcript.kind is TranscriptKind.PARTIAL:
            # Partial events inform UI but CANNOT authorize actions
            self._emit_status(f"Partial speech: {transcript.text}")
            return False

        if transcript.kind in (TranscriptKind.SILENCE_TIMEOUT, TranscriptKind.NO_SPEECH):
            self._state = TurnState.IDLE
            self._is_capture_gated = False
            self._emit_status("No speech heard. Please speak again.", StatusPriority.ASSERTIVE)
            return False

        if transcript.kind is TranscriptKind.ERROR:
            self._state = TurnState.FAILED
            self._is_capture_gated = False
            self._emit_status(f"Speech recognition error: {transcript.text}", StatusPriority.ASSERTIVE)
            return False

        if transcript.is_final:
            self._last_final_transcript = transcript
            self._state = TurnState.PROCESSING
            self._emit_status(f"Heard: {transcript.text}")
            return True

        return False

    def start_speaking(self, response_text: str) -> None:
        """Enter speaking state with half-duplex microphone gating."""
        require_text(response_text, "response_text")
        self._state = TurnState.SPEAKING
        self._is_capture_gated = True  # MUTE capture during playback to avoid self-echo
        self._last_verified_response = response_text
        self._emit_status(f"Assistant speaking: {response_text}")

    def finish_speaking(self) -> None:
        """Playback finished, return to idle and re-enable capture."""
        self._state = TurnState.IDLE
        self._is_capture_gated = False
        self._emit_status("Playback finished. Assistant ready.")

    def stop(self) -> TurnControlOutcome:
        """Explicit accessible stop control.

        Interrupts speech playback and cancels downstream processing.
        IMPORTANT: Clearly distinguishes that stopping speech does NOT undo
        already committed business actions/mutations.
        """
        was_speaking = self._state is TurnState.SPEAKING
        self._state = TurnState.STOPPED
        self._is_capture_gated = False
        msg = "Speech playback stopped. Notice: Already committed cart operations cannot be undone by stop."
        self._emit_status(msg, StatusPriority.ASSERTIVE)
        return TurnControlOutcome(
            action_name="stop",
            success=True,
            stopped_playback=was_speaking,
            action_undone=False,
            message=msg,
        )

    def pause(self) -> TurnControlOutcome:
        self._state = TurnState.PAUSED
        self._is_capture_gated = True
        msg = "Session paused."
        self._emit_status(msg)
        return TurnControlOutcome(
            action_name="pause",
            success=True,
            stopped_playback=False,
            action_undone=False,
            message=msg,
        )

    def resume(self) -> TurnControlOutcome:
        self._state = TurnState.IDLE
        self._is_capture_gated = False
        msg = "Session resumed."
        self._emit_status(msg)
        return TurnControlOutcome(
            action_name="resume",
            success=True,
            stopped_playback=False,
            action_undone=False,
            message=msg,
        )

    def repeat(self) -> str | None:
        """Explicit repeat control.

        Replays the last announced verified response. NEVER executes a mutation.
        """
        if self._last_verified_response is None:
            self._emit_status("No prior response to repeat.", StatusPriority.POLITE)
            return None
        self._emit_status(f"Repeating: {self._last_verified_response}")
        return self._last_verified_response


class AudioPipelineSlice:
    """Early voice feasibility slice connecting ASR -> Verified Template -> TTS.

    Includes cached emergency speech audio fallback when neural TTS fails.
    """

    CACHED_FALLBACK_AUDIO = b"RIFF-MOCK-CACHED-AUDIO-FALLBACK-PROMPT"

    def __init__(
        self,
        asr: SpeechRecognizerProtocol,
        tts: SpeechSynthesizerProtocol,
        controller: HalfDuplexTurnController,
    ) -> None:
        self.asr = asr
        self.tts = tts
        self.controller = controller

    def execute_slice(
        self,
        audio_data: bytes,
        turn_id: str,
        template_fn,
        trace: LatencyTrace | None = None,
    ) -> tuple[Transcript, str, list[AudioChunk]]:
        """Run ASR -> template construction -> TTS with timing and fallback."""
        if trace:
            trace.t_asr_start = time.monotonic()

        transcript = self.asr.transcribe(audio_data, turn_id)

        if trace:
            trace.t_asr_end = time.monotonic()

        valid = self.controller.process_transcript(transcript)
        if not valid or not transcript.can_authorize_action:
            error_response = "Sorry, I could not understand. Please try again."
            return transcript, error_response, []

        # Step 2: Format verified response template
        if trace:
            trace.t_template_start = time.monotonic()

        response_text = template_fn(transcript.text)
        self.controller.start_speaking(response_text)

        if trace:
            trace.t_template_end = time.monotonic()
            trace.t_tts_start = time.monotonic()

        # Step 3: Local TTS synthesis with cached fallback
        audio_chunks: list[AudioChunk] = []
        try:
            for chunk in self.tts.synthesize(response_text):
                if trace and trace.t_first_pcm_chunk == 0.0:
                    trace.t_first_pcm_chunk = time.monotonic()
                audio_chunks.append(chunk)
        except Exception as exc:
            # Neural TTS failure: use cached fallback audio prompt
            if trace:
                trace.failed = True
                trace.failure_reason = f"TTS synthesis failed: {exc}"
            audio_chunks = [
                AudioChunk(
                    pcm_data=self.CACHED_FALLBACK_AUDIO,
                    sample_rate_hz=16000,
                    channels=1,
                )
            ]

        self.controller.finish_speaking()
        return transcript, response_text, audio_chunks


class LatencyBenchmarkRecorder:
    """Collects and evaluates latency traces with full denominator accounting."""

    def __init__(self) -> None:
        self._traces: list[LatencyTrace] = []

    def record(self, trace: LatencyTrace) -> None:
        self._traces.append(trace)

    @property
    def traces(self) -> tuple[LatencyTrace, ...]:
        return tuple(self._traces)

    def summarize(self) -> LatencyBenchmarkSummary:
        total = len(self._traces)
        if total == 0:
            return LatencyBenchmarkSummary(
                total_turns=0,
                successful_turns=0,
                failed_turns=0,
                timeout_turns=0,
                cold_turns=0,
                warm_turns=0,
                p50_audible_onset_s=0.0,
                p95_audible_onset_s=0.0,
                max_audible_onset_s=0.0,
                target_1500ms_pass_rate=0.0,
            )

        failed = [t for t in self._traces if t.failed]
        timeouts = [t for t in self._traces if t.timed_out]
        successful = [t for t in self._traces if not t.failed and not t.timed_out]
        cold = [t for t in self._traces if not t.is_warm]
        warm = [t for t in self._traces if t.is_warm]

        latencies = sorted(t.audible_onset_latency_s for t in successful)
        p50 = latencies[int(len(latencies) * 0.50)] if latencies else 0.0
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
        max_lat = latencies[-1] if latencies else 0.0

        # Pass rate denominator is TOTAL turns, not only successful turns!
        under_target = sum(1 for t in self._traces if t.meets_1500ms_target)
        pass_rate = under_target / total

        return LatencyBenchmarkSummary(
            total_turns=total,
            successful_turns=len(successful),
            failed_turns=len(failed),
            timeout_turns=len(timeouts),
            cold_turns=len(cold),
            warm_turns=len(warm),
            p50_audible_onset_s=p50,
            p95_audible_onset_s=p95,
            max_audible_onset_s=max_lat,
            target_1500ms_pass_rate=pass_rate,
        )
