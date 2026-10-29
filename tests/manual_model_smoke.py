"""Opt-in actual model system smoke, synthetic speech and disposable test DB only.

Run from repository root with PYTHONPATH=. python tests/manual_model_smoke.py.
Requires the explicitly provisioned .local artifacts and private Ollama port 11439.
No microphone, speaker or normal database is accessed.
"""

import json
import time
from pathlib import Path

import numpy as np

from scripts.verify import isolated_postgres
from tests.database_support import fabricated_document, isolated_database
from voicecart.application import ShoppingApplication
from voicecart.domain import HardConstraints, RetrievalRoute, SearchRequest
from voicecart.embeddings import EncoderSpec, OllamaEncoder
from voicecart.ingestion import parse_import
from voicecart.local_http import LocalJSONClient
from voicecart.nlu import OllamaInterpreter
from voicecart.search import PostgresCatalogue
from voicecart.voice import FileArtifact, PiperSynthesizer, WhisperRecognizer


def main():
    root = Path(".local/artifacts")
    hashes = json.loads((root / "verified-hashes.json").read_text())

    def artifact(name):
        return FileArtifact(root / name, hashes[name])

    start = time.monotonic()
    tts = PiperSynthesizer(
        artifact("en_US-ljspeech-medium.onnx"),
        artifact("en_US-ljspeech-medium.onnx.json"),
    )
    asr = WhisperRecognizer(artifact("ggml-base.en.bin"))
    loading = time.monotonic() - start
    client = LocalJSONClient("http://127.0.0.1:11439", timeout=120, max_bytes=1048576)
    tags = {x["name"]: x["digest"] for x in client.request("/api/tags")["models"]}
    encoder = OllamaEncoder(
        client, EncoderSpec("all-minilm:latest", tags["all-minilm:latest"], 384)
    )
    with isolated_postgres():
        database = isolated_database()
        database.migrate()
        start = time.monotonic()
        database.publish(parse_import(fabricated_document()), encoder=encoder)
        embedding_seconds = time.monotonic() - start
        catalogue = PostgresCatalogue(database, encoder)
        start = time.monotonic()
        discovery = catalogue.search(
            SearchRequest(
                HardConstraints("INR", category="backpack"),
                RetrievalRoute.DISCOVERY,
                semantic_query="college laptop backpack",
            )
        )
        search_seconds = time.monotonic() - start
        app = ShoppingApplication(
            database,
            OllamaInterpreter(
                client,
                "qwen3:4b-instruct-2507-q4_K_M",
                tags["qwen3:4b-instruct-2507-q4_K_M"],
            ),
            catalogue,
        )
        session = app.sessions.create()
        turn = app.begin(session)
        phrase = "Find the cheapest black backpack under two thousand rupees and add it to my cart."
        start = time.monotonic()
        chunks = list(tts.synthesize(phrase))
        input_tts = time.monotonic() - start
        rate = chunks[0].sample_rate_hz
        samples = np.frombuffer(
            b"".join(c.pcm_data for c in chunks), dtype="<i2"
        ).astype(float)
        pcm = (
            np.interp(
                np.arange(int(len(samples) * 16000 / rate)) * rate / 16000,
                np.arange(len(samples)),
                samples,
            )
            .astype("<i2")
            .tobytes()
        )
        start = time.monotonic()
        transcript = asr.transcribe(pcm, turn)
        asr_seconds = time.monotonic() - start
        start = time.monotonic()
        response = app.final(session, transcript)
        app_seconds = time.monotonic() - start
        if response.receipt is None or response.receipt.variant_id != "v-cheap":
            raise RuntimeError(
                f"Actual model flow did not confirm expected test receipt: {transcript!r} {response!r}"
            )
        app.final(session, transcript)
        if app.cart.items(session) != {"v-cheap": 1}:
            raise RuntimeError("Duplicate final changed cart")
        start = time.monotonic()
        reply = list(tts.synthesize(response.text))
        reply_seconds = time.monotonic() - start
        result = {
            "method": "Actual synthetic Piper file -> explicit linear 22050-to-16000 resampling -> CPU Whisper -> real Qwen plus independent validation -> real isolated PostgreSQL cart/receipt -> actual Piper confirmation synthesis. Actual MiniLM publication/discovery also exercised. No microphone/speaker/acoustic-onset/human acceptance. Fabricated fixtures only in runner-owned disposable test DB.",
            "synthetic_request": phrase,
            "actual_transcript": transcript.text,
            "response": response.text,
            "receipt_variant": response.receipt.variant_id,
            "final_cart": app.cart.items(session),
            "duplicate_final_added_again": False,
            "semantic_dimensions": 384,
            "semantic_generation": encoder.spec.generation,
            "discovery_match_count": len(discovery.matches),
            "loading_seconds": round(loading, 4),
            "embedding_publication_seconds": round(embedding_seconds, 4),
            "discovery_seconds": round(search_seconds, 4),
            "input_tts_seconds": round(input_tts, 4),
            "asr_seconds": round(asr_seconds, 4),
            "interpret_validate_search_commit_seconds": round(app_seconds, 4),
            "confirmation_tts_seconds": round(reply_seconds, 4),
            "confirmation_pcm_bytes": sum(len(c.pcm_data) for c in reply),
            "model_digests": tags,
        }
        Path("docs/evidence/FULL_MODEL_SMOKE.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
