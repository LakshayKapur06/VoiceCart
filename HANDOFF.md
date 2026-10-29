# VoiceCart operational handoff

29 October 2026. Engineering implementation is runnable; release acceptance remains conditional on owner data, device/language/accessibility and quality decisions. Scope is search plus a local session cart, with no checkout, payment, order tracking or merchant write integration.

## Implementation and evidence

Completed modules: validated domain/money/coverage; loopback Ollama NLU with independently checked literal evidence; full-snapshot ingestion and checksummed migrations; real PostgreSQL FTS/pgvector exact retrieval; separate relevance and minimum roles; persistent sessions/presented lists; atomic idempotent cart/immutable receipts; console orchestration; real optional CPU Whisper/Piper/sounddevice adapters; explicit error/stop/repeat/retry and text equivalents.

Confirmed defects fixed include unsafe/missing final-turn boundaries, misleading audio delivery/latency accounting, unspoken error-path assumptions, incomplete SQL/search/cart/entry-point integration, dropped/malformed model slots, action substrings masquerading as evidence, expired in-memory session retention, native stop blocking and missing semantic scores beyond the dense top-50. Regression evidence is in tests and [Sprint 7](docs/evidence/SPRINT_7.md). This does not establish absence of all possible bugs.

Final automated command: `python scripts/verify.py --postgres --package --audit`: **159 source tests + 159 fresh installed-wheel tests**, real isolated SQL/publication/concurrency/cart/retry/restore/CLI cases, compilation, Ruff lint/format, configured production mypy, Bandit, pip check, diff checks and advisory scan. No known advisory found in audited installed dependencies; editable source is separately checked. Foundation/audio/HTTP/device fault tests include explicitly scripted adapters; they are not model quality or hardware acceptance.

Actual local model evidence: [speech file smoke](docs/evidence/MODEL_SMOKE.json), [NLU reference/challenger](docs/evidence/NLU_SMOKE.json) and [full model system smoke](docs/evidence/FULL_MODEL_SMOKE.json). These use synthetic development requests and guarded fabricated test records only. They do not represent a real catalogue or held-out accuracy benchmark. Initial extraction failures were safely rejected; prompt/literal decoding was repaired rather than weakening semantic validation. Qwen4B remains reference; a faster challenger is not promoted merely for speed.

No microphone/speaker/acoustic-onset, representative blind/low-vision study or Hindi/Hinglish acceptance was completed. The integrated cold/model-switch run took 59.1698 seconds in interpretation/validation/search/commit; ASR took 1.3044 seconds and confirmation synthesis 1.0752 seconds. Model residency/contention needs diagnosis on the approved deployment. Actual file-stage timings do not satisfy the under-1.5-second goal. The owner must define the workload/percentile and measure full meaningful audible output with cold/warm runs, failure/timeout counts, sample sizes and actual device configurations. Exact exhaustive retrieval is correct for the declared scorer/fixtures, not proof of universally best human relevance or production capacity.

## Setup and operation

1. Install Python >=3.11 (verified 3.12.14), maintained patched local PostgreSQL and compatible pgvector. Create a dedicated owner database/role and arrange backups. The old bundled test server is disposable infrastructure only.
2. From the repository: `python3.12 -m venv .venv`, activate it, then `python -m pip install -e '.[dev,voice]'`. Omit `voice` for text-only use. Review distribution terms before bundling runtimes/weights; the repository has no owner-selected LICENSE.
3. Copy `.env.example` to ignored `.env`, edit explicit `VOICECART_DATABASE_URL` and provisioned model groups. Load with `set -a; source .env; set +a`. No automatic dotenv loader exists.
4. Run `voicecart init-db` then `voicecart db-status`. These create/check schema and metadata, never product seeds. Startup does not implicitly migrate.
5. After real data import, use `voicecart run` or `voicecart run --voice --speak`. Commands: `/listen`, `/end`, `/stop`, `/repeat`, `/ack`, `/retry OPERATION_ID`, `/cart`, `/quit`. Read/ack the full text list before an ordinal selection. Completed primary speech can acknowledge it; fallback/interrupted output cannot.
6. Retain session/operation IDs. Retry the original ID after uncertainty; never generate a replacement to resolve an unknown outcome. Restart with `voicecart run --session-id ID` only while unexpired. One-hour default sessions and five-minute lists have explicit expiry; old carts/receipts are removed by cleanup. Cart is not a stock reservation.

