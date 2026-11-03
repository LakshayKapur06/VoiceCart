# Current catalogue and external merchant integration specification

3 November2026. Implemented local adapter/SDK only. No authorized platform sandbox credentials/current source were supplied. Shopify/WooCommerce/Magento, external stock/cart webhooks and operated managed hosting are **not implemented**. This specification is preparation, not an integration success claim. Actual local SDK→HTTP→PostgreSQL path, two-database isolation and source/receipt contracts are tested in the existing suite.

## Required source/authority agreement

Before choosing a platform, owner provides merchant authorization, supported API version/docs, sandbox account, least-privilege product/variant/inventory/cart access and permitted data/media use. Preserve exact upstream product ID, purchasable variant ID/SKU, canonical attributes and parent mapping; never collapse different sizes/colours/prices into one invented variant. Record original currency/integer minor units, tax/price basis, current price timestamp/source revision/expiry, available/quantity semantics and refresh SLA. Unknown stock/price remains unknown. Coverage complete/partial/unknown is an explicit authority assertion, not inferred from pagination or embeddings.

Historical Amazon crawl metadata remains historical/read-only: no current inventory, currency conversion, live-Amazon cart or guaranteed real-world global minimum. Review current-source permissions/terms before importing or displaying media. No synthetic offers may fill missing operational data. Owner's real source must be separately versioned/backed up and imported through strict atomic CAS; incomplete source restricts minimum/no-match claims.

## Contract mapping

| Adapter responsibility | Required external implementation / authoritative record |
|---|---|
| search / lookup | Map supported hard constraints and exact upstream identities; define pagination and coverage, combine lexical/semantic discovery without claiming topK minimum |
| synchronize | Full validated snapshot with new revision/previous_revision CAS, provenance and generation-pinned derived features; obsolete snapshots cannot overwrite newer facts |
| refresh_offers | Read actual upstream current price/stock at bounded IDs; return timestamp/revision/expiry and unknown/error state, not invented success |
| add | Final explicit authorized customer instruction, exact observed variant/price/currency/revision, platform customer/cart mapping and retained operation identity; revalidate in upstream authority |
| set_quantity/remove | Upstream target-state semantics including0 removal, aggregate stock/current offer check; immutable operation result |
| cart | Current upstream cart state/currency/unknown totals and version, local data is not external checkout truth |
| operation | Authoritative upstream operation/receipt reconciliation, prepared/committed/rejected/unknown states; no guessed success |

Merchant BFF authenticates end customers and maps each to a scoped VoiceCart/local session AND upstream cart. Privileged SDK key remains server-side; customer cookies cannot access merchant endpoints. Different tenants use different physical databases/keys/config. Document the scope of any upstream OAuth/app token, rotation/revocation, storage and network permissions. Never put merchant admin credentials in a storefront widget.

## Mutation and failure semantics

Persist operation ID and canonical payload fingerprint before the write. Forward a supported upstream idempotency key, or implement a rigorously verified upstream operation ledger/reconciliation contract before exposing writes; a blind POST retry is not enough. Timeout/connection loss after commit means UNKNOWN until authoritative read. Retry the same original ID/payload only. Changed payload with same ID rejects. A local PostgreSQL commit cannot prove an external platform committed. Cancel before dispatch fences work; after commit return/verify the receipt and do not pretend rollback. Stock changes or price/revision mismatch require refreshed facts/new explicit confirmation.

Map invalid input/auth/permissions/expired session/stale offer/stock shortfall/rate-limit/transient failure/uncertain outcome separately. Show safe recovery text and original ID without SQL/tokens/raw private logs. Do not use successful HTTP status alone as confirmed commerce success. Respect Retry-After on read/status operations; do not automatically repeat writes with a new identity.

Optional future webhooks require actual documented signature verification, timestamp/replay window, event identity/order, source-version comparison and duplicate/out-of-order tests. No webhook endpoint exists now. Polling/full snapshots are implemented locally. Backups/retention and upstream event reconciliation must preserve authority across restart.

## Sandbox acceptance plan (NOT RUN externally)

1. Record written authorization, platform/API version, scopes, sandbox tenant/cart and source rights. Keep credentials private.
2. Import actual sandbox variants with known/missing/stale fields; compare every mapped price/currency/stock/parent against platform. Reject duplicate/orphan/invalid data atomically.
3. Search exact and constrained cases; prove price minimum over the declared complete eligibility scope, not just vector shortlist. Record unknown/partial cases.
4. Explicitly add a current offer and verify upstream committed cart/receipt. Repeat identical ID; verify one mutation. Alter payload under same ID; reject.
5. Change stock/price/deactivate after search; stale add/increase must fail/reconfirm. Test two simultaneous sessions and target-quantity writes using upstream concurrency semantics.
6. Inject precommit failure and committed-but-lost response. Reconcile original ID across BFF/API restart and ensure no duplicate. Unknown remains unknown if authority unavailable.
7. Test wrong tenant/customer/auth scope, expired/revoked credentials, rate limits and (if actually implemented) signed duplicate/out-of-order webhook events.
8. Restore staging backup, refresh upstream facts and compare carts/receipts/revisions before switching. Record resource/load bounds separately from production capacity.

Each case records expected/actual result, environment/SHA/API version, redacted request/receipt/source IDs, failure timing, status and reviewer. No external acceptance may be marked Pass based on the local adapter. See HUMAN_INVOLVEMENT_REQUIRED taskMERCHANT-SANDBOX and CATALOGUE-RIGHTS.
