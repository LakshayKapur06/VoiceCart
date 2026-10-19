# VoiceCart — Voice-First Shopping Assistant

> **Project status: Pre-implementation.** No application components have been implemented yet. This document establishes the project requirements, selected target architecture, development constraints, and architecture-review process. The technologies and workflows described below are design decisions or proposals, not evidence of working software.

---

# 1. Project Overview

## 1.1 What is VoiceCart?

VoiceCart is an accessibility-first, voice-driven commerce system designed primarily for visually impaired users.

Traditional e-commerce platforms require users to navigate search fields, product listings, filters, product details, and cart controls. Screen readers improve accessibility, but shopping can still involve substantial manual navigation and repeated interaction.

VoiceCart aims to simplify this experience by allowing users to search for products, express preferences, and add selected products to their cart using natural spoken commands.

The system is intended to combine local speech recognition, natural-language understanding, semantic product retrieval, deterministic application logic, and spoken responses.

### Example interaction

A user says:

> Find me a blue shirt under ₹1,500 and add the best option to my cart.

The intended workflow is:

1. Capture the user's speech.
2. Convert the speech into text.
3. Interpret the request and extract relevant constraints.
4. Retrieve potentially relevant products from the catalogue.
5. Validate product attributes and enforce explicit constraints.
6. Select an appropriate product or ask for clarification.
7. Execute the requested add-to-cart operation through application-controlled logic.
8. Verify that the operation succeeded.
9. Communicate the result through speech.

The user should not need to navigate a visual interface to complete this workflow.

**Core architectural principle: RAG supplies relevant evidence, the LLM interprets and explains that evidence, and deterministic application logic enforces business rules and executes actions safely.**

## 1.2 Primary objectives

VoiceCart should:

- Provide a voice-first shopping experience with minimal dependence on visual navigation.
- Interpret natural-language product requests.
- Retrieve semantically relevant products from a catalogue.
- Respect explicit constraints such as price, colour, category, and availability.
- Support product selection and add-to-cart operations.
- Ask clarification questions when ambiguity affects the result or action.
- Minimize unnecessary LLM calls.
- Target low end-to-end interaction latency.
- Prefer local inference to avoid paid inference API charges.
- Keep authoritative application state outside the LLM.
- Handle errors safely and communicate failures clearly.
- Preserve session isolation and avoid unnecessary data retention.
- Remain modular, testable, maintainable, and extensible.

The architecture must be evaluated against these objectives rather than selected solely because a particular technology is popular or performs well on unrelated benchmarks.

---

# 2. Project Scope

## 2.1 Current scope

The current implementation scope includes the complete product-search-to-add-to-cart interaction.

### A. Voice input

The system should accept spoken product requests and convert them into text.

### B. Natural-language understanding

The system should interpret the user's intent and extract relevant parameters, including product categories, price constraints, preferences, and selection criteria.

### C. Product retrieval

The system should retrieve relevant products from the catalogue using semantic search and appropriate structured filtering.

### D. Product filtering and selection

The system should support voice-driven filtering and product selection.

Explicit constraints must be enforced reliably. For example, a product above the user's stated budget must not be selected merely because the LLM considers it a better option.

### E. Add to cart

The system should support an explicit request to add a selected product to the cart.

The application must validate the product, execute the requested operation through controlled application logic, and verify the result before reporting success.

The initial implementation needs only the cart functionality required to support this workflow. It does not require a complete shopping-cart management subsystem.

### F. Clarification and spoken responses

The system should ask for clarification when necessary and provide an understandable spoken response for normal, error, and clarification paths.

## 2.2 Future scope

The following capabilities are not part of the initial implementation unless separately approved:

- Comprehensive cart management, including full cart editing and lifecycle management.
- Checkout and order creation.
- Payment processing.
- Order tracking.
- Additional commerce workflows beyond product search and the required add-to-cart operation.
- Production-scale multi-user deployment and other infrastructure introduced only when justified by requirements.

The initial implementation must not expand into checkout or payment processing as part of an unrelated change.

### Future checkout requirements

If checkout is introduced later, it must:

1. Require explicit user confirmation immediately before execution.
2. Cancel execution when the user declines confirmation.
3. Keep payment processing outside the LLM's authority.
4. Use secure application-controlled transaction handling.
5. Verify authoritative transaction outcomes.
6. Handle failures, retries, and duplicate requests safely.

These are future requirements, not current implementation tasks.

## 2.3 Scope boundaries

The following distinctions are important:

| Capability | Scope |
|---|---|
| Voice-based product search | Current |
| Natural-language intent interpretation | Current |
| Semantic product retrieval | Current |
| Voice-driven filtering | Current |
| Product selection | Current |
| Minimal cart functionality required for add-to-cart | Current |
| Validation and verification of add-to-cart operations | Current |
| Comprehensive cart management | Future |
| Checkout and order creation | Future |
| Payment processing | Future |
| Order tracking | Future |

The current scope includes add-to-cart, so the application must implement the minimum necessary cart state and operation to support it. This does not authorize building every possible cart-management or transaction feature.

---

# 3. Project Status and Decision Boundaries

## 3.1 Actual implementation status

**Nothing has been implemented yet.**

There is no verified working application, integrated inference pipeline, functioning retrieval system, or tested add-to-cart flow at this stage.

The architecture described in this README is the selected target design for beginning implementation. Its suitability remains open to independent research and review.

Unless subsequent repository inspection establishes otherwise, treat all application components as unimplemented.

The reviewing agent must inspect the repository and report any actual files, dependencies, prototypes, or partial implementations it discovers. It must not assume that an empty or pre-existing project structure constitutes a working implementation.

## 3.2 Terminology used in this document

- **Selected:** A current architectural choice that serves as the baseline for implementation and review.
- **Target:** The intended design, which has not necessarily been implemented or validated.
- **Implemented:** Present in the repository and integrated into the application.
- **Tested:** Verified through identifiable tests or experiments.
- **Measured:** Supported by recorded experimental results.
- **Planned:** Intended for a later stage.
- **Recommended:** A proposal produced by the architecture-review process.
- **Approved:** Explicitly accepted by the project owner.

A selected technology must not be described as implemented merely because it appears in this README.

A target metric must not be presented as achieved performance.

## 3.3 Source of truth

This README is the consolidated project-context document for future developers and coding agents.

It incorporates the durable requirements previously maintained in `AGENTS.md`, including:

