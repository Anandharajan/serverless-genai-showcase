# Serverless Generative AI Showcase – Technical Whitepaper

## Executive summary
This reference solution demonstrates how to operationalize Generative AI workloads on AWS using fully managed services (Lambda, API Gateway, DynamoDB, Step Functions) and modern developer tooling (Codex CLI, SAM CLI, GitHub Actions). The goal is to give architects an end-to-end example that marries experimentation speed with production guardrails.

## Design principles
1. **Serverless first** – pay per request, leverage managed scaling, and minimize infrastructure toil.
2. **Adapter pattern everywhere** – all model interactions route through `services/adapters`, making it trivial to switch from mock logic to Bedrock, OpenAI, or on-prem models.
3. **Observability baked in** – X-Ray tracing, structured logs, and custom CloudWatch metrics ensure that every request has telemetry breadcrumbs.
4. **Governance as code** – IAM policies, deployment workflows, Responsible AI checklists, and documentation are versioned alongside the application.

## Data & control flow
1. Client issues HTTPS request to the API Gateway HTTP API.
2. API Gateway invokes the corresponding Lambda function (text, RAG, agent, admin, trainer).
3. The handler relies on domain services to call adapters, persist state to DynamoDB, and emit metrics.
4. Responses bubble back to clients with trace-friendly metadata (model ID, tokens used, prompt IDs).
5. Step Functions orchestrates longer-running fine-tune/evaluation jobs by calling the trainer Lambda.

## Deployment model
- **Local development**: `sam local start-api` with JSON file persistence under `/tmp/genai-showcase`.
- **Continuous integration**: GitHub Actions workflow installs dependencies, runs Ruff + pytest, builds SAM artifacts, and surfaces coverage/logs.
- **Continuous delivery**: Deployment workflow assumes AWS IAM via OIDC, runs smoke tests, updates CloudWatch dashboard, and waits for manual approval before touching production stages.

## Security considerations
- Functions run with least-privilege IAM policies that only allow CRUD access to their DynamoDB tables plus observability APIs.
- For production, secrets such as provider API keys belong in AWS Secrets Manager; handlers reference them via environment variables/ARNs.
- Multi-tenant isolation can be accomplished by namespacing table keys with tenant IDs and pinning IAM roles per tenant or per workload.

## Extensibility roadmap
- Replace `RetrievalIndexStore` with OpenSearch Serverless or RDS + pgvector for semantic search at scale.
- Wire `TrainingService` into SageMaker pipelines or Bedrock model-tuning APIs when the mock adapter is swapped.
- Bolt on human feedback loops by extending the Step Functions definition with manual approval states.
- Integrate Bedrock Guardrails or custom moderation endpoints before responses leave the Lambda handler.

## Conclusion
The showcase is intentionally approachable yet complete: it lets teams run demos in minutes while keeping a clear path to enterprise features (compliance, cost controls, partner integrations). Use it as a blueprint for kickoff projects, technical interviews, or internal enablement workshops.
