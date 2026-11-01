# Merchant contract, SDK and deployment models

Implemented: common Python MerchantAdapter protocol, actual LocalMerchantAdapter, authenticated merchant HTTP routes, server-side JavaScript SDK with TypeScript declarations, local session/search/lookup/refresh/add/quantity/receipt path. The customer/admin workflow uses the same local adapter for discovery, mutation and synchronization. Existing core eligibility/session/transaction/receipt logic is preserved.

Not implemented: Shopify, WooCommerce, Magento/Adobe Commerce, external merchant writes/webhooks, a published npm package or an operated managed cloud service. Their names describe extension targets, not supported integrations. Managed deployment is a documented topology requiring an operator, TLS, real merchant credentials/adapter and approved terms. No pretend merchant response is installed in production.

## System of record

For the local adapter, configured PostgreSQL is authoritative for local catalogue/cart/receipts only. Historical dataset offers remain stale/unknown and never become live Amazon inventory. For an external adapter, the merchant platform must own current product facts, price, stock, availability, cart and transaction outcomes. Discovery indexes are caches; refresh/revalidate against the merchant before writing, carry its durable idempotency key, and reconcile its authoritative outcome before confirmation. A timeout is not proof of either success or failure. Orders/checkout remain outside scope.

Contract: search and exact lookup; atomic expected-revision synchronization; bounded offer refresh; session-scoped add and target-quantity/removal; operation status/receipt lookup. Local refresh rereads current PostgreSQL and cannot magically obtain upstream data. Local mutations require finalized explicit intent, stable operation ID, observed revision/unit price, current eligibility and immutable committed receipt. No automatic retry with a new operation ID occurs. The SDK does not retry writes implicitly.

## Actual API and SDK

All merchant operations below require a server-side scoped admin bearer credential. Base: /api/{merchant}/merchant/. POST sessions, search, lookup, refresh, cart, add, quantity, operation. Synchronization uses POST /api/{merchant}/admin/import with the documented full-snapshot schema and previous_revision. Customer browser cookies have no merchant/admin authority. Limits: 100 refresh IDs, quantity 1–99 (0 removes), 2 MiB JSON, configured rate/timeouts. Integer money beyond JavaScript's safe range is returned as decimal strings; the SDK forwards exact minor-unit strings unchanged. No currency conversion is implied.

```js
import {VoiceCartMerchantClient} from './sdk/voicecart.mjs';
const client = new VoiceCartMerchantClient({
  baseUrl: process.env.VOICECART_API_ORIGIN, // HTTPS for managed remote service
  merchant: process.env.VOICECART_MERCHANT,
  adminToken: process.env.VOICECART_MERCHANT_TOKEN // server only, never browser bundle
});
const {session_id} = await client.createSession();
const results = await client.search('coffee maker', {currency: 'USD'});
// Obtain explicit customer authorization and use only a current verified offer.
// Historical metadata is discovery-only and will not authorize this operation.
const item = results.items.find(item => item.can_add);
if (item) {
  const operation_id = crypto.randomUUID(); // persist BEFORE the request
  const receipt = await client.addToCart(session_id, {
    operation_id, variant_id: item.variant_id, quantity: 1,
    currency: item.currency, revision: item.revision,
    unit_price_minor: item.price_minor
  });
  console.log(receipt.status); // confirmation only after verified receipt
}
```

A merchant server/BFF owns end-customer authentication and maps its customers to VoiceCart sessions. Never expose its admin key in a widget or browser. Same-origin customer UI uses HttpOnly capabilities; wildcard cross-origin browser access is not enabled. SDK remote URLs require HTTPS; explicit loopback HTTP is allowed for development. Redirects are rejected to prevent credential forwarding. A failed write carries the caller's retained operation ID; inspect operation status and retry the identical authorized payload, never an invented replacement.

## Isolation and topology

Self-hosted: merchant runs Compose/API plus a dedicated PostgreSQL database and separately provisioned local inference; source/platform refresh and secrets stay under its control. Managed option: operator runs those services, assigns each merchant a distinct database/credential/config and HTTPS API origin; merchant installs only the small server-side SDK/BFF integration. This topology is supported by configuration, not a claim that a managed service is currently deployed.

Optional VOICECART_TENANTS_FILE is private JSON mapping canonical merchant IDs to database_url, admin_token_file and currency. Each entry requires a distinct database; duplicate physical database identity is rejected. Capabilities include tenant and role; wrong merchant credentials/session IDs fail. Maximum 16 explicitly configured merchants per process is a bounded prototype profile, not a measured tenancy capacity. Database, catalogue, cart, analytics and logs are isolated by tenant; TLS, rate limits, secret rotation, backups and retention remain operator responsibilities.

External webhook adapters must verify signatures, event identity, ordering and source revision before publication; no webhook endpoint is invented before an actual merchant contract exists. Polling/full-snapshot synchronization is the implemented integration route. Preserve the protocol and conformance tests when adding an adapter; do not leak platform-specific error/transaction semantics into core authority.

## Verification

`node --test sdk/*.test.mjs` against the disposable browser-driver server runs an actual local SDK→HTTP→PostgreSQL session/search/add/replay/receipt/refresh/quantity/remove flow. `npx tsc --strict --noEmit --module nodenext --target es2022 sdk/typecheck.mts` checks the declarations and required operation identity. Python tests compare adapter/core outcomes and create two actual isolated databases to test catalogue/auth/session isolation. Fixtures remain test-only and labelled. No external merchant certification is claimed.