- Project purpose and actors.
- Current and future scope.
- Functional and quality requirements.
- Logical architecture and component responsibilities.
- Separation of concerns.
- Safety and interaction behaviour.
- Development approach.
- Instructions for coding agents.

The architecture-review deliverable, `Suggestions.md`, will record research and recommendations. It does not automatically override this README.

The project owner must approve material architectural changes before they become binding implementation decisions.

If the repository, this README, or later project-owner instructions conflict, the agent must identify the discrepancy rather than silently inventing a resolution.

---

# 4. Actors and Use Cases

## 4.1 Primary actor: User

The primary actor is a visually impaired user who interacts with the shopping assistant through speech.

The system should minimize dependence on visual navigation and communicate relevant information through understandable spoken responses.

## 4.2 Secondary actor: Administrator

The broader project requirements identify a system administrator who manages the product catalogue and monitors system analytics.

Administrator catalogue management and analytics are part of the broader system vision. Their implementation timing and detailed requirements must be established before they are included in the initial development scope.

Do not build an extensive administrative subsystem without a defined requirement.

## 4.3 Core use cases

The initial user-facing workflow covers:

- Search for products by voice.
- Filter product results using voice commands.
- Select a relevant product.
- Add the selected product to the cart.
- Ask clarification questions when the request cannot be interpreted safely.
- Receive a spoken response for success, failure, and clarification.

---

# 5. Selected Target Architecture

## 5.1 Architecture overview

The current target is a local-first, Python-based application using local inference for speech recognition, language understanding, embeddings, and text-to-speech, with Qdrant providing vector retrieval.

The current design does not use paid inference APIs.

The selected target components are:

| Layer | Selected technology | Intended responsibility |
|---|---|---|
| Speech-to-text | `whisper.cpp` | Transcribe incoming speech locally. |
| Language model | Qwen3 4B Instruct through Ollama | Interpret natural-language requests and generate grounded responses when useful. |
| Embeddings | `BAAI/bge-small-en-v1.5` | Convert queries and product text into vector representations. |
| Vector database | Qdrant | Retrieve semantically relevant catalogue candidates. |
| Application and orchestration | Python | Coordinate processing, validate inputs and outputs, enforce rules, manage required state, and execute approved actions. |
| Text-to-speech | Piper as the selected local TTS direction | Convert responses into spoken audio. |
| Product catalogue | Authoritative structured product data | Supply valid product identifiers and structured product attributes. |
| Add-to-cart handling | Application-controlled logic and appropriate state storage | Execute and verify the minimum cart operation required by the current scope. |

The exact authoritative catalogue storage technology, persistence mechanism, interfaces, and deployment topology have not been finalized.

The architecture review must investigate these choices rather than assume a particular SQL database or deployment model.

## 5.2 Technology distinctions

- **Qwen3 4B Instruct** is the selected language model.
- **Ollama** is the local model runtime, not the model itself.
- **BGE-small-en-v1.5** is the embedding model. It creates vectors; it does not generate conversational responses.
- **Qdrant** is the vector database. It supports vector retrieval and payload filtering but is not automatically the authoritative source of product or cart state.
- **whisper.cpp** performs speech recognition.
- **Piper** is the selected direction for local text-to-speech. Its exact model, runtime, licence, and integration must be determined before implementation.

These technologies are the baseline for evaluation, not proof that they are optimal for every requirement.

The architecture review must assess whether they should be retained, reconfigured, replaced, or supplemented.

## 5.3 Logical architecture diagram

The following diagram represents the intended logical flow. It does not represent an implemented system.

```text
                          USER
                            |
                            v
                  Microphone / Audio Input
                            |
                            v
                       whisper.cpp
                    Local Speech-to-Text
                            |
                            v
                      Transcribed Text
                            |
                            v
                Python Application Layer
                            |
                            v
                   Qwen3 4B Instruct
                     Served by Ollama
                            |
                            v
               Intent and Parameter Extraction
                            |
                            v
                  Application Validation
                            |
                            v
                   Retrieval Coordinator
                            |
                    +-------+-------+
                    |               |
                    v               v
               BGE Embeddings   Structured Filters
                    |
                    v
                   Qdrant
               Vector Retrieval
                    |
                    v
              Retrieved Candidates
                    |
                    v
             Post-Retrieval Processing
                    |
          +---------+----------------+
          |                          |
          v                          v
  Deterministic Validation     Grounded Comparison
  and Hard Constraints         or Explanation, if useful
          |                          |
          +------------+-------------+
                       |
                       v
             Validated Product Selection
                       |
                       v
              Controlled Add-to-Cart
                       |
                       v
              Result Verification
                       |
                       v
               Response Construction
                       |
                       v
                    Piper TTS
                       |
                       v
                Spoken Response
                       |
                       v
                      USER
```

Not every request needs to traverse every stage. For example, a simple confirmation can use a deterministic response template rather than invoking the LLM again.

The architecture may use different internal module boundaries if the repository or subsequent research justifies them, provided the required responsibility and safety boundaries remain intact.

---

# 6. Core Architectural Principle: Hybrid Intelligence

VoiceCart should not be designed as either an entirely deterministic pipeline or an entirely LLM-driven agent.

The intended approach is a hybrid architecture.

Use the LLM for natural-language understanding and flexible language generation where these capabilities provide value. Use semantic retrieval to identify relevant product candidates. Use deterministic application logic for hard constraints, state changes, and operations requiring reliable outcomes.

## 6.1 LLM responsibilities

The LLM may be used to:

- Interpret natural-language shopping requests.
- Identify user intent.
- Extract product categories and preferences.
- Interpret less formal descriptions of shopping criteria.
- Help determine whether clarification is required.
- Compare retrieved products using supplied catalogue information.
- Generate a natural-language summary grounded in retrieved evidence.

The LLM must not be treated as the authoritative source of product information, product availability, price, or application state.

Its outputs must be treated as untrusted input.

## 6.2 Deterministic application responsibilities

Application code must:

- Validate extracted parameters.
- Enforce hard constraints.
- Check structured product attributes against authoritative data.
- Resolve products to valid identifiers.
- Verify relevant product information.
- Apply explicit filtering and sorting rules.
- Execute the required add-to-cart operation.
- Maintain the state needed for the current interaction.
- Validate requested operations against an allowlist.
- Verify operation results before reporting success.
- Handle errors and clarification paths.

The application must not blindly execute arbitrary model-generated instructions or arguments.

