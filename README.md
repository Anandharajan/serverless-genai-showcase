# Serverless Generative AI Showcase

## 🚧 Project Status 🚧

**This project is currently under active development.**

**Latest progress**
- Infrastructure (`infra-architect`) and service layers (`service-engineer`) are complete and exercised directly through the domain services using the `GENAI_LOCAL_ONLY=1` JSON stores for fast feedback.
- Model registry flows now auto-activate newly registered adapters by default, and pytest coverage guards both the automatic and opt-out paths.
- SAM builds succeed locally; linting and tests run via `python -m ruff` and `python -m pytest`, keeping the repo CI-ready once the API comes online.

**Next steps to complete the project**
- Bring up LocalStack (or provision real AWS tables) and run `sam local start-api --env-vars infra/env.dev.json` so the HTTP API can be smoke tested end-to-end rather than through direct service calls.
- Update the `ci` workflow to mirror the local commands (`python -m ruff`, `python -m pytest`, `sam build`) and add a `sam local invoke` or smoke-test step gated on the LocalStack container.
- Once the local API is stable, finish the `ci-ops` backlog: wire the deploy workflow outputs into smoke tests, document the promotion checklist, and flip feature flags for production rollout.

## GitHub-hosted demo
- Use the [Demo workflow](https://github.com/Anandharajan/serverless-genai-showcase/actions/workflows/demo.yml) to spin up the SAM API inside GitHub Actions and run `scripts/smoke_test.py` against the `/v1/gen-text`, `/v1/rag-query`, and `/v1/agent-orchestrate` routes.
- From the **Actions** tab choose **Demo → Run workflow**, then watch the `Run local SAM demo` job for logs or download the `demo-sam-api-log` artifact for the captured API output.

---

Production-minded, serverless reference implementation that highlights LLM adapters, Retrieval Augmented Generation (RAG), lightweight agent orchestration, and governance guardrails with the AWS SAM CLI.

## Why this project exists
- Demonstrate how to ship opinionated GenAI workloads with infrastructure-as-code, CI/CD, observability, and governance artifacts that map to the “Generative AI Architect” job spec.
- Provide an end-to-end sample that can be deployed from the command line, poked locally with SAM, and inspected by platform/security teams.
- Offer pragmatic starter components (mock adapters, DynamoDB schemas, CloudWatch dashboards, model registry, cost tooling) that can be swapped with enterprise-grade providers.

## Architecture at a glance
- **HTTP API (Amazon API Gateway HTTP API)** fan-outs into independent Lambda functions for text generation, RAG Q&A, agent orchestration, model admin, and fine-tune hooks.
- **Persistence layer** uses four DynamoDB tables: `PromptHistory`, `ModelMetadata`, `AgentLifecycle`, and `RetrievalIndex`.
- **Model adapters** live in `services/adapters` and default to a mock adapter that keeps the repo dependency-free while exposing a clean interface for OpenAI, Bedrock, Anthropic, or custom models.
- **Observability**: every Lambda ships with X-Ray tracing enabled, structured logging, custom CloudWatch metrics (`GenAI/Usage` namespace), and a dashboard template (`cloudwatch-dashboard.json`).
- **Governance**: docs include Responsible AI checklist, NIST RMF mapping, EU AI Act readiness notes, a model card, whitepaper, and a CxO-facing one-pager PDF.
- **Automation**: GitHub Actions defines workflows (`build`, `local`, `deploy`, `lint`, `test`, `smoke`, `rollback`). GitHub Actions covers CI and protected deploys.


```
+-------------+       HTTPS        +-----------------------+
|   Clients   | -----------------> | Amazon API Gateway    |
+-------------+                    +-----------------------+
        |                                      |
        | invokes Lambda handlers (text/rag/agents/models/train)
        v
+---------------------------------------------+
| AWS Lambda Functions                        |
|  - GenTextFunction (/text)                  |
|  - RagQueryFunction (/rag)                  |
|  - AgentOrchestrator (/agents)              |
|  - AdminFunction (/models)                  |
|  - ModelTrainerHook (/train)                |
+---------------------+-----------------------+
                      |
                      v
        +-------------------------------+
        | DynamoDB Tables               |
        |  PromptHistory                |
        |  ModelMetadata                |
        |  AgentLifecycle               |
        |  RetrievalIndex               |
        +-------------------------------+
                      |
                      v
        +-------------------------------+
        | Step Functions Trainer State  |
        | Machine + CloudWatch/X-Ray    |
        +-------------------------------+
```



## Builder's blog-style walkthrough

### 1. Framing the challenge
Treat the repo like a real engagement from a platform team: ship a reusable Generative AI foundation that proves the ability to move from idea to AWS production patterns. That means a single place that talks about people, process, and tech, not just "here's some Lambda code".

### 2. Architecting like production
With the problem framed, the architecture diagram above became the contract. API Gateway fans out to purpose-built Lambdas, DynamoDB owns durability, and a Step Functions stub represents long-running training. Every resource, role, and environment variable lives in `infra/template.yaml`, so reviewers can diff exactly what reaches AWS.

### 3. Building & iterating
Adapters and domain services came first so the handlers stay thin. The mock adapter keeps demo runs deterministic while exposing seams for Bedrock or OpenAI. Data stores automatically fall back to local JSON, letting `sam local start-api` run without spinning up LocalStack. Automation scripts wrap common tasks (build, test, deploy) the same way a production CI/CD stack would.

### 4. Operating & governing
Production readiness means observability and accountability. X-Ray tracing, structured logging, and custom CloudWatch metrics (`GenAI/Usage`) ship by default. Governance artifacts - model card, NIST mapping, EU AI Act notes, Responsible AI checklist - live in `docs/` so security and legal reviewers have something concrete. There is also a CloudWatch dashboard template ready to import after deploy.

### 5. Outcomes & next experiments
Running the `/agents` endpoint locally (with `GENAI_LOCAL_ONLY=1`) produces sharable outputs; for example, run `4854ec6d-5441-4801-ab3b-2d1c1214e87f` completed a four-step plan for a student smart-campus assistant. From here the roadmap is clear: swap in a managed LLM adapter, extend the retrieval store to OpenSearch or Pinecone, and connect the Step Functions hook to a real fine-tune workflow. The repo shows exactly how to lead that journey in production.



## Repository layout

```
.
├── infra/
│   ├── template.yaml
│   └── env.dev.json
├── services/
│   ├── adapters/
│   ├── data/
│   ├── domain/
│   └── functions/
├── scripts/
│   ├── cost_estimator.py
│   └── deploy_helpers.sh
├── docs/
│   ├── governance.md
│   ├── model-card.md
│   ├── nist-rmf-mapping.md
│   ├── whitepaper.md
│   ├── examples.md
│   └── CxO-one-pager.pdf
├── tests/
├── cloudwatch-dashboard.json
└── .github/workflows/
```

## Getting started

### 1. Prerequisites and environment

- Host tools required (install once):
  - Docker and docker-compose
  - AWS CLI v2
  - Python 3.11, pip
  - SAM CLI (optional if running containerized)
  - jq, curl
- Repository location (example): ~/projects/genai-showcase
- Create a `.env` file at the root of the repository with the following content:
```env
STACK_NAME=genai-showcase-dev
AWS_REGION=ap-south-1
STAGE=dev
LOCALSTACK_EDGE_PORT=4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

### 2. Finalize infra and local resources

Validate SAM template:
```bash
pip install cfn-lint
cfn-lint infra/template.yaml
```

Create LocalStack compose and start LocalStack:
```bash
cat > docker-compose.localstack.yml <<'EOF'
version: "3.8"
services:
  localstack:
    image: localstack/localstack:latest
    environment:
      - SERVICES=lambda,dynamodb,apigateway,cloudwatch,iam,stepfunctions,secretsmanager,kms
      - DEFAULT_REGION=${AWS_REGION}
      - EDGE_PORT=${LOCALSTACK_EDGE_PORT}
    ports:
      - "${LOCALSTACK_EDGE_PORT}:4566"
EOF

docker compose -f docker-compose.localstack.yml up -d
```

Create DynamoDB tables and secrets in LocalStack (use AWS CLI with endpoint override):
```bash
export AWS_ENDPOINT_URL=http://localhost:${LOCALSTACK_EDGE_PORT}

aws --endpoint-url=$AWS_ENDPOINT_URL dynamodb create-table \
  --table-name genai-prompt-dev \
  --attribute-definitions AttributeName=requestId,AttributeType=S \
  --key-schema AttributeName=requestId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws --endpoint-url=$AWS_ENDPOINT_URL dynamodb create-table \
  --table-name genai-model-dev \
  --attribute-definitions AttributeName=modelId,AttributeType=S \
  --key-schema AttributeName=modelId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws --endpoint-url=$AWS_ENDPOINT_URL secretsmanager create-secret --name genai/provider/openai --secret-string '{"api_key":"mock-key"}'
```

### 3. Finish services, adapters, tracing, tests

Install dev deps:
```bash
python3 -m pip install -r requirements-dev.txt
```

Run unit tests:
```bash
pytest -q tests/unit
```

Build the SAM application (containerized build recommended):
```bash
sam build --use-container
```

### 4. Run locally
Run the API locally (SAM local; if using LocalStack, point calls to LocalStack DynamoDB):
Option A — host SAM available:
```bash
sam local start-api --env-vars infra/env.dev.json --port 3000
```
Option B — run inside build container:
```bash
docker run --rm -v "$(pwd)":/workspace -w /workspace public.ecr.aws/sam-cli-build-image-python3.11 \
  sh -c "sam local start-api --env-vars infra/env.dev.json --host 0.0.0.0 --port 3000"
```

Validate gen-text endpoint (example):
```bash
curl -sS -X POST http://localhost:3000/v1/gen-text \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Summarize serverless AI in one line","requestId":"smoke-req-1"}' | jq .
```

Check DynamoDB write via LocalStack:
```bash
aws --endpoint-url=$AWS_ENDPOINT_URL dynamodb get-item --table-name genai-prompt-dev --key '{"requestId":{"S":"smoke-req-1"}}'
```

### 5. Deploy to AWS (Optional)
```bash
sam build
sam deploy --stack-name ${STACK_NAME} --capabilities CAPABILITY_NAMED_IAM --parameter-overrides Stage=${STAGE}
```
Get API endpoint from CloudFormation outputs:
```bash
aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" --output text --region ${AWS_REGION}
```

## API surface

| Path      | Method | Description                                |
|-----------|--------|--------------------------------------------|
| `/text`   | POST   | Free-form generation or summarization      |
| `/rag`    | POST   | Retrieval augmented QA                     |
| `/agents` | POST   | Plans & executes basic multi-step actions  |
| `/models` | POST   | Register/switch/list models                |
| `/train`  | POST   | Enqueue fine-tune/evaluation job           |

See `docs/examples.md` for cURL samples and expected payloads/results.

## Observability & governance
- X-Ray tracing is enabled by default (`Tracing: Active`). When running locally with SAM, traces emit to console; in AWS they flow into the service map automatically.
- `services/observability/metrics.py` publishes custom metrics (`TokenUsageByModel`, `AgentRuntimeMs`) to `GenAI/Usage`. Local mode logs them instead.
- Import `cloudwatch-dashboard.json` via `aws cloudwatch put-dashboard` to visualize latency, error rate, DynamoDB RCUs/WCUs, and custom metrics.
- Governance artifacts live in `docs/` and cover Responsible AI checklists, model-card metadata, EU AI Act readiness, NIST RMF mappings, and architecture rationale.

## Testing & quality
- `pytest` executes service-level tests with in-memory stores.
- `ruff .` and `cfn-lint infra/template.yaml` runs Ruff on Python code and cfn-lint on `infra/template.yaml`.
- GitHub Actions (`.github/workflows/ci.yml`) enforces lint + tests on every PR; `deploy.yml` gates production deploys behind manual approval and OIDC.

## Roadmap & customization
- Swap `services/adapters/mock_adapter.py` with connectors to Bedrock, Vertex, or Azure OpenAI without touching handlers.
- Extend `scripts/cost_estimator.py` with live CloudWatch data to tighten cost governance.
- Plug `RetrievalIndexStore` into OpenSearch Serverless, Pinecone, or Aurora PostgreSQL with pgvector if DynamoDB embedded vectors are insufficient.

See `docs/whitepaper.md` for a deeper architectural narrative and `docs/governance.md` for risk mitigations before pushing to production.
