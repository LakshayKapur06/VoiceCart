> Historical sprint contract/evidence. Current runnable behavior and release limitations are in README and HANDOFF.

# Sprint 1: deterministic catalogue foundation

This increment implements **F-01–F-06** from [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md). It is an offline pure-Python domain slice, not a working voice shopping application. The PostgreSQL/pgvector reference and all model integrations remain planned. [ARCHITECTURE.md](ARCHITECTURE.md) is unchanged historical research; its pre-implementation statements describe its recorded review commit.

## Implemented surface

| File | Responsibility |
|---|---|
| `voicecart/domain.py` | Frozen typed products/variants, integer money, price operators, constraints, identifier/request/result types and explicit unknown/scope/error states. |
| `voicecart/catalogue.py` | Small Catalogue protocol, pure three-valued qualification and immutable in-memory authority snapshot with exact lookup and exhaustive structured selection. |
| `voicecart/ranking.py` | Versioned policy protocol and qualified-ID permutation validation; no default scorer/weights. |
| `tests/fixtures.py` | Clearly synthetic, explicitly current/completeness-controlled test data builders. No production special cases. |
| `tests/test_domain.py` | Money/type/identity/request validation and immutability. |
| `tests/test_catalogue.py` | Complete-set oracle, constraints, unknowns/freshness/coverage, variant identity, ties and exact lookup. |
| `tests/test_ranking.py` | Ranking/minimum role separation and rejection of ineligible/duplicate/missing policy outputs. |
| `pyproject.toml` / `.gitignore` | Python >=3.11, zero runtime dependencies, bounded setuptools build backend, pinned optional Ruff; local environment/build/cache exclusions. |

No runtime application framework, SQL service, inference SDK, async workflow engine, network call or persistent sensitive-data logging was added. Tests use stdlib unittest. Ruff is a development-only lint/format tool, not an application dependency or type checker.

## Supported contracts and assumptions

- **Identity:** separate canonical product and purchasable variant IDs, optional unique variant SKU and product model number. Typed exact lookup distinguishes namespaces and uses case-sensitive equality. Product/model IDs may resolve to multiple variants; a lookup is not a purchase authorization or a unique size/colour decision.
- **Money:** nonnegative integer minor units with an explicit three-uppercase-letter currency code. Formatting is checked, not a full ISO registry. Floats, booleans, strings and values outside PostgreSQL bigint’s nonnegative range are rejected. No conversion or natural-language amount parsing occurs.
- **Budget:** PriceOperator.LT means strict “under”; LTE means inclusive “at most.” Budget/search currency must agree. Sprint 1 supports a **unit-price budget**, even for quantity >1. Total-increment/existing-cart budgets require a future typed extension and semantic validation, not reinterpretation of this field.
- **Hard fields:** canonical category, colour, size, currency, unit-price bound, active/available state and requested quantity. Values are exact canonical strings; no alias, fuzzy, case folding or description-based inference. Unsupported keyword fields fail construction; descriptive text must use DISCOVERY, which explicitly returns UNSUPPORTED in this increment. Do not silently route a subjective request through the structured API.
- **Unknowns:** missing category/colour/size, price/currency, price freshness, availability or multi-unit stock remain unknown when relevant. A known mismatch makes the record a nonmatch even if another attribute is unknown. No matching hard fact is extracted from prose.
- **Availability:** available=True explicitly asserts at least one unit; unknown stock quantity cannot establish quantity >1. Known quantity must cover the request. This is fixture eligibility only, not inventory reservation or aggregate cart validation; those require Sprint 5 transactions.
- **Freshness:** each variant’s price freshness defaults to UNKNOWN. A missing, stale or unverified price cannot qualify or prove a budget nonmatch, even when its old price exceeds the limit. CURRENT is a source assertion about this immutable snapshot, not an implemented TTL, merchant check or perpetual guarantee.
- **Coverage:** defaults to UNKNOWN and never follows from all loaded rows being well formed. COMPLETE asserts that **all purchasable variants in the declared source** are present, not that the whole market is covered. PARTIAL/UNKNOWN block complete minimum/no-match claims. Reject invalid/duplicate/orphan snapshot records rather than dropping them and declaring the rest complete.
- **Snapshot:** frozen records and a copied read-only item map prevent mutation through the public interface or later changes to input lists. Every result carries its catalogue revision. Publication, updates, per-row action revisions and database snapshot isolation are later adapter work.

