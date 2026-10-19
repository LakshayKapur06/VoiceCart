# VoiceCart architecture review

Review date: **19 October 2026**. Repository: [LakshayKapur06/VoiceCart](https://github.com/LakshayKapur06/VoiceCart). Reviewed commit: **f41fca7283b10bc7f0bac1c09c335373afd45f37** (`README`).

**Status: recommendations for owner review, before implementation.** This document is the sole deliverable. None of the proposed architecture, experiments, model configurations, or roadmap steps has been implemented or benchmarked during this review.

## 1. Executive summary

**Retain the local, modular Python architecture, but change how retrieval, audio turns, and authoritative state are specified before coding starts.** The repository contains only its README. It provides sound responsibility boundaries, but it does not yet establish a complete executable design.

The most consequential findings are:

1. **Sorting vector candidates cannot guarantee the cheapest matching product in the catalogue.** README §6.3 retrieves candidates and then sorts them. A qualifying cheaper variant can fall outside the retrieved top K. For a fully structured request, compute the answer across the complete eligible catalogue using SQL. For a subjective request, state the narrower search scope and clarify before making an unsupported global claim. This is a logical correctness finding, independent of the embedding model.
2. **Choose a small authoritative catalogue store now.** Recommend SQLite for the initial single-host prototype, with product variants, integer monetary values, a category/attribute vocabulary, and FTS5. Keep Qdrant as a derived semantic index. Specify update, deletion, version, and recovery rules. SQLite is a recommendation under an explicit deployment assumption, not an observed repository dependency. See [SQLite deployment guidance](https://www.sqlite.org/whentouse.html).
3. **Use three retrieval routes:** exact identifier/reference resolution; complete structured filtering and sorting; and semantic discovery combining lexical and dense candidates. A reranker is a deferred experiment. It cannot repair candidates that were never retrieved or override hard constraints. FTS5 and Qdrant provide the needed retrieval building blocks. See [FTS5](https://www.sqlite.org/fts5.html), [Qdrant filtering](https://qdrant.tech/documentation/search/filtering/), and [hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/).
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
| Semantic retrieval | Local Qdrant with payload filtering | Retain; add route selection and lexical retrieval. |
| Business logic | Python, schema validation, deterministic constraints, controlled actions | Retain; specify interfaces and state transitions. |
| TTS | Piper direction; exact runtime/voice/licence open | Resolve upstream identity and voice eligibility; benchmark alternatives. |
| Catalogue/cart | Authoritative structured data outside LLM; technology open | Recommend SQLite catalogue and minimal session-lifetime cart state. |
| Responses | Templates for simple confirmations; grounded LLM assistance only when useful | Retain. An unconditional second LLM call is already excluded. |

The baseline conceptual sequence is audio → transcription → extraction → validation → embeddings/Qdrant → deterministic filtering or optional comparison → controlled add → verified response → TTS. It exists in documentation only.

### 2.3 Assumptions and unresolved requirements

For a concrete reference design, assume **one host, one interactive user initially, a locally managed catalogue, INR price examples, and English as the first evaluation profile**. These assumptions are provisional, not owner-approved requirements. Neither this chat's language nor the README's currency examples establish that Hindi/Hinglish is mandatory or that English-only is acceptable for release.

Before a supported release, identify hardware/OS, input and output languages, catalogue size and update source, concurrency, and whether the cart is a local demonstration or must call an existing commerce system. A local cart proves only a local cart operation. It cannot claim to modify a merchant's cart without an authoritative merchant integration.

The design gaps are: global selection semantics; money/budget operators; variant completeness; catalogue/index consistency; exact model identity; bounded extraction; audio endpointing and cancellation; result-list reference lifetime; minimal duplicate handling; TTS failure accessibility; and a reproducible device-specific performance gate. README already requires validation, safe actions, session isolation, and templates. Those principles are retained rather than counted as newly invented changes.

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
| R21: Can Qdrant filter candidates? | [Filtering](https://qdrant.tech/documentation/search/filtering/), [indexing](https://qdrant.tech/documentation/manage-data/indexing/) | Official database docs | Rolling; 2026-10-19 | Payload conditions and indexes support structured restrictions during retrieval. | Reduce invalid candidates. | Correctness still depends on payload freshness and candidate coverage. | Retain Qdrant; validate against authority. |
| R22: How should lexical/dense rankings combine? | [Qdrant hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/) | Official retrieval docs | Rolling; 2026-10-19 | Rank fusion and staged queries are supported. | Supports combining different retrieval signals. | This proposal fuses SQL FTS and Qdrant lists in Python; Qdrant cannot directly fuse an external SQL result without application integration. | Add lightweight application-side rank fusion. |
| R23: What local authoritative store fits? | [SQLite uses](https://www.sqlite.org/whentouse.html), [transactions](https://www.sqlite.org/lang_transaction.html) | Official database docs | Rolling; 2026-10-19 | Embedded local storage and transactional access; concurrent writes have limits. | Fits proposed single-host catalogue and minimal local operations. | No evidence yet about write contention or external inventory integration. | Choose for prototype; reconsider for shared multi-host writes. |
| R24: Is a lexical engine needed as another service? | [SQLite FTS5](https://www.sqlite.org/fts5.html) | Official extension docs | Rolling; 2026-10-19 | Full-text matching and BM25 ranking are available inside SQLite; lower bm25 values rank better. | Adds product-name/brand term retrieval without another daemon. | FTS is not exact SKU equality or automatically typo/multilingual aware. | Add FTS5 plus separate exact identifier lookup. |
| R25: Could storage be consolidated? | [pgvector](https://github.com/pgvector/pgvector) | Official extension docs | Rolling; 2026-10-19 | Exact/approximate vector search in PostgreSQL; filtered ANN requires care. | Strong alternative if PostgreSQL is already required. | Adds a database server for a single-device prototype; query tuning still needed. | Defer; consider for a real shared commerce backend. |
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
| R35: What about weights, host language and embedded libraries? | [Whisper](https://github.com/openai/whisper), [Python licence](https://docs.python.org/3/license.html), [SQLite copyright](https://www.sqlite.org/copyright.html), [FastEmbed licence](https://github.com/qdrant/fastembed/blob/main/LICENSE), [ONNX Runtime licence](https://github.com/microsoft/onnxruntime/blob/main/LICENSE) | Official repository/licence texts | Rolling; 2026-10-19 | Whisper code/weights declare MIT; Python PSF-2.0 with incorporated-software terms; SQLite public domain; FastEmbed Apache-2.0; ONNX Runtime MIT. | Completes the reference-stack inventory beyond serving daemons. | Downloaded builds, conversions, models and dependencies must match the inspected declarations. | Record shipped artifacts separately from top-level package names. |

### 3.4 Interpretation limits

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

Changing the embedding model, even to another 384-dimensional model, requires a new collection/generation and re-embedding. No mixed-vector collection is valid merely because shapes match. Cross-language claims need cross-language query/product judgments; an English benchmark cannot settle them.

### 4.4 Retrieval, storage, and selection

**Recommendation: retain Qdrant for semantic discovery, add SQLite authority/FTS5, and route by query semantics. Confidence: high for the correctness boundary, medium for this storage combination.**

The counterexample to README §6.3 is simple: ten highly similar black backpacks cost ₹1,200–₹1,900, while a poorly described qualifying variant costs ₹900. A top-ten semantic search can exclude the ₹900 item. Sorting the ten retrieved variants gives a locally cheapest result, not a catalogue-wide minimum. Increasing K reduces this risk but proves nothing unless retrieval is exhaustive over the eligible set.

For a canonical category, colour and price request, use authoritative structured filtering and `ORDER BY price_minor, variant_id`. Use strict `<` for “under”; use `<=` for “at most.” If a category is ambiguous or the request includes subjective predicates that cannot be evaluated exhaustively, clarify or explicitly limit the claim to the candidates found. Deterministic code owns this distinction.

For discovery, union dense and lexical candidates, deduplicate variant IDs, validate current structured records, and fuse ranks. Use exact SKU/brand/model identity lookups as a distinct path. An FTS tokenizer is not a product-ID parser. Avoid introducing Elasticsearch, a separate sparse model, and a cross-encoder simultaneously before measuring the simpler hybrid. Qdrant's filtered search remains useful, but payloads cannot become the price authority. [Filtering](https://qdrant.tech/documentation/search/filtering/), [FTS5](https://www.sqlite.org/fts5.html), [fusion](https://qdrant.tech/documentation/search/hybrid-queries/).

| Storage/retrieval alternative | What it offers | What it sacrifices | Verdict |
|---|---|---|---|
| SQLite + in-process exact dense scan | Fewer daemons and simpler index deployment for a small catalogue | App-owned vector persistence/search and uncertain growth/latency fit | Serious simplification experiment once N and memory are known. Retain Qdrant until measured unnecessary. |
| PostgreSQL + pgvector + text search | One shared transactional system with SQL and vectors | Server administration and more tuning for a device prototype | Prefer if a real backend already uses PostgreSQL or shared writers justify it. [pgvector](https://github.com/pgvector/pgvector). |
| Qdrant-only authority | Fewer stores | Requires separately establishing transactional cart semantics and complete catalogue-query guarantees | Reject for this reference design; semantic index and commerce truth have different lifecycles. |
| SQLite structured/lexical search only | Small footprint and complete structured answers | Gives up requested semantic discovery unless supplemented | Useful ablation/fallback, insufficient as the full final recommendation. |

Defer reranking until labelled discovery cases show adequate candidate recall but poor order. Compare no reranker against a small cross-encoder on a bounded candidate set; keep hard constraints outside it. A passage reranker's reported score is not proof of product relevance. [Candidate card](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2).

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
| B. Recommended modular hybrid | Local ASR + endpointing; one schema NLU; SQLite exact/structured routes; FTS+BGE/Qdrant discovery; deterministic add; resident Piper | Complete structured answers, bounded inference, usable failures | Two catalogue representations and a sync contract | New typed adapters/schema; no existing migration | Recommended reference; E01–E09 validate the combination. |
| C. Low-resource streaming local | Moonshine for a matching language; smaller NLU; SQLite plus exact dense scan; compact local TTS | Smaller footprint and shorter post-speech work | Language/accuracy trade-offs; dense-scan scaling; different adapters | Replace tested models/index implementation behind interfaces | Conditional if device profiling shows B too heavy and task-quality gates pass. |
| D. Multilingual accelerated local | Whisper or Qwen3-ASR; Qwen3.5 challenger; E5/M3; SQL+Qdrant hybrid; eligible multilingual TTS | Hindi/Hinglish/cross-language retrieval | More test data, resident memory, language-specific voices and licence checks | Re-embed catalogue, change model contracts, expand voice fixtures | Required comparison if multilingual is confirmed; current English reference cannot claim this support. |
| E. Shared local server | Approved ASR clients; GPU model server; PostgreSQL+pgvector/text search; controlled cart backend | Shared catalogue, concurrency, existing commerce integration | Network boundary/authentication, queueing, service operations | Significant new deployment and storage integration | Defer until shared users/backend are requirements; test capacity at batch 1 as well as concurrent load. |
| F. Native audio-to-intent model | Audio-capable local model emits a typed interpretation; separate retrieval/action/TTS remains | Possibly remove a distinct ASR step | Harder transcript/provenance debugging, new grammar/runtime path, unmeasured critical-word errors | New adapter and audit/evaluation design | Exploratory only; no evidence supports replacing independent ASR now. |

All recommended paths preserve local inference, retrieval before product-grounded generation, application-owned state and the current search/add scope. Cloud inference is excluded by the current constraints, not treated as a fallback. No complete-system option has been measured here.

## 5. Change-only diff against the README target

These eight entries contain actual proposed additions or refinements to the target design. Retaining Python, whisper.cpp, Qdrant, BGE-small for English, application validation and optional response generation is not counted as a change. “Migration” below concerns future artifacts: there is no implemented system to migrate now.

### Change ID: ARCH-001 — Route complete structured selection separately

- **Component or layer:** Retrieval coordinator and selection policy.
- **Current baseline:** README §§6.3, 7.3 and 8 retrieve semantic candidates and deterministically select the cheapest valid candidate; complete-catalogue optimality is unspecified.
- **Proposed change:** Introduce exact/reference, exhaustive structured, and semantic-discovery routes. Resolve a fully structured cheapest query with a complete authoritative SQL predicate and stable price ordering. Return an explicit selection scope. Clarify subjective/unmapped eligibility instead of claiming a global minimum from top K.
- **Reason for change:** ANN/dense relevance ranking can omit the cheapest eligible variant even if every returned candidate passes constraints.
- **Supporting research:** The counterexample in §4.4 is a logical proof of this gap. [Qdrant filtering](https://qdrant.tech/documentation/search/filtering/) supports restrictions, while [SQLite query use](https://www.sqlite.org/whentouse.html) supports structured filtering/ordering; neither source claims semantic top K proves a price minimum.
- **Expected benefits:** Correct global cheapest answers for expressible structured requests; less unnecessary embedding work on that route.
- **Trade-offs and risks:** Requires complete, normalized eligible-product data. Category mistakes or missing records still invalidate catalogue-wide claims.
- **Dependencies and migration implications:** ARCH-002 catalogue schema, typed query plan, tests comparing against a complete oracle. No existing index migration.
- **Validation required:** E01 adversarial top-K fixture, boundary prices, variant ties, missing attributes and full eligible-set comparison.
- **Priority:** High; directly affects a representative required action.
- **Confidence:** High for the gap and route separation; medium for taxonomy coverage until real data exists.

### Change ID: ARCH-002 — Specify catalogue authority and derived-index lifecycle

- **Component or layer:** Data model, ingestion and storage.
- **Current baseline:** README §§5.1 and 12 leave authoritative storage, persistence and update interfaces open; §7.4 requires freshness without an update protocol.
- **Proposed change:** Use SQLite for the initial local authoritative catalogue and minimal session-scoped cart/operation records. Define purchasable variants, canonical attributes, currency plus integer minor-unit prices, and record/catalogue revisions. Treat FTS and Qdrant as derived indexes with explicit ready/pending/deleted state, reconciliation and versioned rebuilds.
- **Reason for change:** A working action boundary needs a concrete source for current product eligibility and operation results. Asynchronous index updates otherwise create unexplained omissions or stale facts.
- **Supporting research:** [SQLite deployment](https://www.sqlite.org/whentouse.html), [transactions](https://www.sqlite.org/lang_transaction.html), [Qdrant payload indexing](https://qdrant.tech/documentation/manage-data/indexing/). Store selection is an inference under the single-host assumption.
- **Expected benefits:** Reproducible catalogue truth, atomic local add verification and recoverable derived indexes.
- **Trade-offs and risks:** Duplicate representations, synchronization work and SQLite write contention. Session-scoped records require expiry/cleanup; this does not specify a full durable cart product.
- **Dependencies and migration implications:** Data-source contract and variant IDs first. Changing encoder requires a new generation/re-embedding; changing storage later needs repository adapters and data export.
- **Validation required:** E01 insert/update/delete and crash-window tests; E06 transaction tests; E09 rebuild/reconciliation tests.
- **Priority:** High; blocks correct integration.
- **Confidence:** High for authority/versioning; medium for SQLite pending deployment evidence.

### Change ID: ARCH-003 — Add lexical candidates to semantic discovery

- **Component or layer:** Product discovery retrieval.
- **Current baseline:** README §7 uses BGE/Qdrant dense candidate generation; no lexical ranking path is selected.
- **Proposed change:** Add SQLite FTS5 title/brand/model/description retrieval and exact identifier lookup. Fuse validated lexical and dense ranks in Python for discovery. Keep exhaustive structured selection separate; defer a neural reranker behind an experiment gate.
- **Reason for change:** Dense similarity is not sufficient evidence of exact SKU/model identity, and lexical-only matching can miss paraphrases. Combining these signals is a targeted addition without another search service.
- **Supporting research:** [FTS5](https://www.sqlite.org/fts5.html), [rank fusion](https://qdrant.tech/documentation/search/hybrid-queries/) and the product relevance categories in [ESCI](https://github.com/amazon-science/esci-data).
- **Expected benefits:** Hypothesis: better discovery coverage for exact names and descriptive queries with a modest extra retrieval cost.
- **Trade-offs and risks:** More candidate/rank logic; tokenizer and fusion settings can hurt some queries; similarity is still not identity.
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
- **Proposed change:** Define a finite state machine and immutable turn/result-list IDs, per-session serialization, a validated pending action, and session-lifetime operation deduplication. Check/recompute authoritative eligibility at the mutation boundary and verify the stored result. Clarify a changed previously announced offer.
- **Reason for change:** Repeated ASR finals, late callbacks and timeout retries can duplicate an add or resolve “second” against the wrong results in an otherwise small prototype.
- **Supporting research:** README current action/session requirements; [SQLite transaction semantics](https://www.sqlite.org/lang_transaction.html) and [Python cancellation semantics](https://docs.python.org/3/library/asyncio-task.html). The proposed protocol is engineering design.
- **Expected benefits:** Controlled local action ordering and accurate known/unknown outcomes without a distributed transaction platform.
- **Trade-offs and risks:** More explicit state and cancellation rules. Guarantee ends at the documented session lifetime; external systems need their own idempotency contract.
- **Dependencies and migration implications:** ARCH-002 minimal tables and ARCH-004 typed intent; TTS consumes verified outcome events only.
- **Validation required:** E06 duplicates, conflicting operation payloads, new intentional adds, stale references, interleaved sessions and cancel/commit races.
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
- **Validation required:** E07 cold/warm/full-pipeline latency and E09 offline/resource/failure tests. Publish misses as well as successes.
- **Priority:** High; feasibility depends on the supported profile.
- **Confidence:** High for measuring early; low for meeting 1.5 seconds before experiments.

## 6. Reasons behind the combined diff

ARCH-001 and ARCH-002 solve different parts of the cheapest-selection problem. Exhaustive sorting over incomplete or wrongly normalized data is still wrong. Conversely, a well-structured store does not help if the application only sorts ANN candidates. Together they define an eligible set, an ordering and an authoritative snapshot for the claim being made.

ARCH-003 improves discovery coverage without forcing every query into another model call. Its lexical branch should not influence a complete structured minimum: relevance scores cannot override “cheapest.” A neural reranker is rejected as a default because it adds latency before evidence that ranking, rather than recall or data normalization, is the problem. A complete Qdrant replacement is likewise premature without catalogue size or comparative measurements.

ARCH-004 and ARCH-005 connect language understanding to controlled action. Grammar-constrained JSON is useful but insufficient: the system still needs to prove which turn requested an add, which list “second” names and whether the action already happened. A generic autonomous agent is a poor fit for a fixed search/clarify/add workflow because it expands the number of execution paths and tool decisions that must be verified.

ARCH-006 makes the intent boundary meaningful for actual speech. A correct validator operating on a truncated or self-echoed transcript can execute the wrong human request. Half-duplex audio is a deliberate initial simplicity trade-off; a discoverable stop control is therefore required. Free-form voice interruption should be introduced only when the microphone does not turn the assistant's own confirmation into a new command.

ARCH-007 is a concrete completion of the README's open TTS decision, not a claim that Piper should always win. A high-quality voice with unsuitable terms is not a release choice, and a legally eligible voice that users cannot understand also fails. Kokoro and language-specific alternatives remain valuable experiments rather than predetermined replacements.

ARCH-008 tests the combined cost of these choices. Measuring an LLM alone cannot show whether ASR, embedding inference and TTS still fit in memory together. Warming every model indiscriminately can increase contention. First measure one supported profile; then tune residency, precision or model size against quality gates. The combined design therefore favours correctness and evidence before optional optimization.

The high-confidence proposal is the responsibility structure. SQLite, exact ASR checkpoints, voice choice, candidate counts and model precision remain revisable through the documented gates. No claim of measured superiority over the baseline is made.

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
| SQLite catalogue repository | Parameterized structured query → current product variants/snapshot | Product IDs, current attributes, price, stock, catalogue revision | Authority for prototype data. External merchant adapter is a separate integration decision. |
| SQLite FTS5 | Safe lexical query + filters → ranked variant IDs | Derived term index | Covers names/brand/model terms without another daemon. |
| BGE-small-en-v1.5 via FastEmbed | Semantic query/document → normalized vector | Encoder/tokenizer/serializer version | Retained for provisional English profile; language gate unresolved. |
| Local single-node Qdrant | Vector + allowed payload filters → candidate IDs/scores | Derived semantic retrieval | Retained; one named 384-dimensional cosine vector for the BGE reference. |
| Python merge/selector | Current candidates + SearchPlan → Selection with scope/evidence | Deduplication, rank fusion, hard constraints, deterministic selection | Computes global structured minima or scoped discovery choices. No default reranker. |
| Session state machine | Turn/result/action events → next state/pending clarification | References, one active mutation per session, result-list order, operation identity | Prevents stale callbacks and cross-session leakage. |
| Minimal cart repository in SQLite | Validated operation + current catalogue predicate → stored outcome | Session-scoped cart rows and operation results | Atomic local mutation and readback; no checkout, reservations, order or payment authority. |
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
    P -- exact or structured --> D[(SQLite authoritative catalogue)]
    P -- semantic discovery --> L[SQLite FTS5 lexical candidates]
    P -- semantic discovery --> E[BGE local query embedding]
    E --> Q[(Local Qdrant derived index)]
    L --> M[Merge ranks and hydrate current records]
    Q --> M
    D --> M
    M --> F[Hard constraints and scoped deterministic selection]
    F --> X{Explicit valid add intent?}
    X -- no --> R
    X -- yes --> T[Session lock and SQLite local add transaction]
    D --> T
    T --> O[Stored outcome and readback verification]
    O --> R
    R --> B[Playback: resident Piper or cached error speech]
    R --> AT[Assistive-technology status]
    B --> U
    AT --> U
    I[Local catalogue ingestion and reconciliation] --> D
    I --> L
    I --> E2[BGE document embeddings]
    E2 --> Q
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
| SearchPlan | Canonical IDs, hard predicates, soft preferences, sort, quantity, currency, route, claim scope, query text | Construct SQL/filter objects in code; model never supplies SQL or executable filters. |
| Candidate/Selection | Variant ID, current row revision, retrieval provenance, validated fields, result-list ID and selection scope | Rehydrate; scores are ranking signals, not probability or price truth. |
| AddCommand | Server-owned operation_id, session/turn IDs, variant/quantity, expected observed revision/offer, predicates and scope | Validate session ownership, deduplicate, recheck before committing. |
| AddOutcome | Operation status, stored variant/quantity/result, version, authoritative error/reason | Report success only after stored outcome/readback; unknown outcome is not failure or success. |
| ResponseEvent | State/outcome code, bounded text, language, turn ID, replayable response ID | TTS renders it; stop/repeat cannot replay business operations. |

These schemas are proposed interfaces, not source files. Keep the same contracts behind alternative ASR, encoder, runtime, store and TTS implementations.

### 7.4 Deployment boundary

Use a local application process with blocking inference workers, an Ollama process and a local Qdrant node; the SQLite database stays on the same host. Piper may run in a resident worker, chosen for crash/resource isolation rather than a claimed licensing exemption. No network-accessible model ports are needed for the reference profile.

Pre-download models and voice artifacts during setup, record hashes and test with external network access disabled. Startup checks include device access, model readiness, schema/encoder compatibility, index freshness and a playable local error prompt. The app should communicate “ready” only when its supported workflow is available. Native Apple acceleration should run through a verified host build rather than assuming a container supplies the same acceleration path. Multi-host and remote-user deployment remain outside this reference profile.

## 8. Detailed application flow

Example request: **“Find the cheapest black backpack under ₹2,000 and add it to my cart.”** The following flow assumes an approved English/INR profile, a complete local catalogue category mapping and a valid session. No example product or price is claimed to exist in this repository.

1. **Start a listening turn.** The client creates a turn through the application, receives a turn ID, announces listening state, captures audio, and records the microphone clock. Previous playback is stopped or capture is gated according to the half-duplex policy.
2. **Detect the endpoint.** VAD tracks speech/silence; the user may explicitly end the turn. Allow pauses without treating an incomplete command as final. Record physical speech-end reference and endpoint-detection time separately. Silence/no-speech produces a concise retry prompt and no search/add.
3. **Finalize transcription.** whisper.cpp returns final text bound to this turn. Provisional text cannot authorize a mutation. If the final text is empty, truncated, unsupported-language or otherwise suspect, ask the user to repeat relevant information. Evaluate critical-word errors through E03; do not treat a high ASR diagnostic as proof.
4. **Interpret the request.** Since this is a general shopping sentence, call the schema-constrained Qwen extractor once. It proposes category backpack, colour black, price operator `<`, amount 2000 INR, sort price ascending, quantity one and explicit add intent. It supplies text evidence rather than an invented product ID.
5. **Validate and normalize.** Python validates the schema and allowed intent, resolves the category/colour vocabulary, verifies add intent/negation evidence and parses the amount independently into **200000 paise with an exclusive bound**. If “under,” “at most,” quantity or currency is unclear, ask a targeted clarification before mutation. An ASR error already present in final text may escape these checks; this is why audio-level evaluation and clarification policy are necessary.
6. **Select the query route.** All eligibility predicates here are structured, and cheapest is an objective sort. Choose complete structured retrieval. Skip query embedding, Qdrant, lexical fusion, reranking and product-comparison generation. This preserves retrieval before product-grounded response generation: the evidence is retrieved through SQL.
7. **Retrieve the complete eligible-set minimum.** The catalogue repository executes a parameterized query over active purchasable variants: mapped backpack category, canonical black, INR, nonmissing price below 200000, required quantity available, and other explicit mandatory attributes. Apply stable ordering by price then variant ID. Unknown required attributes do not match. The complete predicate, not an ANN shortlist, defines eligibility.
8. **Handle no match or ambiguous eligibility.** If nothing qualifies, state that no available matching backpack was found under the budget. Offer to change one constraint only through a new user response. If “black” is mixed-colour/unknown or category mapping is disputed, ask. Do not silently substitute navy, exceed budget or remove the colour predicate.
9. **Resolve selection and variants.** Produce a validated variant ID and selection scope `complete_structured_catalogue`. If a mandatory size/variant remains unresolved, ask for it. For equal-price interchangeable candidates, use a documented stable tie rule; if the tie changes an important unrequested choice, ask instead of hiding it.
10. **Use the existing explicit add authorization.** The initial sentence already requests add-to-cart. Do not require a redundant confirmation for every valid add. Confirm only unresolved interpretation, a materially changed previously announced offer, or another action-affecting ambiguity. The model does not decide whether an action is permitted.
11. **Execute under application control.** Acquire the session mutation lock. The application, not the model, creates or retrieves the operation ID for this turn. In a short SQLite transaction, check for an existing operation result. For this direct structured request, rerun the eligibility/minimum query in the mutation snapshot if the catalogue has changed, then validate the final choice. Store the minimal cart update and operation outcome atomically. The original predicate authorizes the recomputed cheapest match; an explicitly referenced/announced different item must not be silently replaced.
12. **Verify the result.** Read the stored operation/cart row and verify variant and quantity. Record which catalogue revision supported the selection. Adding to a cart does not reserve or decrement stock in this scope. Availability is valid at the check; no checkout availability guarantee is implied.
13. **Construct the response.** Use a template populated from the verified outcome, such as “Added one [name], black, for [spoken price] to your cart.” Include size if relevant and only claim cheapest within the recorded scope. Missing or unknown outcome produces an accurate pending/error response, never an “added” guess. No second LLM call is needed.
14. **Synthesize and play.** Normalize the actual amount into speakable rupees/paise and pass the complete verified phrase to the resident Piper worker. Start playback from available PCM chunks; measure actual audible onset. Match all chunks to the active response/turn so cancelled old speech cannot resume later.
15. **Retain minimal follow-up state.** Store the response for repeat, ordered result-list mapping when one was announced, pending clarification if any, and operation result for retry deduplication. Discard turn audio by default. Session expiry invalidates ordinal references and clears session-scoped state according to the retention policy.
16. **Recover truthfully.** A timeout before commit can be retried with the same operation ID. A timeout with uncertain commit status requires operation lookup before retry. If TTS fails after a successful add, retain that successful outcome and replay only its confirmation through fallback; do not repeat the add. If the catalogue or index is unavailable, distinguish an unavailable search from a genuine no-match result.

For **“find a good backpack for college”**, route through dense plus lexical discovery, hydrate/filter current records, and present a small spoken list. Subjective “good” cannot become a global minimum claim. Ask preferences where they change the action. A second LLM call is justified only for a comparison the user needs and for which retrieved facts exist; use bounded evidence, validate returned IDs and render factual attributes through templates.

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
| Catalogue/index status | monotonically changing catalogue revision, per-variant text/content hash, encoder/serializer fingerprint, index revision and ready/pending/deleted state |
| Session/results | session_id, expiry, turn counter, last fully announced result-list ID, ordered variant references and observed revisions, pending clarification/selection |
| Minimal cart/operation | session_id, variant_id, quantity; unique operation_id with session/turn binding, command fingerprint, outcome and resulting quantity |

Use integer minor units for money, explicit currency, nonnegative prices and positive integer quantities. Reject missing prices/currencies or unknown required attributes. Do not convert currencies silently. “Under ₹2,000” means `< 200000`; “₹2,000 or less” means `<= 200000`. Explain the interpretation when unclear. Prices and stock come from the authoritative structured record, never from generated descriptions or vector scores.

Represent each purchasable variant separately. A black parent product with an unavailable black variant must not be offered using another colour's price/stock. If an attribute is multi-valued, define whether the user permits it; do not interpret the presence of “black” somewhere in an array as an unqualified solid-black match.

The reference catalogue is local application truth. If a real merchant system is required, define which API owns current price/stock and cart outcomes; re-check through that API at action time. SQLite cannot create freshness guarantees for an external inventory source whose update contract is unknown.

### 9.4 Ingestion, indexes and freshness

Validate a local import against the schema, normalize variants/attributes and assign stable IDs. Update the authoritative rows and FTS content in one SQLite transaction. Record pending semantic-index work in the same store. A small local reconciliation task can read pending rows, serialize stable text, embed it, upsert/delete in Qdrant and mark the indexed revision only after an acknowledged update. No separate message broker is needed.

Make the update process repeatable by variant ID and revision. Handle crashes after authority commit but before index update, after index acknowledgement but before status update, and during deletion. Tombstone deleted variants in authority immediately; hydration must suppress them even if Qdrant still returns their IDs.

Revalidation prevents stale candidates from being added, but **does not recover new relevant items omitted by an out-of-date index**. For a small prototype, serve semantic search only on a reconciled catalogue snapshot, or merge pending changed variants using a bounded exhaustive fallback. If neither is feasible, label semantic search unavailable/updating instead of saying there are no matches. Structured/exact SQL search can remain available. This is the proposed consistency policy; its update latency must be measured.

Create a new collection generation when encoder, serializer, pooling or tokenizer behaviour changes. Build, reconcile, evaluate and switch the configured collection reference after readiness checks; retain the prior generation for rollback. Schema/version mismatch should fail readiness rather than produce mixed-vector results. Indexing price/stock-only updates should not require re-embedding if semantic text is unchanged.

### 9.5 Encoder and Qdrant collection

For the retained BGE reference, create one vector per purchasable variant using a stable text order: name, brand, category, colour/size and useful descriptive attributes. Keep important distinguishing fields before truncation; validate document length with the actual tokenizer. Avoid volatile stock/prices in embedding text; use structured fields for those constraints.

Use the documented 384-dimensional BGE output, normalized consistently, with cosine search. Query instructions apply according to the encoder's contract; test prefixed versus unprefixed short queries on development data rather than assuming one improves this catalogue. Pin the selected behaviour. [BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5).

Qdrant payload: variant_id, product_id, category_id, canonical colour/size fields, currency, price_minor, available flag, source_revision, text hash and encoder generation. Create payload indexes on fields actually used in filters. Ensure payload types match query values. Qdrant point IDs must be supported numeric/UUID identifiers; map an arbitrary SKU through a stable application mapping and keep its original form in the payload. Hydrate every selected result from authority. [Indexing docs](https://qdrant.tech/documentation/manage-data/indexing/).

A multilingual encoder swap changes this contract. E5's query:/passage: preprocessing and a same-sized vector do not preserve BGE semantics. Other encoders need their own dimension, pooling and instruction settings. Never combine vectors from different encoders in one unnamed space.

### 9.6 Query construction, fusion and ranking

The planner emits a finite set of parameterized query templates. No model-generated SQL, arbitrary database field names, executable code or direct cart tool calls are accepted. Exact IDs use equality; category/colour/budget constraints use canonical types and explicit operators. A filter on a mandatory missing attribute must fail eligibility.

For semantic discovery, run FTS and dense retrieval under the same snapshot/predicate policy where possible, merge IDs, hydrate current records, remove invalid variants and fuse the surviving rankings. Use an explicit application formula such as `sum(1 / (c + rank))` with a documented one-based rank convention. Choose c and candidate counts on development data. This is an application proposal, not a statement of Qdrant's default rank convention. Do not directly add cosine and FTS5 BM25 values; their scales/directions differ. [FTS5 ranking](https://www.sqlite.org/fts5.html), [fusion mechanisms](https://qdrant.tech/documentation/search/hybrid-queries/).

Start E04 with candidate depths 10, 20 and 50 as experimental comparison points, not production defaults. If hydration removes many candidates, bounded overfetch or fresh-index reconciliation may be needed. Do not silently return an empty valid set as proof that the catalogue has no match. Stable exact identifiers outrank fuzzy similarities only when identity was explicitly and correctly resolved.

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

For local adds, keep transactions short: acquire session serialization, begin the catalogue/cart transaction, check operation identity/fingerprint, validate authority, apply cart increment, store operation outcome and commit. No LLM, ASR, embedding or TTS work occurs inside the transaction. Repeated operation IDs return the stored outcome; a different payload using the same ID is rejected. A new deliberate add gets a new ID. The cart quantity is not a stock reservation, and adding does not create an order.

Session-scoped SQLite rows are chosen for atomic local verification, not for a comprehensive cross-session cart feature. Expire and clean them under a documented policy. Do not promise recovery of a lost session after restart unless the client/session token and expiry contract is implemented and tested. Never replay pending actions automatically into a new session. If later using an external cart API, preserve its idempotency key/result lookup or disclose the weaker guarantee; a local ledger cannot prove an external exactly-once effect.

Once commit completes, stop/cancellation affects playback and later work; it cannot truthfully say the add was cancelled. After a timeout, consult the stored outcome before retrying. If the outcome remains unknowable, say it cannot be verified and prevent a fresh blind retry. [SQLite transactions](https://www.sqlite.org/lang_transaction.html), [task cancellation](https://docs.python.org/3/library/asyncio-task.html).

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
| Application/storage | [Python PSF-2.0 and incorporated terms](https://docs.python.org/3/license.html); [SQLite public domain](https://www.sqlite.org/copyright.html); [Qdrant Apache-2.0](https://github.com/qdrant/qdrant/blob/master/LICENSE) | A dependency's terms do not establish the project's own licence; that owner decision is still open. |
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

**Assessment:** warm, short, structured requests are a plausible target because the proposed route removes vector/second-generation work when unnecessary and uses resident models. However, even one extractor call must finish its full structured output before action validation. GPU/CPU contention, long transcription tails, model loading, language errors/retries and TTS initialization can exceed the budget. Available source benchmarks cannot determine whether the target will hold on this project hardware. No justified numerical stage budget or expected speedup is available yet.

README does not specify percentile, utterance length, hardware, concurrency or whether acknowledgement counts. Propose **P95 under 1.5 seconds for meaningful first audio on the declared warm supported workload**, alongside median, cold-start results and the fraction of all turns exceeding 1.5 seconds. This percentile/profile interpretation requires owner acceptance; it does not silently replace the original target. If the owner intends every cold and warm turn to meet 1.5 seconds, treat that stronger requirement explicitly and demonstrate it or report failure. A slower tier or revised target also requires an explicit decision.

### 10.3 Experimental controls and resource accounting

Run the first measurements on the actual intended device, not a guessed developer laptop. If available, compare a CPU-only profile, an Apple Silicon profile and a CUDA profile. Record exact CPU/GPU, RAM/VRAM, OS, audio device, drivers, acceleration backend, thread counts, power mode and thermal conditions. These are comparison profiles, not purchase recommendations or verified minimum requirements.

For every run record runtime versions, immutable model/voice revisions and hashes, quantization, chat template, context/output limits, sampling settings, ASR beam/language settings, VAD policy, sample rate, encoder preprocessing, catalogue snapshot, candidate depths, index settings and concurrency. Keep these constant in a paired experiment; change one factor or an explicitly named complete configuration.

Measure isolated stages and the combined resident stack. Include peak RSS/VRAM, sustained CPU/GPU use, swap, model eviction/reload, startup-to-ready time, queue delay and index-build/update cost. Never derive total memory from model parameter count or download size. As a planning calculation only, 100,000 float32 vectors of dimension 384 occupy 153,600,000 bytes before indexes, IDs, payloads, process memory or model weights; this is not measured Qdrant RAM.

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
- Ordinals, new searches versus refinements, repeat/stop, stale lists and two-session interleavings.
- Malformed/truncated model output, prompt injection in user/catalogue text and unsupported intents.
- Duplicate completions, response timeouts, late cancellation, stock/price changes and index failure.

Use synthetic fixtures for deterministic corner cases and consented real recordings for speech/accessibility. Synthetic speech alone cannot establish accent/noise usability. Do not retain identifying recordings by default; maintain a consent/retention process for the evaluation set.

### 10.5 Metrics and release gates

| Area | Measure | Acceptance criterion / how to establish it |
|---|---|---|
| Hard constraints | Invalid additions divided by all additions; explicit-budget/category/colour/quantity violations | Zero on deterministic fixtures and held-out action challenges. Any violation blocks promotion; finite zero-error samples do not prove universal correctness. |
| Global cheapest | Match to the complete structured oracle, including stable ties and snapshot version | Exact agreement for every supported structured fixture. A scoped discovery answer must never claim a catalogue-wide minimum. |
| Add intent | False-add rate on search-only, negation, silence, echoed speech and cancelled turns | Zero observed unintended mutations in the release challenge suite; investigate every failure rather than averaging it away. |
| Mutation semantics | Duplicate effects, wrong-session effects, command-fingerprint mismatch, known/unknown outcome truthfulness | Zero duplicate/wrong-session effects in the declared guarantee window; every uncertain external outcome is surfaced truthfully. |
| ASR | WER plus exact critical-value accuracy for prices, negation, colour, names, quantities; false speech and early cutoff rates | Select among candidates on these critical fields and downstream action results. Establish tolerable non-action transcription error through the pilot/user study. |
| NLU | Intent accuracy, slot F1, whole-plan exact match, operator/amount/negation/add accuracy, malformed rate, clarification precision/recall | No candidate promotion with a critical safety regression. Set absolute noncritical quality thresholds before held-out testing using the pilot and owner needs. |
| Discovery retrieval | Recall@10/20/50, Precision@K, nDCG@K, exact identity accuracy and no-match error | Require a reliable paired improvement over dense-only for adopting extra ranking/model layers, without critical slice regressions. Freeze an absolute relevance floor from labelled pilot data before release. |
| Freshness | Wrong/stale selected facts, missing-new-item rate, reconciliation lag, rebuild success | No stale invalid add; pending/incomplete semantic coverage is handled through the documented ready/fallback policy. Exact lag target depends on the real update SLA. |
| Grounding | Unsupported spoken product claims and IDs outside retrieved validated evidence | Zero in release fixtures; fall back to evidence templates if validation cannot support free prose. |
| Latency | First feedback, meaningful first audio, verified outcome audio, full-response time; median/P95 and over-1.5-second fraction | Report all by cold/warm, route, language and device. Gate against the owner's agreed interpretation of the unchanged 1.5-second goal. |
| Resources | Peak/sustained RAM/VRAM, swap, thermal throttling, CPU/GPU use, startup-to-ready | Fit the declared supported device with agreed headroom under combined workload; no universal minimum inferred from artifact size. |
| Accessibility/TTS | Task completion, amount/name comprehension, clarification loops, keyboard/screen-reader access, interruption recovery | Every critical control/failure path works without sight; obtain representative-user acceptance before release. Naturalness alone is insufficient. |
| Privacy/offline | External network use after provisioning; retained audio/transcripts; session isolation | Workflow succeeds offline for local catalogue data; no unauthorized content retention or cross-session exposure in tests. |

For noncritical accuracy/relevance targets, the absence of user and catalogue evidence makes a specific numeric floor arbitrary. The actionable procedure is: collect pilot judgments → agree acceptable task completion/error costs → pre-register thresholds and any noninferiority margin → freeze the test set → evaluate → accept/reject. Do not choose a threshold after seeing which model wins. Use paired confidence intervals for differences and confidence bounds for rare failures; report denominators and correlated samples. This quality-threshold decision is a release gate, not a reason to stop the present report.

### 10.6 Prioritized experiments

| Experiment | Problem / hypothesis | Baseline → alternative | Dataset/conditions and metrics | Adoption gate, regressions and decision |
|---|---|---|---|---|
| **E01: Catalogue correctness and consistency** | Top-K cheapest and stale indexes can give incomplete answers. Complete structured authority should fix the expressible case. | README candidate sorting → ARCH-001/002 SQL oracle route and revisioned index lifecycle | Complete fixture; vary candidate K, corrupt/missing attributes, strict/inclusive price boundaries, cheap omitted variants, updates/deletes and ingestion crash windows. Measure oracle agreement and stale/missing-item handling. | Exact supported-query agreement; no silent fallback to a partial global claim. Missing taxonomy/required fields block that query type rather than relaxing predicates. |
| **E02: NLU contract and model choice** | Bounded structured extraction may preserve quality with less generation; smaller current models might be adequate. | Prompt-only reference parsing → same 2507 checkpoint with schema; then Qwen3.5-2B/4B, Gemma E2B; optional LFM English | Same finalized text, schema, evidence and semantic validator; compare precision variants separately; repeated paired runs. Measure exact plan/critical fields, format failures, repair frequency, token counts, latency and memory. | Zero critical regression on challenge cases; choose a smaller model only when whole-task quality gates and E07 pass. Reject candidates needing frequent repair or hidden thinking latency. |
| **E03: ASR and endpointing** | Post-utterance work and early cutoffs may dominate speech latency/correctness. | whisper.cpp base/small variants with explicit turns → incremental/VAD policy; matching Moonshine or Qwen-ASR; faster-whisper on CUDA | Same recordings/device; control Whisper weights/decoding when comparing runtimes. Include pause-before-negation, amounts, accents, noise, silence and speaker echo. Measure WER, critical values, early cutoff, false turns and remaining ASR tail. | No new unintended actions/cutoffs on critical fixtures; choose profile by task accuracy and E07. Hindi needs its own evidence; no extrapolation from English. |
| **E04: Discovery retrieval and optional rerank** | Exact names and paraphrases need different evidence. Hybrid may improve recall/ranking. | Dense-only → FTS-only → fusion; then encoder alternatives if required; only then optional cross-encoder | Same snapshot, hard predicates and judged queries; stratify names/SKUs/subjective queries/languages. Depth 10/20/50 experimental grid. Measure Recall/Precision/nDCG, exact identity, no-match behaviour, stage latency and memory. | Promote hybrid/model/reranker only for measured paired benefit on failing slices and E07 fit. Reranker needs adequate candidate recall and may never change hard constraints or global-minimum route. |
| **E05: TTS voice and playback** | Short factual prompts and rupee pronunciation need intelligibility and low first-audio delay. | Pinned OHF Piper + eligible English voice → eligible Kokoro/other approved-language voice | Same short/long templates, amounts, product/SKU names and failure prompts; warm/cold playback on actual device. Measure audible onset, synthesis time, memory, comprehension and user preference; inspect shipped terms. | All critical values understood and errors recoverable without sight; voice/artifact eligibility recorded. Do not promote on naturalness alone or assume a voice list proves Hinglish support. |
| **E06: Action/state fault injection** | Repeated finals, stale lists and retries can duplicate or redirect actions. | Naive turn dispatch → ARCH-005 state/operation protocol | Inject duplicates, different payload same ID, intentional repeated add, late callbacks, stale/part-spoken lists, interleaved sessions, cancel before/during/after commit, timeout before/after commit. | No duplicate/wrong-session effects within declared lifetime; stored outcome matches response. Restart/session loss never blindly replays a new operation. No claim of external exactly-once without its tested API contract. |
| **E07: Combined latency feasibility** | Individually fast stages may contend when combined. | Instrumented safe version of sequential reference → recommended routes/residency/configuration | Actual target machine; representative route/language mix, cold, first-ready, warm, idle unload and required concurrency. At least 200 warm repetitions per primary route/profile as an initial sampling plan, expanded if P95 uncertainty is large. | Show complete latency distributions and misses against the agreed target, with quality held fixed. If it fails, identify measured bottleneck, rerun only the justified change, or obtain an explicit target/hardware decision. |
| **E08: Accessibility task study** | Voice-first behaviour cannot be validated through sighted developer inspection alone. | Minimal happy-path prototype → full nonvisual controls/status/fallback | Consented representative blind/low-vision users; keyboard/screen-reader and voice interaction; slow speech, stop/repeat, no matches, ambiguous amounts, TTS failure, no-audio recovery. Measure completion, misunderstanding, repeated clarification and user feedback. | No sight-dependent critical step; resolve task-blocking defects before release. Sample/recruitment plan agreed with users; no conformance claim from this review. |
| **E09: Deployment, offline and recovery** | Hidden downloads, model eviction, missing artifacts and index failures can defeat local reliability. | Unpinned defaults → pre-provisioned manifests/readiness/resource limits | Disable internet after provisioning; remove model/voice; exhaust worker; corrupt version/fingerprint; interrupt index rebuild; simulate DB busy/unavailable and audio-device failure. Inspect network activity, memory, recovery and redacted traces. | Safe, accessible failure; no false success/no-match; no cloud fallback; reproducible pinned rebuild and index rollback. All project data stays within documented retention/isolation policy. |

Run E01 and a thin E03/E05/E07 voice slice early. They can invalidate the data or hardware assumptions before a large implementation investment. Run E02 with text first to separate interpretation failures from ASR errors, then repeat critical cases with real audio. Compare the final combined configuration again after any model, encoder or voice promotion.

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
| **1. Immediate: contracts and catalogue slice** | ARCH-001/002/004: typed interpretation/SearchPlan/Selection/Outcome contracts; normalized variant fixture; parameterized structured repository | Proposed `domain`, `validation`, `catalogue`; no models required | E01 complete cheapest oracle, price operators, variants, unknown fields; deterministic fixtures pass | Taxonomy/data mismatch; fix authority contract before adding model complexity. |
| **2. Immediate: early voice feasibility slice** | ARCH-006/007/008: instrument capture/endpoint → local ASR → fixed verified response → TTS; add model extraction timing next | Proposed `audio`, `adapters/asr`, `adapters/tts`, `diagnostics`; approved test artifacts | Initial E03/E05/E07/E09; observable actual playback, offline readiness and nonvisual failure controls | Hardware or language failure discovered early; replace an adapter/test profile without disturbing catalogue logic. |
| **3. Immediate: schema NLU and runtime gate** | ARCH-004/008: pin reference, build constrained extraction and validator; evaluate small current challengers | Step 1 contracts and step 2 instrumented device; proposed `adapters/nlu`, model manifest | E02 text then audio, bounded repair, unsupported/negative intent rejection; choose a reproducible reference configuration | New model changes semantics/template; retain previous pinned configuration and fixture results. |
| **4. Immediate: semantic/lexical retrieval** | ARCH-002/003: stable serializer, BGE embeddings, Qdrant collection/payload indexes, FTS updates and candidate fusion | Step 1 catalogue; proposed `ingestion`, `adapters/embedding`, `retrieval` | E01 update/delete/pending coverage and E04 ablations; retrieval always hydrates current authority | Mixed encoders/stale omissions; roll back collection generation, keep exact/structured route available with truthful status. |
| **5. Immediate: minimal action/session slice** | ARCH-002/005: per-session state/list IDs, clarification loop, minimal cart rows and operation result transaction | Steps 1/3/4; proposed `workflow`, `session`, `cart` | E06 fault tests; correct add from direct request and ordinal reference; verified success wording | Duplicate or redirected add; disable mutation dispatch until invariant fixtures pass. Read-only search can remain usable. |
| **6. Before supported demo/release** | ARCH-006/007: integrate actual response templates, controls, cached failures and assistive status | Voice/action slices; proposed `responses`, `client`; release voice decision | E05/E08: all important paths usable without sight; exact amounts/variant identity understood | TTS/echo/accessibility failure; retain proven voice and half-duplex policy while repairing. |
| **7. Before latency/quality claims** | ARCH-008 plus combined configuration: run complete E01–E09, measure contention, tune only diagnosed bottlenecks | Integrated workflow, locked data/test sets | Report all quality/latency/resource gates; owner accepts profile or explicitly revises target if needed | Optimization hides semantic errors; reject a faster configuration failing correctness; restore previous manifest. |
| **8. Deferred optimization only on evidence** | Optional smaller model, multilingual encoder, reranker, in-process dense scan, direct llama.cpp/MLX/vLLM | Failed measurable metric and matching experiment from §10 | Paired improvement and combined-gate pass; new collection/re-embedding when appropriate | Additional memory and migration cost; feature/configuration rollback with old artifacts retained. |

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
| **D07: How large/busy is deployment?** | One device/user; interleaved local sessions; shared remote service | No scale/concurrency figures; SQLite and local serving have contention limits | Catalogue count/size, update rates and expected concurrent users; E07/E09 | SQLite/reference topology can serve experiments; revisit before shared deployment. |
| **D08: Which NLU artifact wins?** | 2507 reference; Qwen3.5-2B/4B; Gemma E2B; optional smaller English model | Current candidates verified through primary cards; no task measurements | E02 with fixed schema and E07 combined stack | Nonblocking for contracts; blocks an accuracy/performance endorsement of a release model. |
| **D09: Is BGE-small sufficient?** | Retain English model; E5-small; BGE-M3/Qwen encoder; optional translation experiment | Encoder contracts and migration consequences documented | Approved language profile and E04 catalogue relevance/latency results | Nonblocking for English reference. A multilingual release cannot assume success. |
| **D10: Are reranking or a simpler vector store justified?** | No reranker/Qdrant reference; bounded cross-encoder; exact in-process dense search; pgvector with shared backend | Feasible alternatives documented, no workload comparison | Candidate recall failures or daemon/resource burden measured in E04/E07 | Safely defer; premature adoption creates migration/latency cost. |
| **D11: Which interaction controls/voice do users accept?** | Accessible end/stop controls with half-duplex; later tested voice barge-in; eligible Piper/Kokoro voices | Failure/echo hazards and voice candidates identified; no user study | E05/E08 with representative users, device and languages | Blocker for accessibility/readiness claim; thin slice should run early. |
| **D12: What retention and session expiry are required?** | Ephemeral turns and expiring local session cart; separately consented diagnostics; future durable identity | README requires minimization/isolation but gives no durations or restart contract | Owner/user privacy policy, expiry semantics and E06/E09 | Default to no raw content retention for prototype; block retention/restart guarantees until specified. |
| **D13: What noncritical quality floors are acceptable?** | Pilot-derived task completion/relevance thresholds with pre-registered gates | No labelled dataset or user cost model yet; hard invariants and existing latency goal are known | Pilot, owner/user review, held-out sample-size/threshold plan before candidate selection | Nonblocking for evaluation harness; blocker for release acceptance. |

### 12.2 Recommendation status

| Decision | Status after this review |
|---|---|
| Local inference/no paid inference APIs/current search-to-add scope | Preserved requirements. |
| Python, whisper.cpp, Ollama, Qdrant and English BGE reference | Recommended retention, subject to the specified device/language tests. |
| ARCH-001/002/004/005 responsibility contracts | High-confidence proposals for owner approval; not implemented or automatically binding. |
| ARCH-003 hybrid discovery | Recommended measured addition; catalogue relevance benefit remains unmeasured. |
| ARCH-006/008 audio/lifecycle/early validation | Recommended required responsibilities; exact thresholds depend on experiments. |
| ARCH-007 runtime/voice decision | Recommended explicit identity/eligibility gate; release voice remains open. |
| Smaller/newer model, multilingual encoder, reranker, alternate runtime/store | Experiments or conditional future choices, not unconditionally adopted changes. |
| Comprehensive cart management, checkout, payments, order tracking | Deferred by the existing scope. |

### 12.3 Review completion record

- The repository and the complete README were inspected; pre-implementation status is verified for the recorded commit.
- Research covers every selected component, current credible challengers and complete-system alternatives, with direct sources, access dates and limitations.
- Eight actual proposed changes are recorded against the README target, each with rationale, research, risks, dependencies, validation, priority and confidence.
- The complete recommended architecture, interfaces, authority boundaries, application flow, deployment assumptions and recovery paths are specified.
- Experiments, metrics, acceptance procedures, a future implementation order and unresolved release decisions are documented.
- No VoiceCart benchmark or implemented behaviour is claimed. All future modules and configurations are proposals.
- The deliverable is `Suggestions.md`; README and other project files are outside the review's edit scope.
