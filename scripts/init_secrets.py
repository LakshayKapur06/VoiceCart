"""Explicit private local secrets provisioning; never prints secret values."""

import os
import secrets
from pathlib import Path

root = Path(".secrets")
root.mkdir(mode=0o700, exist_ok=True)
os.chmod(root, 0o700)
for name in ("database_password", "http_secret", "admin_token"):
    descriptor = os.open(root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as target:
        target.write(secrets.token_urlsafe(48) + "\n")
        target.flush()
        os.fchmod(
            target.fileno(), 0o444
        )  # Private parent protects host access; read-only container mount is readable by uid 10001.
    print("Created private file:", root / name)
