# Implemented HTTP API (0.2.0)

Same-origin JSON over the configured API origin. HTTP loopback is development only; remote deployment requires HTTPS and fixed VOICECART_PUBLIC_ORIGIN. Successful /health is database/schema readiness, not proof of speech devices/model quality. No wildcard CORS. Host/Origin, body/type/rate limits and tenant capabilities are enforced server-side.

All request bodies are JSON objects, maximum 2 MiB. Money uses integer minor units; exact decimal strings are accepted where documented for JS precision. Returned integers beyond 2^53−1 are encoded as decimal strings. Never round or convert currencies implicitly. Session/turn/list/operation identities are canonical UUIDs. Customer capability cookies are HttpOnly/SameSite=Strict, scoped to merchant API paths; admin uses its own role/cookie or server-side scoped bearer key. Credentials never belong in storefront JS.

## Public/static

| Method/path | Behavior |
|---|---|
| GET / | Customer semantic HTML client |
| GET /admin | Separate admin client; API data still requires admin authorization |
| GET /app.js, /admin.js, /style.css | Packaged same-origin static assets |
| GET /health | Checks packaged migration checksums/schema and pgvector; returns status/service/merchant count or unavailable |

## Customer /api/{merchant}/

POST sessions creates or resumes an unexpired customer capability. Other routes require its cookie. The default configured merchant ID is local; multi-tenant storefront URL is /?merchant=ID (admin link preserves it).

| Method/resource | Body / response contract |
|---|---|
| POST sessions | `{}` → session_id, merchant, currency; sets customer cookie on new session |
| POST turns | `{}` → turn_id; register before an async final instruction. Existing unresolved prepared operation blocks a new turn. |
| POST search | query (0–1000 chars), optional turn_id, brand/category, currency, under_minor (integer/string), inclusive (boolean), offset≥0, limit1–100 → items,total,revision,coverage,known-price role and scope. All filters apply; text price instructions must match explicit controls or are rejected. |
| POST query | text (1–4000 chars), required registered turn_id → actual application Response including code/text/listing/operation_id/receipt where available. Cancelled/superseded finals cannot restart execution. |
| POST ack | list_id,turn_id → acknowledged; user explicitly confirms the complete current list before ordinal references |
| POST cancel | `{}` → stopped status; already committed writes remain committed and need receipt verification |
| POST repeat | `{}` → last response without another search/write |
| POST transcribe | pcm_base64: mono signed 16-bit little-endian 16kHz, max30s → text,requires_review=true,cart_mutated=false. Configured local ASR only; stale/cancelled results rejected. |
| POST speak | `{}` → actual local Piper audio/wav for the last response; unavailable configuration fails with text recovery. Synthesis is not audible-delivery proof. |
| GET cart | Current verified-price lines, per-currency integer subtotals, unpriced_lines/totals_complete, scope; no checkout |
| GET operations | Up to10 recent owned add/quantity operation IDs/status/timestamps for interruption recovery; no other session records |
| POST cart/add | operation_id,variant_id,quantity1–99,currency,revision,unit_price_minor → verified immutable receipt/application confirmation; same ID/payload replays safely |
| POST cart/quantity | operation_id,variant_id,quantity0–99,currency → committed target-state receipt. Zero removes; increases revalidate current total stock. |
| POST cart/retry | operation_id → reconcile/replay an existing owned authorized operation. Never creates a replacement ID. |

Each item identifies variant/product, known attributes, currency/price/freshness, source metadata, historical flag, revision and can_add. Unknown/stale offers cannot be made current by changing a client field. Public metadata excludes raw source payload/video/user fields. Historical minimum is only a lowest known matching imported price, never a live global minimum. Optional dense discovery is generation-checked and explicitly uncalibrated.

Example final flow: POST sessions; POST turns; POST query with returned turn_id and reviewed text. Display the full truthful response; POST ack only after explicit complete-list review. Explicit UI product buttons instead submit an exact observed variant/price/revision and caller-generated operation ID. Store the operation ID before sending. Cancel/abort is not rollback of an in-flight mutation; inspect cart/operations and retry the original ID after uncertainty.

## Admin /api/{merchant}/admin/

| Method/resource | Behavior |
|---|---|
| POST login | token32–256 chars → scoped30-minute admin cookie; rate-limited constant-time credential comparison |
| POST logout | Clears browser admin cookie; rotation required to revoke copied capabilities centrally |
| POST catalogue | query/brand/category/currency/offset/limit → actual catalogue/provenance, never fake rows |
| GET export | Current full source snapshot, preserving raw source facts rather than expired-display substitutions; assign a new revision/expected previous revision before reimport |
| POST import | Validated full snapshot → atomic committed revision/counts. Invalid/duplicate/stale input returns issues or reload instruction; no partial publication. |
| GET imports | Actual last100 publication records |
| GET analytics | Actual environment-scoped event aggregates/catalogue coverage/committed local adds; raw popular queries and checkout conversion explicitly unmeasured |
| GET health | Actual DB/publication/model identity check, environment and telemetry failure counter; physical devices not measured |

Create/edit/variant/deactivation UI operates through full-snapshot export/validated CAS import. No separate unsafe row-write or CSV endpoint is invented. Owner must supply factual source/expiry/current offer data; historical prices are not silently promoted. Large imports use CLI file validation.

## Merchant-server /api/{merchant}/merchant/

All routes POST and require the configured merchant's admin bearer credential (or admin capability), separate from customer cookies. sessions `{}` creates a local session; search accepts query/filters; lookup product_id; refresh variant_ids (1–100); cart session_id; add session_id plus exact AddIntent; quantity session_id plus target-state fields; operation session_id,operation_id returns committed receipt/prepared/rejected/cancelled/unknown state. Synchronize via admin/import. See MERCHANT_SDK.md for the actual JS/TS client and platform-authority requirements. No webhook or external-platform endpoint is implemented.

## Errors and uncertainty

400 invalid types/limits/schema or stale admin revision; 403 missing/expired/wrong role/tenant/origin/host; 404 unknown static/admin/merchant endpoint where implemented; 405 merchant method mismatch; 409 unverified/rejected/conflicting/uncertain cart or cancelled transcript/search; 429 rate window; 503 unavailable DB/model/runtime. Application query/retry may return HTTP200 with a non-success Response.code such as clarify/retry_rejected; clients must inspect it. Only a committed verified receipt is success. Infrastructure errors never return SQL, secrets or a fabricated transaction outcome. Socket saturation can close an excess connection; retain IDs exactly as for any unknown response.
