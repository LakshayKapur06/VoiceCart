"""Explicit deployment-only service hostname allowlists; loopback is default."""

import os
import re


def trusted_hosts(kind: str) -> set[str]:
    names = {
        name.strip()
        for name in os.environ.get("VOICECART_TRUSTED_" + kind + "_HOSTS", "").split(
            ","
        )
        if name.strip()
    }
    if any(
        not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]{0,252}", name) for name in names
    ):
        raise ValueError("Invalid trusted service hostname")
    return names
