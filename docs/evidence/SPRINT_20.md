# Sprint20 — transaction expiry, uncertain receipts and bounded concurrent sessions

Seven new real-SQL transaction scenarios and two correctness fixes delivered. Targeted25 pass; source215+fresh wheel215 pass, static/type/security/package/advisory checks and measured coverage retained. Initial wrong error-type expectation retained and corrected to the existing public CartError code. No assertions weakened or core replacement. [Detailed report](../TRANSACTION_AND_SCALE_20261103.md).

Actual128 searches/eight workers/2000 synthetic variants and16 concurrent idempotent cart sessions completed with zero failures; resource/timing/scope limits recorded. No production/voice SLA claim. [Load](20261103_S20_load/LOAD.json). Current-source rights/credentials/external sandbox unavailable; [merchant specification](../MERCHANT_INTEGRATION_SPEC.md) prepares real integration without installing a fake adapter. Human/owner staging recovery remains required.