## 6.3 Example: Cheapest backpack under a budget

Suppose the user says:

> Find the cheapest black backpack under ₹2,000 and add it to my cart.

The intended processing is:

1. Interpret the request and extract the category, colour, budget, and selection criterion.
2. Retrieve relevant backpack candidates from Qdrant.
3. Apply the required colour, price, and availability constraints using structured product data.
4. Select the cheapest valid candidate using deterministic sorting.
5. Ask for clarification if the request cannot be fulfilled reliably.
6. Execute the add-to-cart operation through application-controlled logic.
7. Verify the resulting state.
8. Speak a concise confirmation.

The LLM must not select a product that violates the explicit budget merely because it describes that product as a better option.

For a subjective request such as “Find me a good backpack for college,” the LLM may help interpret preferences and explain trade-offs among retrieved products. It must still use available catalogue evidence rather than inventing product specifications.

**Deterministic logic is not automatically correct.** It must be implemented correctly, tested, and supplied with reliable data. Likewise, a high vector-similarity score does not guarantee that a product satisfies every explicit constraint.

---

# 7. Retrieval-Augmented Generation (RAG)

VoiceCart follows a retrieval-first design direction.

Retrieval-Augmented Generation combines retrieval from an external information source with language-model generation. In this project, the external information source is the product catalogue.

## 7.1 Conceptual RAG flow

```text
User Request
     |
     v
Query Interpretation
     |
     v
Query Embedding
     |
     v
Vector Retrieval
     |
     v
Relevant Product Records
     |
     v
Context Construction
     |
     v
LLM Generation, When Useful
     |
     v
Application Validation
     |
     v
Response or Controlled Action
```

This is a conceptual flow. The actual implementation may differ depending on whether a request requires conversational generation, deterministic processing, or both.

## 7.2 Embedding generation

The selected embedding model is `BAAI/bge-small-en-v1.5`.

Its intended responsibilities are to:

- Convert catalogue text into vector representations during ingestion or catalogue updates.
- Convert user queries into vector representations during retrieval.
- Enable semantic matching between natural-language queries and product descriptions.

The model is English-focused. The architecture review must investigate whether its language coverage is sufficient for the intended users and whether a multilingual model would provide a meaningful improvement.

The review must also verify vector dimensionality, preprocessing consistency, similarity configuration, and compatibility with the Qdrant collection design.

## 7.3 Vector retrieval

Qdrant is responsible for retrieving semantically relevant candidates.

Product payloads may contain:

- Product ID or SKU.
- Product name.
- Product description.
- Category.
- Brand.
- Colour.
- Size or variant.
- Price.
- Availability metadata.
- Other attributes needed for filtering and comparison.

The actual schema must be established during implementation.

Use stable product identifiers. Where variants differ in price, size, availability, or other purchasable attributes, retrieval and selection must resolve to the correct variant.

Vector similarity is a candidate-generation mechanism, not a substitute for validating structured business constraints.

## 7.4 Grounding and data freshness

RAG can improve grounding, but it does not eliminate hallucinations or stale data.

Therefore:

- Product descriptions must be based on retrieved or authoritative catalogue records.
- Price and availability constraints must be checked against appropriate structured data.
- The LLM must not invent missing product attributes.
- Missing evidence must lead to clarification, a qualified response, or a safe failure.
- Product updates and deletions must be reflected in retrieval results.
- Critical facts must be validated outside the LLM.

Fine-tuning is not a substitute for retrieving current catalogue information.

---

# 8. Post-Retrieval Processing and Product Selection

Post-retrieval processing must combine deterministic validation with LLM assistance where useful.

It must not require an unconditional second LLM call after every retrieval.

## 8.1 Deterministic processing

Deterministic application logic is appropriate for:

- Enforcing price limits.
- Filtering by explicit colour, size, category, or availability requirements.
- Removing invalid or unavailable products.
- Sorting by price.
- Selecting the cheapest product that satisfies all required constraints.
- Resolving references such as “add the second one” against the current session's result list.
- Validating product identifiers.
- Executing add-to-cart operations.
- Constructing simple confirmations.

## 8.2 LLM-assisted processing

LLM assistance may be appropriate for:

- Interpreting subjective criteria such as “good for college.”
- Comparing trade-offs among retrieved products.
- Explaining why a product may suit the user's preferences.
- Handling flexible natural-language descriptions.
- Formulating clarification questions.

Any model-generated comparison must be grounded in supplied catalogue evidence.

## 8.3 Decision policy

| Request | Preferred handling |
|---|---|
| “Cheapest black backpack under ₹2,000” | Retrieve candidates, enforce structured constraints, and select deterministically. |
| “Show me blue shirts” | Retrieve candidates and enforce the colour requirement against structured attributes. |
| “Which of these is better for college?” | Use grounded comparison when the catalogue contains enough relevant information. |
| “Add the second one” | Resolve the reference against the current session's results, validate the product, and execute the operation. |
| Ambiguous product request | Ask for clarification when ambiguity affects the result or action. |
| Simple cart confirmation | Use a deterministic template if it communicates the verified result adequately. |

Use the least complex processing path that reliably satisfies the request.

---

# 9. Python Application and Orchestration

Python is the selected application and orchestration language.

The application layer coordinates the system and enforces boundaries between probabilistic model behaviour and authoritative application behaviour.

The implementation should separate responsibilities into clear modules or equivalent components for:

1. Audio input and speech-recognition integration.
2. Intent interpretation and parameter extraction.
3. Input and schema validation.
4. Query embedding and retrieval.
5. Product filtering and selection.
6. Required session and add-to-cart state.
7. Response construction.
8. Text-to-speech integration.
9. Error handling and observability.

These are logical responsibilities, not a requirement to create a separate service for every item.

Do not introduce unnecessary services, frameworks, or deployment complexity without an engineering justification.

## 9.1 Model output validation

Model output should be parsed and validated against a defined schema.

The application should:

- Accept only recognized intents.
- Validate required parameters and their types.
- Reject invalid product IDs and unsupported operations.
- Use allowlisted actions.
- Apply bounded retries or request clarification when parsing fails.
- Prevent free-form model output from becoming executable application code.
- Keep business rules in application code rather than relying on prompt instructions alone.

If an orchestration framework is considered, evaluate its actual contribution.

A conventional Python implementation using explicit functions, schemas, a dispatcher, and a controlled state machine may be sufficient. A workflow framework may be justified if the actual complexity warrants it.

