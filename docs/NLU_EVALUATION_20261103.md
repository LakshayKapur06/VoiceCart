# Frozen NLU comparison — 3 November 2026

No production NLU prompt, schema or independent validator was changed. H01–H12 texts/labels remain; the new bank adds20 carefully authored English probes and additional canonical-slot annotations frozen before inference. `tests/nlu_eval_v2.json` contains32 cases with explicit action-permission labels, origin notes and expected fields. Both actual runs record the same dataset SHA256. It is not representative user data or a commercial accuracy acceptance study. Labels were not changed after failures.

## Metrics and boundaries

`scripts/nlu_evaluation.py` evaluates exact annotated expectations and intent including declared rejection. Canonical slots cover product category, colour, size, quantity, identifier/ordinal, amount/operator and route where annotated; free-form query semantic equivalence is not inferred. Slot microprecision TP/(TP+FP), recall TP/(TP+FN), F1 2TP/(2TP+FP+FN). A wrong non-null slot creates FP+FN, absent output on required slot FN, unannotated slots excluded. Per-slot annotated/correct/TP/FP/FN counts are in JSON. Quantity accuracy is conditional on the four authored annotated quantity cases, not every utterance.

Only InterpretationError is a semantic rejection. Timeout/transport errors are failures, and unexpected exceptions are separately counted. The legacy12-case benchmark was corrected too and refuses overwriting an existing output. Evaluator integrity tests independently exercise malformed structures, negated injected adds, service outage versus rejection and known metric counts. Schema/protocol fixtures are controlled validation tests, not actual model-quality observations.

A false action authorization here is an accepted validated intent proposal with explicit_add on a case labelled action_allowed=false. No application/SQL/cart write occurs in this evaluation. Zero observed false proposals on27 nonaction cases is not proof of a zero population mutation risk. Semantic rejection rate includes false rejections; it is not correctness.

## Actual local observations

| Same32-case bank, one sequential pass | Pinned4B reference | Pinned0.6B challenger |
|---|---|---|
| Exact expectations / intent expectations |26/32 /26/32 |21/32 /21/32 |
| Slot TP/FP/FN |33/0/10 |10/0/33 |
| Microprecision / recall / F1 |1.000 /0.7674 /0.8684 |1.000 /0.2326 /0.3774 |
| Quantity exact / annotated |2/4 |1/4 |
| Semantic rejections / service errors |16 /0 |23 /0 |
| False action proposals / nonaction cases |0/27 |0/27 |
| First request after explicit model eviction |13.446s |2.878s |
| All-case mean / p50 |6.066s /6.549s |0.979s /0.929s |
| p95 / p99 |Not estimated |Not estimated |

Actual [reference JSON](evidence/20261103_S17_qwen4b/NLU.json) and [challenger JSON](evidence/20261103_S17_qwen06b/NLU.json) retain every case, outcome, annotated output, timing and nested runtime spans. First request follows keep_alive0 eviction, not a guaranteed cold OS cache. Subsequent requests are labelled warm-request/residency-observed, not assumed continuously resident. Same M1 host, hardware, prompt, validator, vocabulary, frozen inputs and timing methodology; run order/thermal state/OS caches uncontrolled. Do not attribute November2→November3 differences solely to any optimization. Neither number is end-to-end voice latency. Sample32 does not justify strong tail percentile claims.

Reference failures H04,H05,V17,V18,V20,V30 include safe false rejections of negated search, quantity/identifier/control cases and an adversarial rejection expectation answered with a harmless search. Challenger failures H01,H02,H03,H05,H10,H12,V15,V16,V19,V20,V28 show substantially lower slot recall; V28 unsupported removal can become harmless search rather than the desired clarification. These are quality defects/limitations, not labels to rewrite. Current natural-language contract does not implement cart target quantity/removal; use explicit UI/API. Pending human work includes representative accents/languages, ambiguity judgments and true product relevance.

Decision: retain4B reference. The smaller model is faster on this small profile but loses more requested slots/valid cases; speed alone does not justify replacement. No validator weakening or tune-on-holdout fix is made for H05. Prepare separate development cases for quantity/evidence failures, then evaluate a newly frozen bank after any justified prompt/model change.

## Reproduce

Start the already-provisioned private Ollama runtime per HANDOFF_PERFORMANCE; use OLLAMA_NO_CLOUD=1, one parallel request, recorded residency profile. From repo with dedicated dev dependencies:

```sh
PYTHONPATH=. python scripts/record_run.py --label nlu-reference -- python scripts/nlu_evaluation.py --model qwen3:4b-instruct-2507-q4_K_M --digest 0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0 --unload-first
PYTHONPATH=. python scripts/record_run.py --label nlu-challenger -- python scripts/nlu_evaluation.py --model qwen3:0.6b --digest 7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435 --unload-first
python -m unittest tests.test_nlu_evaluation -v
```

Default outputs are separate UTC timestamp directories. Nonzero process exit means execution failure; a completed measurement command can still contain failed quality expectations, which must be read from NLU.json. Do not convert its process success into a model-quality pass.
