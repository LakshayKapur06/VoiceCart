"""Explicit environment configuration; never seeds data or downloads models."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from voicecart.embeddings import EncoderSpec
from voicecart.voice import FileArtifact


class ConfigurationError(ValueError):
    pass


def artifact(prefix: str) -> FileArtifact | None:
    path, digest = os.environ.get(prefix + "_FILE"), os.environ.get(prefix + "_SHA256")
    if not path and not digest:
        return None
    if not path or not digest:
        raise ConfigurationError(f"Configure both {prefix}_FILE and {prefix}_SHA256")
    return FileArtifact(
        Path(path).expanduser(),
        digest,
        os.environ.get(prefix + "_SOURCE"),
        os.environ.get(prefix + "_LICENCE", "unverified"),
    )


@dataclass(frozen=True)
class Settings:
    database_url: str
    ollama_url: str = "http://127.0.0.1:11434"
    nlu_model: str | None = None
    nlu_digest: str | None = None
    encoder: EncoderSpec | None = None
    asr: FileArtifact | None = None
    voice: FileArtifact | None = None
    voice_config: FileArtifact | None = None
    fallback: FileArtifact | None = None
    timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> Settings:
        database = os.environ.get("VOICECART_DATABASE_URL")
        if not database:
            raise ConfigurationError(
                "Set VOICECART_DATABASE_URL to your explicit local PostgreSQL database. No catalogue is automatically loaded."
            )
        model, digest = (
            os.environ.get("VOICECART_NLU_MODEL"),
            os.environ.get("VOICECART_NLU_DIGEST"),
        )
        if bool(model) != bool(digest):
            raise ConfigurationError(
                "Configure both VOICECART_NLU_MODEL and VOICECART_NLU_DIGEST"
            )
        embedding = os.environ.get("VOICECART_EMBED_MODEL")
        spec = None
        if embedding:
            try:
                spec = EncoderSpec(
                    embedding,
                    os.environ["VOICECART_EMBED_DIGEST"],
                    int(os.environ["VOICECART_EMBED_DIMENSIONS"]),
                    os.environ.get("VOICECART_QUERY_PREFIX", ""),
                    os.environ.get("VOICECART_DOCUMENT_PREFIX", ""),
                )
            except (KeyError, ValueError) as exc:
                raise ConfigurationError(
                    "Configure the embedding model, digest and dimensions together"
                ) from exc
        try:
            timeout = float(os.environ.get("VOICECART_INFERENCE_TIMEOUT", "30"))
        except ValueError as exc:
            raise ConfigurationError("Invalid inference timeout") from exc
        if not 1 <= timeout <= 120:
            raise ConfigurationError("Inference timeout must be 1–120 seconds")
        return cls(
            database,
            os.environ.get("VOICECART_OLLAMA_URL", "http://127.0.0.1:11434"),
            model,
            digest,
            spec,
            artifact("VOICECART_ASR"),
            artifact("VOICECART_VOICE"),
            artifact("VOICECART_VOICE_CONFIG"),
            artifact("VOICECART_FALLBACK"),
            timeout,
        )