Do not assume that a framework is required for the architecture to work.

---

# 10. Local Inference and Cost Constraints

The current target architecture avoids paid inference APIs.

The selected local-inference direction is:

| Capability | Current target |
|---|---|
| Speech recognition | `whisper.cpp` |
| Language-model inference | Qwen3 4B Instruct through Ollama |
| Text embeddings | `BAAI/bge-small-en-v1.5` |
| Vector retrieval | Local Qdrant |
| Application logic | Python |
| Text-to-speech | Piper local TTS |

Local inference means avoiding per-request inference API charges. It does not mean the system has zero operating cost.

Local execution may require CPU or GPU resources, memory, storage, electricity, model management, runtime configuration, and ongoing maintenance.

The architecture review must evaluate whether the selected models can satisfy accuracy, latency, memory, and concurrency requirements on realistic target hardware.

Do not assume that parameter count or model file size alone establishes runtime memory requirements or latency.

The exact model versions, quantization choices, inference settings, runtime versions, and hardware assumptions must be recorded and tested.

Any proposal to use a paid inference API must be presented as an alternative that changes the current constraint. It must not be silently incorporated into the recommended architecture.

Free-tier APIs must not be assumed to be permanently free, reliable, or available without restrictions.

---

# 11. Latency and Performance

The project has a target of **under 1.5 seconds from the end of the user's utterance to the first audible response**.

This is a design target, not an achieved result.

It must not be reported as measured performance unless supported by actual experiments.

## 11.1 Sources of latency

Potential contributors include:

- Speech-recognition inference.
- Intent interpretation.
- Query embedding.
- Vector retrieval.
- Structured filtering and selection.
- Additional LLM generation, when required.
- Response construction.
- Text-to-speech initialization and synthesis.
- Audio buffering and playback.

## 11.2 Performance methodology

Record timestamps for relevant pipeline stages and measure:

- End-of-utterance-to-first-audible-response latency.
- Per-stage latency.
- Median latency.
- P95 latency.
- Cold-start and warm-start performance.
- Speech-recognition accuracy.
- Intent and parameter extraction accuracy.
- Product retrieval quality.
- Constraint-satisfaction accuracy.
- Add-to-cart success and failure rates.
- Resource consumption under representative workloads.

Test representative shopping requests, including product names, numerical constraints, ambiguous references, and requests requiring clarification.

Record the hardware, software versions, model configuration, test conditions, and sample count.

A hypothetical latency budget may help planning, but it is not evidence of actual performance. Do not fabricate benchmark results or present estimated component timings as measurements.

The architecture review must assess whether the target is realistic for the selected local models and target hardware. If it is not, it should recommend evidence-based changes or propose a revised target for the project owner to approve.

---

# 12. Product Data, Session State, and Add-to-Cart

The application, not the LLM, owns authoritative application state.

The design must distinguish between:

- Conversation context.
- The current search results.
- The user's current selection.
- The minimum state needed to execute an add-to-cart request.
- Authoritative product and price information.

For example, “Add the second one” must resolve against the appropriate result list for the active session. It must not depend on an ambiguous conversational reference or unsupported model recollection.

## 12.1 Add-to-cart requirements

The current implementation must:

1. Resolve the requested product to a valid product identifier.
2. Validate the product and relevant attributes.
3. Confirm that the requested operation is supported.
4. Execute the operation through application-controlled logic.
5. Verify the resulting state.
6. Return an accurate confirmation or error.
7. Prevent one user's session state from leaking into another session.

The project requires only the minimum cart state and functionality needed to support this workflow.

Comprehensive cart management, durable cross-session cart persistence, full transaction handling, and checkout are not automatically required for the initial implementation.

## 12.2 Data ownership

Qdrant is the retrieval system, not automatically the authoritative product or cart database.

The implementation must establish an authoritative source for the structured product information required to validate selection and add-to-cart operations.

The storage technology and persistence requirements must be decided based on the repository, data model, and intended deployment.

For a future production implementation, evaluate durable cart state, transaction safety, idempotency, concurrency control, and recovery according to the actual persistence model.

Do not introduce a full transactional subsystem without a requirement that justifies it.

---

# 13. Safety, Security, and Privacy

VoiceCart is an action-oriented application. The model must not be treated as a trusted authority.

## 13.1 Required safety boundaries

1. Model output is an untrusted request.
2. Application code validates every action.
3. Product identifiers are checked against authoritative records.
4. Business rules are enforced by application code.
5. Add-to-cart operations are executed through controlled application interfaces.
6. Success is reported only after the outcome has been verified.
7. Invalid or ambiguous requests fail safely.
8. Session data remains isolated.
9. Audio and conversational data are not retained unnecessarily.
10. Any future payment processing remains outside the LLM's authority.

Prompt instructions alone are not a security boundary.

Retrieved product descriptions and user-provided text must be treated as untrusted input. Prompt injection or malicious catalogue content must not be allowed to bypass application validation.

## 13.2 Future production security

If the application is extended to production, review:

- Authentication and authorization.
- API input validation.
- Rate limiting.
- Secrets management.
- Logging and data minimization.
- Dependency and model security.
- Data retention.
- Access control for administrative operations.
- Transaction safety for future checkout.

These are requirements to evaluate, not claims that security controls have already been implemented.

---

# 14. Accessibility and Error Handling

Every normal interaction, error, and clarification path should converge on a usable spoken response.

The system should handle:

- Speech that cannot be transcribed reliably.
- Unsupported or unclear requests.
- Missing search constraints.
- No matching products.
- Retrieval failures.
- Missing or stale catalogue attributes.
- Invalid model output.
- Invalid product references.
- Add-to-cart failures.
- Text-to-speech failures.

Responses should be concise, understandable, and useful to a person who may not be looking at the screen.

The application must not claim that a product was added when the operation failed.

When the system cannot safely determine the user's intent, it should ask for clarification rather than guessing.

Accessibility must be validated throughout development, not postponed until the end.

---

# 15. Testing and Evaluation

Testing must cover individual components and the complete user workflow.

## 15.1 Speech recognition

Evaluate transcription quality across representative speech patterns, accents, product names, and numerical constraints.

Word Error Rate (WER) is:

`WER = (Substitutions + Deletions + Insertions) / Number of reference words`

Overall WER alone is insufficient. Errors involving product names, colours, quantities, and prices must also be evaluated because they can directly affect product selection.

## 15.2 Intent and parameter extraction

