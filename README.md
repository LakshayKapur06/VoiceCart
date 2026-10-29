# VoiceCart

A local voice-first product search and **local session cart** application. Python owns catalogue facts, eligibility, money, ranking, writes and committed receipts. Local models extract requests and provide speech. Checkout, payments, merchant checkout integration and order tracking are outside scope.

The implemented prototype includes PostgreSQL/pgvector storage, validated full-snapshot import, exact/structured/hybrid search, bounded Ollama extraction, persistent idempotent cart operations, a console and optional real Whisper/Piper/device adapters. Engineering verification is recorded in [the evidence directory](docs/evidence/SPRINT_7.md). Release acceptance still requires real catalogue data, representative users and actual audio-device measurements. It cannot guarantee the human-most-relevant product for every possible query.

## Project layout and examples

`voicecart/` contains the domain, catalogue, NLU/transport, ingestion/embeddings/database/search, sessions/cart/application, audio/voice/settings/CLI modules and packaged SQL migrations. `tests/` contains guarded fabricated fixtures, automated regressions and an opt-in real-model test; `scripts/` contains verification and NLU smoke commands. `docs/` contains necessary architecture decisions and dated evidence.

With real data and the configured English NLU, requests such as “Find a black backpack under 2,000 rupees” search using a strict budget; “Find the cheapest black backpack under 2,000 rupees and add it to my cart” dispatches only with complete/current eligible source evidence. “Do not add anything” never authorizes a write. “Add second” requires the still-current, completely presented result list. Unsupported/ambiguous fields request clarification.

## Install and initialize

