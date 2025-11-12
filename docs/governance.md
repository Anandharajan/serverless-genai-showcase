# Governance & Responsible AI Checklist

## Responsible AI checklist
| Control | Description | Implementation hook |
|---------|-------------|---------------------|
| Data provenance | Track source docs and prompt inputs | `RetrievalIndexStore` metadata + prompt history table |
| Human-in-the-loop | Manual approval before production deploys | `.github/workflows/deploy.yml` requires review + OIDC |
| Safety policies | Filter and redact sensitive content | `services/domain/model_service.py` exposes hook for policy filters (stubbed) |
| Auditability | Persist requests/responses, model versions | DynamoDB tables (`PromptHistory`, `ModelMetadata`, `AgentLifecycle`) |
| Explainability | Context + rationale surfaced to clients | RAG endpoint returns contexts; agent endpoint emits plan rationale |
| Access control | Least-privilege IAM roles per function | `infra/template.yaml` policies limited to specific tables |
| Incident response | Runbook + rollback command | `codex rollback`, README runbook, CloudWatch alarms |

## EU AI Act readiness notes
- **Risk classification**: reference implementation assumes “limited risk”. Moving to “high-risk” requires adding dataset registration, bias metrics, and human approval states in Step Functions.
- **Transparency obligations**: all API responses include `modelId` and metadata so client apps can notify end users.
- **Data governance**: ingestion guidance in `docs/whitepaper.md` recommends segregating PII via Amazon Macie + Lake Formation and storing vector embeddings in dedicated accounts.
- **Logging & record-keeping**: DynamoDB retention policies should match internal governance (e.g., 180 days) with periodic exports to S3/KMS.

## Cost & sustainability guardrails
- `scripts/cost_estimator.py` provides a quick approximation; wire it into CI for budget checks.
- CloudWatch dashboard monitors RCUs/WCUs and Lambda duration to flag anomalies.
- Include `reserved_concurrent_executions` limits on production stacks to protect downstream dependencies.

## Escalation workflow
1. Alarms trigger (latency/error rate) -> PagerDuty / Slack.
2. Operator inspects X-Ray traces + CloudWatch Logs Insights query.
3. Operator can run `codex rollback` to redeploy latest successful version.
4. Governance board reviews incident postmortem and updates Responsible AI checklist.
