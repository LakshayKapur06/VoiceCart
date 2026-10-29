"""Bounded, loopback-only JSON transport. No proxies, redirects or cloud fallback."""

from __future__ import annotations

import ipaddress
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class LocalServiceError(RuntimeError):
    pass


def strict_json(data: str) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Nonfinite JSON number")

    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LocalServiceError("Local service redirects are disabled")


class LocalJSONClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        *,
        timeout: float = 30,
        max_bytes: int = 262144,
    ):
        parsed = urllib.parse.urlsplit(base_url)
        try:
            loopback = (
                parsed.hostname == "localhost"
                or ipaddress.ip_address(parsed.hostname or "").is_loopback
            )
        except ValueError:
            loopback = False
        if (
            parsed.scheme != "http"
            or not loopback
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
        ):
            raise ValueError("Inference URL must be an HTTP loopback origin")
        if (
            type(timeout) not in (int, float)
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("Timeout must be finite and positive")
        if type(max_bytes) is not int or not 1024 <= max_bytes <= 1048576:
            raise ValueError("Invalid response size limit")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), NoRedirect()
        )

    def request(self, path: str, payload: dict | None = None) -> dict:
        if not path.startswith("/api/") or "?" in path or "#" in path or ".." in path:
            raise ValueError("Unsupported local endpoint")
        data = (
            json.dumps(payload, allow_nan=False).encode()
            if payload is not None
            else None
        )
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                body = response.read(self.max_bytes + 1)
            if len(body) > self.max_bytes:
                raise LocalServiceError("Local response exceeds size limit")
            result = strict_json(body.decode("utf-8"))
            if not isinstance(result, dict):
                raise LocalServiceError("Local service must return a JSON object")
            return result
        except TimeoutError:
            raise
        except (urllib.error.URLError, OSError, UnicodeError, ValueError) as error:
            raise LocalServiceError(
                "Local inference unavailable or invalid response"
            ) from error


def verify_model(client: LocalJSONClient, model: str, digest: str) -> None:
    if (
        not isinstance(digest, str)
        or len(digest.removeprefix("sha256:")) != 64
        or any(c not in "0123456789abcdef" for c in digest.removeprefix("sha256:"))
    ):
        raise ValueError("An explicit SHA-256 model digest is required")
    models = client.request("/api/tags").get("models", [])
    if not isinstance(models, list):
        raise LocalServiceError("Invalid local model inventory")
    expected = digest.removeprefix("sha256:")
    if not any(
        isinstance(item, dict)
        and item.get("name") == model
        and str(item.get("digest", "")).removeprefix("sha256:") == expected
        for item in models
    ):
        raise LocalServiceError(
            "Configured local model is missing or its digest changed"
        )