Test whether the application correctly identifies:

- Search intent.
- Product category.
- Price limits.
- Colour and other explicit attributes.
- Sorting or selection criteria.
- Add-to-cart intent.
- Ambiguity requiring clarification.

Evaluate valid outputs and malformed or unsupported model responses.

## 15.3 Retrieval

Evaluate retrieval using suitable metrics, including:

- Recall@K.
- Precision@K.
- nDCG@K.

Use representative queries and relevant-product judgments. Do not rely exclusively on vector similarity scores.

## 15.4 Business logic and add-to-cart

Test:

- Hard-constraint enforcement.
- Product-ID validation.
- Correct selection of the cheapest valid product.
- Handling of missing or stale product information.
- Session isolation.
- Correct add-to-cart behaviour.
- Failure handling.
- Prevention of unintended mutations.

## 15.5 End-to-end testing

Verify that spoken requests lead to the expected product results, safe add-to-cart operations, and understandable spoken responses.

Use fixture-based tests where possible so expected outcomes are reproducible.

Record actual results and limitations. Do not claim that the system is accurate, reliable, or production-ready without supporting evidence.

---

# 16. Development Approach

The project should follow an **iterative and incremental SDLC**.

Build a working increment, validate it using tests and realistic voice/accessibility conditions, and refine the next increment. Validate safety and accessibility continuously.

The following progression is proposed:

| Increment | Focus |
|---|---|
| Sprint 0 | Architecture, repository structure, interfaces, and implementation plan. |
| Sprint 1 | Product catalogue representation, ingestion, embeddings, and retrieval. |
| Sprint 2 | Intent interpretation, parameter extraction, validation, and orchestration. |
| Sprint 3 | Product filtering, selection, and the minimum add-to-cart functionality. |
| Sprint 4 | Speech recognition and text-to-speech integration. |
| Sprint 5+ | End-to-end testing, accessibility evaluation, and performance optimization. |

This progression is a proposal, not a statement that any sprint has been completed.

The implementation order may change if the architecture review identifies a more effective way to reduce risk or validate assumptions.

Do not implement future checkout or payment functionality as part of the initial increments.

---

# 17. Future Production Considerations

The initial implementation should remain appropriately scoped.

Potential future improvements include:

- A defined API boundary between the client and application.
- Durable cart and session persistence.
- Catalogue ingestion, update, and deletion workflows.
- Reliable embedding regeneration and vector-index updates.
- Model-serving isolation and resource management.
- Request validation and rate limiting.
- Structured logs and request correlation IDs.
- Per-stage latency and error metrics.
- Health checks, timeouts, and controlled retries.
- Backup and recovery.
- Model and dependency versioning.
- Authentication and authorization.
- Concurrency control and idempotent operations.
- Deployment and resource planning.
- Comprehensive cart management.
- Secure checkout and payment integration, if approved.

Do not assume that microservices, message queues, distributed caches, multiple databases, or an agent framework are inherently beneficial.

Every additional architectural layer must solve a specific problem and justify its operational and maintenance cost.

---

# 18. Mandatory Architecture Review by ChatGPT Pro

## 18.1 Objective

The project will be handed to a teammate who will use ChatGPT Pro to independently review the architecture before implementation.

The reviewing agent must conduct a thorough, evidence-based assessment of the selected models, runtimes, data stores, component boundaries, application flow, and potential architectural improvements.

The objective is to determine whether the current target architecture is appropriate for VoiceCart's requirements and, if not, what should change.

The agent must not merely validate the existing decisions.

It must investigate credible alternatives, identify missing responsibilities or unnecessary layers, and consider different ways to solve the underlying problem.

The current architecture is a baseline for evaluation, not an immutable design.

## 18.2 First inspect the repository

Before conducting the review:

1. Inspect the repository structure.
2. Read the existing source code, configuration, dependency files, tests, and documentation.
3. Establish whether anything has been implemented since this README was written.
4. Identify existing prototypes, dependencies, interfaces, and data structures.
5. Trace the actual application flow wherever code exists.
6. Identify the current catalogue representation and any existing retrieval configuration.
7. Record architectural decisions supported by code and distinguish them from assumptions.
8. Identify contradictions between the implementation, this README, and other project documentation.

Do not invent implementation details.

If a critical fact cannot be established, identify the uncertainty and explain how it affects the review.

The current baseline is pre-implementation, but the agent must still inspect the repository rather than assuming its state.

## 18.3 Conduct thorough external research

Use current, authoritative sources wherever possible.

Prioritize:

- Official model documentation.
- Official model repositories and model cards.
- Official inference-runtime documentation.
- Official vector database and storage documentation.
- Relevant technical papers.
- Reproducible performance evaluations.
- Licensing information.
- Credible engineering reports and independent comparisons.

Use community discussions as supplementary evidence when they reveal practical issues not covered by official documentation.

For significant sources, record:

- Source title.
- Direct URL.
- Publication or release date, where available.
- Date accessed.
- Relevant findings.
- Limitations.
- Impact on the architectural decision.

Do not rely exclusively on vendor marketing, leaderboard rankings, isolated anecdotes, or outdated comparisons.

Distinguish clearly between:

- Results reported by a source.
- Results measured in the VoiceCart repository.
- Third-party experimental results.
- Hypotheses requiring further experiments.

Do not claim to have run benchmarks, inspected code, or verified facts that were not actually examined.

## 18.4 Re-evaluate the selected technologies

The review must investigate every selected component and the assumptions behind it.

### A. Speech recognition

Current selection: `whisper.cpp`.

Investigate:

- Suitability for local, low-latency speech recognition.
- Model-size and quantization trade-offs.
- CPU and GPU requirements.
- Accuracy on relevant accents, product names, and numerical constraints.
- Streaming or incremental transcription capabilities, if needed.
- Alternative local models and runtimes.
- Whether a different model or audio-processing approach would be more appropriate.

Compare candidates against the actual workload, not only general-purpose speech benchmarks.

### B. Language model

Current selection: Qwen3 4B Instruct through Ollama.

Investigate:

- Suitability for intent classification and structured parameter extraction.
- Reliability of structured outputs.
- Performance on grounded product comparison and clarification.
- Whether a smaller model would reduce latency and resource consumption without unacceptable quality loss.
- Whether a larger model would provide a meaningful improvement.
- Whether another model family better suits the workload.
- Quantization, context length, inference configuration, and memory requirements.
- Runtime compatibility, concurrency, and cold-start behaviour.
- Whether one model should handle all language tasks or whether a deterministic classifier or specialized model would be more appropriate for some tasks.

