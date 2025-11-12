# Model Card – Mock Adapter

| Field | Value |
|-------|-------|
| Model name | `mock-primary-001` |
| Owners | Platform Architecture Team |
| Version | 0.1.0 |
| Date | 2025-11-07 |

## Intended use
- Demonstrate serverless scaffolding for GenAI workloads without reaching out to real providers.
- Provide deterministic, reproducible responses for CI and documentation screenshots.

## Out-of-scope use
- Production deployments that require privacy controls, factual accuracy, or latency SLAs.
- Benchmarking language models or comparing providers.

## Training data
- Synthetic, rule-based generation derived from the input prompt. No external training corpus.

## Evaluation
- Unit tests (`tests/test_model_service.py`) ensure control flow and metadata emission.
- Smoke tests validate HTTP integration and data persistence behavior.

## Limitations
- Deterministic output can feel repetitive and is not aligned to actual LLM quality.
- Does not enforce safety filters beyond simple prompt validation, leaving responsibility to client layers.

## Ethical considerations
- Encourage teams to replace this adapter with real providers plus policy enforcement frameworks (Bedrock Guardrails, content filters, etc.).
- See `docs/governance.md` for Responsible AI checklist steps tied to the overall solution.
