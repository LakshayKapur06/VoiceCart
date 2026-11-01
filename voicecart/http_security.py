"""Server-enforced local capabilities, roles and bounded rate limits."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import threading
import time
from collections import OrderedDict
from http.cookies import SimpleCookie


class AccessDenied(ValueError):
    pass


def tenant_id(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9-]{0,31}", value
    ):
        raise ValueError("Invalid merchant identity")
    return value


class Capabilities:
    def __init__(self, secret: bytes):
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("Configure a private capability key of at least 32 bytes")
        self.secret = secret

    def issue(self, tenant, identity, role, *, ttl=3600):
        tenant_id(tenant)
        if role not in ("customer", "admin"):
            raise ValueError("Invalid role")
        body = (
            base64.urlsafe_b64encode(
                json.dumps(
                    [tenant, identity, role, int(time.time()) + ttl],
                    separators=(",", ":"),
                ).encode()
            )
            .decode()
            .rstrip("=")
        )
        digest = hmac.new(self.secret, body.encode(), hashlib.sha256).hexdigest()
        return body + "." + digest

    def verify(self, token, tenant, role):
        try:
            if not isinstance(token, str) or len(token) > 2048:
                raise ValueError("Invalid token")
            body, signature = token.split(".")
            expected = hmac.new(self.secret, body.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError("Invalid signature")
            owner, identity, scope, expires = json.loads(
                base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
            )
            if (
                owner != tenant
                or scope != role
                or type(expires) is not int
                or expires <= time.time()
            ):
                raise ValueError("Invalid scope or expiry")
            return identity
        except (ValueError, TypeError, UnicodeError) as error:
            raise AccessDenied("Authentication required or expired") from error

    def from_cookie(self, header, tenant, role):
        cookie = SimpleCookie()
        try:
            cookie.load(header or "")
        except Exception as error:
            raise AccessDenied("Invalid cookie") from error
        key = ("vca_" if role == "admin" else "vcc_") + tenant
        if key not in cookie:
            raise AccessDenied("Authentication required")
        return self.verify(cookie[key].value, tenant, role)


class RateLimiter:
    def __init__(self):
        self.windows: OrderedDict[tuple, tuple[float, int]] = OrderedDict()
        self.lock = threading.Lock()

    def allow(self, key, limit=120, *, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            start, count = self.windows.pop(key, (now, 0))
            if now - start >= 60:
                start, count = now, 0
            self.windows[key] = (start, count + 1)
            while len(self.windows) > 4096:
                self.windows.popitem(last=False)
            return count < limit