Investigate the latest relevant model releases available at the time of the review.

Do not recommend a model solely because it has more parameters or performs well on unrelated benchmarks.

### C. Embeddings

Current selection: `BAAI/bge-small-en-v1.5`.

Investigate:

- Product-search retrieval quality.
- Model size and inference latency.
- English-only versus multilingual requirements.
- Alternative embedding models.
- Compatibility with the intended similarity metric and Qdrant configuration.
- Consistency between indexing and query preprocessing.
- Whether product names, attributes, descriptions, and queries need different preprocessing.
- Whether query rewriting or hybrid retrieval would improve results.

Consider the consequences of changing embedding models, including vector dimensions, collection configuration, re-indexing, and re-embedding catalogue records.

### D. Vector database and retrieval

Current selection: Qdrant.

Investigate:

- Suitability for the expected catalogue size and query patterns.
- Vector search and payload-filtering capabilities.
- Hybrid retrieval combining dense vectors with lexical search.
- Exact-match handling for product names, SKUs, brands, and identifiers.
- Structured filtering and deterministic ranking.
- Alternatives that may offer a better fit.
- Separation between catalogue storage and vector retrieval.
- Catalogue updates, deletions, and product variants.
- Whether a separate reranking stage is justified.

Do not recommend replacing the vector database merely because another system offers more features.

### E. Local inference runtime

Current selection: Ollama for language-model inference.

Investigate:

- Suitability for the development and intended deployment requirements.
- Resource management and concurrent requests.
- Model loading and unloading.
- Cold-start latency.
- Operational simplicity.
- Alternatives for serving local models.
- Whether different runtimes would benefit particular components.

Separate model quality from runtime performance. A better runtime does not necessarily imply a better model.

### F. Text-to-speech

Current direction: Piper local TTS.

Investigate:

- Naturalness and intelligibility.
- Language and voice availability.
- Time to first audio.
- CPU and memory requirements.
- Streaming or chunked output, if relevant.
- Model and voice licences.
- Alternative local TTS options.

Confirm the precise model and runtime choice before implementation.

### G. Application architecture and orchestration

Current direction: Python application with application-controlled orchestration and business logic.

Investigate:

- Whether a simple modular application is sufficient.
- Whether an explicit state machine or workflow graph would improve reliability.
- Whether an orchestration framework is justified.
- Whether additional API, service, caching, queue, or persistence layers are necessary.
- Whether the current design has unnecessary layers or missing responsibilities.
- Whether model inference should be isolated from application logic.
- Whether synchronous, asynchronous, or streaming execution is appropriate.
- Whether the proposed design is testable and maintainable without excessive complexity.

If recommending a framework or additional layer, explain the specific problem it solves and the operational cost it introduces.

Do not add layers merely because they are common in larger systems.

## 18.5 Explore alternative end-to-end architectures

Do not limit the review to replacing individual models.

Evaluate credible combinations of technologies and alternative application designs.

Potential research directions include:

- A fully local inference pipeline.
- Different combinations of local speech recognition, language models, embeddings, and TTS.
- A smaller specialized intent model paired with a separate conversational model.
- Deterministic handling of simple requests and LLM handling of complex requests.
- Dense retrieval combined with lexical or structured search.
- A dedicated reranking stage.
- Alternative catalogue representation or indexing strategies.
- State-machine-based orchestration.
- Streaming or incremental processing to reduce perceived latency.
- API or service boundaries where they provide clear benefits.
- Additional validation, caching, persistence, or observability layers.
- Removal of components that introduce complexity without meaningful value.

These are research directions, not predetermined recommendations.

Explore other credible approaches where the evidence suggests they are relevant.

For every serious alternative, explain:

1. How it works.
2. Which requirements it serves.
3. What it improves.
4. What it sacrifices.
5. Resource and operational implications.
6. Integration and migration costs.
7. How it should be tested.
8. Whether it is worth adopting for VoiceCart.

## 18.6 Preserve the project constraints

The review must preserve these requirements unless it explicitly identifies a constraint that requires a separate decision:

- Voice-first accessibility.
- Product search and add-to-cart as the initial functional scope.
- Local inference as the current target.
- No paid inference APIs in the current target architecture.
- Retrieval-first processing.
- Minimal unnecessary LLM calls.
- Application-controlled add-to-cart operations.
- Authoritative product and application state outside the LLM.
- Clarification when necessary.
- Safe failure behaviour.
- Session isolation and privacy.
- No comprehensive cart-management or checkout expansion without approval.
- No checkout or payment implementation in the initial scope.

If an alternative requires relaxing a constraint, identify the trade-off clearly.

Do not silently change the requirements.

## 18.7 Evaluate the complete system

Evaluate the architecture against:

- End-to-end latency.
- Per-stage latency.
- Retrieval relevance.
- Constraint-satisfaction accuracy.
- Intent and parameter extraction accuracy.
- Speech-recognition quality.
- Response grounding.
- Add-to-cart correctness.
- Memory and compute requirements.
- Local deployment complexity.
- Reliability and failure recovery.
- Privacy and security.
- Maintainability.
- Testability.
- Licensing.
- Upgrade and migration costs.

Consider cold starts, repeated requests, larger catalogues, and concurrent users where relevant.

Do not assume that improving an individual component necessarily improves the end-to-end system.

For example, a larger LLM might improve conversational quality while increasing latency enough to undermine the voice-first experience. A reranker might improve relevance while introducing a new inference bottleneck.

Recommendations must account for system-level interactions.

## 18.8 Develop a practical validation plan

The review must not end with theoretical recommendations.

For every major proposed change, specify:

- The problem being addressed.
- The hypothesis.
- The baseline.
- The alternative.
- The metrics to measure.
- The test dataset or request categories.
- Hardware and runtime conditions.
- Expected benefits.
- Possible regressions.
- Acceptance criteria.
- Evidence required before adoption.

Where numerical thresholds are not justified, explain how to establish them instead of inventing arbitrary values.

Prioritize experiments that could materially change the architectural decision.

## 18.9 Produce a reasoned recommendation

After evaluating the evidence, recommend:

- Which existing choices should remain.
- Which components should be reconfigured.
- Which components should be replaced, if any.
- Which new layers or responsibilities should be introduced.
- Which unnecessary layers should be removed.
- Which changes should be deferred.
- Which uncertainties require experiments before a decision can be made.

