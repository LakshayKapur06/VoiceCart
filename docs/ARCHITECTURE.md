# Architecture and decision record

Updated 29 October 2026. This consolidates the useful architecture review; executable modules and [README](../README.md) define current behavior. Earlier review instructions and speculative implementation status have been retired.

## Authority and flow

Explicit microphone turn → CPU Whisper final → bounded local Ollama schema extraction → independent evidence/negation/amount/attribute validation → exact, structured or discovery route → qualified/ranked results with separate cheapest scope → fully presented selection → prepared operation → transactional cart/receipt → fresh receipt lookup → text/optional Piper response. The model never owns prices, inventory, qualification, IDs, writes or outcomes. Cancellation fences late work; it cannot undo a committed transaction. Incomplete audio delivery cannot establish that a list was presented.

| Review change | Implemented responsibility and reason |
|---|---|
| ARCH-001 | `catalogue.py`, `search.py`: full-source structured qualification; semantic shortlists cannot prove a minimum. Unknown potentially eligible records block a complete claim. Missing variants also count as unknown. |
| ARCH-002 | `database.py`, migrations: PostgreSQL facts, vectors, FTS, sessions and receipts share a publication/transaction/recovery boundary. Repeatable-read search snapshots and guarded publication prevent mixed revisions. |
| ARCH-003 | `search.py`: lexical and exact dense discovery; positive semantic/lexical candidates, deterministic hard filters, deduplication and stable ties. No unmeasured ANN shortcut. |
| ARCH-004 | `nlu.py`, `local_http.py`: pinned artifact, JSON schema, literal evidence-constrained decoding, independent validation. Structured syntax does not establish permission or facts. Malformed/dropped/negated fields fail safely. |
| ARCH-005 | `sessions.py`, `cart.py`, `application.py`: turn fencing, once-only finals, expiring presented lists, operation fingerprints, session isolation, immutable receipts and bounded concurrency/recovery. |
| ARCH-006 | `audio.py`, `voice.py`, `cli.py`: half duplex, bounded explicit capture, stop/repeat/end controls, text equivalents and explicit output failure. Older AudioPipelineSlice is a contract helper, not proof of spoken errors. |
| ARCH-007 | Verified local Whisper/Piper files and runtime versions; separate runtime/voice/source terms. GPL/voice distribution remains an owner decision. |
| ARCH-008 | Real local inference smoke on a recorded M1 host; no fabricated device latency, percentiles or memory minimum. Shared inference contention and cold loads remain relevant. |
| ARCH-009 | Literal coverage tier, experimental .65 title + .25 semantic + .10 price utility (100000-minor scale); distinct cheapest role. Exact score coverage regression includes a relevant middle-price product outside a former dense top-50. Human relevance is still unmeasured. |

Discovery's cheapest role is scoped to verified literal-query matches where available, not an assertion that a vague semantic request defines the globally correct category. Its minimum can be unavailable when evidence is insufficient. Every query attempts this role; impossible guarantees are reported as uncertain instead of inventing a product. Structured complete/current sources support a stronger minimum. Presentation keeps overall relevance and cheapest distinct. No neural reranker is justified before owner relevance judgments establish ordering rather than recall as the bottleneck.

## Why PostgreSQL and pgvector

The selected reference uses one SQL store because eligibility, complete price ordering, atomic catalogue publication, session cart mutation and receipts need relational consistency. A separate SQLite/Qdrant pair requires coordinating authority, derived-index versions, recovery and freshness across stores. One snapshot/transaction boundary reduces that work. It does not automatically make multiple default-isolation reads consistent; explicit snapshots and locks are still required.

This decision was based on required consistency, not a preference vote or measured speed advantage. PostgreSQL adds a daemon, extension administration, patching, backups and resource costs. SQLite plus an in-process exact vector scan remains credible for a strict embedded/no-daemon device. Dedicated Qdrant remains credible if measured vector workload justifies coordination costs; its local/embedded modes must be evaluated separately from its server. No equal-quality performance comparison was possible without the approved real catalogue/device workload. Revisit after matching predicates/embeddings/scorer/recall and measuring full-turn latency, update/recovery cost and resources. Exact exhaustive vector scoring favors correctness at prototype scale; large-source capacity is not accepted yet.

Primary design references retained from the review: [pgvector exact/approximate search](https://github.com/pgvector/pgvector), [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [PostgreSQL text search](https://www.postgresql.org/docs/current/textsearch.html), [SQLite use cases](https://www.sqlite.org/whentouse.html), [SQLite transactions](https://www.sqlite.org/lang_transaction.html), [FTS5](https://www.sqlite.org/fts5.html), [Qdrant filtering](https://qdrant.tech/documentation/search/filtering/). These document mechanisms, not VoiceCart benchmark outcomes.

## Model alternatives and evaluation

Keep the exact Qwen3-4B-Instruct-2507 reference until held-out shopping extraction supports replacement. A smaller Qwen0.6B was smoke-tested, not promoted. Current MiniLM integration proves a real encoder/storage/query boundary, not superiority to the original BGE-small English reference. Version model/digest/dimensions/prefixes/serializer together; re-embed on any generation change. Candidate alternatives retained for later task-driven comparison include [BGE-small](https://huggingface.co/BAAI/bge-small-en-v1.5), [multilingual E5-small](https://huggingface.co/intfloat/multilingual-e5-small), [Qwen3 embedding](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [Moonshine](https://github.com/moonshine-ai/moonshine), [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), and a [MiniLM cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2). No replacement is justified by general leaderboard results alone.

[Qwen checkpoint](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs), [whisper.cpp](https://github.com/ggml-org/whisper.cpp), [continuing Piper](https://github.com/OHF-Voice/piper1-gpl), [Piper voice terms](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md), [LJ card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/medium/MODEL_CARD) remain the provenance/contract references. Hindi voices and multilingual ASR need their own exact license/language evaluation. [Keyboard access](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) and [status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) inform controls; they do not establish console conformance.

## Open decisions preserved from the review

| ID | Current decision / remaining gate |
|---|---|
| D01 | M1/16 GiB is an observed development host; approve supported device/OS and resource floor. |
| D02 | English prototype only; owner must specify Hindi/Hinglish/scripts before language acceptance. |
| D03 | Owner must supply authoritative full source, taxonomy, completeness and price/stock refresh SLA. |
| D04 | Local session cart implemented; external merchant cart would require a new authoritative integration. |
| D05 | Project license and distribution policy unresolved; Piper GPL and each voice/dependency need approval. |
| D06 | Original sub-1.5-second goal retained; define workload/percentile with owner and measure actual audible output. |
| D07 | Real scale/update/concurrency unknown; parser limits are not capacity guarantees. |
| D08 | Reference and challenger smoke evidence exists; held-out critical-slot/action quality and latency comparison pending. |
| D09 | Real MiniLM integration exists; BGE/E5/language relevance comparison and generation migration acceptance pending. |
| D10 | No neural reranker until adequate recall plus poor judged ordering and beneficial paired latency evidence. |
| D11 | Keyboard controls/text recovery implemented; representative blind/low-vision users and real audio devices still needed. |
| D12 | Default one-hour sessions/five-minute lists, periodic logical cleanup, no raw audio/transcript persistence; owner must approve retention/WAL/backup policy. |
| D13 | Pilot-derived relevance/task-completion floors and held-out sample sizes need owner/user error-cost judgments. |
| D14 | Separate cheapest role alongside overall relevance implemented; owner/user presentation/comprehension acceptance pending. |
| D15 | PostgreSQL reference selected for consistency; embedded/dedicated equal-recall resource comparison remains open. |
