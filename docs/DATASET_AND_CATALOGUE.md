# Historical demonstration catalogue

The continuation explicitly selects [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/) product metadata. Official [field definitions](https://amazon-reviews-2023.github.io/#data-fields) identify prices as US dollars at crawl time and parent_asin as the parent metadata identity, not a verified purchasable variant. This is neither live Amazon inventory nor an Amazon merchant/cart integration.

Pinned official [dataset repository](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/2b6d039ed471f2ba5fd2acb718bf33b0a7e5598e), Appliances category, first 300 source rows. Local extract SHA-256 a3b27ecae6fa5c498860b7ea9dbd706fbe7906eed0c03d7d22e965cbdeb4809b. The source URL/revision and per-record line/hash/provenance are preserved. Raw source records, images and normalized product files are ignored local assets, not distributed in this repository. Only counts and quality evidence are committed.

```sh
python scripts/download_metadata.py --rows 300
python -m voicecart.dataset .local/datasets/appliances-first300.jsonl .local/datasets/appliances-source.json --output .local/datasets/appliances-normalized.json --report /tmp/catalogue-quality.json
voicecart init-db
voicecart import-catalogue .local/datasets/appliances-normalized.json
```

Normalization preserves title/category/descriptions/features, known brand/attributes/images, original price representation and raw metadata. Missing data stays missing. Decimal parsing converts valid historical USD to integer cents without exchange-rate conversion; malformed/negative/nonfinite/fractional-cent prices remain unknown. Parent metadata gets an explicitly unspecified discovery representation, not an invented sellable size/variant. Explicit source colour/size fields are retained. Availability/stock remain unknown and price freshness stale, so existing commerce qualification prohibits adding these records. Full source snapshots still publish atomically with expected revision, all derived search text, metadata and import history. Repeating an unchanged revision conflicts rather than duplicating records.

Read-only CatalogueBrowser exposes such records without relaxing cart safety. Price comparisons are scoped to imported historical matching data with explicit currency; never a live global minimum. Exact identity and lexical/brand/category discovery are supported. Dense retrieval in the existing core remains separately versioned; configuring an encoder for import generates actual local vectors. Missing stock is not made available merely to let a demo cart succeed. Supported current-offer/cart tests use isolated, clearly fabricated fixtures only; a real merchant must supply current authoritative facts for real adds.

Initial quality: 300 source rows, 298 admitted, 2 rejected, 0 duplicate IDs, 169 known historical prices and 0 known current-stock records. Exact report and source revision are in evidence/DATA_QUALITY_20261102.json. Rejected rows are indexed without committing their contents. Source fields exceeding strict existing contract bounds are rejected, not silently truncated into apparently complete records.

## Terms and attribution

Official dataset card/site inspected 2026-11-02 contained no explicit dataset redistribution license declaration. Access is not proof of commercial redistribution rights. The owner's requested private research/development extract was downloaded; no raw dataset/voice/image assets are packaged. Redistribution/commercial deployment remains blocked on owner rights verification. Contact the dataset maintainers for terms. Attribute: Hou, Li, He, Yan, Chen and McAuley, “Bridging Language and Items for Retrieval and Recommendation,” 2024, arXiv:2403.03952. Images remain external URLs and require a separate rights/privacy decision before loading or redistributing.

## Actual dense discovery check

The existing encoder/pgvector adapter also published all 298 admitted real records with the opt-in metadata-prefix-256utf8bytes-v1 profile (full source/FTS text preserved), then executed an actual MiniLM+pgvector microwave query. Publication took 2.9040s and query 0.0393s in this development observation, with zero actionable historical page records. Exact model digest/generation/methodology are in DATA_SEMANTIC_20261102.json. This does not establish relevance quality or a comparable before/after speedup. Enable VOICECART_EMBED_SERIALIZER together with the pinned MiniLM model/digest/dimensions and reimport the complete snapshot using a new revision to activate this profile; changing it requires matching re-embedding. See ADR-002.