`qualify(item, constraints)` returns QUALIFIED, REJECTED or UNKNOWN with reason codes. `search` visits the full snapshot (or exact-identifier set), retains only qualified records and computes the minimum by `(price_minor_units, variant_id)`. Input order does not change a tie. The `matches` tuple is in stable variant-ID order; this is **not** relevance-ranked or an approved spoken presentation.

## Result states and scope

| Result state | Meaning / caller obligation |
|---|---|
| MATCHES with COMPLETE_CATALOGUE | The complete provided structured source supports this constrained minimum at its recorded snapshot. `can_claim_catalogue_minimum` is true when a qualifying item exists. It is not a future-price or universal relevance claim. |
| MATCHES with EXACT_IDENTIFIER | The complete declared identifier set has qualified results; `can_claim_catalogue_minimum` stays false. Do not replace an explicitly identified variant or confuse its minimum with a whole-catalogue minimum. |
| INCOMPLETE | Potentially qualifying unknowns or partial/unknown source coverage remain. A cheapest known qualified candidate may be returned under VERIFIED_RECORDS scope, but cannot satisfy a catalogue-wide cheapest authorization without clarification/agreement to narrower scope. An empty result is not verified no-match. |
| NO_MATCH | Complete coverage and known rejections establish no eligible item in the declared query/identifier scope. `can_claim_no_match` is true; no minimum exists. |
| UNSUPPORTED | Discovery is not implemented. No structured fallback, unverified relevance claim or false no-match is produced. |

Every supported structured/exact search computes the cheapest qualifying role even if ranking is not configured. Unknowns can make it unavailable or scope-limited, with explicit issues. **No action executor exists**; downstream code must not treat a known scoped candidate as authority to mutate under an unfulfilled global-minimum request.

## Ranking seam and D14

An optional RankingPolicy receives only already-qualified immutable CatalogueItems and the typed request. It must expose a nonblank version and return every qualified variant ID exactly once. Invalid, missing, duplicate or foreign IDs raise RankingContractError; canonical facts are hydrated from the original records, not supplied by a scorer. A policy that changes its version during rank() is also rejected so that results cannot silently record an outdated policy identity. This check does not make arbitrary policy code thread-safe; implementations must still preserve immutable version/configuration contracts.

`ranked_matches`/`overall_match` are separate from `cheapest_qualifying_match`. Without a policy, ranked_matches is empty and overall_match is None, accurately reflecting unevaluated relevance. Tests inject explicit fixture judgments to show that a better-fitting higher-priced match can rank first while a cheaper match remains separately available; this is not an implemented optimal production formula or a human relevance measurement.

Sprint 4 must validate query-fit/preference/price features, qualification and weights on development labels, freeze policy versions, compare held-out human judgments and exhaustive composite-score recall, and measure cost. No final weights or arbitrary “best for every query” promise is supplied here. **D14 is unresolved:** separate cheapest presentation is a working proposal; backend roles do not approve its UI placement.

## Executable example

This doctest uses one synthetic product with two distinct purchasable variants. Both prices/coverage are explicitly asserted for this example only.

    >>> from voicecart.catalogue import InMemoryCatalogue
    >>> from voicecart.domain import (Coverage, Freshness, HardConstraints, Money,
    ...     PriceLimit, PriceOperator, Product, ProductId, SearchRequest, Variant, VariantId)
    >>> parent = Product(ProductId("bag"), "Example backpack", category="backpack")
    >>> cheap = Variant(VariantId("v-cheap"), parent.product_id, Money(90000, "INR"),
    ...     colour="black", available=True, stock_quantity=3, price_freshness=Freshness.CURRENT)
    >>> dear = Variant(VariantId("v-dear"), parent.product_id, Money(150000, "INR"),
    ...     colour="black", available=True, stock_quantity=3, price_freshness=Freshness.CURRENT)
    >>> db = InMemoryCatalogue([parent], [dear, cheap], revision="example-v1", coverage=Coverage.COMPLETE)
    >>> query = SearchRequest(HardConstraints("INR", category="backpack", colour="black",
    ...     price_limit=PriceLimit(Money(200000, "INR"), PriceOperator.LT)))
    >>> result = db.search(query)
    >>> str(result.cheapest_qualifying_match.variant.variant_id)
    'v-cheap'
    >>> result.can_claim_catalogue_minimum
    True
    >>> result.overall_match is None
    True

The result does not claim that a real ₹900 product exists or that anything was added to a cart.

## Development and verification

Use an installed Python >=3.11; system Python 3.9 is unsupported. Tests are available directly from the repository root without installation or network access:

```sh
python3.12 -m venv .venv
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -S -m unittest discover -s tests -q
.venv/bin/python -m doctest docs/SPRINT_1.md
.venv/bin/python -m compileall -q voicecart tests
```

The `-S` run disables site-packages to check that the domain/tests need no installed application, inference library or third-party test dependency. It is not a network interception or full offline voice/privacy test.

For editable packaging and configured lint/format checks:

```sh
.venv/bin/python -m pip install --no-cache-dir -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pip check
git diff --check
```

Package installation can contact the package index; no model/runtime service was provisioned. The pure tests do not import network/model adapters. A later PostgreSQL implementation must run the same observable contract cases plus real SQL isolation, publication, recovery and concurrency tests rather than replacing these with green mocks.

### Verification record

**Follow-up completed on 27 October 2026.** The first Sprint 1 push (`048421c`) deliberately deferred final checks at the owner’s request. This follow-up completes those checks and fixes a reproduced ranking-version audit bug: if a policy changes version during rank(), the result is now rejected rather than labelled with the old version. A regression test covers that case.

The development interpreter is CPython 3.12.14. Python 3.11 is the declared minimum but was not independently exercised on this machine. Ruff 0.14.2 is pinned; the offline wheel build used the bundled Python with setuptools 84.1.0, within the declared build bounds. No static type checker is configured; lint and compilation are not type-check verification.

| Check / command executed | Actual outcome |
|---|---|
| `.venv/bin/python -m unittest discover -s tests -v` | All **54 tests passed** after the ranking guard and regression test. |
| `.venv/bin/python -S -m unittest discover -s tests -q` | All **54 tests passed** with site-packages disabled. |
| `.venv/bin/ruff check .` | Passed; no lint findings. |
| `.venv/bin/ruff format --check .` | Passed; all nine Python files already formatted. |
| `.venv/bin/python -m doctest -v docs/SPRINT_1.md` | All **11 example checks passed**. |
| `.venv/bin/python -m compileall -q voicecart tests` | Passed. |
| `.venv/bin/python -m pip check` | No broken requirements found. |
| Offline wheel build using `pip wheel --no-build-isolation --no-deps --no-index --no-cache-dir` | Passed; the wheel’s four application modules matched current source byte-for-byte, with no tests, caches or virtual-environment code included. |
| Fresh temporary venv: `pip install --no-index --no-deps <wheel>`, isolated `-I` import, full unittest suite, doctest and pip check | Passed outside the checkout, importing the installed wheel from site-packages; **54 tests and 11 example checks passed**. |
| Document structure/local-link audit | Markdown table widths, fences, local file links, README section order and E01–E11/D01–D15 register coverage passed. ARCHITECTURE.md remained byte-identical to the original review commit. |
| Dependency/import and change review | Application imports remain stdlib/local only; no inference/network/process adapter was added. The final diff and whitespace review found no unrelated changes; a limited tracked-file secret-pattern scan found no matching keys/tokens. |

No Sprint 1 check remains deferred from the fast push. This evidence covers the deterministic slice on the stated interpreter, not the future voice/database application, every supported Python version or universal real-world correctness. The wheel/install checks used only local files; they are not a full offline voice/privacy experiment.

The suite includes a deliberately omitted cheapest semantic candidate, exact lookup namespaces, variant colour/size/price/stock isolation, price ties under input permutations, missing/unknown/stale facts, currency, zero price, coverage default/partial/complete, empty/no-match scopes, hard qualification before ranking, overall-versus-cheapest roles and rejection of policy-version changes during ranking. An independent full-source oracle checks 25 seeded generated catalogues under both LT and LTE. This is deterministic fixture evidence, not universal correctness or product relevance benchmarking.

## Not delivered or measured

PostgreSQL/pgvector/FTS, embeddings, a production semantic/ranking policy, model artifact downloads, ASR/NLU/TTS, microphones/playback, screen-reader integration, sessions/result-list announcements, cart mutation/idempotency/receipts and merchant APIs are not implemented. Neither a voice workflow nor accessibility, language coverage, end-to-end latency, resource capacity, offline model operation or storage-comparison win has been established. No add, checkout, payment, order or deployment is performed.

D01–D15 stay in the plan; in particular D14’s presentation and D15’s measured storage fit remain open. Sprint 2 should build the narrow local audio feasibility/control/timing slice, with eligible artifacts and explicit device/language assumptions, without expanding into later sprints.
