# Compose and local development

Status: configuration and native API/SQL boundaries tested; **container execution Not Run on this host because Docker is not installed**. Do not infer clean container boot, restart persistence, GPU access or Windows/macOS/Linux portability from static configuration. The image tags/digests were checked against official Docker Hub metadata on 2026-11-02. Maintain patch updates deliberately; a reproducible digest is not a security guarantee.

```sh
python scripts/init_secrets.py
docker compose config --quiet
docker compose up --build
```

Secrets are created explicitly in ignored .secrets files in an owner-only (0700) directory with read-only (0444) files readable by the unprivileged container mount, never printed or baked into images. Keep them private and do not recreate/rotate a PostgreSQL password without coordinating the existing database volume. The one-shot migration waits for healthy pgvector PostgreSQL; backend waits for migration success and serves the customer/admin assets from the same origin. One backend service suffices; separate frontend containers are unnecessary for static same-origin clients. No products are seeded. Use the explicit owner import workflow.

Compose uses a named PostgreSQL volume, no published DB port and a localhost-only API port 8080. Backend runs as uid 10001 with a read-only root filesystem and writable temporary memory. The private parent directory prevents other host users from traversing to the read-only secret files; mounted files are readable by uid 10001. Verify actual secret mounts on your Compose platform. Do not copy these files into a publicly traversable directory. Health checks use /health, not a fabricated model readiness claim. Stop with docker compose down; restarting preserves the volume. Never use down --volumes against needed data. Back up and test restoration before any deliberate reset.

Ollama/model weights stay outside images. Docker Desktop uses host.docker.internal; Linux extra_hosts maps host-gateway. The host inference runtime must be reachable on the trusted interface/firewall while remaining protected from public networks. Default native clients permit loopback only; explicit VOICECART_TRUSTED_DATABASE_HOSTS=db and VOICECART_TRUSTED_INFERENCE_HOSTS=host.docker.internal authorize only the configured deployment service names. They are administrator-controlled allowlists, not request parameters. Configure pinned NLU/embedding digest groups when provisioned; the default Compose profile does not invent or download them. CPU works where the runtime supports it; NVIDIA GPU and Apple Metal run in the separately configured host runtime and require platform validation. Browser/host audio is not captured by a headless container.

Native API: initialize the explicit local DB with voicecart init-db; set VOICECART_HTTP_SECRET_FILE and VOICECART_ADMIN_TOKEN_FILE to provisioned private files, VOICECART_PUBLIC_ORIGIN=http://127.0.0.1:8080, then python -m voicecart.server. Default bind is loopback. Public deployment requires a TLS reverse proxy, a fixed public origin, backups, secret management, resource/rate controls and the owner acceptance in SECURITY_AND_PRIVACY.md. Managed hosting is an architecture option, not a deployed service.