Exact artifact sources, SHA-256 values, model digests and setting groups are in [README](README.md#local-inference-and-speech-configuration) and `.env.example`. Provision from those pinned sources separately: English Whisper base.en, LJ Speech medium ONNX/config and local Ollama Qwen4B; embedding is optional and generation-pinned. This host's tested assets are ignored under `.local/artifacts`, runtime under `.local/runtime`, model blobs under `.local/ollama-models`. They are not shipped in Git. The task's private Ollama 11439 process is stopped after tests; restart explicitly if using that profile:

```sh
OLLAMA_MODELS="$PWD/.local/ollama-models" OLLAMA_NO_CLOUD=1 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1 .local/runtime/ollama serve
```

That command uses Ollama's default loopback 11434; configure `VOICECART_OLLAMA_URL` consistently. Set `OLLAMA_HOST=127.0.0.1:11439` explicitly to reproduce the recorded smoke port. Do not expose inference publicly or enable remote model substitution. Whisper adapter is English CPU; Piper runtime is GPL-3.0 and voice/data terms are distinct. Approve intended distribution and project license before release.

## Real catalogue: owner action required

The normal application database intentionally has no product records until the owner supplies/imports them. No owner database DSN was configured or inspected during this task; only guarded temporary test databases received fixtures. A separate fresh application database was initialized and actually started, retaining **zero products/variants**. Synthetic fixture imports must never be used in normal operation.

Required SQL groups are `products` (product ID/name/category/model/description/activity), `variants` (variant/parent/SKU/colour/size/integer price/currency/availability/stock/freshness/activity), `variant_search` (versioned derived text/vector features), `catalogue_state` (revision/coverage/source/expiry/aliases/generation). Session/cart/command/receipt tables are separate. [Packaged migrations](voicecart/migrations) are the exact SQL authority.

Input is UTF-8 full-snapshot JSON with schema version 1, new revision, expected previous revision, explicit source/coverage, future timezone-aware expiry, products/variants arrays and optional lowercase alias maps. First previous revision is `unpopulated`. Stable case-sensitive product/variant IDs must be unique; parent IDs must exist and non-null SKUs must be unique. Required/optional fields and types are fully enumerated in [README's import contract](README.md#real-catalogue-contract-and-import). Money is nonnegative integer minor units with explicit uppercase currency; missing prices/stock/attributes remain unknown. Current price, affirmative availability and sufficient known stock are required for action; stale/incomplete source blocks stronger minimum claims.

Resolve source ownership, taxonomy, stock authority, currency policy, refresh SLA, category completeness and expiry before claiming real coverage. Supply real records, validate aliases, back up prior source/database, then:

```sh
voicecart init-db
voicecart db-status
voicecart import-catalogue /absolute/path/to/owner-catalogue.json
voicecart db-status
voicecart search --category CATEGORY --currency INR --under-minor 200000
```

Import rejects the entire snapshot on indexed invalid fields, duplicates, orphan variants, stale manifests or revision conflicts. It never partly publishes. A full replacement removes omitted records. Configured embeddings are prepared locally before an atomic facts/index publication; service failures preserve the old revision. Without encoder config, lexical/structured operation remains available. On model/digest/dimensions/prefix/serializer change, re-import the full real source using a new revision and matching query config. Do not mix vector spaces. Parser maxima are not measured capacity limits.

Without owner data, unit/synthetic service/model safety and empty-startup behavior can be verified. Real coverage, upstream freshness, relevance/cheapest usefulness, real prices/SKUs and target-language user success require the owner's catalogue and judgments.

## Recovery, privacy and manual acceptance

For an outage, restore the local DB/model/device and retry the same operation ID. Receipt verification, not speech success, determines whether an add committed. `/stop` cannot reverse a completed add. `/repeat` does not add again. Expired sessions require a new session; no durable user-account recovery is promised. Wrong model/file hashes require fixing provisioned configuration, not disabling integrity checks. Stale catalogue requires an authoritative refreshed full snapshot.

For database recovery use a matching maintained PostgreSQL toolchain and a dedicated destination database. Back up with `pg_dump --format=custom --dbname="$VOICECART_DATABASE_URL" --file=/private/path/voicecart.dump`; restore into a separate empty destination with `pg_restore --exit-on-error --dbname=LOCAL_RESTORE_DSN /private/path/voicecart.dump`, then run `db-status` and verify the revision/receipt/cart data before switching application configuration. Never restore over live owner data blindly. Automated dump/restore of schema/catalogue metadata ran only on the guarded test server. Existing cart/restart/recovery tests cover committed receipt replay; production backups and retention need an owner drill.

Normal execution does not persist raw audio/transcripts. Session logical deletion does not securely erase WAL/backups. Protect local IDs, DB, service logs and backups; approve retention. Current console is a local single-device capability surface, not a shared authenticated service.

Owner release checklist: provide real source/coverage/update SLA; approve English versus Hindi/Hinglish and supported hardware; approve project/runtime/voice terms; test VoiceOver/keyboard controls, real microphone permissions/noise/echo, interrupted lists, stop/repeat/error recovery and rupee/SKU comprehension with representative users; collect judged relevance cases before tuning weights; measure device latency/resource contention and equal-recall storage alternatives before performance claims. [D01–D15](docs/ARCHITECTURE.md#open-decisions-preserved-from-the-review) preserves unresolved decisions.

## Commits, cleanup and history approval

Ordinary implementation increments use the existing `main` / `https://github.com/LakshayKapur06/VoiceCart.git` remote, human authorship and no AI co-author trailers:

| Sprint | Ordinary commit | Verification and push |
|---|---|---|
| S3 NLU | `62f4a758a64edb5f470db7693dbddfcdb38fa0cc` | 111 source/wheel tests; pushed, remote verified |
| S4 storage/search | `5b67ba20891bb15c25e9e40ede3609845b983ab5` | 127 source/wheel tests; pushed, remote verified |
| S5 cart | `ef4acec04a674cbe83053c052210287083143c1c` | 143 source/wheel tests; pushed, remote verified |
| S6 runnable speech app | `233ad714e7d8c5d973ed83b4dc59b06099e7536e` | 155 source/wheel tests; pushed, remote verified |
| S7 final verification/docs | `67e526e252f4f2e00ffb8fd9421be8a96061accc` | 159 source/wheel tests; pushed and origin/main verified |

README was consolidated, necessary review knowledge moved into ARCHITECTURE/ADR, obsolete review-only restrictions removed and Suggestions.md deleted from the working tree. Source/tests/config/migrations were preserved. Owner data/models/recordings/secrets/build/cache directories are ignored. No AI trailers were found in original reachable history; human authors remain unchanged. History removal changes hashes despite identical final source content.

History artifacts are prepared **after** final ordinary commits/pushes in the sibling `history-backups` directory (outside the repository): `voicecart-pre-cleanup.bundle`, `refs-before.txt`, `manifest.json`, `voicecart-cleaned.git`, `voicecart-cleaned-review`, and `HISTORY_HANDOFF.md`. The final external handoff records verified backup SHA-256, original/rewritten refs, author/message/path checks, commit map and post-rewrite tests. This avoids committing a self-referential final commit hash. The primary checkout and GitHub retain ordinary history until approval.

Recovery: `git bundle verify ../history-backups/voicecart-pre-cleanup.bundle`; `git clone ../history-backups/voicecart-pre-cleanup.bundle ../voicecart-recovered`. This restores backed-up refs without touching the live checkout. Original human authors/emails/dates and unrelated trailers must remain intact in the separate rewrite. Suggestions.md is the only requested historical file purge; no other source is purged.

Remote history synchronization affects **refs/heads/main only** (no tags/other branches at preparation). Existing collaborator clones will diverge; coordinate a fresh clone or explicit recovery/cherry-pick of their independent work. User prompt §12.3 requires explicit approval before any history-overwriting push. The exact reviewed command, generated with the recorded old remote hash, is in sibling HISTORY_HANDOFF.md. Until approved, no force-push is executed and historical Suggestions.md remains on GitHub despite its deletion from the latest tree.
