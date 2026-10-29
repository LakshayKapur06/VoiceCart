"""Explicit local encoder generation. Never mixes same-shaped different spaces."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

from voicecart.domain import require_integer
from voicecart.local_http import LocalJSONClient, LocalServiceError, verify_model


def validate_vector(values, dimensions: int) -> tuple[float, ...]:
    if not isinstance(values, (list, tuple)) or len(values) != dimensions:
        raise ValueError("Embedding dimensions disagree")
    if any(
        type(value) not in (float, int) or not math.isfinite(value) for value in values
    ):
        raise ValueError("Embedding must contain finite numbers")
    norm = math.sqrt(sum(value * value for value in values))
    if not math.isfinite(norm) or norm == 0:
        raise ValueError("Embedding must have a finite nonzero norm")
    return tuple(float(value) / norm for value in values)


def vector_literal(vector: tuple[float, ...]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"


@dataclass(frozen=True)
class EncoderSpec:
    model: str
    digest: str
    dimensions: int
    query_prefix: str = ""
    document_prefix: str = ""
    serializer: str = "variant-text-v1"

    def __post_init__(self):
        require_integer(self.dimensions, "dimensions", 1)
        if self.dimensions > 4096:
            raise ValueError(
                "Embedding dimensions exceed supported exact-search profile"
            )

    @property
    def generation(self) -> str:
        return hashlib.sha256(
            json.dumps(self.__dict__, sort_keys=True).encode()
        ).hexdigest()


class OllamaEncoder:
    def __init__(self, client: LocalJSONClient, spec: EncoderSpec):
        self.client, self.spec = client, spec

    def encode(
        self, texts: list[str], *, query: bool = False
    ) -> list[tuple[float, ...]]:
        if not texts:
            return []
        if len(texts) > 32 or any(
            not text.strip() or len(text) > 4000 for text in texts
        ):
            raise ValueError(
                "Encoder input must be nonempty, bounded and batched at 32"
            )
        verify_model(self.client, self.spec.model, self.spec.digest)
        prefix = self.spec.query_prefix if query else self.spec.document_prefix
        response = self.client.request(
            "/api/embed",
            {
                "model": self.spec.model,
                "input": [prefix + text for text in texts],
                "truncate": False,
                "keep_alive": "5m",
            },
        )
        vectors = response.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise LocalServiceError("Embedding response count disagrees")
        try:
            return [validate_vector(vector, self.spec.dimensions) for vector in vectors]
        except ValueError as exc:
            raise LocalServiceError("Invalid local encoder output") from exc