Separate high-confidence recommendations from speculative or low-confidence opportunities.

Prefer the simplest architecture that satisfies the requirements, but do not use simplicity as an excuse to ignore demonstrated correctness, performance, or reliability problems.

---

# 19. Mandatory Architecture-Review Deliverable: `Suggestions.md`

The architecture-review agent must create a new file named `Suggestions.md` in the project root.

**The agent must not modify this README, implement proposed changes, or modify unrelated project files as part of the review.**

The purpose of `Suggestions.md` is to provide:

- An auditable research record.
- A reasoned assessment of the current target architecture.
- A change-only diff.
- Reasons supporting each proposed change.
- A complete description of the recommended final architecture.
- An implementation roadmap.
- An explicit record of unresolved decisions.

The report must be sufficiently detailed for the project owner and another engineer to understand the reasoning and implement approved changes without needing to reconstruct the research.

## 19.1 Executive summary

Summarize:

- The architecture reviewed.
- The most important findings.
- Whether the current target architecture should be retained or changed.
- The most significant recommendations.
- Major unresolved questions.
- Recommended next steps.

Make the conclusion clear without requiring the reader to read the entire report first.

## 19.2 Repository and baseline assessment

Document:

- The actual repository structure relevant to the architecture.
- The current implementation status.
- Existing files, dependencies, prototypes, and tests.
- The application flow established by code inspection, if any.
- Existing interfaces and data boundaries.
- Available benchmark evidence.
- Discrepancies between the repository and this README.
- Important facts that could not be verified.

Clearly distinguish observations from assumptions.

Do not claim an application flow is implemented if it exists only as a proposed design.

## 19.3 Research log

Maintain a structured record of meaningful research.

Use a table with these fields:

| Field | Description |
|---|---|
| Research question | The architectural question investigated. |
| Source | Source title and direct URL where available. |
| Source type | Official documentation, model card, paper, benchmark, community discussion, or another category. |
| Date | Publication or release date where available, and access date. |
| Key finding | Relevant evidence obtained. |
| Relevance | How the evidence affects VoiceCart. |
| Limitation | Important limitations or uncertainty. |
| Decision impact | Whether the finding supports retaining, changing, or testing a component. |

Include citations throughout the report so the reviewer can verify important claims.

Document meaningful research rather than listing every page opened.

## 19.4 Architecture assessment and alternatives

Evaluate the current design and the strongest credible alternatives.

For each relevant component, explain:

- Current choice.
- Requirements and constraints.
- Alternative candidates.
- Comparative evidence.
- Advantages and disadvantages.
- Integration implications.
- Recommendation.
- Confidence level.
- Remaining validation requirements.

Include end-to-end architecture alternatives, not only isolated model comparisons.

## 19.5 Change-only diff

This section is mandatory.

Record **only what should change relative to the current target architecture**.

Do not repeat unchanged components merely to create a comprehensive architecture inventory.

For every proposed change, use the following format.

### Change ID: `ARCH-001`

**Component or layer:**  
Identify the relevant component, interface, model, runtime, data store, or architectural boundary.

**Current baseline:**  
State the existing choice or behaviour, supported by the README or repository evidence.

**Proposed change:**  
Describe the precise modification.

**Reason for change:**  
Explain the problem with the current approach and why the proposed alternative is preferable.

**Supporting research:**  
Cite the evidence supporting the recommendation.

**Expected benefits:**  
Describe the expected effect on quality, latency, reliability, maintainability, cost, privacy, or another relevant objective.

**Trade-offs and risks:**  
Explain regressions, additional complexity, migration costs, and new failure modes.

**Dependencies and migration:**  
Identify affected interfaces, configurations, models, collections, data, tests, and other components.

**Validation required:**  
Specify how the change should be tested and what evidence would justify adopting it.

**Priority:**  
High, medium, or low, with a brief justification.

**Confidence:**  
High, medium, or low, with a brief explanation.

Create one entry per meaningful architectural change.

If a component should remain unchanged, do not create a change entry for it. Record the decision to retain it in the assessment or final recommendation instead.

If a proposed change depends on an unverified assumption, label it as conditional.

If no change is justified for a component, say so in the assessment rather than manufacturing a diff.

Because the project is pre-implementation, the diff should be against the selected target architecture in this README, not against a fictional implemented system.

## 19.6 Reasons behind the diff

After the change-only diff, provide a consolidated explanation of the reasoning behind the proposed changes.

Address:

- Specific shortcomings or risks identified.
- Why existing choices are insufficient, if applicable.
- Why proposed alternatives are better suited to the requirements.
- Why plausible alternatives were rejected.
- Interactions between changes across different layers.
- Why the combined proposal is preferable to isolated changes.
- Evidence supporting important conclusions.
- Remaining uncertainties.

The objective is to make the proposed changes understandable and reviewable, not merely to list conclusions.

## 19.7 Final recommended architecture

Describe the complete recommended architecture after applying all proposed changes conceptually.

Include unchanged components as well as changed ones.

Provide:

1. A component and technology table.
2. The responsibility of every layer.
3. Interfaces between layers.
4. The authoritative source of product data.
5. Ownership of session and add-to-cart state.
6. Inference and retrieval responsibilities.
7. Validation and security boundaries.
8. Error-handling strategy.
9. Intended deployment model.
10. Rationale for each important architectural boundary.

If a choice remains unresolved, identify the candidates and the evidence required to decide between them.

Do not present an unresolved decision as final.

## 19.8 Final application flow

Provide a numbered end-to-end flow for a representative request, such as:

> Find the cheapest black backpack under ₹2,000 and add it to my cart.

Explain what each layer does and which component owns each decision.

Include the following stages where applicable:

1. Audio capture.
2. Speech recognition.
3. Intent and parameter extraction.
4. Input and schema validation.
5. Query construction and embedding.
6. Vector, lexical, or structured retrieval.
7. Structured filtering.
8. Optional reranking.
9. Deterministic selection or grounded comparison.
10. Clarification when needed.
11. Controlled add-to-cart operation.
12. Verification of the result.
13. Response construction.
14. Text-to-speech.
15. Error and recovery paths.

The flow must reflect the final recommendation, not merely reproduce the current architecture diagram.

Explain which steps can be skipped for simple requests and when additional LLM calls are justified.

Do not expand the flow into checkout or payment processing.