Use Python 3.11 or newer (verification used 3.12.14), a maintained patched local PostgreSQL installation and compatible pgvector. The database role must be able to create the vector extension during initialization, or have it preinstalled by an administrator. Provision a dedicated database and limit local access. Do not expose PostgreSQL or Ollama publicly.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,voice]'
cp .env.example .env
# Edit .env with the explicit local database and optional model configuration.
set -a
source .env
set +a
voicecart init-db
voicecart db-status
voicecart run
```

Omit `voice` from extras for typed operation. PostgreSQL service installation is OS-specific; [pgvector installation](https://github.com/pgvector/pgvector#installation) documents supported extension setup. The test runner's bundled PostgreSQL 16.2/pgvector 0.6.2 is disposable test infrastructure, not the supported patch level for an owner deployment. Startup checks migrations; `init-db` applies checksummed SQL assets. Never edit applied migrations; add a new one.

**Real catalogue: owner action required.** No normal owner database was configured or populated during this work. Migrations/install/startup insert no products. The separate fresh application test database has zero products and variants after initialization and actual console startup. An unpopulated catalogue is reported as such, not as proof of no matching real-world products. Real records must be supplied and explicitly imported by the owner.

## Real catalogue contract and import

Supply UTF-8 JSON, a complete replacement snapshot, maximum 128 MiB. No sample catalogue or seed command is provided. These are field definitions, not product records:

| Object | Fields and types |
|---|---|
| Manifest, all required | `schema_version`: integer 1; `revision`: new nonblank string; `previous_revision`: current DB revision (`unpopulated` for first import); `coverage`: `complete`, `partial` or `unknown`; `source`: nonblank provenance string; `valid_until`: future ISO timestamp with timezone; `products`, `variants`: arrays |
| Product required | `product_id`, `name`: nonblank strings |
| Product optional | `category`, `model_number`: string or null; `description`: string (default empty); `active`: boolean (default true) |
| Variant required | `variant_id`, `product_id`: stable nonblank strings; parent must exist |
| Variant optional | `sku`, `colour`, `size`: string or null; `price`: null or object with integer `minor_units` and uppercase three-letter `currency`; `available`: boolean or null; `stock_quantity`: nonnegative integer or null; `price_freshness`: `current`, `stale`, `unknown` (default unknown); `active`: boolean (default true) |
| Manifest optional | `aliases`: object containing `category`, `colour`, `size` maps, each mapping lowercase literal aliases to canonical strings. Canonical values must agree with actual fields. |

IDs are case sensitive, globally unique within their entity type and must remain stable across revisions. Non-null SKUs must be unique. Prices use integer minor units (INR paise), never floats/bools; maximum 2^63−1. Missing facts stay unknown. Actionable variants require verified current price, affirmative availability, sufficient known stock and all requested attributes. Expired source timestamps make availability/freshness unsafe. Coverage is an assertion by the catalogue owner; code cannot verify an upstream source's completeness. Do not mark partial extracts complete.

Unknown fields, invalid values, duplicates, orphan variants and stale manifests reject the **entire import** with indexed issues; nothing is partly published. Maximum 100,000 products/250,000 variants are parser bounds, not measured capacity promises. A successful import removes records absent from the new full snapshot. Preserve/export the previous authoritative source and back up first.

```sh
voicecart db-status
voicecart import-catalogue /absolute/path/to/owner-catalogue.json
voicecart db-status
voicecart search --category CATEGORY --colour COLOUR --currency INR --under-minor 200000
```

The relational tables are `products`, `variants`, `variant_search`, `catalogue_state`; migrations also create session/cart/command/receipt tables. See [schema assets](voicecart/migrations) for exact SQL fields. Embeddings are derived from names/descriptions/category/model/SKU/colour/size, excluding price/stock. With the embedding configuration enabled, import generates vectors locally in batches and publishes facts/vectors/revision atomically. A failure preserves the prior snapshot; compare-and-set `previous_revision` prevents overwriting a newer publication. Without an encoder, import/search supports lexical and structured retrieval. Changing model/digest/dimensions/prefixes/serializer requires a fresh full import and matching query configuration; vectors from different generations are never mixed. Large text exceeding an encoder's actual token window is rejected instead of silently truncated.

Resolve the real source, taxonomy, supported currencies, size/colour aliases, stock authority, refresh schedule, coverage and expiry SLA before real cheapest claims. Do not import test fixtures into an owner database.

## Search, selection and cart

Exact IDs/SKUs/models, complete structured filtering and lexical/dense discovery are separate routes. Hard constraints always precede ranking; under is strict, at-most inclusive. Normal discovery ranks literal query coverage first, then experimental title/semantic/price features. Every admitted candidate gets its exact dense score; a semantic top-K is never used to prove the minimum. Price contributes to relevance but does not dominate every request. The cheapest qualifying role is computed separately for every query where supported; unknown/incomplete/subjective discovery limits its claim scope. A full current structured source is required for catalogue-wide minimum/no-match claims.

The current weights and English model candidates have not been tuned on owner judgments. Semantic-only subjective requests cannot safely auto-add a supposedly globally cheapest product. Eligible exact adds and complete structured cheapest-and-add requests can dispatch; ordinary results require a selection. [Architecture and decisions](docs/ARCHITECTURE.md) explains these boundaries and why PostgreSQL was selected over SQLite plus Qdrant.

```sh
voicecart run                          # typed text, real NLU if configured
voicecart run --voice --speak          # explicit microphone turns + optional speech
voicecart run --session-id SESSION_ID  # recover only an unexpired session
voicecart add --session-id SESSION_ID --variant-id VARIANT_ID --operation-id OPERATION_ID --quantity 1 --currency INR
voicecart retry --session-id SESSION_ID --operation-id OPERATION_ID
```

The application prints session/operation IDs. Commands are `/listen`, `/end`, `/stop`, `/repeat`, `/ack`, `/retry OPERATION_ID`, `/cart`, `/quit`. Listen/end controls define a bounded 30-second microphone turn; microphone and output are half duplex. Read a complete text result list, then `/ack` before selecting an ordinal. Completed real response playback can acknowledge that list; interrupted or fallback speech cannot. Repeat replays the response without searching or adding. Stop fences unfinished work and playback; a committed cart add remains committed.

A prepared command persists its operation ID before execution. Cart increment and immutable outcome receipt commit together, followed by a new-connection receipt verification. Retry the **same** ID on uncertain outcomes; never submit a fresh ID to resolve uncertainty. Sessions default to one hour and result lists to five minutes; cleanup occurs at startup and periodically during console use. Expiry removes session carts, commands and receipts; restart recovery is limited to a still-live session and retained operation ID. This is not a stock reservation or merchant cart. IDs are local capabilities, not a multi-user authentication system.

## Local inference and speech configuration

Application startup never downloads models. Provision artifacts separately, verify provenance/terms, then configure explicit hashes. `.env.example` lists every supported setting. The tested Ollama server ran on a private loopback port 11439; normal default is 11434. Use `OLLAMA_NO_CLOUD=1`, bound concurrency and model residency for your device. The client rejects non-loopback endpoints, proxies, redirects, remote model metadata, wrong digests, truncated/nonfinite/duplicate-key output and invalid evidence. No general keyword NLU fallback substitutes for the configured model. Clear configuration errors are returned when unavailable; direct structured CLI search does not need NLU.

Tested local artifacts (development smoke, not a release endorsement):

| Component | Identity / integrity |
|---|---|
| Ollama | 0.40.13 darwin archive SHA-256 `bae29252232b9e1358cf5801a7d65a07442af18fb5467cb68c7fc3711f59c511` |
| NLU reference | `qwen3:4b-instruct-2507-q4_K_M`, manifest digest `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0` |
| NLU challenger | `qwen3:0.6b`, digest `7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`; no automatic promotion |
| Encoder integration candidate | `all-minilm:latest`, digest `1b226e2802dbb772b5fc32a58f103ca1804ef7501331012de126ab22f67475ef`, 384 dimensions, empty prefixes. BGE-small/E5 comparisons remain open. |
| CPU ASR | pywhispercpp 1.5.1, `ggml-base.en.bin`, SHA-256 `a03779c86df3323075f5e796cb2ce5029f00ec8869eee3fdfb897afe36c6d002`, [source revision](https://huggingface.co/ggerganov/whisper.cpp/tree/5359861c739e955e79d9a303bcbc70fb988958b1) |
| TTS | Piper 1.8.0, LJ Speech medium ONNX SHA-256 `6f52a751e2349abe7a76735eb09dc1875298c77ea2342ffd2fef79ff81b87f22`; config SHA-256 `141d612cc0a95ed7efc1ca936b845c2364967f2e9217c5dbfcf69fc4d6c65860`, [source revision](https://huggingface.co/rhasspy/piper-voices/tree/5041a7a49ae5b3a0f30e6837769eb03fdbb231bd/en/en_US/ljspeech/medium) |

Whisper is fixed to English CPU inference in this adapter. Hindi/Hinglish and other platforms are not accepted language profiles. Qwen is Apache-2.0, Whisper/whisper.cpp MIT, MiniLM model terms must be checked against its exact registry artifact; Piper's continuing runtime is GPL-3.0. The LJ card declares its dataset public domain; runtime, voice and transitive dependency terms are separate. There is no project LICENSE decision yet. Owner must approve distribution/licensing before redistribution; downloaded weights remain ignored locally.

## Verification and limitations

```sh
python scripts/verify.py --postgres --package --audit
PYTHONPATH=. python scripts/model_smoke.py --model qwen3:4b-instruct-2507-q4_K_M --output /tmp/nlu-smoke.json
```

The first command runs isolated real PostgreSQL/pgvector, unit/integration/system tests, a separate empty startup probe, compile, Ruff lint/format, mypy, Bandit, pip dependency checks, a fresh installed-wheel regression suite and advisory scanning. Its destructive fixtures require a runner-owned temporary socket/database marker; it never uses the normal application DSN. Advisory scanning and package installation need network. Without `--postgres`, service tests explicitly skip, so that mode is not equivalent evidence. Synthetic products exist exclusively in guarded test code/databases.

Real file-based Piper→Whisper smoke ran on Apple M1, 16 GiB, macOS 26.5.2. Two development utterances preserved budget/negation. Synthesis took 1.3145/0.2302 seconds, ASR 0.6147/0.6159 seconds, initial loading 17.687 seconds. [Model evidence](docs/evidence/MODEL_SMOKE.json) and [NLU evidence](docs/evidence/NLU_SMOKE.json) distinguish actual inference from scripted protocol/device tests. The [full real-model smoke](docs/evidence/FULL_MODEL_SMOKE.json) also verified MiniLM publication/discovery, a Whisper→Qwen→committed PostgreSQL cart/receipt→Piper confirmation and duplicate-final replay without a second increment. That model-switch/cold-context run took 59.1698 seconds for interpretation/validation/search/commit, 1.3044 seconds ASR and 1.0752 seconds confirmation synthesis; model loading/contention is a material deployment limitation. Three development NLU cases are not a held-out accuracy estimate. Initial model failures were safely rejected and prompted extraction fixes.

No microphone/speaker/human accessibility acceptance or calibrated audible latency was measured. PortAudio drain is not acoustic onset. The sub-1.5-second target remains unverified; observed model-stage delays already exceed it in some cases. No meaningful full-turn percentiles can be reported without real device observations and failure denominators. No storage-speed winner, arbitrary-query relevance guarantee or supported maximum catalogue size is claimed.

Audio/transcripts are not written by normal execution. Session data expires in the database; this is logical deletion, not secure erasure of WAL/backups. Keep local service logs and backups private and apply an owner retention policy. Use a screen-reader-compatible terminal; actual VoiceOver/user usability remains a manual gate. For missing devices/models use text controls; for a database outage restore service and retry the original operation ID. For stale data import a validated current full snapshot; never disable safety checks to make a result appear.

See [HANDOFF.md](HANDOFF.md) for remaining owner actions, recovery, Git history approval and verification records; [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) maps sprint acceptance and deferred release experiments.
