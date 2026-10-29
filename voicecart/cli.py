"""Accessible local console and explicit administration commands; no data seeding."""

from __future__ import annotations

import argparse
import json
import queue
import threading
from dataclasses import asdict
from pathlib import Path

import psycopg

from voicecart.application import Response, ShoppingApplication
from voicecart.audio import (
    CachedSpeechPrompt,
    HalfDuplexTurnController,
    Transcript,
    TranscriptKind,
)
from voicecart.cart import AddCommand, CartError, CartService, OutcomeUnknown
from voicecart.database import Database, DatabaseUnavailable, PublicationConflict
from voicecart.domain import (
    HardConstraints,
    Money,
    PriceLimit,
    PriceOperator,
    RetrievalRoute,
    SearchRequest,
)
from voicecart.embeddings import OllamaEncoder
from voicecart.ingestion import ImportValidationError, load_import
from voicecart.local_http import LocalJSONClient
from voicecart.nlu import OllamaInterpreter
from voicecart.search import PostgresCatalogue
from voicecart.sessions import SessionError, SessionStore
from voicecart.settings import ConfigurationError, Settings
from voicecart.voice import (
    MicrophoneInput,
    PiperSynthesizer,
    ResponseSpeaker,
    SoundDeviceOutput,
    VoiceError,
    WhisperRecognizer,
)


def components(settings: Settings):
    database = Database(settings.database_url)
    client = LocalJSONClient(
        settings.ollama_url, timeout=settings.timeout_seconds, max_bytes=1048576
    )
    interpreter = (
        OllamaInterpreter(client, settings.nlu_model, settings.nlu_digest)
        if settings.nlu_model and settings.nlu_digest
        else None
    )
    encoder = OllamaEncoder(client, settings.encoder) if settings.encoder else None
    catalogue = PostgresCatalogue(database, encoder)
    return database, encoder, ShoppingApplication(database, interpreter, catalogue)


