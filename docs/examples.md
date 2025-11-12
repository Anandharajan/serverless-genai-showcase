# Example API Calls

Use `sam local start-api` (or a deployed endpoint) and run the following cURL commands.

## Text generation
```bash
curl -X POST "$API_URL/text" \
  -H "Content-Type: application/json" \
  -d '{
        "prompt": "Summarize the architecture of the showcase.",
        "mode": "summarize",
        "userId": "demo-user"
      }'
```

## RAG Q&A
```bash
curl -X POST "$API_URL/rag" \
  -H "Content-Type: application/json" \
  -d '{
        "question": "How do we observe GenAI workloads?",
        "documents": [
          {"docId": "obs", "content": "CloudWatch dashboard + X-Ray tracing."}
        ]
      }'
```

## Agent orchestration
```bash
curl -X POST "$API_URL/agents" \
  -H "Content-Type: application/json" \
  -d '{
        "goal": "Prepare a readiness summary",
        "context": {"audience": "CxO"}
      }'
```

## Model administration
```bash
curl -X POST "$API_URL/models" \
  -H "Content-Type: application/json" \
  -d '{
        "action": "register",
        "modelId": "bedrock-titan-1",
        "provider": "bedrock",
        "costPer1kTokens": 0.012
      }'
```

## Fine-tune hook
```bash
curl -X POST "$API_URL/train" \
  -H "Content-Type: application/json" \
  -d '{
        "dataset": "finance-docs",
        "evaluationMetric": "factuality"
      }'
```
