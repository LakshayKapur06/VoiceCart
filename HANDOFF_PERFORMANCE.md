# Performance investigation — continuation

Historical S7 full-model smoke recorded embedding publication 17.2177s, discovery 0.0217s, ASR 1.3044s, combined interpretation/validation/search/commit 59.1698s and confirmation synthesis 1.0752s on an M1/16 GiB host. This is one development observation. Its combined duration cannot retrospectively be divided into invented component measurements.

## Instrumentation and confirmed unnecessary work

Opt-in `voicecart.telemetry.measurements()` records bounded, context-isolated numeric spans with no raw input, SQL, credentials or catalogue contents. Stages cover application final/presentation/add, NLU schema/validation/total, local HTTP, encoder, database inspect/snapshot/vocabulary/publication/transaction and cart add/verification. Ollama's returned load/prompt-evaluation/token-evaluation/total nanosecond counters are converted to seconds. Nested spans overlap; do not sum them as disjoint costs. Failures remain in the denominator.

Vocabulary previously reconstructed complete Product/Variant objects and prices for every interpretation. It now queries only distinct canonical attributes and aliases, caching copies by (revision,published_at). Every use still reads publication metadata inside a consistent snapshot; action facts are never cached. Exhaustive dense scoring no longer orders the entire vector table before Python ranks candidates; no candidate cutoff or weaker minimum guarantee was introduced. Fresh-wheel installation explicitly reinstalls the built artifact to resist source egg-info being mistaken for a wheel installation.

No pooling or asynchronous mutation rewrite was introduced without evidence. Short PostgreSQL transactions, session locks and new-connection receipt verification remain authoritative. Cold loads and eviction are plausible contributors to the old 59s stage: the old smoke interleaved MiniLM and Qwen with MAX_LOADED_MODELS=1. This is a hypothesis, not an established attribution. The continued run permits two resident models and records actual runtime counters; it is not a controlled before/after comparison with the historical run.

## Reproduce

```sh
OLLAMA_HOST=127.0.0.1:11439 OLLAMA_MODELS="$PWD/.local/ollama-models" OLLAMA_NO_CLOUD=1 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=2 .local/runtime/ollama serve
PYTHONPATH=. python scripts/benchmark_nlu.py --output /tmp/nlu-holdout.json
python scripts/verify.py --postgres --package --audit
```

The frozen 12-case bank was created before this measurement and is not used to tune this prompt. It covers strict/inclusive/decimal/spoken amounts, product/colour aliases, quantity, negation, unsupported currency, multiple bounds, ordinal selection and subjective requirements. Accepted but incorrect extractions and safe rejections are reported distinctly; protocol regression tests additionally supply malformed outputs. This is a small text holdout, not general ASR/NLU accuracy or commerce acceptance.

Client process CPU/max-RSS is recorded separately from inference-server observations; macOS ru_maxrss is bytes, Linux uses KiB. A process snapshot is not peak memory or average utilization. Physical audible response latency cannot be inferred from PCM enqueue, synthesis completion, PortAudio drain or these text measurements. Sub-1.5s remains unachieved/unverified; a pilot must collect full device turns, language/hardware/concurrency profiles, failures/timeouts and sufficient samples before percentile claims.

## Remaining measurement gates

Physical microphone/speaker endpoint and audible-onset instrumentation, representative users/languages, approved catalogue scale, controlled residency=1 versus 2 trials, representative model contention and maintained-server deployment need separate acceptance. Explicit text fallback and a processing indicator reduce uncertainty but are not counted as a successful meaningful audible response. Final continuation evidence and conclusions are appended after the actual measurements complete.

## Actual continuation text observations

Frozen holdout: 11/12 declared expectations met. H05 (two-item search-and-add) was safely rejected and remains a release-quality limitation; no unsafe mutation was dispatched. First request 32.0628s; all-request mean 18.9535s, median 18.7214s. Subsequent calls remained slow; this does not establish an optimization win or a 1.5s turnaround. Exact per-call/runtime load/prompt/eval spans, failures and client resource counters are in docs/evidence/NLU_HOLDOUT_20261102.json. The baseline and new test profiles differ; no causal before/after speedup is claimed.

A concurrent process snapshot observed Ollama launcher RSS 29,808 KiB and model worker RSS 3,126,576 KiB / 46.5% CPU at one instant; this is not peak RSS, aggregate system utilization or a minimum memory requirement. Further device-specific inference profiling is required. No container or physical-audio latency was measured.

## Search/load and real-data continuation

The isolated 2000-variant/128-search/eight-worker load had zero failures, elapsed 3.0984s, mean .18895s, median .19166s and exploratory empirical P95 .22057s. P99 is not estimated. Client CPU was 3.2991s; client peak RSS 54,804,480 bytes on macOS, excluding PostgreSQL/model processes. No capacity/SLA claim follows. Real 298-record historical MiniLM publication took 2.9040s and one hybrid query .0393s with the explicit bounded derived profile; conditions differ from the old smoke. Physical audible latency and broad model/device contention remain unverified.

Continuation instrumentation on the first frozen Qwen request attributed 2.81159s to runtime-reported model load, 8.541275s prompt evaluation and 20.620773s generation within 31.99555s runtime total (32.063s client wall). This directly shows inference/prompt costs on that run; it does not reconstruct the historical 59.17s or prove a one-knob fix. Database-only optimization cannot be advertised as meeting the audio goal.