## 19.9 Layer-by-layer design details

Document the implementation-relevant details of the final proposal.

Cover:

- Model selection and configuration.
- Inference runtimes.
- Embedding generation and vector dimensions.
- Catalogue ingestion and updates.
- Vector collection and payload design.
- Retrieval and ranking.
- Structured validation.
- Orchestration and workflow state.
- Product and minimal cart data management.
- Session isolation.
- Response generation.
- Text-to-speech.
- Error handling.
- Observability.
- Testing.
- Deployment and resource requirements.

Include version, configuration, or migration considerations where supported by evidence.

Do not invent configuration values or claim that proposed changes have been implemented.

## 19.10 Performance and evaluation plan

Define a practical plan for comparing the baseline against recommended alternatives.

Include:

- End-to-end latency.
- Per-stage latency.
- Median and P95 latency.
- Speech-recognition quality.
- Intent and parameter extraction accuracy.
- Retrieval metrics.
- Hard-constraint satisfaction.
- Add-to-cart correctness.
- Resource consumption.
- Cold-start and warm-start behaviour.
- Concurrency testing where relevant.

Identify which measurements already exist and which still need to be collected.

Do not invent benchmark results.

## 19.11 Implementation roadmap

Convert the recommended diff into an ordered implementation plan.

For each step, identify:

- The change IDs it implements.
- Dependencies.
- Files or modules likely to be affected, where established through repository inspection.
- Tests to add or update.
- Risks and rollback considerations.
- Acceptance criteria.
- Whether the step is required immediately or can be deferred.

Prioritize correctness and high-impact improvements before optional optimizations.

Do not implement roadmap items as part of the architecture review.

## 19.12 Open questions and decision register

Record unresolved decisions that require additional evidence or explicit project-owner approval.

For each decision, state:

- The question.
- Available options.
- Relevant constraints.
- Evidence already collected.
- The experiment or information needed.
- Consequences of delaying the decision.

Distinguish genuine blockers from questions that can safely be resolved during implementation.

---

# 20. Review Rules and Completion Criteria

The architecture review is complete only when the agent has:

- Inspected the actual repository.
- Established the actual implementation status.
- Conducted substantive external research.
- Evaluated the selected models and tools.
- Considered alternative end-to-end architectures.
- Investigated whether additional layers are justified or unnecessary.
- Distinguished source-backed facts from assumptions.
- Produced a change-only diff.
- Explained the reasons behind every recommended change.
- Described the complete recommended architecture.
- Documented the end-to-end application flow.
- Identified performance and correctness validation requirements.
- Produced an ordered implementation roadmap.
- Recorded unresolved decisions.
- Created `Suggestions.md`.

### Non-negotiable rules

1. Do not modify `README.md` during the architecture review.
2. Create or update only `Suggestions.md` for the review deliverable, unless the project owner separately authorizes another file to be changed.
3. Do not implement architectural changes during the review.
4. Do not fabricate measurements, benchmark results, implementation status, citations, or research findings.
5. Do not assume that a popular technology is the best fit.
6. Do not recommend a change without explaining the problem it solves.
7. Do not introduce architectural layers without justifying their complexity.
8. Do not omit important alternatives merely because the current design already has a selected technology.
9. Do not change the local-inference or no-paid-inference-API constraints without explicitly identifying the change in assumptions.
10. Do not expand the initial functional scope into comprehensive cart management, checkout, or payment processing without approval.
11. Preserve application ownership of authoritative product and cart state.
12. Ensure that every recommendation can be traced to a requirement, repository observation, research finding, or clearly labelled hypothesis.
13. Do not describe the target architecture as implemented.
14. Do not treat recommendations in `Suggestions.md` as approved decisions until the project owner accepts them.

The goal is not to defend the existing architecture or replace components for the sake of novelty.

The goal is to determine, through careful research and engineering reasoning, which architecture best satisfies VoiceCart's accessibility, correctness, latency, privacy, cost, reliability, and maintainability requirements—and exactly what should change to achieve it.

---

# 21. Instructions for Future Coding Agents

Before making code changes:

1. Read this README and `Suggestions.md`, if present.
2. Inspect the existing source code, configuration, dependency files, and tests.
3. Confirm the actual implementation status.
4. Identify the requested scope.
5. Preserve established architectural boundaries unless the task explicitly authorizes changing them.
6. Explain consequential assumptions and ask for clarification when necessary.
7. Make scoped, testable changes.
8. Add or update tests for affected behaviour.
9. Report what changed, what was tested, and what remains unverified.

Do not treat proposed recommendations in `Suggestions.md` as implemented architecture.

The project owner must review and approve architectural recommendations before they become binding implementation decisions.

Do not assume that every technology listed in this README has already been integrated into the repository.

When implementation details remain uncertain, inspect the code and configuration before deciding.

When the requirements or documentation conflict, surface the conflict rather than silently inventing a requirement or technology choice.

---

# 22. Final Project Principles

Every implementation and architecture decision should preserve the following principles:

1. **Accessibility first:** Design around spoken interaction and minimize visual dependence.
2. **Retrieval before generation:** Retrieve relevant catalogue evidence rather than relying on model memory.
3. **Hybrid intelligence:** Use LLMs for language understanding and flexible explanation; use deterministic code for hard constraints and controlled operations.
4. **Authoritative application state:** Keep product truth and cart-operation outcomes outside the LLM.
5. **Safe action execution:** Validate model outputs and verify operations before reporting success.
6. **Minimal unnecessary inference:** Avoid extra model calls when deterministic processing or templates suffice.
7. **Local-first target:** Prefer local inference and avoid paid inference APIs under the current constraints.
8. **Measurable performance:** Treat latency and quality targets as hypotheses until measured.
9. **Incremental implementation:** Build and validate small, meaningful increments.
10. **Evidence-based architecture:** Research alternatives before making consequential architectural decisions.
11. **Controlled scope:** Implement product search and add-to-cart first; defer comprehensive cart management, checkout, and payments.
12. **No invented facts:** Distinguish selected designs, actual implementation, measured results, and future proposals.
13. **Simplicity with justification:** Avoid both unnecessary architectural complexity and oversimplification that compromises correctness or reliability.
14. **Explicit approval:** Keep architectural recommendations separate from approved implementation decisions.

**The immediate objective is to establish and validate the best practical architecture, then implement the product-search-to-add-to-cart workflow incrementally. No component should be considered implemented until it exists in the repository and has been verified.**