"""Explicit private local secrets provisioning; never prints secret values."""

import os
import secrets
from pathlib import Path

root = Path(".secrets")
root.mkdir(mode=0o700, exist_ok=True)
for name in ("database_password", "http_secret", "admin_token"):
    descriptor = os.open(root / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as target:
        target.write(secrets.token_urlsafe(48) + "\n")
    print("Created private file:", root / name)
