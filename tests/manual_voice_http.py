"""Opt-in real local speech HTTP smoke; fixtures ONLY in guarded test database."""

import argparse
import base64
import hashlib
import http.client
import io
import json
import os
import threading
import time
import uuid
import wave
from pathlib import Path

import numpy as np

from scripts.verify import isolated_postgres
from tests.database_support import fabricated_document, isolated_database
from voicecart.ingestion import parse_import
from voicecart.server import Merchant, Server, WebApplication
from voicecart.settings import Settings
from voicecart.voice import FileArtifact, PiperSynthesizer


def main():
    from scripts.evidence import identity, run_directory, write_new

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(".local/artifacts")
    hashes = json.loads((root / "verified-hashes.json").read_text())

    def artifact(name):
        return FileArtifact(root / name, hashes[name])

    voice = artifact("en_US-ljspeech-medium.onnx")
    config = artifact("en_US-ljspeech-medium.onnx.json")
    synthesizer = PiperSynthesizer(voice, config)
    chunks = list(synthesizer.synthesize("Backpack."))
    raw = np.frombuffer(
        b"".join(chunk.pcm_data for chunk in chunks), dtype="<i2"
    ).astype(float)
    rate = chunks[0].sample_rate_hz
    pcm = (
        np.interp(
            np.arange(int(len(raw) * 16000 / rate)) * rate / 16000,
            np.arange(len(raw)),
            raw,
        )
        .astype("<i2")
        .tobytes()
    )
    with isolated_postgres():
        database = isolated_database()
        database.migrate()
        database.publish(parse_import(fabricated_document()))
        settings = Settings(
            os.environ["VOICECART_TEST_DSN"],
            asr=artifact("ggml-base.en.bin"),
            voice=voice,
            voice_config=config,
        )
        application = WebApplication(
            {
                "local": Merchant(
                    settings,
                    hashlib.sha256(
                        b"TEST-ONLY-HTTP-VOICE-ADMIN-KEY-DO-NOT-USE"
                    ).hexdigest(),
                )
            },
            b"TEST-ONLY-HTTP-VOICE-CAPABILITY-SECRET",
            environment="test",
        )
        server = Server(("127.0.0.1", 0), application)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        client = http.client.HTTPConnection(*server.server_address, timeout=120)
        cookie = ""

        def request(resource, body=None, raw_response=False):
            nonlocal cookie
            client.request(
                "POST" if body is not None else "GET",
                "/api/local/" + resource,
                body=json.dumps(body) if body is not None else None,
                headers={"Cookie": cookie, "Content-Type": "application/json"},
            )
            response = client.getresponse()
            content = response.read()
            if response.getheader("Set-Cookie"):
                cookie = response.getheader("Set-Cookie").split(";")[0]
            if response.status not in (200, 201):
                raise RuntimeError((response.status, content[:200]))
            return content if raw_response else json.loads(content)

        try:
            request("sessions", {})
            start = time.perf_counter()
            transcript = request(
                "transcribe", {"pcm_base64": base64.b64encode(pcm).decode()}
            )
            asr = time.perf_counter() - start
            write_new(
                (args.output_dir or run_directory()) / "ASR_OBSERVATION.json",
                {
                    **identity(),
                    "synthetic_source_text": "Backpack.",
                    "pcm_sha256": hashlib.sha256(pcm).hexdigest(),
                    "observed_transcript": transcript["text"],
                    "asr_http_seconds": asr,
                    "method": "Actual local Piper synthetic input and Whisper HTTP; no human microphone, no commerce authorized by transcript.",
                },
            )
            if "backpack" not in transcript["text"].casefold():
                raise RuntimeError("Speech identity not preserved")
            if not transcript["requires_review"] or transcript["cart_mutated"]:
                raise RuntimeError("Unsafe transcription contract")
            result = request(
                "search",
                {"query": "backpack", "category": "backpack", "currency": "INR"},
            )
            item = result["items"][0]
            operation = str(uuid.uuid4())
            body = {
                "operation_id": operation,
                "variant_id": item["variant_id"],
                "quantity": 1,
                "currency": "INR",
                "revision": item["revision"],
                "unit_price_minor": item["price_minor"],
            }
            confirmed = request("cart/add", body)
            request("cart/add", body)
            if request("cart")["items"][0]["quantity"] != 1:
                raise RuntimeError("Duplicate add")
            start = time.perf_counter()
            audio = request("speak", {}, True)
            tts = time.perf_counter() - start
            with wave.open(io.BytesIO(audio)) as source:
                frames = source.getnframes()
                sample_rate = source.getframerate()
            if frames <= 0:
                raise RuntimeError("No actual confirmation speech")
            report = {
                "method": "Actual Piper synthetic input -> actual CPU Whisper HTTP transcription -> explicit reviewed deterministic selection -> real isolated PostgreSQL receipt -> actual Piper HTTP WAV. Duplicate identical add stayed quantity 1. No microphone/speaker, NLU speed, audible onset or human comprehension claim.",
                "actual_transcript": transcript["text"],
                "confirmation": confirmed["text"],
                "asr_http_seconds": asr,
                "tts_http_seconds": tts,
                "confirmation_frames": frames,
                "sample_rate_hz": sample_rate,
                "duplicate_add_incremented": False,
            }
            write_new(
                (args.output_dir or run_directory()) / "VOICE_HTTP.json",
                {**identity(), **report},
            )
            print(json.dumps(report))
        finally:
            client.close()
            server.shutdown()
            server.server_close()
            thread.join(2)


if __name__ == "__main__":
    main()