def interactive(
    settings: Settings,
    app: ShoppingApplication,
    *,
    session_id: str | None,
    voice: bool,
    speak: bool,
) -> None:
    app.database.check_ready()  # Startup checks schema, never migrates or imports products.
    app.sessions.cleanup_expired()
    session = session_id or app.sessions.create()
    with app.database.connect() as connection:
        app.sessions.require(connection, session)
    microphone = MicrophoneInput() if voice else None
    recognizer = None
    speaker = None
    controller = HalfDuplexTurnController(audio_input=microphone)
    if voice:
        if settings.asr is None:
            raise ConfigurationError(
                "Configure the verified ASR file and SHA-256 for --voice"
            )
        recognizer = WhisperRecognizer(settings.asr)
    if speak:
        if settings.voice is None or settings.voice_config is None:
            raise ConfigurationError(
                "Configure verified Piper voice and config files for --speak"
            )
        synthesizer = PiperSynthesizer(settings.voice, settings.voice_config)
        fallback = None
        if settings.fallback:
            fallback = CachedSpeechPrompt.from_wav(
                "Speech unavailable. Use the accessible text response or retry.",
                settings.fallback.verify().read_bytes(),
            )
        speaker = ResponseSpeaker(
            controller, synthesizer, SoundDeviceOutput(), fallback=fallback
        )
    print("VoiceCart local search and cart. No checkout or payment.")
    print("Session:", session)
    print(
        "Commands: /listen, /end, /stop, /repeat, /ack, /retry OPERATION_ID, /cart, /quit."
    )
    print(
        "Read a complete result list, then /ack before selecting by number. Speech is optional; text stays available."
    )
    jobs: queue.Queue = queue.Queue(maxsize=1)
    busy = threading.Event()
    shutdown = threading.Event()
    output_lock = threading.Lock()
    latest = [None]

    def render(response):
        if not response.text:
            return
        with output_lock:
            print(f"\n{response.text}", flush=True)
            if response.operation_id:
                print("Operation:", response.operation_id, flush=True)
            latest[0] = response
        if speaker:
            delivery = speaker.deliver(response)
            if delivery.kind == "response_completed" and response.listing:
                app.sessions.mark_presented(
                    session, response.listing.list_id, response.turn_id
                )
            if delivery.kind not in ("response_completed", "cancelled"):
                print(
                    "Speech delivery:",
                    delivery.kind,
                    ". Read the text; use /repeat without repeating the add.",
                    flush=True,
                )
        if response.listing and not speaker:
            print("Type /ack when you have read the full list.", flush=True)

    def worker():
        while not shutdown.is_set():
            try:
                item = jobs.get(timeout=0.1)
            except queue.Empty:
                continue
            if item is None:
                return
            kind, data, turn = item
            try:
                if kind == "text":
                    response = app.final(
                        session, Transcript(TranscriptKind.FINAL, data, turn)
                    )
                elif kind == "voice":
                    try:
                        if recognizer is None:
                            raise VoiceError("ASR is not configured")
                        transcript = recognizer.transcribe(
                            data, turn, cancelled=app.cancellation_event(session, turn)
                        )
                        accepted = controller.process_transcript(transcript)
                        if not accepted:
                            response = (
                                app.error(
                                    session,
                                    turn,
                                    "asr_unusable",
                                    "No usable final speech was heard. Please try again.",
                                )
                                if app.sessions.is_active(session, turn)
                                else Response("cancelled", "", session, turn)
                            )
                        else:
                            response = app.final(session, transcript)
                    except Exception:
                        response = app.error(
                            session,
                            turn,
                            "asr_error",
                            "Local speech recognition failed. Please retry or type the request.",
                        )
                elif kind == "retry":
                    response = app.retry(session, data)
                else:
                    response = app.repeat(session)
                active = not response.turn_id or app.sessions.is_active(
                    session, response.turn_id
                )
                if response.code != "cancelled" and active:
                    render(response)
                elif response.receipt is not None:
                    print(
                        "An add committed before stop. Receipt operation:",
                        response.operation_id,
                        flush=True,
                    )
            except Exception:
                render(
                    app.error(
                        session,
                        turn or "",
                        "runtime_error",
                        "The operation could not be verified. Use the original operation ID to check any pending add; do not create a replacement.",
                    )
                )
            finally:
                busy.clear()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    listening_turn = None
    try:
        while True:
            try:
                text = input("VoiceCart> ").strip()
            except EOFError:
                break
            if text == "/quit":
                break
            if text == "/stop":
                outcome = controller.stop()
                try:
                    print(app.cancel(session).text)
                except Exception:
                    print(
                        "Speech stop requested; the pending cart outcome still needs verification."
                    )
                if not outcome.success:
                    print("Audio device recovery is required before listening again.")
                listening_turn = None
                continue
            if text == "/cart":
                print(json.dumps(app.cart.items(session), sort_keys=True))
                continue
            if text == "/ack":
                response = latest[0]
                accepted = bool(
                    response
                    and response.listing
                    and app.sessions.mark_presented(
                        session, response.listing.list_id, response.turn_id
                    )
                )
                print(
                    "Current result list acknowledged."
                    if accepted
                    else "No current complete result list can be acknowledged."
                )
                continue
            if busy.is_set():
                print(
                    "A request is running. Use /stop; retry once cancellation completes."
                )
                continue
            if text == "/listen":
                if microphone is None:
                    print(
                        "Start with --voice after configuring the local ASR artifact."
                    )
                    continue
                listening_turn = app.begin(session)
                try:
                    controller.start_listening(listening_turn)
                    print("Listening. Type /end when finished, or /stop to cancel.")
                except Exception:
                    controller.stop()
                    print(
                        "Microphone unavailable. Use typed input or repair device permissions."
                    )
                continue
            if text == "/end":
                if listening_turn is None or microphone is None:
                    print("No active listening turn.")
                    continue
                controller.end_turn_manually(listening_turn)
                try:
                    data = microphone.take_pcm()
                except Exception:
                    render(
                        app.error(
                            session,
                            listening_turn,
                            "capture_error",
                            "Audio capture failed or exceeded its duration. Repeat a shorter request.",
                        )
                    )
                    listening_turn = None
                    continue
                busy.set()
                jobs.put_nowait(("voice", data, listening_turn))
                listening_turn = None
                continue
            if text == "/repeat":
                busy.set()
                jobs.put_nowait(("repeat", None, None))
                continue
            if text.startswith("/retry "):
                busy.set()
                jobs.put_nowait(("retry", text[7:].strip(), None))
                continue
            if not text:
                continue
            if text.startswith("/"):
                print(
                    "Unknown control. Use /listen, /end, /stop, /repeat, /ack, /retry ID, /cart or /quit."
                )
                continue
            if listening_turn is not None:
                controller.stop()
                listening_turn = None
            turn = app.begin(session)
            busy.set()
            jobs.put_nowait(("text", text, turn))
    finally:
        shutdown.set()
        try:
            controller.stop()
            app.cancel(session)
        except Exception:
            print(
                "Cleanup could not verify cancellation. Retain the original operation ID for recovery.",
                flush=True,
            )
        if microphone:
            microphone.stop_capture()
        thread.join(2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Local VoiceCart search and cart; no automatic product seeds."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "init-db", help="Apply explicit metadata/schema migrations without product data"
    )
    sub.add_parser("db-status", help="Inspect population, revision and coverage")
    ingest = sub.add_parser(
        "import-catalogue",
        help="Validate and atomically import the owner's real snapshot",
    )
    ingest.add_argument("path", type=Path)
    run = sub.add_parser("run", help="Accessible interactive console")
    run.add_argument("--session-id")
    run.add_argument("--voice", action="store_true")
    run.add_argument("--speak", action="store_true")
    search = sub.add_parser(
        "search", help="Deterministic structured or descriptive search; no action"
    )
    search.add_argument("query", nargs="?")
    search.add_argument("--category")
    search.add_argument("--colour")
    search.add_argument("--size")
    search.add_argument("--currency", default="INR")
    limits = search.add_mutually_exclusive_group()
    limits.add_argument("--under-minor", type=int)
    limits.add_argument("--at-most-minor", type=int)
    add = sub.add_parser(
        "add", help="Explicit exact local add; retain operation ID for retry"
    )
    add.add_argument("--session-id", required=True)
    add.add_argument("--variant-id", required=True)
    add.add_argument("--operation-id", required=True)
    add.add_argument("--quantity", type=int, default=1)
    add.add_argument("--currency", default="INR")
    retry = sub.add_parser(
        "retry", help="Reconcile/retry an existing authorized operation"
    )
    retry.add_argument("--session-id", required=True)
    retry.add_argument("--operation-id", required=True)
    args = parser.parse_args(argv)
    try:
        settings = Settings.from_env()
        database, encoder, app = components(settings)
        if args.command == "init-db":
            print(
                json.dumps(
                    {"applied": database.migrate(), "state": database.inspect()},
                    default=str,
                )
            )
        elif args.command == "db-status":
            print(json.dumps(database.inspect(), default=str))
        elif args.command == "import-catalogue":
            bundle = load_import(args.path)
            revision = database.publish(bundle, encoder=encoder)
            print(
                json.dumps(
                    {
                        "revision": revision,
                        "semantic_generation": encoder.spec.generation
                        if encoder
                        else None,
                        "state": database.inspect(),
                    },
                    default=str,
                )
            )
        elif args.command == "run":
            interactive(
                settings,
                app,
                session_id=args.session_id,
                voice=args.voice,
                speak=args.speak,
            )
        elif args.command == "search":
            state = database.inspect()
            if not state["populated"]:
                print(
                    "Catalogue not populated. Import the real owner catalogue; no demo products exist."
                )
                return 0
            limit = None
            if args.under_minor is not None:
                limit = PriceLimit(
                    Money(args.under_minor, args.currency), PriceOperator.LT
                )
            elif args.at_most_minor is not None:
                limit = PriceLimit(
                    Money(args.at_most_minor, args.currency), PriceOperator.LTE
                )
            request = SearchRequest(
                HardConstraints(
                    args.currency, args.category, args.colour, args.size, limit
                ),
                RetrievalRoute.DISCOVERY if args.query else RetrievalRoute.STRUCTURED,
                semantic_query=args.query,
            )
            session = app.sessions.create()
            response = app.present(session, app.begin(session), request)
            print(json.dumps(asdict(response), default=str))
        elif args.command == "add":
            sessions = SessionStore(database)
            cart = CartService(database)
            try:
                command = cart.load_command(args.session_id, args.operation_id)
                if (
                    command.selection != "exact"
                    or command.variant_id != args.variant_id
                    or command.request.constraints.quantity != args.quantity
                    or command.request.constraints.currency != args.currency
                ):
                    raise CartError("operation_identity_conflict")
            except CartError as exc:
                if exc.code != "unknown_operation":
                    raise
                turn = sessions.begin_turn(args.session_id)
                command = AddCommand(
                    args.session_id,
                    turn,
                    args.operation_id,
                    "exact",
                    SearchRequest(
                        HardConstraints(args.currency, quantity=args.quantity)
                    ),
                    args.variant_id,
                )
            receipt = cart.add(command)
            print(json.dumps(asdict(receipt), default=str))
        elif args.command == "retry":
            print(
                json.dumps(
                    asdict(
                        CartService(database).retry(args.session_id, args.operation_id)
                    ),
                    default=str,
                )
            )
        return 0
    except OutcomeUnknown:
        print(
            "Outcome unknown. Retry using the SAME session and operation ID; do not create a replacement add."
        )
        return 3
    except (
        ConfigurationError,
        ImportValidationError,
        PublicationConflict,
        CartError,
        SessionError,
        ValueError,
        VoiceError,
        FileNotFoundError,
    ) as exc:
        print("VoiceCart:", str(exc))
        return 2
    except (DatabaseUnavailable, psycopg.Error):
        print(
            "Local database unavailable or schema not ready. Check configuration and run init-db explicitly. Pending adds require their original operation ID."
        )
        return 2
    except RuntimeError:
        print(
            "Local runtime failed. Repair the model/device setup; pending cart operations still require receipt verification."
        )
        return 2
    except ImportError:
        print(
            "Optional local runtime missing. Install voicecart[voice] for microphone, ASR and speech output."
        )
        return 2
