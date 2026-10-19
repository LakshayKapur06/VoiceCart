# VoiceCart architecture review

Review date: **19 October 2026**. Repository: [LakshayKapur06/VoiceCart](https://github.com/LakshayKapur06/VoiceCart). Reviewed commit: **f41fca7283b10bc7f0bac1c09c335373afd45f37** (`README`).

The architecture baseline above is unchanged. This revision also audits the original report at commit **2862ea29ca2a69a625ed9fc14e356bea046ab5d4** and revises the storage recommendation from **74977fe3f9164d010b6718b059787de37b1aa90e**; repository observations below describe the baseline snapshot, before Suggestions.md was added.

**Status: recommendations for owner review, before implementation.** This document is the sole deliverable. None of the proposed architecture, experiments, model configurations, or roadmap steps has been implemented or benchmarked during this review.

## 1. Executive summary

**Retain the local, modular Python architecture, but change how retrieval, audio turns, and authoritative state are specified before coding starts.** At the architecture baseline, the repository contained only its README. It provides sound responsibility boundaries, but it does not yet establish a complete executable design.

The most consequential findings are:

1. **Sorting vector candidates cannot guarantee the cheapest matching product in the catalogue.** README §6.3 retrieves candidates and then sorts them. A qualifying cheaper variant can fall outside the retrieved top K. For a fully structured request, compute the answer across the complete eligible catalogue using SQL. For a subjective request, state the narrower search scope and clarify before making an unsupported global claim. This is a logical correctness finding, independent of the embedding model.
2. **Use PostgreSQL + pgvector as the reference data store.** Put catalogue facts, built-in full-text search, derived embeddings and minimal session cart/operation receipts in one local PostgreSQL database. This replaces the README’s Qdrant choice and supersedes this report’s earlier SQLite + Qdrant proposal. The decisive benefit is a single transaction/snapshot and recovery boundary, without a cross-store publication protocol. The earlier proposal already included a Qdrant server, so PostgreSQL does not add a database daemon relative to that topology. This is an architecture recommendation, not a measured speed or relevance improvement. See §4.4 and [pgvector](https://github.com/pgvector/pgvector), [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html).
3. **Use three retrieval routes and an explicit relevance policy:** exact identifier/reference resolution; complete structured filtering; and discovery combining lexical, dense and qualifying low-price candidates. Rank normal search results by query match, supported preferences and price; reserve price-first ordering for an explicit cheapest objective or an accepted placement policy. A cheaper irrelevant product must not displace a relevant match. The cheapest qualifying option and top overall match are different output roles. Candidate generation alone cannot guarantee the human-best result for every query. See [PostgreSQL text search](https://www.postgresql.org/docs/current/textsearch.html) and the candidate/ranking contract in §9.6.
4. **Pin the actual non-thinking language checkpoint and constrain its output.** Start with Qwen3-4B-Instruct-2507 through Ollama as the reference configuration; the README's shorter model name is insufficient to reproduce it. Use JSON-schema-constrained extraction plus independent semantic validation. Test current Qwen3.5-2B/4B and Gemma 4 E2B instruction variants as challengers before promoting a replacement. Newness and general benchmark scores do not establish shopping extraction quality. See the [Qwen checkpoint card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) and [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).
5. **Make audio turn handling and operation identity first-class responsibilities.** Endpoint detection, partial versus final transcripts, stopping playback, cancellation before mutation, and distinguishing a retry from a new add request are missing operational decisions. Introduce these inside the Python application, without a distributed workflow engine.
6. **Keep Piper provisionally, with a precise runtime and voice decision.** The original Piper repository is archived; the continuing OHF project uses GPL-3.0. Voice terms vary. In particular, the inspected Hindi Pratham card points to a noncommercial dataset licence. An English test voice and a Hindi release voice are separate decisions. See [original Piper](https://github.com/rhasspy/piper), [OHF Piper](https://github.com/OHF-Voice/piper1-gpl), and [Pratham's model card](https://huggingface.co/rhasspy/piper-voices/blob/main/hi/hi_IN/pratham/medium/MODEL_CARD).

**The under-1.5-second target is an unverified engineering goal.** It may be achievable for warm, bounded requests on suitable hardware, especially when ASR does work while the user speaks and responses use templates. There is no evidence here to promise it for the full sequential baseline, CPU-only devices generally, cold starts, long requests, or concurrent sessions. Endpoint delay, the complete extraction output, and audible playback all count. Keep the target, measure it early, and request an explicit owner decision if the supported hardware cannot meet it. Do not hide slow substantive answers behind an acknowledgement sound.

Highest-confidence changes concern retrieval correctness, explicit data ownership, constrained interfaces, turn identity, and truthful feedback. Hardware-specific model replacements, multilingual quality, and reranking benefits remain hypotheses. The immediate next step after approval is to establish the hardware/language profile and run an instrumented voice slice alongside a deterministic catalogue/cart slice.

## 2. Repository and baseline assessment

### 2.1 Observed repository state

Inspection used the complete README, `git ls-tree -r --name-only HEAD`, `git ls-files`, the working directory listing, and Git status/history. The worktree was clean before this review.

~~~text
VoiceCart/
├── .git/       Git metadata
└── README.md   Only tracked project file before this review
~~~

| Area | Observation at the reviewed commit | Consequence |
|---|---|---|
| Implementation | No application source, prototype, API, executable entry point, or UI | There is no implemented application flow to trace. |
| Dependencies/configuration | No package manifest, lockfile, model manifest, runtime settings, containers, or environment example | No runtime or model version is established by code. |
| Data | No catalogue, ingestion code, sample records, taxonomy, prices, inventory, or external commerce endpoint | Data quality and selection completeness cannot be measured. |
| Tests/evaluation | No tests, recordings, evaluation set, benchmark scripts, or results | All VoiceCart performance and accuracy results remain unmeasured. |
| Storage/interfaces | No database schema, Qdrant collection, cart implementation, or session protocol | All interfaces below are proposals. |
| Documentation/licensing | README only; no tracked AGENTS.md or project LICENSE | README contains the project instructions; the project's distribution licence remains undecided. |
| Alignment | README explicitly says pre-implementation | No contradiction with the files inspected. |

The README SHA-256 at inspection was `71909411f073696cca98619fd4af0ea0fabe5c7b42107bfca7f4ff9a9c029bf1`. Its numbered sections are the baseline references throughout this report. External pages describe upstream capabilities, not working VoiceCart integrations.

### 2.2 Selected target, as documented

| Component | README baseline | Assessment disposition |
|---|---|---|
| ASR | whisper.cpp; model unspecified | Retain runtime initially; select checkpoint by language/hardware tests. |
| NLU/optional response generation | Qwen3 4B Instruct through Ollama | Retain reference family/runtime; pin checkpoint and extraction contract. |
| Embeddings | BAAI/bge-small-en-v1.5 | Retain for the provisional English reference; multilingual decision stays open. |
| Semantic retrieval | Local Qdrant with payload filtering | Replace with pgvector in the authoritative PostgreSQL database; retain Qdrant as a benchmark challenger. |
| Business logic | Python, schema validation, deterministic constraints, controlled actions | Retain; specify interfaces and state transitions. |
| TTS | Piper direction; exact runtime/voice/licence open | Resolve upstream identity and voice eligibility; benchmark alternatives. |
| Catalogue/cart | Authoritative structured data outside LLM; technology open | Choose PostgreSQL for catalogue and minimal session-lifetime cart/receipts. |
| Responses | Templates for simple confirmations; grounded LLM assistance only when useful | Retain. An unconditional second LLM call is already excluded. |

The baseline conceptual sequence is audio → transcription → extraction → validation → embeddings/Qdrant → deterministic filtering or optional comparison → controlled add → verified response → TTS. It exists in documentation only.

### 2.3 Assumptions and unresolved requirements

For a concrete reference design, assume **one host, one interactive user initially, a locally managed catalogue, INR price examples, and English as the first evaluation profile**. These assumptions are provisional, not owner-approved requirements. Neither this chat's language nor the README's currency examples establish that Hindi/Hinglish is mandatory or that English-only is acceptable for release.

Before a supported release, identify hardware/OS, input and output languages, catalogue size and update source, concurrency, and whether the cart is a local demonstration or must call an existing commerce system. A local cart proves only a local cart operation. It cannot claim to modify a merchant's cart without an authoritative merchant integration.

The design gaps are: global selection semantics; money/budget operators; variant completeness; catalogue/index consistency; exact model identity; bounded extraction; audio endpointing and cancellation; result-list reference lifetime; minimal duplicate handling; TTS failure accessibility; and a reproducible device-specific performance gate. README already requires validation, safe actions, session isolation, and templates. Those principles are retained rather than counted as newly invented changes.

**Additional owner requirement for this revision:** relevance must reflect the user's query and preferences, with price as a ranking factor rather than the sole objective. The owner also stated that retrieving the cheapest product is required for every query. The proposed contract therefore separates price-aware ranked matches from a cheapest-qualifying-option role; placement of that option is the clarification recorded in D14. This applies to product search, not permission to replace an explicitly named product or an ordinal add request. Relevant means satisfying hard requirements plus supported semantic/preference fit; a low price cannot excuse an irrelevant substitute.

**Storage decision requested by the owner:** independently compare SQLite + Qdrant with PostgreSQL + pgvector. Consolidation is evaluated against correctness, operations, retrieval and device cost; it is not assumed to win merely because it was suggested. The decision is PostgreSQL + pgvector for this reference, with the conditions for choosing an alternative in §4.4 and validation in E11.

## 3. Research log and evidence rules

**All sources below were accessed on 2026-10-19.** “Rolling” means the inspected documentation did not establish a fixed publication date. A checkpoint name is a version identifier, not independently verified release history. Links point to primary documentation, repositories, model cards, or author papers. Upstream main branches and tags can change; implementation must record immutable revisions and checksums.

Evidence labels used in this report:

- **Observation:** directly inspected repository fact.
- **Source fact:** an upstream documented capability, specification, or licence declaration.
- **Source benchmark:** results reported by the source under its own conditions.
- **Inference/proposal:** engineering reasoning or a design recommended here.
- **Hypothesis:** an expected effect requiring VoiceCart experiments.

No VoiceCart inference, accessibility study, load test, or model benchmark was run. Documentation inspection is not a runtime compatibility test. The log records decision-relevant findings rather than every search result.

### 3.1 Speech and language understanding

| ID / research question | Source and direct URL | Source type | Publication/version; access | Key finding | Relevance | Limitation | Decision impact |
|---|---|---|---|---|---|---|---|
| R01: Is whisper.cpp a credible local default? | [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | Official runtime docs | Rolling; 2026-10-19 | CPU, Metal and other acceleration paths, quantization, VAD, and a streaming example are documented. | Broad local platform fit. | Example streaming is not a guarantee of stable final transcripts or a voice latency SLA. | Retain; test model, backend and endpoint policy. |
| R02: Does faster-whisper prove a universal speed advantage? | [faster-whisper benchmarks and usage](https://github.com/SYSTRAN/faster-whisper) | Maintainer benchmark/docs | Benchmark names v1.1.0 and whisper.cpp v1.7.2; 2026-10-19 | Results depend on device, precision, beam and batching; unbatched and batched results differ substantially. | Strong CUDA/Python alternative. | Long audio throughput and old runtime versions do not predict this turn pipeline. | Benchmark on target; no automatic runtime replacement. |
| R03: Is a streaming-native ASR alternative credible? | [Moonshine Voice](https://github.com/moonshine-ai/moonshine), [v2 paper](https://arxiv.org/abs/2602.12241), [licence](https://github.com/moonshine-ai/moonshine/blob/main/LICENSE) | Official project, author paper, licence | Paper 2026-02-12; rolling repo; 2026-10-19 | Streaming encoder aims to bound incremental work. Current licence distinguishes streaming/English models from enumerated legacy non-English exceptions. | Useful challenger for short spoken commands. | Exact language, checkpoint and device support must be verified; toolkit marketing is not a VoiceCart measurement. | Test for an approved matching language profile. |
| R04: Is there a current Hindi-capable ASR challenger? | [Qwen3-ASR-0.6B](https://huggingface.co/Qwen/Qwen3-ASR-0.6B) | Official model card | Paper identifier 2601.21337; 2026-10-19 | Card lists Hindi, streaming/offline support, Apache-2.0 and local backends. | Relevant multilingual alternative. | Language coverage does not prove Hinglish recognition; throughput at high concurrency is not turn latency. | Include in multilingual ASR experiment. |
| R05: Can Parakeet replace Whisper for all users? | [Parakeet-TDT-0.6B-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3), [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | Official model/runtime docs | v3; rolling; 2026-10-19 | Parakeet v3 lists 25 European languages and CC-BY-4.0. Sherpa offers local speech runtime integrations. | Possible English/device-specific option. | Hindi is absent from the v3 list; conversion/backend parity needs verification. | Conditional experiment, unsuitable as an assumed Hindi replacement. |
| R06: How should speech boundaries be detected? | [Silero VAD](https://github.com/snakers4/silero-vad) | Official model/runtime docs | Rolling; 2026-10-19 | Local ONNX/JIT VAD supports 8/16 kHz; MIT declared. | Lightweight endpoint signal. | VAD detects speech, not whether a shopping request is semantically complete. | Add an endpoint policy plus explicit end-turn control. |
| R07: Which Qwen 4B is meant? | [Qwen3-4B-Instruct-2507 card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), [Ollama exact tag](https://ollama.com/library/qwen3:4b-instruct-2507-q4_K_M) | Official model card/registry | 2507 checkpoint; 2026-10-19 | This checkpoint is non-thinking; the registry exposes a specific Q4_K_M artifact. | Reproducible reference for bounded extraction. | Card evaluations do not measure VoiceCart slots or quantized correctness. | Pin checkpoint/artifact; measure semantics. |
| R08: Should a newer small Qwen replace it? | [Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B), [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B), [Ollama Qwen3.5](https://ollama.com/library/qwen3.5) | Official cards/registry | 3.5 family; 2026-10-19 | Current small multimodal checkpoints and local artifacts exist; thinking defaults require attention. | Credible same/smaller-size challengers. | Text-only extraction, disabling thinking, quantization and runtime interaction need testing. | Test 2B first, then 4B; no unsourced promotion. |
| R09: Is another current model family worth testing? | [Gemma 4 E2B instruction card](https://huggingface.co/google/gemma-4-E2B-it) | Official model card | Gemma 4; 2026-10-19 | Apache-2.0, configurable thinking and multimodal inputs; E2B has more total parameters than its effective size suggests. | Alternative extraction model and possible future audio-input experiment. | Effective parameter count is not memory usage; multimodal features are unnecessary for the reference text boundary. | Secondary challenger; preserve independent action validation. |
| R10: Could a much smaller specialist help? | [LFM2.5-1.2B-Instruct](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct) | Official model card | 2.5 family; 2026-10-19 | Edge model positioned for extraction/RAG; card declares lfm1.0 and a language list without Hindi. | Potential low-resource English option. | Vendor speed claims use different devices; custom terms and target-language quality remain unresolved. | Optional English-only experiment, below multilingual Qwen priority. |
| R11: Were newer larger releases considered? | [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) | Official model cards | 3.8 / 3.6 checkpoints; 2026-10-19 | Newer larger dense/MoE alternatives are available. | Prevents treating 2025 baseline as the only current option. | Active MoE parameters do not describe total weight storage; no target hardware or task evidence supports this escalation. | Defer unless small candidates fail quality gates on adequate hardware. |

### 3.2 Runtime, retrieval, and data

| ID / research question | Source and direct URL | Source type | Publication/version; access | Key finding | Relevance | Limitation | Decision impact |
|---|---|---|---|---|---|---|---|
| R12: Can output structure be enforced locally? | [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs) | Official docs | Rolling; 2026-10-19 | A JSON schema can be passed through the format field and validated in Python. | Stronger contract than free text followed by parsing. | Schema compliance does not establish truth, permission or correct extracted values. | Use constrained extraction plus semantic checks. |
| R13: What causes serving delays? | [Ollama FAQ](https://docs.ollama.com/faq) | Official docs | Rolling; 2026-10-19 | keep_alive/preloading, queueing, concurrency and context-dependent memory behaviour are documented. | Model residency and backpressure affect voice latency. | Defaults/platform behaviour can change; memory must be measured for the installed version. | Warm deliberately and bound requests. |
| R14: Is direct llama.cpp preferable? | [llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server), [grammars/schema docs](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md) | Official runtime docs | Rolling; 2026-10-19 | Local server and grammar/schema mechanisms permit direct serving control. | Alternative when packaging or profiling exposes a need. | Schema subset/template compatibility must be tested; changing servers alone cannot improve model knowledge. | Keep behind an adapter; benchmark only if serving is the bottleneck. |
| R15: Are MLX/vLLM justified initially? | [MLX-LM](https://github.com/ml-explore/mlx-lm), [vLLM structured outputs](https://github.com/vllm-project/vllm/blob/main/docs/features/structured_outputs.md) | Official runtime docs | Rolling; 2026-10-19 | Apple-specific local inference and GPU-oriented serving with structured output are credible alternatives. | Hardware-specific deployment choices. | They add conversion/compatibility work and do not establish single-turn gains here. | Defer replacement of Ollama; use paired runtime tests if needed. |
| R16: Is BGE-small configured precisely enough? | [BGE-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) | Official model card | v1.5; 2026-10-19 | English model: 384 dimensions, 512-token input; query instruction and normalized embedding examples documented; MIT declared. | Cheap reference encoder with a clear contract. | Generic retrieval scores and similarity thresholds do not transfer automatically. | Retain English reference; fix preprocessing and calibrate rejection. |
| R17: Is a small multilingual alternative available? | [multilingual-e5-small card](https://huggingface.co/intfloat/multilingual-e5-small/raw/main/README.md) | Official model card | Report 2024; 2026-10-19 | 384-dimensional, 512-token encoder; query:/passage: prefixes and multilingual limitations are explicit. | First compact multilingual challenger. | Same dimensionality does not make vector spaces compatible; Hinglish is unverified. | Compare if language profile requires it; fully re-embed on change. |
| R18: Would BGE-M3 simplify multilingual hybrid retrieval? | [BGE-M3](https://huggingface.co/BAAI/bge-m3) | Official model card | Paper 2024; 2026-10-19 | Dense/sparse/multivector capabilities; 1024 dense dimensions and long multilingual input support. | Potential larger multilingual retrieval stack. | More features do not establish better latency or catalogue relevance. | Defer beyond E5 comparison unless relevance failures justify it. |
| R19: Are newer generative encoders relevant? | [Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) | Official model card | Paper 2506.05176; 2026-10-19 | Multilingual instruction-aware encoder; output dimensions up to 1024. | Another credible quality challenger. | Longer context and larger encoder may consume the latency/memory budget. | Test after compact alternatives, not by leaderboard alone. |
| R20: Which embedding runtime is appropriate? | [FastEmbed](https://github.com/qdrant/fastembed) | Official library docs | Rolling; 2026-10-19 | ONNX Runtime-based local inference and custom model registration are documented. | Avoid a separate embedding service for BGE-small. | Export, pooling, normalization and tokenizer parity still need verification. | Recommend local FastEmbed adapter for reference encoder. |
| R21: Can Qdrant filter candidates? | [Filtering](https://qdrant.tech/documentation/search/filtering/), [indexing](https://qdrant.tech/documentation/manage-data/indexing/) | Official database docs | Rolling; 2026-10-19 | Payload conditions and indexes support structured restrictions during retrieval. | A credible dedicated vector challenger. | Payload freshness and candidate coverage still require a separate authority protocol. | Retain as an E11 comparator; no measured requirement justifies two stores yet. |
| R22: How should lexical/dense rankings combine? | [Qdrant hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/) | Official retrieval docs | Rolling; 2026-10-19 | Rank fusion and staged queries are supported. | Distinguishes candidate fusion from business scoring. | The mechanism is not evidence that VoiceCart must use Qdrant or that RRF includes price. | Fuse PostgreSQL lexical/dense lists in Python; measure ranking independently. |
| R23: What local authoritative store fits? | [SQLite uses](https://www.sqlite.org/whentouse.html), [transactions](https://www.sqlite.org/lang_transaction.html) | Official database docs | Rolling; 2026-10-19 | Embedded transactional storage; concurrent writes have limits. | Strong fit when avoiding a database daemon is a requirement. | Pairing it with a Qdrant server loses a fully embedded deployment and introduces cross-store coordination. | Conditional SQLite + in-process-vector alternative; not the reference pair. |
| R24: Is a lexical engine needed as another service? | [SQLite FTS5](https://www.sqlite.org/fts5.html) | Official extension docs | Rolling; 2026-10-19 | Embedded full-text matching and BM25 ranking; lower bm25 values rank better. | Useful lexical baseline and embedded alternative. | PostgreSQL’s built-in ranking is a different mechanism, so quality cannot be assumed equivalent. | Compare FTS5 in E11; use PostgreSQL text search in the reference. |
| R25: Could storage be consolidated? | [pgvector](https://github.com/pgvector/pgvector) | Official extension docs | Rolling; 2026-10-19 | PostgreSQL extension supports exact and approximate vector search alongside relational data. | Allows one data authority, SQL interface and transaction boundary. | Still needs a server, extension setup and workload tuning; no automatic relevance/latency win. | Select PostgreSQL + pgvector; justify against the whole SQLite + Qdrant pair, not SQLite alone. |
| R26: Does a reranker have credible evidence? | [MS MARCO MiniLM-L6-v2 cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) | Official model card/benchmark | v2; 2026-10-19 | Scores query-document pairs and reports passage-ranking evaluation. | Candidate for subjective relevance reranking. | Passage benchmarks and throughput are not VoiceCart product results. | Evaluate only after candidate recall is adequate. |

### 3.3 Speech output, accessibility, evaluation, and licences

| ID / research question | Source and direct URL | Source type | Publication/version; access | Key finding | Relevance | Limitation | Decision impact |
|---|---|---|---|---|---|---|---|
| R27: Which Piper upstream/licence applies? | [Archived rhasspy Piper](https://github.com/rhasspy/piper), [OHF Piper](https://github.com/OHF-Voice/piper1-gpl), [Python API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md) | Official repositories/API docs | Archive dated 2025-10-06; rolling continuation; 2026-10-19 | Old MIT project redirects to GPL-3.0 continuation; Python API supports synthesis chunks. | Resolve package identity and first-audio integration. | A runtime licence does not settle voice/data terms; docs do not give device latency. | Retain direction provisionally; pin and test continuing runtime. |
| R28: Which voices can be used? | [Voice guidance](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md), [LJ Speech medium card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/medium/MODEL_CARD), [Hindi Pratham card](https://huggingface.co/rhasspy/piper-voices/blob/main/hi/hi_IN/pratham/medium/MODEL_CARD) | Official voice cards/docs | Rolling; 2026-10-19 | Individual cards matter: LJ dataset declared public domain; Pratham dataset link declares CC-BY-NC-SA-4.0. | Distribution and language choices are consequential. | Dataset declarations are not a complete bundled-dependency audit or intelligibility study. | English test candidate; Hindi release voice remains unresolved. |
| R29: Is Kokoro a practical challenger? | [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), [voices/limitations](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) | Official model card/docs | v1.0 dated 2025-01-27; 2026-10-19 | Apache-2.0 weights; Hindi voices listed; docs warn of short-utterance/non-English weaknesses. | Compact local TTS alternative. | Weights licence alone does not clear phonemizer dependencies; subjective quality needs users. | A/B test short confirmations and rupee amounts. |
| R30: Should a newer generative TTS be adopted? | [Qwen3-TTS 0.6B CustomVoice](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice) | Official model card | Paper 2601.15621; 2026-10-19 | Streaming-oriented Apache-2.0 model; listed ten languages exclude Hindi. | Potential quality-oriented local alternative. | Published low-latency claim is not a shared-device VoiceCart result. | Defer; no Hindi assumption or voice cloning requirement. |
| R31: Is spoken output alone enough for accessibility? | [W3C status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html), [keyboard access](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) | Official standards guidance | WCAG 2.2 understanding docs; 2026-10-19 | Expose status changes to assistive technology and provide keyboard operation. | Supports failure fallback and nonvisual turn controls. | Guidance is not evidence of whole-application conformance or usability. | Add accessible status/control surface and user tests. |
| R32: Which Python mechanisms support boundaries? | [Pydantic strict mode](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/), [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html) | Official library/language docs | Rolling; 2026-10-19 | Strict validation, cancellation and timeouts are available. | Supports explicit schemas and bounded orchestration. | Cancelling a task does not roll back a completed external mutation or necessarily stop native inference. | Use typed contracts and explicit operation states. |
| R33: How should product relevance be labelled? | [Amazon Shopping Queries / ESCI](https://github.com/amazon-science/esci-data) | Author dataset, evaluation code and paper reference | 2022; 2026-10-19 | Exact, Substitute, Complement, Irrelevant labels separate product relationships. | Useful pattern for product-specific judgments. | Public data lacks this project's audio, fresh stock and complete INR catalogue truth. | Use for supplemental evaluation; build local ground truth. |
| R34: Are core runtime licences recorded? | [Ollama licence](https://github.com/ollama/ollama/blob/main/LICENSE), [Qdrant licence](https://github.com/qdrant/qdrant/blob/master/LICENSE) | Official licence texts | Rolling; 2026-10-19 | MIT and Apache-2.0 respectively. | Supports a recorded dependency/model inventory. | Model, voice, data and transitive terms remain separate. | Pin versions and preserve notices before distribution. |
| R35: What about weights, host language and embedded libraries? | [Whisper](https://github.com/openai/whisper), [Python licence](https://docs.python.org/3/license.html), [SQLite copyright](https://www.sqlite.org/copyright.html), [FastEmbed licence](https://github.com/qdrant/fastembed/blob/main/LICENSE), [ONNX Runtime licence](https://github.com/microsoft/onnxruntime/blob/main/LICENSE) | Official repository/licence texts | Rolling; 2026-10-19 | Whisper code/weights declare MIT; Python PSF-2.0 with incorporated-software terms; SQLite public domain; FastEmbed Apache-2.0; ONNX Runtime MIT. | Covers reference execution libraries and embedded alternatives. | Downloaded builds, conversions, models and dependencies must match the inspected declarations. | Record shipped artifacts separately from top-level package names. |
| R36: Does an acknowledged index update establish freshness? | [Qdrant point updates](https://qdrant.tech/documentation/manage-data/points/), [upsert API](https://api.qdrant.tech/api-reference/points/upsert-points) | Official database/API docs | Rolling; 2026-10-19 | Receipt acknowledgement differs from completed application; explicit wait requests completion. | Explains a real coordination cost of the split-store alternative. | Completion is not an atomic transaction with SQLite or a relevance guarantee. | If E11 favours Qdrant later, require completed updates plus a tested cross-store publication protocol. |
| R37: Are SQLite checks/transactions safe by default? | [Transactions](https://www.sqlite.org/lang_transaction.html), [foreign-key settings](https://www.sqlite.org/pragma.html#pragma_foreign_keys), [FTS syntax](https://www.sqlite.org/fts5.html#full_text_query_syntax) | Official database docs | Rolling; 2026-10-19 | Single-writer contention, connection settings, commit errors and MATCH grammar need handling. | Defines the embedded alternative’s correctness obligations. | These SQLite rules must not be copied into PostgreSQL transaction/query code. | Keep as comparator evidence; reference contracts use PostgreSQL snapshots, locks and plain-text query construction. |
| R38: Does hybrid fusion alone rank by value and user fit? | [Qdrant custom scoring](https://qdrant.tech/documentation/search/hybrid-queries/#custom-scoring-with-a-formula-query), [Shopping Queries paper](https://arxiv.org/abs/2206.06588) | Official retrieval docs and author paper | Rolling docs; paper 2022; 2026-10-19 | Hybrid retrieval and final business scoring are separate stages; product relevance labels distinguish actual matches from related items. | Supports query relevance plus bounded price/preference scoring after retrieval. | Neither source supplies optimal VoiceCart weights or guarantees the human-best result for arbitrary queries. | Add ARCH-009, measure price-aware candidate recall and final relevance, and keep ranking claims scoped. |

### 3.4 Storage consolidation evidence

| ID / research question | Source and direct URL | Source type | Publication/version; access | Key finding | Relevance | Limitation | Decision impact |
|---|---|---|---|---|---|---|---|
| R39: Can PostgreSQL provide lexical retrieval? | [Text search controls](https://www.postgresql.org/docs/current/textsearch-controls.html), [tables/indexes](https://www.postgresql.org/docs/current/textsearch-tables.html) | Official PostgreSQL docs | Rolling; 2026-10-19 | tsvector/GIN, plain-text query conversion and built-in term/cover-density ranking are available. | Retains a lexical path in the consolidated database. | Tokenization/language and ranking differ from FTS5 BM25; exact identifiers need equality. | Use explicit configurations and plainto_tsquery; evaluate E04/E11. |
| R40: Is one database automatically one search snapshot? | [Isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [locking](https://www.postgresql.org/docs/current/explicit-locking.html) | Official PostgreSQL docs | Rolling; 2026-10-19 | Read Committed may change snapshots between statements; Repeatable Read holds a snapshot and can require retries. | Makes atomic publication and consistent multi-branch retrieval possible. | The application must choose isolation, lock relevant rows and bound whole-transaction retries; a shared server alone is insufficient. | Specify short retrieval snapshots and guarded action transactions in §9.4/9.7. |
| R41: Can filtered pgvector ANN omit matches? | [Filtering and iterative scans](https://github.com/pgvector/pgvector#filtering) | Official extension docs | Rolling; 2026-10-19 | Approximate-index filtering can underfill results; iterative scans search farther within limits. | Prevents equating a WHERE predicate with exhaustive ANN coverage. | Ordered approximate results still need recall validation and do not prove a price minimum. | Begin with exact vector search; gate ANN on E11 selectivity/recall/latency tests. |
| R42: Does consolidation remove backup operations? | [PostgreSQL dump/restore](https://www.postgresql.org/docs/current/backup-dump.html) | Official PostgreSQL docs | Rolling; 2026-10-19 | Database dump/restore supports a consistent database backup. | One database avoids reconciling separately captured catalogue/vector snapshots. | Server/extension provisioning, model files, credentials and restore testing remain separate operational work. | Test clean-host restore with pinned PostgreSQL/pgvector and model manifests in E09/E11. |
| R43: What are the proposed store’s licence terms? | [PostgreSQL licence](https://www.postgresql.org/about/licence/), [pgvector licence](https://github.com/pgvector/pgvector/blob/master/LICENSE) | Official licence texts | Rolling; 2026-10-19 | Both inspected texts use the PostgreSQL licence. | Updates the reference dependency inventory. | Client driver, packaged builds and transitive dependencies require their own records. | Replace reference SQLite/Qdrant entries; preserve notices for exact shipped artifacts. |
| R44: Which invariants can the relational store enforce? | [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) | Official PostgreSQL docs | Rolling; 2026-10-19 | NOT NULL, CHECK, UNIQUE and foreign keys express row/reference invariants. | Supports operation uniqueness and cart/catalogue relations in one database. | Cross-row business rules still need transaction logic and tests. | Define schema invariants plus E01/E06 concurrency/fault tests. |
| R45: Must Qdrant run as a server? | [Python client local mode](https://github.com/qdrant/qdrant-client#local-mode), [Qdrant Edge](https://qdrant.tech/documentation/edge/) | Official client/engine docs | Rolling; 2026-10-19 | Client local mode can persist without a server; Edge is an embedded engine currently labelled beta. | Provides real no-daemon alternatives; “Qdrant always needs a server” would be incorrect. | Embedding it beside SQLite still leaves two publication/transaction boundaries; Edge packaging/API stability needs evaluation. | Compare embedded options if device constraints require them; server-count reasoning applies to the previous report’s topology only. |

### 3.5 Interpretation limits

One useful **source benchmark**, rather than a VoiceCart result, is faster-whisper's comparison of 13 minutes of audio on an RTX 3070 Ti 8 GB with CUDA 12.4: FP16, beam 5, unbatched faster-whisper took 63 seconds versus whisper.cpp with Flash Attention at 65 seconds; faster-whisper batch size 8 took 17 seconds with more VRAM. These historical conditions demonstrate why a throughput headline is insufficient to choose a voice runtime. They do not predict current versions, endpoint latency, or this project's accents. [Benchmark source](https://github.com/SYSTRAN/faster-whisper).

No inspected benchmark compares the entire proposed stack on the intended VoiceCart machine. Publisher model results are not independent replications. This review uses specifications to identify feasible candidates and experiments, not to assign fabricated accuracy or speed rankings.

## 4. Architecture assessment and credible alternatives

### 4.1 Speech recognition and audio input

**Recommendation: retain whisper.cpp as the reference runtime, with an explicit audio/ASR adapter and a model selection gate. Confidence: medium for runtime retention; low for any unmeasured latency prediction.** The README selects a runtime, not a Whisper checkpoint. Begin comparisons with multilingual base/small; include English-only counterparts only if the approved profile is English-only. Larger/turbo candidates belong in an accelerated-hardware comparison if critical-word errors persist. These are experimental candidates, not selected release configurations.

The adapter must expose finalization and timestamps. Provisional transcripts may drive non-mutating previews, but only the finalized turn can authorize an add. Include speech detection, silence trimming, maximum utterance handling and an explicit end-turn control. A brief pause before “don't add it” must not prematurely commit a cart operation. No ASR confidence score is a calibrated probability of correct intent.

| Alternative | Potential improvement | Cost or limitation | Adoption test/disposition |
|---|---|---|---|
| faster-whisper/CTranslate2 | Python integration and CUDA/int8 options | Different GPU/build stack; throughput advantage may disappear at batch 1 | Compare same Whisper weights/decoding, critical-slot accuracy and end-of-turn tail. Retain whisper.cpp unless measured improvement matters. [Source](https://github.com/SYSTRAN/faster-whisper). |
| Moonshine streaming | Work during speech; reduced finalization work | Matching language/model support and new integration must be checked | Test English commands and pauses before adopting; do not infer Hindi support from English evidence. [Project](https://github.com/moonshine-ai/moonshine), [paper](https://arxiv.org/abs/2602.12241). |
| Qwen3-ASR-0.6B | Multilingual and streaming candidate | Additional backend/resource integration | First current alternative to test if Hindi/Hinglish is required. Compare amounts, brands, negation and code switching. [Card](https://huggingface.co/Qwen/Qwen3-ASR-0.6B). |
| Parakeet v3 / compatible local runtime | Alternative English/multilingual-European ASR | Documented language set does not cover Hindi | Test only matching users/device; verify checkpoint conversion and licence. [Card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3), [sherpa](https://github.com/k2-fsa/sherpa-onnx). |

A streaming recognizer does not remove endpoint detection or correction handling. Do not install diarization, forced alignment or a wake-word engine by default: the initial workflow needs a clear user-controlled listening turn, not continuous ambient conversation analysis.

### 4.2 Language model and serving runtime

**Recommendation: keep one Qwen3-4B-Instruct-2507 model through Ollama as the initial reference, configured for compact schema extraction. Confidence: medium.** The exact available reference artifact is `qwen3:4b-instruct-2507-q4_K_M`; the inspected registry reports a 2.5 GB artifact. That is a download size, not total resident RAM. Record its full digest at implementation, template and runtime version. The checkpoint-specific card identifies non-thinking behaviour; do not substitute a generic family tag. [Registry](https://ollama.com/library/qwen3:4b-instruct-2507-q4_K_M), [card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507).

Constrained decoding improves the output interface. It does not prevent swapping “under” for “at most,” dropping a negation, inventing a product ID or misreading two thousand as twenty thousand. Python must check supported operations, canonical attributes, numerical spans, unresolved values and session references. Never send the whole catalogue or unrestricted chat history to the extractor.

Run paired extraction tests against Qwen3.5-2B, then Qwen3.5-4B, with thinking disabled through the tested model/runtime mechanism. Promote the smallest model meeting semantic and end-to-end gates. Gemma 4 E2B-it is a credible secondary family; its effective parameter label must not be treated as a memory estimate. LFM2.5-1.2B-Instruct is an optional English low-resource candidate with custom licence terms. Larger Qwen3.8/3.6 candidates are deferred because the current problem has no evidence that large-model inference is needed. [Qwen 2B](https://huggingface.co/Qwen/Qwen3.5-2B), [Qwen 4B](https://huggingface.co/Qwen/Qwen3.5-4B), [Gemma](https://huggingface.co/google/gemma-4-E2B-it), [LFM](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct), [larger current model](https://huggingface.co/Qwen/Qwen3.8-27B).

Use exact, narrowly specified fast paths for session ordinals and simple pending-question replies. General shopping language still goes through NLU. A broad regex/keyword classifier can erase negation or misinterpret multi-clause requests; it is not a free correctness improvement. A separately trained intent model needs labelled data absent here, and keeping a second conversational model resident increases memory/operational cost. Defer both.

Ollama remains a reasonable development boundary. llama.cpp server is a credible deployment alternative if precise scheduling or packaging becomes a measured issue; MLX-LM is a device-specific alternative on Apple Silicon; vLLM is worth considering for a justified GPU/concurrency profile. Use the same checkpoint, prompt, precision, output schema and workload when comparing runtimes. Moving to an agent framework or a different server is not evidence of better extraction. [llama.cpp](https://github.com/ggml-org/llama.cpp/tree/master/tools/server), [MLX-LM](https://github.com/ml-explore/mlx-lm), [vLLM](https://github.com/vllm-project/vllm/blob/main/docs/features/structured_outputs.md).

### 4.3 Embeddings and language coverage

**Recommendation: retain BGE-small-en-v1.5 for the provisional English reference, using local FastEmbed/ONNX Runtime. Confidence: medium.** Pin tokenizer, pooling, normalization, query instruction policy and document serializer. Use one encoder contract for ingestion and requests. Do not select by vector dimension alone. [BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5), [FastEmbed](https://github.com/qdrant/fastembed).

If Hindi or Hinglish is in the required profile, test multilingual-e5-small first, followed by BGE-M3 and Qwen3-Embedding-0.6B if compact retrieval misses relevance gates. E5 retains a compact vector dimension but requires different preprocessing and a complete vector-space migration. Translation to English through the LLM is another possible experiment, but adds inference and can alter brand names, negation or amounts. It is not the default language bridge. [E5](https://huggingface.co/intfloat/multilingual-e5-small/raw/main/README.md), [BGE-M3](https://huggingface.co/BAAI/bge-m3), [Qwen encoder](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B).

Changing the embedding model, even to another 384-dimensional model, requires a new named vector generation and re-embedding. No mixed-vector space is valid merely because shapes match. Cross-language claims need cross-language query/product judgments; an English benchmark cannot settle them.

### 4.4 Retrieval, storage, and selection

**Decision: PostgreSQL + pgvector + built-in text search is the reference store. Replace Qdrant in the proposed design and withdraw the earlier SQLite + Qdrant recommendation. Confidence: high for removing cross-store correctness work, medium for device/performance fit until E11.**

This decision follows from the complete VoiceCart workload: relational eligibility/price selection, lexical and semantic discovery, and a verified cart increment. The earlier argument that PostgreSQL adds a server compared SQLite alone with PostgreSQL, although the proposed pair already included a Qdrant server. Both options need one database service; the pair additionally needs an embedded authority and a protocol to reconcile two persistence boundaries. There is no implemented code/data migration to protect and no measured Qdrant advantage to offset that coordination cost. This is an engineering inference from the architecture, not a database benchmark.

| Decision criterion | SQLite + Qdrant Server | PostgreSQL + pgvector | VoiceCart judgment |
|---|---|---|---|
| Catalogue, vector and cart changes | Relational transactions cannot atomically publish Qdrant changes; needs revision/readiness/recovery coordination. | Related rows and derived vectors can publish in one SQL transaction. | Favour consolidation for correctness and less application machinery. |
| Retrieval consistency | Payload/authority duplication needs a publication protocol; filtering stale results cannot recover omitted new matches. | Lexical, vector and structured branches can read one snapshot with the explicit isolation contract below. | Favour PostgreSQL; merely putting calls on one server is insufficient. |
| Local deployment | Qdrant daemon plus SQLite file and two storage adapters. | PostgreSQL daemon, pgvector installation and SQL adapter; still requires provisioning, maintenance and backups. | No extra database service versus the pair; operations are simpler in kind, not free. |
| Search quality and speed | Dedicated filtered-vector capabilities are a credible advantage to test. | Full-text and vector candidates are available, but lexical scoring and filtered ANN behaviour differ. | No winner claimed without equal-quality workload tests. |
| Constraints and concurrent adds | SQLite transactions work, with one writer; per-session app locks alone are insufficient. | Constraints and row locks can protect related cart/receipt updates; retry/deadlock handling remains necessary. | Fits the needed action boundary without a second state system. |
| Backup/recovery | Capture authority and reconcile/rebuild its external vector index. | One consistent database backup; restore must include compatible extension provisioning. | Fewer independently versioned data stores to recover. |

Qdrant itself does not always require a daemon: its Python client has a persistent local mode, and Qdrant Edge is an in-process engine currently labelled beta. SQLite beside either still has separate transaction/publication boundaries. These are credible embedded candidates if a no-daemon requirement emerges, not proof that PostgreSQL is always the simplest device deployment. [Client local mode](https://github.com/qdrant/qdrant-client#local-mode), [Edge](https://qdrant.tech/documentation/edge/).

Sources for capabilities, rather than measured comparative claims: [pgvector](https://github.com/pgvector/pgvector), [PostgreSQL snapshots](https://www.postgresql.org/docs/current/transaction-iso.html), [text search](https://www.postgresql.org/docs/current/textsearch.html), [backup](https://www.postgresql.org/docs/current/backup-dump.html), [SQLite deployment guidance](https://www.sqlite.org/whentouse.html), [Qdrant filtering/indexing](https://qdrant.tech/documentation/manage-data/indexing/).

**What this choice does not establish:** the same embeddings and ranking policy do not become more relevant merely by changing databases. PostgreSQL’s ts_rank/ts_rank_cd are not a drop-in BM25 replacement. Filtered approximate search can miss/underfill results; iterative scans reduce that risk within scan limits, not eliminate it. Start with exact vector search for the initial catalogue and introduce ANN only when measured need and recall gates justify it. Exact nearest neighbours are exact under a vector metric, not proof of human relevance. One database also does not make asynchronous embedding generation instantaneous: source fingerprints and atomic publication remain required. §§9.4–9.7 specify these contracts. [Text search ranking](https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-RANKING), [filtered ANN](https://github.com/pgvector/pgvector#filtering).

The counterexample to README §6.3 is unchanged by storage choice: ten highly similar black backpacks cost ₹1,200–₹1,900, while a poorly described qualifying variant costs ₹900. A semantic top ten can omit the ₹900 item. Sorting that shortlist does not establish a catalogue minimum. For a canonical category/colour/budget request, use authoritative structured filtering and `ORDER BY price_minor, variant_id`; strict `<` means “under,” while `<=` means “at most.” A global claim needs complete imported coverage and evaluable required fields for potentially matching records. Unknown price/colour/category/stock is unknown eligibility, not a nonmatch. Clarify or obtain agreement to a narrower verified-record scope if unknowns could affect the answer. The claim is relative to its recorded catalogue snapshot, not a promise that prices can never change afterward.

For discovery, union lexical, dense and qualified low-price candidates, deduplicate variant IDs, and apply the same hard predicates and relevance gate before the versioned §9.6 scorer. RRF alone has no price feature. Rank by query fit, supported preferences and bounded price utility, and identify a qualified cheapest role separately, with D14 placement still open. A cheap accessory cannot displace the requested product. Ratings, durability or suitability features require actual catalogue evidence. Even exact vector search does not guarantee recall for the final composite score; E10 compares candidate unions with exhaustive scoring and human judgments.

| Alternative / trigger | Decision |
|---|---|
| SQLite + in-process vectors | Prefer if a strict embedded/no-database-daemon requirement emerges and catalogue/device tests pass. Compare an app-owned exact scan with Qdrant client local mode or Edge where appropriate. They remove the daemon, but the search representation still needs persistence, revision/rebuild and consistency tests; assess Edge’s beta/packaging constraints. |
| SQLite + Qdrant | Keep as an E11 challenger, not the default. Reconsider only for a demonstrated retrieval/resource benefit large enough to justify the synchronization protocol. |
| PostgreSQL authority + Qdrant | Future option if measured vector/filter scale defeats pgvector at the required recall/latency. It reintroduces dual-store publication and recovery costs. |
| Qdrant-only authority | Reject for this reference: reducing store count alone does not establish the required relational action/receipt contract. |
| Extra sparse model, Elasticsearch, cross-encoder | Defer until labelled failures identify a need; they do not fix unknown catalogue facts or an incomplete eligible set. |

E11 compares storage alternatives on the same snapshot, encodings, predicates, ranking policy, hardware and recall target. It can overturn the performance fit of the reference recommendation. It is not a reason to leave the architecture decision unresolved now. A bounded [cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) remains a separate E04 experiment only when candidate recall is adequate but ordering is poor.

### 4.5 Python orchestration and action handling

**Recommendation: one modular Python application with an explicit finite state machine, typed adapters, bounded native workers and minimal session state. Confidence: high.** This specifies the simple dispatcher/state-machine direction already considered in README §9. No LangChain/LangGraph, distributed queue, Redis, Kafka, Kubernetes or autonomous tool loop is justified by the current workflow.

Use async orchestration for I/O and separate execution for blocking inference; placing blocking native work in an async function does not make it nonblocking. A per-session lock serializes state transitions. An application-generated operation ID, preserved across retries, prevents a repeated completion or timeout retry from adding twice within the session lifetime. An intentional new “add another” receives a new operation ID. This is a minimal requirement for a trustworthy add operation, not comprehensive cart management. [Python task semantics](https://docs.python.org/3/library/asyncio-task.html).

### 4.6 TTS, interaction, and privacy

**Recommendation: use the continuing OHF Piper runtime as the provisional TTS direction and test en_US-ljspeech-medium for the English reference. Confidence: medium; release voice unresolved.** The inspected LJ voice card names a public-domain dataset, but the whole distribution still needs an inventory of runtime, weights, phonemizer and notices. Packaging a process separately does not, by itself, settle licence obligations. Do not describe the new runtime as the old MIT Piper. [OHF](https://github.com/OHF-Voice/piper1-gpl), [LJ card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/medium/MODEL_CARD).

For Hindi, do not silently adopt Pratham for commercial use: its card points to CC-BY-NC-SA-4.0 dataset terms. Evaluate an eligible Hindi voice and Kokoro's listed Hindi candidates, including phonemizer terms and intelligibility. Kokoro's own docs identify weaknesses on very short speech, a critical workload here. Qwen3-TTS is a credible generative alternative but its inspected language list excludes Hindi, and a second substantial generative workload can compete with NLU. [Pratham](https://huggingface.co/rhasspy/piper-voices/blob/main/hi/hi_IN/pratham/medium/MODEL_CARD), [Kokoro voices](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md), [Qwen TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice).

Keep the TTS engine resident. Stream complete, verified response phrases through its chunk API. Normalize monetary amounts, abbreviations, quantities and SKUs deliberately. Never speak partial unvalidated extraction or an “added” prefix before mutation verification. Cache a few non-sensitive failure prompts. If neural TTS fails, try the cached spoken error and expose equivalent status text to an already available screen reader. If playback itself fails, a visual toast is insufficient; the application must surface an assistive-technology status and accessible retry control. Avoid simultaneous screen-reader and app speech unless requested. [Piper API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md), [W3C status guidance](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html).

Local inference reduces external disclosure only when models are pre-provisioned and requests stay local. Keep raw audio and transcripts in memory by default, discard them after the turn/session policy, bind model/database endpoints to loopback, and exclude personal content from routine traces. Test offline operation and actual network behaviour. Local execution alone does not prove privacy.

### 4.7 Complete-system alternatives

| Architecture combination | How it works / useful requirements | Benefits to test | Sacrifices/resources | Integration and migration | Decision and test |
|---|---|---|---|---|---|
| A. README sequential reference | Whisper → 4B extraction → BGE/Qdrant → validation/add → Piper | Establish a reproducible comparison | Sequential tail; top-K cheapest gap; unspecified state/endpointing | No existing code to preserve | Build only as a controlled benchmark variant; unsafe selection is never enabled for real adds. |
| B. Recommended modular hybrid | Local ASR + endpointing; one schema NLU; PostgreSQL structured/text search + BGE/pgvector and low-price candidates; price-aware ranking; deterministic add; resident Piper | Snapshot-consistent routes, atomic catalogue/vector publication and cart receipts, bounded inference and usable failures | Database/extension administration, exact-vector scaling, ranking calibration | New typed SQL adapters/schema; no existing implementation migration | Recommended reference; E01–E11 validate it. |
| C. Low-resource streaming local | Moonshine for a matching language; smaller NLU; SQLite plus exact dense scan; compact local TTS | Smaller footprint and shorter post-speech work | Language/accuracy trade-offs; dense-scan scaling; different adapters | Replace tested models/index implementation behind interfaces | Conditional if device profiling shows B too heavy and task-quality gates pass. |
| D. Multilingual accelerated local | Whisper or Qwen3-ASR; Qwen3.5 challenger; E5/M3; PostgreSQL hybrid; eligible multilingual TTS | Hindi/Hinglish/cross-language retrieval | More test data, resident memory, language-specific voices and licence checks | Re-embed catalogue, change model contracts, expand voice fixtures | Required comparison if multilingual is confirmed; current English reference cannot claim this support. |
| E. Shared local server | Approved ASR clients; GPU model server; PostgreSQL+pgvector/text search; controlled cart backend | Shared catalogue, concurrency, existing commerce integration | Network boundary/authentication, queueing, service operations | New client/network and merchant integration; reference database can remain | Defer shared deployment until it is required; test capacity at batch 1 as well as concurrent load. |
| F. Native audio-to-intent model | Audio-capable local model emits a typed interpretation; separate retrieval/action/TTS remains | Possibly remove a distinct ASR step | Harder transcript/provenance debugging, new grammar/runtime path, unmeasured critical-word errors | New adapter and audit/evaluation design | Exploratory only; no evidence supports replacing independent ASR now. |

All recommended paths preserve local inference, retrieval before product-grounded generation, application-owned state and the current search/add scope. Cloud inference is excluded by the current constraints, not treated as a fallback. No complete-system option has been measured here.

## 5. Change-only diff against the README target

These nine entries contain actual proposed additions or refinements to the target design, including the owner's added relevance/price requirement. Retaining Python, whisper.cpp, BGE-small for English, application validation and optional response generation is not counted as a change. “Migration” below concerns future artifacts: there is no implemented system to migrate now.

### Change ID: ARCH-001 — Route complete structured selection separately

- **Component or layer:** Retrieval coordinator and selection policy.
- **Current baseline:** README §§6.3, 7.3 and 8 retrieve semantic candidates and deterministically select the cheapest valid candidate; complete-catalogue optimality is unspecified.
- **Proposed change:** Introduce exact/reference, exhaustive structured, and semantic-discovery routes. Resolve a fully structured cheapest query only after a source/attribute completeness gate, using an authoritative SQL predicate and stable price ordering. Represent unknown eligibility explicitly. Return selection scope; clarify subjective/unmapped/incomplete eligibility instead of claiming a global minimum from top K or a partial import.
- **Reason for change:** ANN/dense relevance ranking can omit the cheapest eligible variant even if every returned candidate passes constraints.
- **Supporting research:** The counterexample in §4.4 is a logical proof of this gap. [Qdrant filtering](https://qdrant.tech/documentation/search/filtering/) supports restrictions, while [PostgreSQL SELECT/ordering](https://www.postgresql.org/docs/current/sql-select.html) supports structured filtering/ordering; neither source claims semantic top K proves a price minimum.
- **Expected benefits:** Correct global cheapest answers for expressible structured requests; less unnecessary embedding work on that route.
- **Trade-offs and risks:** Requires complete, normalized eligible-product data. Category mistakes or missing records still invalidate catalogue-wide claims.
- **Dependencies and migration implications:** ARCH-002 catalogue schema, typed query plan, tests comparing against a complete oracle. No existing index migration.
- **Validation required:** E01 adversarial top-K fixture, boundary prices, variant ties, missing attributes and full eligible-set comparison.
- **Priority:** High; directly affects a representative required action.
- **Confidence:** High for the gap and route separation; medium for taxonomy coverage until real data exists.

### Change ID: ARCH-002 — Consolidate authoritative and derived data in PostgreSQL

- **Component or layer:** Data model, ingestion, storage and minimal local action persistence.
- **Current baseline:** README §§5.1 and 12 leave authority/persistence open, §7 chooses Qdrant, and §7.4 requires freshness without a publication protocol.
- **Proposed change:** Choose one local PostgreSQL database with pgvector, built-in text search, catalogue/variant facts, source completeness and session cart/operation receipts. Replace Qdrant in the reference. Publish content and matching embeddings atomically under revision checks; use short consistent retrieval snapshots. Start with exact vectors; gate ANN on E11.
- **Reason for change:** The workflow needs relational eligibility and action transactions as well as vectors. One database removes the earlier proposal’s cross-store publication/recovery protocol without introducing an additional database daemon relative to SQLite + Qdrant.
- **Supporting research:** [pgvector](https://github.com/pgvector/pgvector), [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [text search indexes](https://www.postgresql.org/docs/current/textsearch-tables.html), [dump/restore](https://www.postgresql.org/docs/current/backup-dump.html). Preference for consolidation is an engineering inference, not measured superiority.
- **Expected benefits:** One authority/transaction/snapshot boundary, no duplicated Qdrant price/stock payload, atomic local action receipts and fewer recovery paths.
- **Trade-offs and risks:** PostgreSQL service/extension provisioning, maintenance, resource contention, filtered-ANN recall and different lexical ranking. Exact vectors may become too slow; asynchronous embedding work still needs content/version validation. No speed or relevance gain is promised.
- **Dependencies and migration implications:** Data-source/variant contracts and a pinned compatible PostgreSQL/pgvector build plus SQL client first. There is no existing implementation to migrate; encoder changes still require a separate named generation and re-embedding. Keep embedded SQLite + vectors conditional on device requirements.
- **Validation required:** E01 atomic publication and completeness; E06 concurrency/retry/receipt tests; E09 clean-host restore; E11 equivalent-recall storage/resource comparison.
- **Priority:** High; establishes the correctness and deployment boundary before implementation.
- **Confidence:** High for reducing cross-store coordination; medium for workload/device fit before measurement.

### Change ID: ARCH-003 — Add lexical candidates to semantic discovery

- **Component or layer:** Product discovery retrieval.
- **Current baseline:** README §7 uses BGE/Qdrant dense candidate generation; no lexical ranking path is selected.
- **Proposed change:** Add PostgreSQL title/brand/model/description text search using explicit configurations, tsvector/GIN and parameterized plainto_tsquery, plus separate exact identifier lookup. Fuse validated lexical and dense ranks in Python for discovery. Keep exhaustive structured selection separate; defer a neural reranker behind an experiment gate.
- **Reason for change:** Dense similarity is not sufficient evidence of exact SKU/model identity, and lexical-only matching can miss paraphrases. Combining these signals is a targeted addition without another search service.
- **Supporting research:** [PostgreSQL text search](https://www.postgresql.org/docs/current/textsearch-controls.html), [rank fusion](https://qdrant.tech/documentation/search/hybrid-queries/) and the product relevance categories in [ESCI](https://github.com/amazon-science/esci-data).
- **Expected benefits:** Hypothesis: better discovery coverage for exact names and descriptive queries with a modest extra retrieval cost.
- **Trade-offs and risks:** More candidate/rank logic; tokenizer and fusion settings can hurt some queries; built-in PostgreSQL ranking is not BM25, and similarity is still not identity.
- **Dependencies and migration implications:** ARCH-002 owns FTS updates and canonical IDs. Tune candidate counts and fusion on development judgments; revalidate current attributes before selection.
- **Validation required:** E04 dense-only, lexical-only and hybrid ablations on the same snapshot, especially identifiers and substitutes/complements.
- **Priority:** Medium; exact/structured correctness comes first.
- **Confidence:** Medium; complementary mechanisms are established, catalogue-specific gains are unmeasured.

### Change ID: ARCH-004 — Make NLU checkpoint and constrained contract reproducible

- **Component or layer:** Language-model adapter and request interpretation.
- **Current baseline:** README names Qwen3 4B Instruct/Ollama and post-output validation, without an exact artifact, decoding constraint or field provenance contract.
- **Proposed change:** Pin the 2507 non-thinking checkpoint/artifact as reference. Request compact JSON through a schema; strictly validate it and preserve evidence for prices, negation and action intent. Bound context, output and repair attempts. Benchmark current small challengers before substituting them.
- **Reason for change:** A generic model tag and prompt-only JSON format are not reproducible interfaces. Syntactically valid output can still authorize the wrong operation.
- **Supporting research:** [Checkpoint card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507), [exact registry artifact](https://ollama.com/library/qwen3:4b-instruct-2507-q4_K_M), [Ollama schema output](https://docs.ollama.com/capabilities/structured-outputs), [strict validation](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/).
- **Expected benefits:** Traceable experiments and fewer malformed interfaces; semantic correctness remains an evaluation requirement.
- **Trade-offs and risks:** Grammar overhead, truncation, forced-but-wrong fields and prompt/schema maintenance. Low temperature does not guarantee correct intent.
- **Dependencies and migration implications:** Shared schema, canonical vocabulary, artifact manifest and paired text/audio tests. Re-run fixtures on model/template/runtime upgrades.
- **Validation required:** E02 schema versus prompt-only extraction; critical-slot accuracy and unsupported-action rejection; same quantization comparisons.
- **Priority:** High; NLU feeds actions.
- **Confidence:** High for contract/pinning; medium for reference model suitability.

### Change ID: ARCH-005 — Specify turn, reference and operation state

- **Component or layer:** Python orchestration and minimal add handling.
- **Current baseline:** README requires session/reference correctness; §9 suggests a state machine, while retry/idempotency details are mostly future considerations in §§12 and 17.
- **Proposed change:** Define a finite state machine, immutable turn/list IDs, per-session serialization, a validated pending action and session-lifetime operation deduplication. Bind identity to the authorized command before dispatch; persist an immutable receipt. In a bounded database write transaction, check current eligibility, completeness and aggregate cart quantity. Clarify changed announced offers; verify/replay the receipt without treating historical cart state as current.
- **Reason for change:** Repeated ASR finals, late callbacks and timeout retries can duplicate an add or resolve “second” against the wrong results in an otherwise small prototype.
- **Supporting research:** README current action/session requirements; [PostgreSQL isolation/locking](https://www.postgresql.org/docs/current/transaction-iso.html) and [Python cancellation semantics](https://docs.python.org/3/library/asyncio-task.html). The proposed protocol is engineering design.
- **Expected benefits:** Controlled local action ordering and accurate known/unknown outcomes without a distributed transaction platform.
- **Trade-offs and risks:** More explicit state and cancellation rules. Guarantee ends at the documented session lifetime; external systems need their own idempotency contract.
- **Dependencies and migration implications:** ARCH-002 minimal tables and ARCH-004 typed intent; TTS consumes verified outcome events only.
- **Validation required:** E06 duplicates, conflicting commands, new intentional adds, aggregate quantities, stale references, interleaved sessions, replay after later cart updates, row-lock contention, serialization/deadlock retries, commit uncertainty and cancel/commit races.
- **Priority:** High; action correctness.
- **Confidence:** High for state ownership; implementation must prove each transition.

### Change ID: ARCH-006 — Add explicit audio turns and accessible recovery

- **Component or layer:** Capture, endpointing, playback and interaction surface.
- **Current baseline:** README moves directly from microphone to ASR and requires spoken normal/error paths, including TTS failures, without defining controls or a fallback channel.
- **Proposed change:** Add local VAD plus an explicit end-turn control, a partial/final transcript boundary, stop/repeat controls, playback ownership and cancellation. Use cached local error speech and assistive-technology-readable status when neural TTS fails. Start with half-duplex capture/playback and an accessible stop control; enable voice barge-in only after echo handling tests.
- **Reason for change:** Endpoint waiting consumes the latency target, assistant speech can be transcribed as a new command, and a failed TTS engine cannot reliably announce its own failure.
- **Supporting research:** [Silero](https://github.com/snakers4/silero-vad), [Piper chunk API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md), [W3C keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) and [status guidance](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html).
- **Expected benefits:** Clear nonvisual turn boundaries and recoverable errors; latency benefit is a hypothesis.
- **Trade-offs and risks:** Early cutoff versus delay, half-duplex interruption limits, audio-device differences. Failure of both playback and assistive technology must be reported as an unusable session.
- **Dependencies and migration implications:** Audio events, session state, language-specific fixtures and user testing; no wake-word service required.
- **Validation required:** E03 pauses/noise/negation/silence; E05 playback failures; E08 blind-user and keyboard/screen-reader tasks.
- **Priority:** High; central accessibility requirement.
- **Confidence:** High for responsibility; medium for precise endpoint/control policy.

### Change ID: ARCH-007 — Resolve Piper runtime and voice eligibility

- **Component or layer:** TTS supply chain and voice profile.
- **Current baseline:** README selects Piper direction but leaves exact runtime, voice and licence open.
- **Proposed change:** Reference the continuing OHF Piper runtime, pin its version/artifacts and inventory phonemizer dependencies. Evaluate en_US-ljspeech-medium for English. Make every release voice pass a separate language/intelligibility/terms gate; do not assume the repository-level voices label covers each voice. Hindi voice remains a decision gate.
- **Reason for change:** The old archived project and current runtime have different licences; inspected voice cards have materially different dataset terms.
- **Supporting research:** [Archive](https://github.com/rhasspy/piper), [OHF runtime](https://github.com/OHF-Voice/piper1-gpl), [voice guidance](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md), [LJ card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/medium/MODEL_CARD), [Pratham card](https://huggingface.co/rhasspy/piper-voices/blob/main/hi/hi_IN/pratham/medium/MODEL_CARD).
- **Expected benefits:** A reproducible, reviewable TTS profile and fewer distribution surprises.
- **Trade-offs and risks:** GPL distribution obligations need a project-specific decision. A voice with simpler terms may be less intelligible for target users; model-card declarations need verification for shipped artifacts.
- **Dependencies and migration implications:** Owner distribution/language decision, notices, local cached prompts and TTS adapter; no voice has been installed in this review.
- **Validation required:** E05 Piper/Kokoro tests, amount/SKU comprehension and recorded artifact/terms inspection.
- **Priority:** High before selecting release artifacts.
- **Confidence:** High for the need to resolve identity/terms; medium for voice selection.

### Change ID: ARCH-008 — Establish a measured deployment profile early

- **Component or layer:** Model lifecycle, performance instrumentation and development order.
- **Current baseline:** README §11 specifies the latency target; §16 places speech integration in Sprint 4; §17 lists several serving/observability controls as future considerations.
- **Proposed change:** Move a thin audio→NLU→verified-template→audio experiment into the first implementation increment. Pre-provision/pin local artifacts, warm required models, bound inference queues/timeouts, and trace utterance-end through actual playback. Record supported hardware, languages and workload before making a latency claim.
- **Reason for change:** Four local inference stages compete for resources; late discovery of a device/language mismatch could invalidate the rest of the design.
- **Supporting research:** [Ollama residency/queue behaviour](https://docs.ollama.com/faq), the workload limitations of [ASR benchmarks](https://github.com/SYSTRAN/faster-whisper), and README §§10–11.
- **Expected benefits:** Earlier evidence and controlled resource use; no numerical improvement is asserted.
- **Trade-offs and risks:** Startup warmup and resident memory cost; native cancellation may be imperfect; initial benchmarks take effort.
- **Dependencies and migration implications:** Model/voice manifest, timestamp interface and real target machine. No new metrics service or distributed scheduler is required.
- **Validation required:** E07 cold/warm/full-pipeline latency and E09 offline/resource/failure tests. Include missing responses, timeouts and early-cutoff failures in outcome/deadline denominators; publish misses as well as successes.
- **Priority:** High; feasibility depends on the supported profile.
- **Confidence:** High for measuring early; low for meeting 1.5 seconds before experiments.

### Change ID: ARCH-009 — Rank for query relevance with price as one factor

- **Component or layer:** Candidate generation, final ranking and result presentation.
- **Current baseline:** README allows subjective fit and deterministic cheapest selection but supplies no general relevance/price scoring contract. The original report's RRF proposal merged lexical/dense ranks without a price feature.
- **Proposed change:** Preserve hard constraints; retrieve lexical/dense matches and qualifying low-price candidates; rank ordinary matches using bounded query-fit, supported preference-fit and price features. Produce distinct ranked-match and lowest-price-match roles with scope/evidence. Explicit cheapest commands use price-first selection only within the qualified set. D14 resolves lowest-price placement in general results.
- **Reason for change:** Sorting all queries by price loses user fit; RRF-only ranking omits the newly required price factor. A price-sensitive final scorer can also favour products missed by a text-only shortlist, requiring a candidate-recall check.
- **Supporting research:** Owner requirement, [hybrid/custom scoring mechanisms](https://qdrant.tech/documentation/search/hybrid-queries/#custom-scoring-with-a-formula-query), [product relevance judgments](https://arxiv.org/abs/2206.06588). Weights and eligibility thresholds remain hypotheses.
- **Expected benefits:** Query-sensitive results that can prefer a better-fitting higher-priced product while still considering value and retrieving a qualifying low-price alternative.
- **Trade-offs and risks:** Weight/scale bias, weak attribute evidence, imperfect semantic eligibility, additional candidate evaluation and no universal relevance guarantee. An ANN shortlist cannot prove either the best composite score or a global semantic cheapest result.
- **Dependencies and migration implications:** ARCH-001/002/003/004; versioned ranking policy, features and price basis; updated SearchPlan/SearchResult contracts and labels.
- **Validation required:** E04/E10 price ablations, candidate recall against exhaustive small-catalogue scoring, human pairwise relevance/value judgments, cheapest-option inclusion/placement and E07 latency.
- **Priority:** High; explicitly requested result behaviour.
- **Confidence:** High that an explicit policy is required; medium for the proposed scorer and low for weights before evaluation.

## 6. Reasons behind the combined diff

ARCH-001 and ARCH-002 solve different parts of the cheapest-selection problem. Exhaustive sorting over incomplete or wrongly normalized data is still wrong. Conversely, a well-structured store does not help if the application only sorts ANN candidates. Together they define an eligible set, an ordering and an authoritative snapshot for the claim being made.

ARCH-003 improves discovery coverage without forcing every query into another model call. Its lexical branch should not influence a complete structured minimum: relevance scores cannot override “cheapest.” A neural reranker is rejected as a default because it adds latency before evidence that ranking, rather than recall or data normalization, is the problem. ARCH-002 replaces Qdrant for a different reason: removing an otherwise unnecessary cross-store correctness protocol before implementation. It does not assume a faster vector engine; E11 can justify a dedicated service if the actual workload needs it.

ARCH-009 closes a separate gap: finding textually similar products is not the same as ranking the best shopping matches. It adds price-aware relevance after qualification, with price-only selection retained for an explicit cheapest objective. Its low-price candidate branch addresses recall under the final scoring objective, not only textual recall. The placement policy must not silently turn every request into a price-first list. For subjective requests, completeness and human relevance remain empirical limits even with an exhaustive model scorer.

ARCH-004 and ARCH-005 connect language understanding to controlled action. Grammar-constrained JSON is useful but insufficient: the system still needs to prove which turn requested an add, which list “second” names and whether the action already happened. A generic autonomous agent is a poor fit for a fixed search/clarify/add workflow because it expands the number of execution paths and tool decisions that must be verified.

ARCH-006 makes the intent boundary meaningful for actual speech. A correct validator operating on a truncated or self-echoed transcript can execute the wrong human request. Half-duplex audio is a deliberate initial simplicity trade-off; a discoverable stop control is therefore required. Free-form voice interruption should be introduced only when the microphone does not turn the assistant's own confirmation into a new command.

ARCH-007 is a concrete completion of the README's open TTS decision, not a claim that Piper should always win. A high-quality voice with unsuitable terms is not a release choice, and a legally eligible voice that users cannot understand also fails. Kokoro and language-specific alternatives remain valuable experiments rather than predetermined replacements.

ARCH-008 tests the combined cost of these choices. Measuring an LLM alone cannot show whether ASR, embedding inference and TTS still fit in memory together. Warming every model indiscriminately can increase contention. First measure one supported profile; then tune residency, precision or model size against quality gates. The combined design therefore favours correctness and evidence before optional optimization.

The high-confidence proposal is the responsibility structure and one transactional data boundary. PostgreSQL resource/index tuning, exact ASR checkpoints, voice choice, candidate counts and model precision remain revisable through the documented gates. No claim of measured superiority over the baseline is made.

## 7. Final recommended architecture

### 7.1 Complete component inventory

This is the recommended **reference design after owner approval**, not an implemented system or proof of release readiness. Unresolved release choices are identified explicitly.

| Layer / technology | Receives → produces | Owns | Why it exists / decision status |
|---|---|---|---|
| Minimal accessible local client | Microphone/control input → audio/events; response events → playback/status | Capture/playback devices, explicit end/stop/repeat controls | Provides a nonvisual interaction surface. Exact toolkit remains open. |
| Audio adapter + Silero-compatible local VAD | Mono audio frames → speech boundaries and finalized turn audio | Endpoint policy, audio timestamps, no-speech/timeout detection | Prevents silence/partial turns becoming actions. Thresholds require E03. |
| whisper.cpp worker | Finalized audio, optional provisional stream → final transcript/diagnostics | ASR runtime lifecycle, no commerce authority | Retained reference; checkpoint/backend chosen by E03. |
| Intent adapter: Qwen3-4B-Instruct-2507 via Ollama | Final text + bounded typed context → structured interpretation | Language interpretation only | Retained reference with schema decoding. Small-model challenger promotion requires E02/E07. |
| Python validator/query planner | Interpretation + canonical vocabulary → validated SearchPlan, reference or clarification | Types, money normalization, allowed intents, route and scope | Sole compiler of allowlisted queries/actions. |
| PostgreSQL catalogue repository | Parameterized structured query → authoritative variants/snapshot | Product IDs, attributes, price/stock, coverage and catalogue revision | One local authority; external merchant truth remains a separate integration decision. |
| PostgreSQL built-in text search | Plain-text query + predicates → ranked variant IDs | Derived tsvector/GIN lexical representation with explicit configuration | Covers names/brand/model terms in the same database; not a BM25/identity guarantee. |
| BGE-small-en-v1.5 via FastEmbed | Semantic query/document → normalized vector | Encoder/tokenizer/serializer version | Retained for provisional English profile; language gate unresolved. |
| pgvector in the same PostgreSQL database | Vector + SQL predicates → candidate IDs/distances | Versioned derived embeddings, exact search first | Replaces Qdrant; one 384-dimensional cosine space for the BGE reference; ANN requires E11. |
| Python merge/ranker/selector | Current candidates + SearchPlan + ranking policy → ranked matches, lowest-price role and Selection with scope/evidence | Deduplication, relevance qualification, fusion, bounded preference/price scoring and objective-specific selection | Computes qualified structured minima or relevance-ranked discovery; no default neural reranker. |
| Session state machine | Turn/result/action events → next state/pending clarification | References, one active mutation per session, result-list order, operation identity | Prevents stale callbacks and cross-session leakage. |
| Minimal cart/receipt repository in PostgreSQL | Validated operation + catalogue snapshot → immutable outcome | Session-scoped cart rows, unique operation identity, guarded increment | Uses the same database transaction; no checkout/reservations/order/payment authority. |
| Response builder; optional grounded Qwen call | Verified outcome/current evidence → bounded speakable text | Factual success/error wording and rendering of amounts | Templates on ordinary path; optional explanation after retrieval. |
| OHF Piper worker; cached failure audio | Verified complete text phrase → PCM chunks | Synthesis and voice profile, no business authority | Retained direction; English LJ test candidate, release voice/terms require E05. |
| Local diagnostics/lifecycle module | Stage events/health → redacted timings and readiness | Version manifest, timeouts, resource gates, index reconciliation | Makes local deployment measurable without an observability service. |

### 7.2 Architecture diagram

~~~mermaid
flowchart TD
    U[User: speech and accessible controls] --> A[Audio turn controller and VAD]
    A --> S[whisper.cpp: finalized transcript]
    S --> N[Bounded intent adapter: exact fast path or Qwen via Ollama]
    N --> V[Python strict validation and query planner]
    V --> C{Clarification needed?}
    C -- yes --> R[Verified response builder]
    C -- no --> P{Retrieval route}
    subgraph DB[One local PostgreSQL database]
        D[(Catalogue facts coverage and revisions)]
        L[Built-in text search]
        Q[pgvector embeddings: exact search first]
        CR[(Session cart and operation receipts)]
        G[Generation and publication metadata]
    end
    P -- exact or structured --> D
    P -- semantic discovery --> L
    P -- semantic discovery --> E[BGE local query embedding]
    E --> Q
    L --> M[Merge and validate in one short database snapshot]
    Q --> M
    D --> M
    G -. readiness .-> M
    M --> F[Relevance qualification price-aware ranking and scoped selection]
    F --> Y{Valid selection and supported scope?}
    Y -- no --> R
    Y -- yes --> X{Explicit valid add intent?}
    X -- no --> R
    X -- yes --> T[Session serialization and guarded SQL transaction]
    D --> T
    T --> CR
    CR --> O[Committed receipt verification]
    O --> R
    R --> B[Playback: resident Piper or cached error speech]
    R --> AT[Assistive-technology status]
    B --> U
    AT --> U
    I[Validated import and embeddings prepared outside transaction] --> PUB[Atomic SQL publication]
    PUB --> D
    PUB --> L
    PUB --> Q
    PUB --> G
    ST[Python session state and turn IDs] -. coordinates .-> V
    ST -. coordinates .-> T
    ST -. coordinates .-> R
~~~

Optional grounded comparison sits between retrieved validated evidence and response construction. It cannot mutate the cart or choose an out-of-scope ID. For structured queries, the merge/hydration box simply passes the complete SQL result; no vector or FTS inference is necessary.

### 7.3 Core contracts and authority

| Contract | Required content | Consumer obligations |
|---|---|---|
| AudioTurn | App-created session_id/turn_id, PCM format, monotonic capture times, end reason, cancellation token | ASR cannot invent session/turn identity; enforce duration and format limits. |
| Transcript | Matching IDs, final flag, text, detected language/diagnostics when available | Provisional text may not reach mutation dispatch. |
| Interpretation | Intent enum, explicit-add flag, attribute/value/operator candidates, original evidence spans, ordinal/reference, unresolved fields | Treat as untrusted; reject unknown fields/operations, check spans and independently normalize critical values. |
| SearchPlan | Canonical IDs, hard predicates, soft preferences, sort, quantity, currency, unit/total budget basis, route, claim scope, query text | Construct SQL/filter objects in code; model never supplies SQL or executable filters. |
| SearchResult | Catalogue revision, active ready encoder generation, ranking-policy version, ordered matches with feature evidence, lowest-price match with qualification/scope or explicit unverified status | Preserve the presented order for ordinals; price may not rescue an irrelevant item; identify a missing/unverifiable required lowest-price result truthfully. |
| Candidate/Selection | Variant ID, current row revision, retrieval provenance, validated fields, result-list ID and selection scope | Rehydrate; scores are ranking signals, not probability or price truth. |
| AddCommand | Server-owned operation_id, session/turn IDs, selection mode (exact variant or query), immutable validated plan/quantity, observed offer if applicable | Allocate identity once before dispatch; fingerprint the authorized command, deduplicate before reselection, and recheck before committing. |
| AddOutcome | Immutable operation receipt: status, chosen variant, added quantity, unit/line price and resulting quantity at commit, catalogue revision, error/reason | Verify the committed receipt by operation_id; replay does not assert that historical cart quantity or price is still current. |
| ResponseEvent | State/outcome code, bounded text, language, turn ID, replayable response ID | TTS renders it; stop/repeat cannot replay business operations. |

These schemas are proposed interfaces, not source files. Keep the same contracts behind alternative ASR, encoder, runtime, store and TTS implementations.

### 7.4 Deployment boundary

Use a local application process with blocking inference workers, Ollama and one local PostgreSQL service with pgvector installed. Pin a supported PostgreSQL/extension pair, schema migrations and SQL driver; provisioning may use a local package or pinned container after a packaging test. Restrict database access to the local application with a non-superuser runtime role, bounded connection pool, statement/lock timeouts and no public listener. Maintain/test a database backup and restore procedure; model/voice files and application settings still need their own manifest. Qdrant and SQLite are not reference runtime dependencies. Piper may run in a resident worker, chosen for crash/resource isolation rather than a claimed licensing exemption. No network-accessible model ports are needed for the reference profile.

Pre-download models and voice artifacts during setup, record hashes and test with external network access disabled. Startup checks include device access, model readiness, schema/encoder compatibility, index freshness and a playable local error prompt. The app should communicate “ready” only when its supported workflow is available. Native Apple acceleration should run through a verified host build rather than assuming a container supplies the same acceleration path. Multi-host and remote-user deployment remain outside this reference profile.

## 8. Detailed application flow

Example request: **“Find the cheapest black backpack under ₹2,000 and add it to my cart.”** The following flow assumes an approved English/INR profile, a complete local catalogue category mapping and a valid session. No example product or price is claimed to exist in this repository.

1. **Start a listening turn.** The client creates a turn through the application, receives a turn ID, announces listening state, captures audio, and records the microphone clock. Previous playback is stopped or capture is gated according to the half-duplex policy.
2. **Detect the endpoint.** VAD tracks speech/silence; the user may explicitly end the turn. Allow pauses without treating an incomplete command as final. Record physical speech-end reference and endpoint-detection time separately. Silence/no-speech produces a concise retry prompt and no search/add.
3. **Finalize transcription.** whisper.cpp returns final text bound to this turn. Provisional text cannot authorize a mutation. If the final text is empty, truncated, unsupported-language or otherwise suspect, ask the user to repeat relevant information. Evaluate critical-word errors through E03; do not treat a high ASR diagnostic as proof.
4. **Interpret the request.** Since this is a general shopping sentence, call the schema-constrained Qwen extractor once. It proposes category backpack, colour black, price operator `<`, amount 2000 INR, sort price ascending, quantity one and explicit add intent. It supplies text evidence rather than an invented product ID.
5. **Validate and normalize.** Python validates the schema and allowed intent, resolves the category/colour vocabulary, verifies add intent/negation evidence and parses the amount independently into **200000 paise with an exclusive bound**. If “under,” “at most,” quantity or currency is unclear, ask a targeted clarification before mutation. An ASR error already present in final text may escape these checks; this is why audio-level evaluation and clarification policy are necessary.
6. **Select the query route.** All eligibility predicates here are structured, and cheapest is an objective sort. Choose complete structured retrieval. Skip query embedding, pgvector, lexical fusion, reranking and product-comparison generation. This preserves retrieval before product-grounded response generation: the evidence is retrieved through SQL.
7. **Retrieve the complete eligible-set minimum.** First check snapshot coverage and three-valued eligibility: verified match, verified nonmatch, or unknown. Only when potentially matching records have the required information can the repository claim a complete minimum. Query active purchasable variants with mapped backpack category, canonical black, INR, price below 200000 and sufficient quantity, using stable price/variant-ID ordering. Unknown records cannot be added without validation and cannot silently disappear from a completeness claim.
8. **Handle no match or ambiguous eligibility.** State no available matching backpack was found only when coverage and required attributes support that conclusion. If relevant records have unknown colour, price, category or stock, state that the result cannot be verified; ask for clarification or consent to a clearly narrower verified-record search. Offer to change a constraint only through a new user response. Do not silently substitute navy, exceed budget or remove the colour predicate.
9. **Resolve selection and variants.** Produce a validated variant ID and selection scope `complete_structured_catalogue`. If a mandatory size/variant remains unresolved, ask for it. For equal-price interchangeable candidates, use a documented stable tie rule; if the tie changes an important unrequested choice, ask instead of hiding it.
10. **Use the existing explicit add authorization.** The initial sentence already requests add-to-cart. Do not require a redundant confirmation for every valid add. Confirm only unresolved interpretation, a materially changed previously announced offer, or another action-affecting ambiguity. The model does not decide whether an action is permitted.
11. **Execute under application control.** Acquire session serialization and use the operation ID allocated once before dispatch. Begin the short PostgreSQL action transaction described in §9.7; lock the session row and check its stored receipt/fingerprint before selecting again. For this direct structured request, recheck completeness and recompute the eligible minimum in that snapshot; lock/revalidate the selected variant and aggregate quantity, then commit the increment and immutable receipt together. Conflicting updates require rollback and a bounded whole-transaction retry using the same operation ID. A query-selection command authorizes recomputation under unchanged predicates; an explicitly referenced/announced item must not be silently replaced.
12. **Verify the result.** Validate the cart update inside the transaction, commit, and confirm the stored receipt by operation_id. Do not compare an old receipt's resulting quantity with a mutable cart row that may already contain a later intentional add. Record the action snapshot’s catalogue revision and validated price used for the committed add. A minimum is scoped to that snapshot, not guaranteed against a later catalogue insertion. Adding does not reserve or decrement stock; no checkout availability guarantee is implied.
13. **Construct the response.** Use a template populated from the verified outcome, such as “Added one [name], black, for [spoken price] to your cart.” Include size if relevant and only claim cheapest within the recorded scope. Missing or unknown outcome produces an accurate pending/error response, never an “added” guess. No second LLM call is needed.
14. **Synthesize and play.** Normalize the actual amount into speakable rupees/paise and pass the complete verified phrase to the resident Piper worker. Start playback from available PCM chunks; measure actual audible onset. Match all chunks to the active response/turn so cancelled old speech cannot resume later.
15. **Retain minimal follow-up state.** Store the response for repeat, ordered result-list mapping when one was announced, pending clarification if any, and operation result for retry deduplication. Discard turn audio by default. Session expiry invalidates ordinal references and clears session-scoped state according to the retention policy.
16. **Recover truthfully.** A timeout before commit can be retried with the same operation ID. A timeout with uncertain commit status requires operation lookup before retry. If TTS fails after a successful add, retain that successful outcome and replay only its confirmation through fallback; do not repeat the add. If the catalogue or index is unavailable, distinguish an unavailable search from a genuine no-match result.

For **“find a good backpack for college”**, interpret any explicit attributes/preferences first; ask for missing information that would change an action. Generate dense/lexical candidates plus a qualifying low-price candidate branch, hydrate authoritative facts, and apply the §9.6 relevance/price scorer. Return ordered best matches plus the lowest-price-qualified role with its declared scope; presentation placement follows D14. A cheap luggage accessory cannot replace a relevant backpack merely because it is inexpensive. Subjective “good” is not a provable global-minimum or human-best claim. A second LLM call is justified only for an evidence-supported comparison the user needs, with factual attributes rendered through templates.

For **“add the second one”**, resolve a narrow accepted phrase against the last fully announced result-list ID in that session, then revalidate the chosen variant. Skip ASR only for typed input; skip LLM/embedding/retrieval discovery when the reference is unambiguous. If the list is expired, was only partly spoken or belongs to an old turn, clarify. “Repeat that” replays a response, never an operation.

## 9. Layer-by-layer design details

### 9.1 Audio, ASR and playback ownership

Capture mono PCM using the ASR adapter's documented input contract; resample explicitly and record both source/output rates. Keep a bounded audio ring buffer, clear ownership of the active turn, and a maximum turn duration with an audible recovery prompt. VAD history and initial audio padding must prevent clipping word onsets. Tune endpoint silence against pauses, final negation and slow speech using E03; a source example's threshold is not a validated setting.

Initially use half-duplex playback/listening with a keyboard/assistive stop control and a clear ready-to-listen cue. If hands-free interruption is required, add tested echo cancellation or playback-reference suppression before allowing microphone-based barge-in to issue commands. A stop request cancels future speech and computation where possible; it does not claim to undo a committed add. Make that distinction available in the resulting status.

Use a persistent whisper.cpp worker or binding rather than loading model weights for every turn. Choose a maintained integration path after a small packaging spike; no binding version has been verified here. Run the same checkpoint unquantized/reference versus the candidate quantization to quantify critical-word regressions. Endpointing and model inference are separately timed. [whisper.cpp documentation](https://github.com/ggml-org/whisper.cpp).

### 9.2 NLU and validation contract

An illustrative interpretation shape is below. It describes a proposed contract, not implemented parsing code or a claim of model output:

~~~json
{
  "intent": "search_and_add",
  "category_text": "backpack",
  "colour_text": "black",
  "price": {"amount_text": "2000", "currency_text": "rupees", "operator": "lt"},
  "sort": "price_asc",
  "quantity": 1,
  "reference_ordinal": null,
  "explicit_add": true,
  "unresolved": []
}
~~~

The real schema should also carry evidence spans or exact source phrases for critical fields, with application checks that they actually occur in the finalized transcript. IDs and session metadata are supplied by the application. Missing information must be representable as null/unresolved; forced enum choices must not hide ambiguity. Disallow additional properties and type coercion for action-critical fields. [Strict validation](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/).

Independently parse amounts and quantities from retained evidence; normalize Indian number forms, decimals and separators using tested locale rules. Distinguish hard constraints from preferences, maximum unit price from total budget, and a new query from refinement of a prior plan. For quantity greater than one, clarify a budget whose per-unit/total meaning affects eligibility. Never inherit an old budget, colour or add flag accidentally when creating a new search.

Use one versioned JSON schema in the decoder and validator. Set compact context/output limits from the longest supported schema and approved turn fixtures. Compare low/zero temperature and candidate quantizations under E02; exact values are experimental settings to record, not evidence-backed release defaults in this report. Allow at most one bounded repair attempt for malformed output, then ask clarification or return a recoverable failure. Semantic ambiguity should ask the user, not trigger an endless repair loop. Do not execute partial/truncated JSON. [Ollama schema mechanism](https://docs.ollama.com/capabilities/structured-outputs).

### 9.3 Catalogue schema and monetary semantics

Proposed minimal entities:

| Entity | Key fields / invariants |
|---|---|
| Product | product_id, display name, brand, category_id, vetted descriptive attributes, active flag |
| Variant | stable variant_id/SKU, product_id, colour_id, size/variant attributes, price_minor integer, currency, availability/stock, revision, updated_at |
| Canonical vocabulary | category tree/aliases, colour aliases and explicit mixed-colour semantics, allowed units; no inferred hard attributes from prose without a data-quality process |
| Catalogue/search publication | Source coverage, catalogue revision, semantic content revision/hash distinct from price/stock revision, active encoder/serializer generation and ready/pending state; staged imports and derived VariantSearch rows keyed by variant/generation |
| Session/results | session_id, expiry, turn counter, last fully announced result-list ID, ordered variant references and observed revisions, pending clarification/selection |
| Minimal cart/operation | session_id, variant_id, quantity; unique operation_id with session/turn binding, command fingerprint, outcome and resulting quantity |

Use integer minor units for money, explicit currency, nonnegative prices and positive integer quantities. Reject missing prices/currencies or unknown required attributes. Do not convert currencies silently. “Under ₹2,000” means `< 200000`; “₹2,000 or less” means `<= 200000`. Explain the interpretation when unclear. Prices and stock come from the authoritative structured record, never from generated descriptions or vector scores.

Rejecting an unknown record for an action does not establish that it is irrelevant to the user's search. Maintain a completeness gate for global minimum/no-match claims; an incomplete source import also fails that gate even if every imported row is well formed. In narrower searches, disclose the verified-record scope and obtain consent before acting on it when the original request required an exhaustive result.

Specify unit-price versus total-increment budget in SearchPlan. For a total-increment budget, compare `requested_quantity * current_unit_price_minor` with its bound using checked integer arithmetic; an existing-cart total is a different scope requiring an explicit request. For the minimal local add rule, validate `existing_quantity + requested_quantity <= current_known_stock` and any known quantity cap in the write transaction. Unknown stock quantity cannot establish a multi-unit limit; do not invent a count from an availability boolean. These checks do not reserve inventory or make guarantees about later stock changes.

Use PostgreSQL NOT NULL, CHECK, UNIQUE and foreign-key constraints for authoritative invariants; use bigint for minor-unit amounts and checked quantity multiplication. Verify the pgvector extension, schema, encoder dimensions and text-search configuration at startup. Derived VariantSearch rows reference their canonical variant and identify the source content revision; database constraints do not replace cross-row completeness and quantity checks. [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html).

Represent each purchasable variant separately. A black parent product with an unavailable black variant must not be offered using another colour's price/stock. If an attribute is multi-valued, define whether the user permits it; do not interpret the presence of “black” somewhere in an array as an unqualified solid-black match.

The reference catalogue is local application truth. If a real merchant system is required, define which API owns current price/stock and cart outcomes; re-check through that API at action time. PostgreSQL cannot create freshness guarantees for an external inventory source whose update contract is unknown.

### 9.4 Ingestion, publication and snapshot consistency

Validate imports, source coverage, canonical attributes and stable variant IDs. Keep unvalidated/incomplete imports represented in coverage metadata; do not silently discard them and declare the remaining rows complete. Catalogue mutations use the publication adapter; direct writes that bypass content/version invariants are unsupported. Embeddings remain derived data even though they share a database with the facts.

1. Stage new semantic content and prepare its embeddings outside a database transaction. Record the source content revision/hash and encoder/serializer generation. An old worker result cannot overwrite newer content: publication uses compare-and-set revision checks, and rejected work is recomputed or discarded.
2. In one short SQL transaction, serialize publishers on the publication-metadata row; publish validated catalogue changes, matching VariantSearch embeddings/text-search data, coverage and revision together. Semantic-dependent updates normally wait in staging until their vectors are ready. Commit makes the matching set visible together; rollback leaves the prior committed set intact. No model inference occurs while holding these locks.
3. Price/stock-only changes and deletions must not wait for re-embedding. Publish them atomically in canonical rows, with deletion/search-row cleanup and revision/coverage updates; no duplicated price/stock vector payload is maintained. If an urgent semantic correction must be published before its embedding exists, commit the corrected authority and semantic-not-ready state together. Semantic readers encountering that state wait briefly or return an accessible updating status; structured reads may continue. Unknown semantic coverage is not a no-match result.
4. Generate the query vector before opening a read transaction and attach its encoder/serializer fingerprint. Read readiness/active generation, lexical candidates, dense candidates, structured low-price branch and canonical facts in one short `REPEATABLE READ READ ONLY` transaction, or one equivalent SQL statement snapshot. If the active generation differs from the query vector’s fingerprint, close the transaction and recompute outside it within the turn’s retry budget. Multiple statements at default Read Committed do not establish a shared snapshot. Extract bounded facts and close the transaction before optional reranking/LLM/TTS work. An action later takes a fresh snapshot and revalidates; a displayed result is not a price lock.
5. For an encoder/serializer change, build a separate generation from content-revisioned rows. Before switching the active-generation pointer, verify all active searchable variants have matching current content, reconcile concurrent changes/deletes and require the expected dimension/fingerprint. Flip the pointer atomically under the publisher lock. Keep older generations for diagnosis, but a rollback must reconcile their content to current authority or restore a matching database snapshot; never serve stale vectors as current.
6. Crash recovery inspects committed staging/publication metadata. Uncommitted publication rolls back; committed semantic-not-ready state remains unavailable until repaired. Retry jobs idempotently by source revision. Backup/restore tests include canonical data, search rows, generation pointers, coverage and operation receipts, plus compatible extension provisioning and the separate model manifest.

This removes the earlier SQLite/Qdrant read/write publication lease and completed-upsert handshake; PostgreSQL MVCC supplies the database snapshot boundary. It does not remove source-import lag, asynchronous computation, ANN misses or the need for fingerprint/recovery tests. A reader may consistently see the prior committed revision while publication happens; no multi-query result may mix revisions. External merchant freshness still depends on its source contract. [Isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [locking](https://www.postgresql.org/docs/current/explicit-locking.html), [backup/restore](https://www.postgresql.org/docs/current/backup-dump.html).

### 9.5 Encoder and pgvector representation

For the retained BGE reference, create one vector per purchasable variant using a stable text order: name, brand, category, colour/size and useful descriptive attributes. Keep important distinguishing fields before truncation; validate document length with the actual tokenizer. Avoid volatile stock/prices in embedding text; use structured fields for those constraints.

Construct semantic query text from the requested product and descriptive purpose/preferences. Keep action instructions, quantity arithmetic and budget operators in typed plan fields rather than relying on their vector similarity; retain the original transcript for validation. Test the full-query versus extracted-semantic-query choice in E04 so rewriting cannot silently drop a required preference or exclusion.

Use the documented 384-dimensional BGE output, normalized consistently, with cosine search. Query instructions apply according to the encoder's contract; test prefixed versus unprefixed short queries on development data rather than assuming one improves this catalogue. Pin the selected behaviour. [BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5).

Store `VariantSearch(variant_id, encoder_generation, content_revision, text_hash, embedding vector(384), lexical_document)` in PostgreSQL, with a unique variant/generation key and a foreign key to the canonical variant. Join category, colour, currency, price and stock from canonical rows in the same snapshot. Define explicit lexical configurations and a maintained tsvector/GIN representation. A publication transaction updates this derived representation when its source text changes; generated expressions must use a fixed configuration and row-local source text. Exact SKU equality remains separate. Choose structured indexes from measured predicates/query plans rather than copying a Qdrant payload-index layout. [PostgreSQL text indexes](https://www.postgresql.org/docs/current/textsearch-tables.html).

Start with exact cosine-distance ordering on the filtered eligible rows for the initial profile; nearest by vector distance does not mean cheapest or best under the final scorer. Introduce an HNSW cosine index only if E11 shows exact search cannot meet the budget. Keep SQL eligibility/generation predicates, inspect query plans, and test selective filters and incomplete result sets. If ANN is enabled, pin iterative-scan/search limits and compare with an exact oracle; strict distance ordering is not exhaustive recall. Never use ANN for the complete structured minimum. [pgvector filtering](https://github.com/pgvector/pgvector#filtering).

A multilingual encoder swap changes this contract. E5's query:/passage: preprocessing and a same-sized vector do not preserve BGE semantics. Other encoders need their own dimension, pooling and instruction settings; a different dimension requires a compatible separate table/index generation rather than inserting into the reference vector(384) column. Never combine vectors from different encoders in one unnamed space.

### 9.6 Query construction, fusion and ranking

The planner emits a finite set of parameterized query templates. No model-generated SQL, arbitrary database field names, executable code or direct cart tool calls are accepted. Exact IDs use equality; category/colour/budget constraints use canonical types and explicit operators. A mandatory missing attribute blocks an action and remains unknown for completeness checks.

Use bound parameters with `plainto_tsquery` and an explicit matching text-search configuration for ordinary lexical text. It treats the input as text rather than accepting an unrestricted tsquery program. Do not substitute raw `to_tsquery` or `websearch_to_tsquery` merely because SQL is parameterized: their query semantics differ. If OR alternatives/phrase handling are added, the application constructs them from validated literal terms through an allowlisted policy. Test punctuation, quotes, hyphenated model names, operator-looking text, stop-word-only/empty queries and each approved language. Exact identifiers remain equality lookups, and a tokenizer failure is not permission to drop a hard predicate. [Query construction](https://www.postgresql.org/docs/current/textsearch-controls.html).

For semantic discovery, read all branches and canonical facts under §9.4’s snapshot contract, merge IDs, reject invalid/mismatched content generations and fuse surviving ranks. An application formula such as `sum(1 / (c + rank))` uses documented one-based ranks; choose c and branch depths on development data. Do not directly add cosine distance to lexical scores or treat PostgreSQL ranking as FTS5 BM25. Use calibrated features/rank fusion and evaluate whether lexical changes affect product-name coverage. [Ranking](https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-RANKING).

Start E04 with candidate depths 10, 20 and 50 as experimental comparison points, not production defaults. If qualification removes many candidates, bounded overfetch, exact search or publication repair may be needed; distinguish ANN/filter underfill from an absent catalogue match. Do not silently return an empty valid set as proof that the catalogue has no match. Stable exact identifiers outrank fuzzy similarities only when identity was explicitly and correctly resolved.

**Final query-aware ranking policy (ARCH-009):** treat candidate generation, qualification, final scoring and presentation as separate functions:

1. Parse hard requirements, exclusions, semantic intent, soft preferences, objective (`best_match`, explicit `cheapest`, or an explicit price target), budget basis and quantity. Clarify contradictions or an unsupported request rather than returning an arbitrary product. Direct IDs and previously presented ordinal selections remain binding; a general low-price preference cannot replace the selected item.
2. Retrieve a union of exact, lexical, dense and structured low-price candidates under mandatory predicates. Evaluate every candidate with the same query-fit features, including candidates present only in the low-price branch. Use a domain-tested relevance gate for semantic/category/purpose fit before a price boost; accessories, substitutes or irrelevant products do not become exact matches because they are cheap. Missing critical suitability evidence remains unknown.
3. For ordinary best-match queries, use a transparent bounded scorer of the form `score = w_text*T + w_pref*A + w_price*P`, with nonnegative weights summing to one and a positive price weight for supported multi-product searches. T is calibrated query-fit evidence from dense/lexical features (or a validated optional reranker), A measures supported requested preferences, and P measures authoritative price utility. Normalize feature scales using a frozen evaluation profile rather than raw fusion/lexical magnitudes or min/max values from the current shortlist. Weights, relevance gates and missing-feature rules are versioned experimental choices to tune on development judgments; this report invents no optimal weights.
4. A candidate low-price utility is `P = 1 / (1 + p/s)`, where p is the relevant unit/total-increment price and s is a positive category/currency reference scale fixed for the ranking profile. This is a proposed bounded feature, not a published optimum. For an explicit target price, compare distance to the target instead of assuming cheaper is always preferable. Budget is still a hard constraint. Price never stands in for quality, and absent ratings/specifications are not hallucinated. Require an equal-fit cheaper-product test and a better-fit higher-price test before accepting weights.
5. Retrieve a lowest-price-qualified option for each supported product search and expose its scope separately from the best composite match. For fully structured and complete eligibility, SQL can establish the minimum. For subjective eligibility, a cheap item from hard filters must still pass the same relevance qualification. A top-K semantic list only supports “lowest price among the verified matches evaluated.” If a catalogue-wide lowest-price match is mandatory, use exhaustive evaluation of the complete hard-eligible set under the declared qualification policy, or clarify/return an explicitly unverified result; do not relabel a shortlist minimum as global. Even exhaustive model qualification is not proof of human relevance for every possible query.
6. Preserve the relevance-ranked order and identify the qualifying low-price alternative according to the D14 placement decision. Deduplicate a product already serving both roles; for broad discovery, avoid filling the short spoken list with near-identical variants while preserving each purchasable variant's own facts. Do not silently replace the top result with the cheapest product or auto-add a different role. A general “add the best match” uses the agreed best-match policy only when preferences/authorization are sufficient; ambiguous “best” asks for clarification. An explicit “cheapest” objective uses price-first ordering among qualified matches; equal price can use fit and a stable ID tie rule.

A final price-aware scorer can promote a middle-priced product absent from both text top K and a cheap-only branch. Therefore, a low-price branch alone does **not** guarantee composite-score recall. On a small complete catalogue, compare the candidate union with exhaustive scoring using the same feature policy; measure whether true top-ranked model candidates are missed and widen/adapt retrieval or use exhaustive scoring for that supported profile. Separately compare final order with human judgments. If the relevance or coverage gate cannot be met, clarify or state the limited scope; no architecture can honestly promise the most relevant product for every arbitrary query without suitable data and validation. [Scoring-stage mechanisms and scale caveats](https://qdrant.tech/documentation/search/hybrid-queries/#custom-scoring-with-a-formula-query).

Subjective “best” requests need an inspectable policy: ask which factors matter, or state a limited evidence-based ordering. Do not invent popularity, ratings, waterproofing or college suitability. A second model call can draft a comparison using only current supplied facts; to reduce factual drift, let it select evidence/IDs and render key factual claims through deterministic templates. If unsupported prose cannot be validated, use a simpler comparison.

### 9.7 State machine and minimal cart semantics

Proposed transitions:

~~~text
READY → LISTENING → FINALIZING → INTERPRETING → RETRIEVING
      → NEEDS_CLARIFICATION → LISTENING
      → RESULTS_READY → SPEAKING → READY
      → ACTION_PENDING → APPLYING → VERIFIED → SPEAKING → READY
Any noncommitted stage → CANCELLED/RECOVERABLE_ERROR → accessible response
~~~

The implementation must model the branches rather than literally allowing every arrow from every state. Bind asynchronous completions to session_id, turn_id and expected state/version; ignore stale completions. Publish an ordinal reference list only after its ordering has been announced. If speech is interrupted halfway through a list, retain only clearly announced references or re-announce before resolving “second.” A refinement creates a new plan/list and explicitly invalidates old ordinal mappings.

Allocate an operation ID once when a validated action is dispatched, persist its association with the turn, and preserve it across retries. Fingerprint the immutable authorized command: selection mode, exact variant/observed offer or query predicates, quantity, budget basis, currency and scope. For query selection, the finally chosen variant belongs in the receipt; it must not change the retry fingerprint. Look up an existing receipt before recomputing a minimum so a retry cannot add a newly cheaper product a second time. A new intentional add gets a new ID; if a prior outcome is unresolved, reconcile or clarify a repeated spoken request before treating it as a new add.

For local adds, keep application session serialization and use a short PostgreSQL `REPEATABLE READ` write transaction. Lock an existing session row with `FOR UPDATE` before reading cart state or checking the unique operation receipt, and increment its mutation version in every successful add transaction; every cart writer for that session follows this order. Verify the stored fingerprint and return a matching receipt before reselection. A unique operation ID plus session binding is the database backstop against duplicate workers; a conflicting fingerprint/session binding is an error, not a new add. On a unique-operation conflict, roll back before looking up the winner’s receipt in a fresh transaction and compare its binding/fingerprint; never continue a failed transaction or blindly increment again.

For a query-selected structured add, check source/attribute completeness and recompute the minimum in this action snapshot. Lock the chosen canonical variant row before validating current price/stock and `existing_quantity + requested_quantity`; writers changing its facts must contend on that row. Revalidate any separately stored action-critical facts under the same snapshot/lock or revision guard. Apply the increment and immutable receipt together, using database constraints and a consistent session-then-variant lock order. No stock reservation/decrement is introduced. A new cheaper row committed after the snapshot does not retroactively invalidate its recorded scoped minimum; a stronger “cheapest at every future/commit instant” promise is not made.

Bound lock/statement/transaction duration. On serialization failure or deadlock, roll back and retry the whole transaction with the same immutable operation ID/fingerprint, a fresh snapshot and a bounded retry policy. Do not retry only its last statement. In particular, a session or selected variant updated after a Repeatable Read snapshot may require restart. If the client loses the connection during commit, consult the committed receipt on a healthy connection before retrying; absence while another attempt is still unresolved is not proof it failed. Session-row serialization, unique operation identity and bounded reconciliation must prevent a second increment. Never speak success before the commit is known. [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [row locking](https://www.postgresql.org/docs/current/explicit-locking.html).

Validate resulting cart state before commit. After commit, verify the receipt by operation ID rather than requiring the current cart row to equal the historical resulting quantity; a later valid add may already have changed it. Replays report the original operation outcome and its recorded price, not an invented current cart total. No LLM, ASR, embedding or TTS work occurs inside the transaction. The cart quantity is not a stock reservation, and adding does not create an order.

Session-scoped PostgreSQL rows are chosen for atomic local verification, not for a comprehensive cross-session cart feature. Expire and clean them under a documented policy. Do not promise recovery of a lost session after restart unless the client/session token and expiry contract is implemented and tested. Never replay pending actions automatically into a new session. If later using an external cart API, preserve its idempotency key/result lookup or disclose the weaker guarantee; a local ledger cannot prove an external exactly-once effect.

Once commit completes, stop/cancellation affects playback and later work; it cannot truthfully say the add was cancelled. After a timeout, consult the stored outcome before retrying. If the outcome remains unknowable, say it cannot be verified and prevent a fresh blind retry. [PostgreSQL transactions](https://www.postgresql.org/docs/current/transaction-iso.html), [task cancellation](https://docs.python.org/3/library/asyncio-task.html).

### 9.8 Responses, errors, security and observability

Use response codes for no-speech, clarification, no-match, unsupported request, stale offer, search unavailable, invalid reference, busy, add success, add failure and unknown outcome. Each code has a concise spoken template, accessible text equivalent and recovery action. An ambiguous/no-match response never inherits an add authorization for an automatically relaxed query.

Apply request IDs and bounded timeouts at every worker/DB boundary. Retry read operations within the remaining turn budget; retry a mutation only through its operation identity. Limit one active interactive generation per reference device initially, reject/announce overload rather than building an unbounded queue, and measure contention before increasing parallelism. Long-context settings and concurrent model residency need measurement. [Ollama serving behaviour](https://docs.ollama.com/faq).

Treat catalogue prose as untrusted data. Separate it from control instructions, truncate/escape it, allowlist structured fields and never permit it to create action authority. Pydantic is an input boundary, not a prompt-injection cure. Session identity must come from the application/client protocol, never a model field. Restrict direct access to local model/database ports; a remote deployment would require a separately reviewed authentication/authorization boundary.

Record monotonic stage timestamps, operation state codes, model/voice/encoder revisions, prompt/schema version, token counts, result counts, catalogue/index lag, CPU/RAM/VRAM and failure categories. Use pseudonymous correlation IDs; avoid raw audio/transcript/product-description logs by default. Diagnostic recording requires an explicit purpose, consent and retention period. Cache embeddings only under encoder/serializer fingerprints; never cache an authoritative stock/price validation or a mutation result across unrelated sessions.

No distributed tracing backend is necessary initially. Structured local traces and an exportable benchmark summary are sufficient. Health checks should reveal missing models, incompatible schema/vector dimensions, stale semantic index and unusable audio before an action is accepted.

### 9.9 Artifact and licence inventory

This inventory records upstream declarations, not a conclusion that a future bundled application has satisfied every distribution obligation. Recheck the exact shipped artifacts and incorporated dependencies at release; record source revision, download URL, checksum, licence text, notices and intended use in the model/dependency manifest.

| Artifact boundary | Inspected declaration / source | Implementation implication |
|---|---|---|
| ASR runtime and original weights | [whisper.cpp MIT](https://github.com/ggml-org/whisper.cpp); [Whisper code and weights MIT](https://github.com/openai/whisper) | Preserve notices and identify weight conversions/quantization provenance. |
| NLU model and runtime | [Qwen 2507 Apache-2.0](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507); [Ollama MIT](https://github.com/ollama/ollama/blob/main/LICENSE) | Model and server are distinct artifacts; save both declarations and the precise quantized artifact identity. |
| Encoder and execution libraries | [BGE-small MIT](https://huggingface.co/BAAI/bge-small-en-v1.5); [FastEmbed Apache-2.0](https://github.com/qdrant/fastembed/blob/main/LICENSE); [ONNX Runtime MIT](https://github.com/microsoft/onnxruntime/blob/main/LICENSE) | Encoder exports/tokenizers and inference libraries need their own recorded versions and notices. |
| Application/storage | [Python PSF-2.0 and incorporated terms](https://docs.python.org/3/license.html); [PostgreSQL licence](https://www.postgresql.org/about/licence/); [pgvector licence](https://github.com/pgvector/pgvector/blob/master/LICENSE) | Record the chosen SQL driver/build dependencies separately. SQLite/Qdrant licences in the research log describe alternatives, not reference dependencies; the project’s own licence remains an owner decision. |
| VAD | [Silero MIT](https://github.com/snakers4/silero-vad) | Pin the detector model and execution library, not only a Python package version. |
| TTS runtime, voices and phonemizer | [OHF runtime GPL-3.0](https://github.com/OHF-Voice/piper1-gpl); [individual voice guidance](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md) | Evaluate the complete intended distribution. Voice/data terms and phonemizer components remain separate checks; do not infer permissive terms from a repository badge. |

Alternative-model licences in the research log identify potential decisions; they do not authorize a blanket swap. In particular, a model with noncommercial dataset terms or a custom licence needs an intended-use decision rather than being described generically as free/open source.

## 10. Performance and evaluation plan

### 10.1 What is measured today

**Nothing about VoiceCart's runtime performance or quality has been measured.** The repository observations and upstream documentation in this report are the available evidence. The tests below are future experiments; no model weights were downloaded or inference pipeline run for this review.

### 10.2 Latency definition and realism of the target

Let `t0` be the end of the user's actual utterance, established from an annotated recording or controlled replay, not the later time at which VAD declares silence. Let `t_audio` be actual onset of the first audible response at the device. The README metric is:

~~~text
L_first_audio = t_audio - t0

Critical path includes:
endpoint decision + remaining ASR work + interpretation/validation
+ chosen retrieval/selection + required mutation/verification
+ any required response generation + first TTS audio + device buffering
+ queue/IPC waits along that path
~~~

Work completed while the user is talking can reduce the remaining ASR tail; it must still be reported in resource measurements. Measure actual playback with loopback or an external recording to account for device buffers, clocks and leading silence. TTS API return, first generated PCM byte and first audible sound are different timestamps.

Record separately:

- First feedback sound/acknowledgement.
- First meaningful answer or clarification audio.
- First verified success/error confirmation audio for action requests.
- Time until the complete spoken response finishes.

A generic “one moment” may satisfy a literal first-audio definition while leaving the answer slow. Report both metrics; never use it to claim that a complete search/add result met the target. Include endpoint delay in every end-of-utterance result. Do not sum per-stage P95 values and call that end-to-end P95; measure the distribution of each complete request.

Use all eligible test turns in the success-within-deadline denominator. Timeouts, crashes and missing meaningful audio count as failures/misses, not samples to drop from a fast-success average. Report successful-response latency distributions separately with their denominators; mark missing timings as censored/unavailable rather than substituting the timeout duration as a successful response. A premature endpoint/action before the annotated utterance ends is a correctness failure, not a zero/negative-latency success. Track latency of error prompts separately so fast failures cannot demonstrate successful task performance.

**Assessment:** warm, short, structured requests are a plausible target because the proposed route removes vector/second-generation work when unnecessary and uses resident models. However, even one extractor call must finish its full structured output before action validation. GPU/CPU contention, long transcription tails, model loading, language errors/retries and TTS initialization can exceed the budget. Available source benchmarks cannot determine whether the target will hold on this project hardware. No justified numerical stage budget or expected speedup is available yet.

README does not specify percentile, utterance length, hardware, concurrency or whether acknowledgement counts. Propose **P95 under 1.5 seconds for meaningful first audio on the declared warm supported workload**, alongside median, cold-start results and the fraction of all turns exceeding 1.5 seconds. This percentile/profile interpretation requires owner acceptance; it does not silently replace the original target. If the owner intends every cold and warm turn to meet 1.5 seconds, treat that stronger requirement explicitly and demonstrate it or report failure. A slower tier or revised target also requires an explicit decision.

### 10.3 Experimental controls and resource accounting

Run the first measurements on the actual intended device, not a guessed developer laptop. If available, compare a CPU-only profile, an Apple Silicon profile and a CUDA profile. Record exact CPU/GPU, RAM/VRAM, OS, audio device, drivers, acceleration backend, thread counts, power mode and thermal conditions. These are comparison profiles, not purchase recommendations or verified minimum requirements.

For every run record runtime/database/extension versions, immutable model/voice revisions and hashes, quantization, chat template, context/output limits, sampling settings, ASR beam/language settings, VAD policy, sample rate, encoder preprocessing, catalogue snapshot, candidate depths, text-search configuration, ranking-policy version, exact/ANN query plan and scan settings, transaction isolation, pool limits and concurrency. Keep these constant in a paired experiment; change one factor or an explicitly named complete configuration.

Measure isolated stages and the combined resident stack. Include peak RSS/VRAM, sustained CPU/GPU use, swap, model eviction/reload, startup-to-ready time, queue delay and index-build/update cost. Never derive total memory from model parameter count or download size. As a planning calculation only, 100,000 float32 vectors of dimension 384 occupy 153,600,000 bytes before indexes, IDs, payloads, process memory or model weights; this is not measured database RAM; tuples, vector representation, indexes, buffers and workers add overhead.

Test a genuine cold application/model start, the first ready turn, repeated warm turns, idle-unload behaviour, catalogue updates during interaction and two interleaved sessions. Increase concurrency only when the intended deployment requires it. Keep batch-one interactive results separate from throughput batches. Randomize A/B order and repeat after thermal steady state. Capture median/P95 with uncertainty intervals and sample counts per route/profile, not just a pooled average.

### 10.4 Data and test-set design

Create a versioned complete catalogue fixture first. Include price ties, variants, missing attributes, currency differences, quantities, unavailable products, deletion/update cases and deliberately poorly described cheap products. The structured oracle must inspect all eligible records. For discovery, obtain independent product relevance judgments using Exact/Substitute/Complement/Irrelevant labels where useful; catalogue-specific labels are essential. [ESCI rationale and data](https://github.com/amazon-science/esci-data).

Start with a proposed coverage set of approximately **600 annotated text turns** and a separately consented multi-speaker audio subset covering every critical category. This is a test-planning seed, not a claim that the sample is collected or statistically sufficient. Use a pilot to determine per-stratum sample sizes and power before selecting a model. Separate development/tuning and held-out tests by speaker, session and query pattern to reduce leakage. Retain an untouched challenge set for final model/configuration selection.

Include:

- Exact SKUs, brand/model numbers, misspellings and descriptive paraphrases.
- Indian English accents, quiet/noisy rooms, variable speech rate and long pauses.
- Hindi/Hinglish and script/transliteration variants if in the approved language profile.
- “Under” versus “at most,” rupees/paise, Indian number words, corrections and quantities.
- “Don't add,” “find only,” interrupted speech, background speech, silence and assistant echo.
- Subjective preferences, unsupported product facts and missing mandatory variants.
- Equal-fit products with different prices, a better-fitting higher-priced product, cheap irrelevant accessories, explicit target prices, negative preferences and a middle-priced high-value product outside the initial text/cheap candidate lists.
- Ordinals, new searches versus refinements, repeat/stop, stale lists and two-session interleavings.
- Malformed/truncated model output, prompt injection in user/catalogue text and unsupported intents.
- Duplicate completions, response timeouts, late cancellation, stock/price changes and index failure.

Use synthetic fixtures for deterministic corner cases and consented real recordings for speech/accessibility. Synthetic speech alone cannot establish accent/noise usability. Do not retain identifying recordings by default; maintain a consent/retention process for the evaluation set.

### 10.5 Metrics and release gates

| Area | Measure | Acceptance criterion / how to establish it |
|---|---|---|
| Hard constraints | Invalid additions divided by all additions; explicit-budget/category/colour/quantity violations | Zero on deterministic fixtures and held-out action challenges. Any violation blocks promotion; finite zero-error samples do not prove universal correctness. |
| Global cheapest | Match to the complete structured oracle, including source completeness, unknown fields, stable ties and snapshot version | Exact agreement for complete supported fixtures; potentially relevant unknown records block the global/no-match claim. A scoped answer must never claim a catalogue-wide minimum. |
| Add intent | False-add rate on search-only, negation, silence, echoed speech and cancelled turns | Zero observed unintended mutations in the release challenge suite; investigate every failure rather than averaging it away. |
| Mutation semantics | Duplicate/wrong-session effects, aggregate quantity violations, fingerprint mismatch, receipt replay after later adds and unknown outcomes | Zero duplicate/wrong-session/invalid-quantity effects in the declared window; historical receipt verification remains correct after later updates; uncertain external outcomes are surfaced truthfully. |
| ASR | WER plus exact critical-value accuracy for prices, negation, colour, names, quantities; false speech and early cutoff rates | Select among candidates on these critical fields and downstream action results. Establish tolerable non-action transcription error through the pilot/user study. |
| NLU | Intent accuracy, slot F1, whole-plan exact match, operator/amount/negation/add accuracy, malformed rate, clarification precision/recall | No candidate promotion with a critical safety regression. Set absolute noncritical quality thresholds before held-out testing using the pilot and owner needs. |
| Discovery retrieval | Recall@10/20/50, Precision@K, nDCG@K, exact identity accuracy and no-match error | Require a reliable paired improvement over dense-only for adopting extra ranking/model layers, without critical slice regressions. Freeze an absolute relevance floor from labelled pilot data before release. |
| Relevance and price | Human-judged relevance/value nDCG and pairwise preference; composite-score candidate recall against an exhaustive small-catalogue reference; qualified lowest-price-role coverage | Cheap irrelevant products cannot enter through a price boost; equal-fit cheaper and better-fit higher-priced fixtures both behave as the accepted policy requires. Verify minimum scope/inclusion separately from primary relevance order; no universal relevance claim. |
| Freshness | Wrong/stale selected facts, missing-new-item rate, receipt-versus-completion handling, concurrent publication, reconciliation lag and rebuild success | No stale invalid add or mixed-revision ready search; semantic coverage stays unavailable until completed publication. Exact lag target depends on the update SLA. |
| Grounding | Unsupported spoken product claims and IDs outside retrieved validated evidence | Zero in release fixtures; fall back to evidence templates if validation cannot support free prose. |
| Latency | First feedback, meaningful first audio, verified outcome audio, full-response time; median/P95, missing-response rate and deadline success fraction over all eligible turns | Report by cold/warm, route, language and device. Timeouts/no audio and premature endpoints cannot be dropped or counted as fast successes. Gate against the agreed 1.5-second interpretation. |
| Resources | Peak/sustained RAM/VRAM, swap, thermal throttling, CPU/GPU use, startup-to-ready | Fit the declared supported device with agreed headroom under combined workload; no universal minimum inferred from artifact size. |
| Accessibility/TTS | Task completion, amount/name comprehension, clarification loops, keyboard/screen-reader access, interruption recovery | Every critical control/failure path works without sight; obtain representative-user acceptance before release. Naturalness alone is insufficient. |
| Privacy/offline | External network use after provisioning; retained audio/transcripts; session isolation | Workflow succeeds offline for local catalogue data; no unauthorized content retention or cross-session exposure in tests. |

For noncritical accuracy/relevance targets, the absence of user and catalogue evidence makes a specific numeric floor arbitrary. The actionable procedure is: collect pilot judgments → agree acceptable task completion/error costs → pre-register thresholds and any noninferiority margin → freeze the test set → evaluate → accept/reject. Do not choose a threshold after seeing which model wins. Use paired confidence intervals for differences and confidence bounds for rare failures; report denominators and correlated samples. This quality-threshold decision is a release gate, not a reason to stop the present report.

### 10.6 Prioritized experiments

| Experiment | Problem / hypothesis | Baseline → alternative | Dataset/conditions and metrics | Adoption gate, regressions and decision |
|---|---|---|---|---|
| **E01: Catalogue correctness and consistency** | Top-K, incomplete data and mismatched derived content can give unsupported answers. | Candidate sorting → ARCH-001/002 completeness gate, SQL oracle and atomic publication | Vary K, missing cheap-item attributes/records, boundaries, updates/deletes; pause staged embedding jobs, reject stale revisions, crash before/after publication, switch encoder generation during query encoding and update during multi-branch reads. | Exact complete-query agreement; unknowns block global/no-match claims; one snapshot/generation per result, no partially published ready set; snapshot-scoped minimum stated accurately. |
| **E02: NLU contract and model choice** | Bounded structured extraction may preserve quality with less generation; smaller current models might be adequate. | Prompt-only reference parsing → same 2507 checkpoint with schema; then Qwen3.5-2B/4B, Gemma E2B; optional LFM English | Same finalized text, schema, evidence and semantic validator; compare precision variants separately; repeated paired runs. Measure exact plan/critical fields, format failures, repair frequency, token counts, latency and memory. | Zero critical regression on challenge cases; choose a smaller model only when whole-task quality gates and E07 pass. Reject candidates needing frequent repair or hidden thinking latency. |
| **E03: ASR and endpointing** | Post-utterance work and early cutoffs may dominate speech latency/correctness. | whisper.cpp base/small variants with explicit turns → incremental/VAD policy; matching Moonshine or Qwen-ASR; faster-whisper on CUDA | Same recordings/device; control Whisper weights/decoding when comparing runtimes. Include pause-before-negation, amounts, accents, noise, silence and speaker echo. Measure WER, critical values, early cutoff, false turns and remaining ASR tail. | No new unintended actions/cutoffs on critical fixtures; choose profile by task accuracy and E07. Hindi needs its own evidence; no extrapolation from English. |
| **E04: Discovery retrieval and optional rerank** | Exact names and paraphrases need different evidence. Hybrid may improve recall/ranking. | Dense-only → FTS-only → fusion; then encoder alternatives and optional cross-encoder | Same ready revision, predicates and judged queries; names/SKUs/subjective/language strata plus quotes, hyphens, operator-looking text, empty/stop-word-only inputs and explicit lexical configurations. Depth 10/20/50 grid; Recall/Precision/nDCG, identity, no-match, latency and memory. | Promote only for measured paired benefit and E07 fit. Literal query content cannot become unintended FTS operators; reranking cannot repair absent candidates or change hard constraints. |
| **E05: TTS voice and playback** | Short factual prompts and rupee pronunciation need intelligibility and low first-audio delay. | Pinned OHF Piper + eligible English voice → eligible Kokoro/other approved-language voice | Same short/long templates, amounts, product/SKU names and failure prompts; warm/cold playback on actual device. Measure audible onset, synthesis time, memory, comprehension and user preference; inspect shipped terms. | All critical values understood and errors recoverable without sight; voice/artifact eligibility recorded. Do not promote on naturalness alone or assume a voice list proves Hinglish support. |
| **E06: Action/state fault injection** | Repeated finals, stale lists, cart changes and retries can duplicate/redirect actions or corrupt confirmations. | Naive dispatch → ARCH-005 command identity, write transaction and immutable receipt | Inject duplicate/conflicting commands, intentional repeat, existing-plus-added quantity overflow, later-add-before-replay, changed query minimum, stale lists, interleaved sessions, lock timeout, serialization failure, deadlock, unique-operation races, commit connection loss and cancel races. | No duplicate/wrong-session/quantity violations; replay verifies the original receipt after later valid adds. No blind replay into a new session or unsupported external exactly-once claim. |
| **E07: Combined latency feasibility** | Stage contention and survivor-only reporting can hide failed/slow turns. | Safe sequential reference → recommended routes/residency | Target device; route/language mix, cold/first-ready/warm/unload/concurrency, plus injected timeout/no-audio/premature-endpoint cases. Begin with 200 warm repetitions per primary profile; expand if P95 uncertainty is large. | Publish successful-latency distributions and all-turn outcome/deadline rates. Failed/missing/premature responses cannot improve pass rate. If target fails, diagnose and change only the justified factor or seek a target/profile decision. |
| **E08: Accessibility task study** | Voice-first behaviour cannot be validated through sighted developer inspection alone. | Minimal happy-path prototype → full nonvisual controls/status/fallback | Consented representative blind/low-vision users; keyboard/screen-reader and voice interaction; slow speech, stop/repeat, no matches, ambiguous amounts, TTS failure, no-audio recovery. Measure completion, misunderstanding, repeated clarification and user feedback. | No sight-dependent critical step; resolve task-blocking defects before release. Sample/recruitment plan agreed with users; no conformance claim from this review. |
| **E09: Deployment, offline and recovery** | Hidden downloads, model eviction, missing artifacts and index failures can defeat local reliability. | Unpinned defaults → pre-provisioned manifests/readiness/resource limits | Disable internet after provisioning; remove model/voice; exhaust worker; corrupt version/fingerprint; interrupt index rebuild; simulate lock contention/DB unavailable and audio-device failure. Inspect network activity, memory, recovery and redacted traces. | Safe, accessible failure; no false success/no-match; no cloud fallback; reproducible pinned rebuild and index rollback. All project data stays within documented retention/isolation policy. |
| **E10: Price-aware query relevance** | Text-only fusion ignores price; price-only sorting ignores fit; candidate unions may miss high composite-score items. | RRF-only and price-only baselines → qualified multi-feature ranking with low-price retrieval | Independently judged query/product preferences; equal-fit cheaper pairs, higher-price better-fit pairs, cheap accessories, explicit cheapest/target-price queries, unknown attributes and missed middle-price items. Compare union versus exhaustive model scoring on a complete small catalogue; test D14 inclusion/placement separately. | Hard requirements and relevance qualification always precede price. Both pairwise fixture types follow the accepted policy; qualified cheapest scope is truthful. Freeze weights/gates before held-out tests, measure human relevance/value and E07 latency, and disclose remaining model/ANN limits. |
| **E11: Storage architecture and filtered retrieval** | Consolidation reduces coordination, but speed/resource/lexical fit is unmeasured; filtered ANN may underfill. | PostgreSQL exact → PostgreSQL HNSW/iterative scans; compare SQLite FTS5 + Qdrant Server, and SQLite + in-process vectors (exact scan/client local mode or eligible Edge) for an embedded profile | Same real/synthetic catalogue sizes, BGE vectors, query/predicate selectivity, scorer, limits, hardware and warm/cold state. Separate lexical engine quality from vector storage. Compare recall at equal latency and latency at equal recall against exact metric/composite oracles; include updates, concurrent adds, all-turn E07 latency, resident/peak memory, disk/index-build cost, backup/restore and setup/recovery steps. For the split store test acknowledged-but-incomplete writes, stale payloads, missing new matches and crash reconciliation. | Keep PostgreSQL if correctness/relevance/E07/resource gates pass; enable ANN only after selective-filter recall tests. Reconsider Qdrant only for measured required benefit exceeding dual-store costs; choose embedded SQLite + exact vectors only for a confirmed no-daemon/device need and passing gates. No benchmark winner is claimed in this review. |

Run E01, a small E11 correctness/resource slice and a thin E03/E05/E07 voice slice early. They can invalidate the data or hardware assumptions before a large implementation investment. Run E02 with text first to separate interpretation failures from ASR errors, then repeat critical cases with real audio. Compare the final combined configuration again after any model, encoder or voice promotion.

### 10.7 Results record to create during implementation

| Field | Required future record |
|---|---|
| Configuration | Commit, model/voice hashes, runtime versions, settings, schema and catalogue snapshot |
| Workload | Route/language/speaker strata, cold/warm state, concurrency and sample counts |
| Timing | Median/P95/confidence intervals for all end-to-end metrics; stage and queue breakdown |
| Quality | Critical/action errors, NLU metrics, retrieval judgments, TTS comprehension and accessibility defects |
| Resources | Peak/sustained RAM/VRAM, swap/thermal behaviour, load/unload and startup costs |
| Decision | Pass/fail against pre-agreed gates, remaining uncertainty, chosen option and rollback configuration |
| Current status | **Not run. No VoiceCart benchmark result is available in this review.** |

## 11. Ordered implementation roadmap

This is future work requiring approval of material architectural decisions. **No code or configuration has been created as part of this review.** The module names below are suggested responsibilities; none exists in the inspected repository. They are not claims about an established file structure.

| Order / timing | Change IDs and work | Dependencies / proposed modules | Tests and acceptance | Main risk / rollback |
|---|---|---|---|---|
| **0. Before release choices** | Confirm device/OS, languages, catalogue source/size, local versus merchant cart, distribution terms and target interpretation | All changes; owner decisions D01–D06 | Record supported profile and experiment thresholds; obtain representative catalogue/audio access. Implementation experiments may proceed under explicit provisional assumptions. | Wrong profile invalidates results; keep decisions provisional until evidence. |
| **1. Immediate: contracts and catalogue slice** | ARCH-001/002/004: pinned PostgreSQL/pgvector setup, typed contracts, normalized variant fixture, parameterized structured repository | Proposed `domain`, `validation`, `catalogue`; no models required | E01 complete cheapest oracle, price operators, variants and unknowns; E11 initial exact-vector/resource fit and E09 restore setup | Taxonomy/data mismatch; fix authority contract before adding model complexity. |
| **2. Immediate: early voice feasibility slice** | ARCH-006/007/008: instrument capture/endpoint → local ASR → fixed verified response → TTS; add model extraction timing next | Proposed `audio`, `adapters/asr`, `adapters/tts`, `diagnostics`; approved test artifacts | Initial E03/E05/E07/E09; observable actual playback, offline readiness and nonvisual failure controls | Hardware or language failure discovered early; replace an adapter/test profile without disturbing catalogue logic. |
| **3. Immediate: schema NLU and runtime gate** | ARCH-004/008: pin reference, build constrained extraction and validator; evaluate small current challengers | Step 1 contracts and step 2 instrumented device; proposed `adapters/nlu`, model manifest | E02 text then audio, bounded repair, unsupported/negative intent rejection; choose a reproducible reference configuration | New model changes semantics/template; retain previous pinned configuration and fixture results. |
| **4. Immediate: retrieval and relevance/price ranking** | ARCH-002/003/009: serializer, BGE/pgvector exact search, safe PostgreSQL text search, atomic publication, low-price branch and versioned scorer/output roles | Step 1 catalogue and accepted D14 policy; proposed `ingestion`, `adapters/embedding`, `retrieval`, `ranking` | E01/E04/E10/E11 snapshot consistency, safe-query, candidate-coverage and relevance/price ablations; hydrate current authority | Stale omissions or poor value/fit weights; retain previous policy/generation and reconcile before serving. |
| **5. Immediate: minimal action/session slice** | ARCH-002/005: per-session state/list IDs, clarification loop, minimal cart rows and operation result transaction | Steps 1/3/4; proposed `workflow`, `session`, `cart` | E06 fault tests; correct add from direct request and ordinal reference; verified success wording | Duplicate or redirected add; disable mutation dispatch until invariant fixtures pass. Read-only search can remain usable. |
| **6. Before supported demo/release** | ARCH-006/007: integrate actual response templates, controls, cached failures and assistive status | Voice/action slices; proposed `responses`, `client`; release voice decision | E05/E08: all important paths usable without sight; exact amounts/variant identity understood | TTS/echo/accessibility failure; retain proven voice and half-duplex policy while repairing. |
| **7. Before latency/quality claims** | ARCH-008/009 plus combined configuration: run E01–E11, measure contention, tune only diagnosed bottlenecks | Integrated workflow, locked data/test sets and accepted placement/ranking policy | Report all quality/latency/resource gates; owner accepts profile or explicitly revises target if needed | Optimization hides semantic errors; reject a faster configuration failing correctness; restore previous manifest. |
| **8. Deferred optimization only on evidence** | Optional smaller model, multilingual encoder, reranker, pgvector ANN or a justified alternate store, direct llama.cpp/MLX/vLLM | Failed measurable metric and matching experiment from §10 | Paired improvement and combined-gate pass; new encoder generation/re-embedding when appropriate | Additional memory and migration cost; feature/configuration rollback with old artifacts retained. |

Do not defer basic accessible interaction until the last sprint as the original order could imply. The early slice tests the defining voice constraint while the deterministic catalogue slice establishes correctness. Later integration expands the same contracts; it does not begin with an unbounded conversational agent. Full cart editing/history, checkout, payment, order tracking and extensive admin/analytics work remain outside this roadmap.

## 12. Open questions and decision register

### 12.1 Decisions requiring information or experiments

| ID / question | Candidate options | Constraints and evidence already collected | Evidence or owner decision needed | Timing / consequence of delay |
|---|---|---|---|---|
| **D01: What is the supported device/OS?** | Available CPU-only machine; Apple Silicon; CUDA host | No hardware specification in repository; upstream runtimes support different acceleration paths | Exact host inventory and E03/E05/E07/E09 | Blocker for a latency/minimum-memory claim. Adapter/data work can proceed. |
| **D02: Which languages/scripts must work?** | English; Hindi; Hinglish/code switching; further languages | BGE baseline is English; current ASR/TTS language coverage differs | Target users and input/output profile; E02/E03/E04/E05 per language | Blocker for release model/voice choice. English is only a provisional comparison profile. |
| **D03: What catalogue and update source exist?** | Local fixture/import; external merchant; continuously updated catalogue | No dataset, taxonomy, update SLA or authoritative endpoint is present | Representative records, variant policy, category completeness, current price/stock owner and update frequency | Blocker for real global-minimum/freshness claims. Synthetic fixtures support initial tests. |
| **D04: What does “cart” mean for the initial product?** | Local session cart; existing merchant cart API | README requires minimum add operation; no backend is identified | Confirm intended authoritative destination and, if external, API/auth/idempotency/outcome lookup | Blocker for claiming a real merchant add. Local demonstration must be labelled accordingly. |
| **D05: What distribution/licence obligations are acceptable?** | Internal research prototype; GPL-compatible distribution; other deployment requiring another TTS choice | No project licence; current OHF engine GPL-3.0; voice/data terms differ | Owner distribution decision, artifact-specific notices/terms inspection; evaluate alternative voice/runtime if incompatible | Blocker before distributing chosen artifacts, not before this review or controlled eligibility checks. |
| **D06: Precisely how is 1.5 seconds judged?** | Literal first feedback; meaningful audio; verified outcome; universal bound versus declared percentile/profile | README gives the time window without workload/percentile | Accept §10.2 measurement definitions and target scope explicitly; E07 | Blocker for a “target achieved” claim. Do not weaken it through an unapproved interpretation. |
| **D07: How large/busy is deployment?** | One device/user; interleaved local sessions; shared remote service | No catalogue size, update rate or concurrency figures; database and model contention are unmeasured | Representative sizes/updates/users; E07/E09/E11 | PostgreSQL is the concrete reference; resource/capacity claims await these tests. |
| **D08: Which NLU artifact wins?** | 2507 reference; Qwen3.5-2B/4B; Gemma E2B; optional smaller English model | Current candidates verified through primary cards; no task measurements | E02 with fixed schema and E07 combined stack | Nonblocking for contracts; blocks an accuracy/performance endorsement of a release model. |
| **D09: Is BGE-small sufficient?** | Retain English model; E5-small; BGE-M3/Qwen encoder; optional translation experiment | Encoder contracts and migration consequences documented | Approved language profile and E04 catalogue relevance/latency results | Nonblocking for English reference. A multilingual release cannot assume success. |
| **D10: Is a neural reranker justified?** | No reranker reference; bounded cross-encoder after candidate qualification | No labelled evidence that order rather than recall/data is the bottleneck | E04/E10 candidate recall, human ranking judgments and E07 combined latency | Defer neural reranking until a measured need; keep hard constraints outside it. |
| **D11: Which interaction controls/voice do users accept?** | Accessible end/stop controls with half-duplex; later tested voice barge-in; eligible Piper/Kokoro voices | Failure/echo hazards and voice candidates identified; no user study | E05/E08 with representative users, device and languages | Blocker for accessibility/readiness claim; thin slice should run early. |
| **D12: What retention and session expiry are required?** | Ephemeral turns and expiring local session cart; separately consented diagnostics; future durable identity | README requires minimization/isolation but gives no durations or restart contract | Owner/user privacy policy, expiry semantics and E06/E09 | Default to no raw content retention for prototype; block retention/restart guarantees until specified. |
| **D13: What noncritical quality floors are acceptable?** | Pilot-derived task completion/relevance thresholds with pre-registered gates | No labelled dataset or user cost model yet; hard invariants and existing latency goal are known | Pilot, owner/user review, held-out sample-size/threshold plan before candidate selection | Nonblocking for evaluation harness; blocker for release acceptance. |
| **D14: How should the cheapest qualifying option appear?** | Relevance/price-ranked matches with a separately identified cheapest match (recommended); cheapest first; ranking only without mandatory cheapest inclusion | Owner requires query relevance with price as a factor and also states cheapest retrieval is required for every query. RRF-only does not satisfy price-aware ranking. | Clarification requested: inclusion versus first position. Version the accepted placement policy; E10 tunes the separate scoring weights and tests minimum scope. | Price-aware scoring and other corrections can proceed; do not claim the general-query presentation policy is owner-approved until clarified. Never silently interpret this as all queries being price-only. |
| **D15: Does the chosen store fit the deployment?** | PostgreSQL + pgvector reference; conditional SQLite + in-process vectors; dedicated Qdrant challenger | §4.4 independently favours one transactional store; no implementation migration or measured dedicated-vector advantage | E11 with approved device/scale, equal recall/quality and operational recovery; confirm whether a strict no-daemon requirement exists | Architecture decision is made, not waiting for a preference vote. Performance validation can overturn its fit; do not claim PostgreSQL automatically improves relevance or meets 1.5 seconds. |

### 12.2 Recommendation status

| Decision | Status after this review |
|---|---|
| Local inference/no paid inference APIs/current search-to-add scope | Preserved requirements. |
| Python, whisper.cpp, Ollama and English BGE reference | Recommended retention, subject to device/language tests. |
| ARCH-001/002/004/005 responsibility contracts | High-confidence proposals for owner approval; not implemented or automatically binding. |
| ARCH-002 PostgreSQL + pgvector | Recommended replacement for README Qdrant and the earlier SQLite + Qdrant proposal; one database boundary, exact vectors initially; E11 performance/resource validation remains open. |
| ARCH-003 hybrid discovery | Recommended measured addition; catalogue relevance benefit remains unmeasured. |
| ARCH-009 relevance and price | Required policy addition following owner direction; proposed scorer and qualified low-price role need E10. General-query cheapest placement remains the D14 clarification. |
| ARCH-006/008 audio/lifecycle/early validation | Recommended required responsibilities; exact thresholds depend on experiments. |
| ARCH-007 runtime/voice decision | Recommended explicit identity/eligibility gate; release voice remains open. |
| Smaller/newer model, multilingual encoder, reranker, ANN index, alternate runtime/store | Experiments or conditional future choices, not unconditionally adopted changes. |
| Comprehensive cart management, checkout, payments, order tracking | Deferred by the existing scope. |

### 12.3 Review completion record

- The repository and the complete README were inspected; pre-implementation status is verified for the recorded commit.
- Research covers every selected component, current credible challengers and complete-system alternatives, with direct sources, access dates and limitations.
- Nine actual proposed changes are recorded against the README target and the owner's added relevance/price requirement, each with rationale, research, risks, dependencies, validation, priority and confidence.
- The complete recommended architecture, interfaces, authority boundaries, application flow, deployment assumptions and recovery paths are specified.
- Experiments, metrics, acceptance procedures, a future implementation order and unresolved release decisions are documented.
- No VoiceCart benchmark or implemented behaviour is claimed. All future modules and configurations are proposals.
- The previous revision ran isolated in-memory SQLite probes for its former design; those are not PostgreSQL validation. This revision checks document structure, contracts, examples and consistency only. No PostgreSQL/pgvector service, concurrency test or database benchmark was run; E01/E06/E09/E11 remain implementation work.
- The deliverable is `Suggestions.md`; README and other project files are outside the review's edit scope.
