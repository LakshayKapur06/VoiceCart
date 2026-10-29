# Sprint 3 — constrained local interpretation

Implementation: loopback-only Ollama JSON transport with proxy/redirect rejection, explicit model digest verification, bounded request/response generation, strict shared extraction schema and independent evidence checks. Quantity, INR minor units, strict/inclusive and total/per-unit budgets, canonical vocabulary, literal identifiers, ordinals, negation, unsupported fields and malformed/truncated outputs are covered. Unsupported adjectives cannot be discarded to upgrade discovery to a catalogue-wide structured claim. Model output has no database/cart access.

Existing source type errors were corrected without changing the catalogue selection rules. Development type/security/build tools are configured. pip 25.0.1's reported advisories were remediated by upgrading the local development installer to 26.2.2. The normal application database is not configured or populated; this increment creates no product storage and no seeds.

Automated story acceptance: `tests/test_nlu.py`, including real loopback HTTP requests to an explicitly scripted server. No neural extraction quality is inferred from that protocol test. Baseline domain/audio regression remains intact. The shared `scripts/verify.py --package` runs unit/integration/system-boundary/automatable story tests, lint, format, type, security, compilation, dependency, diff and installed-wheel gates.

Reference model remains provisional Qwen3-4B-Instruct-2507 via Ollama. Actual runtime/model inference, held-out shopping-language quality and challenger selection are not signed off by mock responses. Real adapter provisioning and application integration continue in later increments; no universal relevance, hardware, language or latency claim.

Commit/push: engineering gates must pass before normal main push; verified hash is entered in the following increment's execution record to avoid a self-referential commit hash.
