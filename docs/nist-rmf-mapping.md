# NIST AI RMF Mapping

| RMF Function | Showcase Capability | Notes |
|--------------|--------------------|-------|
| Govern | Responsible AI checklist, CI guardrails, CODEOWNERS, manual deploy approvals | `docs/governance.md`, `.github/workflows/deploy.yml` |
| Map | README architecture overview, `docs/whitepaper.md`, cost estimator, CxO one-pager | Ensures stakeholders understand scope and assumptions |
| Measure | CloudWatch dashboard, custom metrics (`GenAI/Usage`), tests measuring control flow | Extend with load testing + human evals for higher assurance |
| Manage | SAM rollback command, incident workflow, Step Functions trainer stub, model registry | Supports lifecycle + change management |

## Controls detail
- **Data management**: DynamoDB schemas preserve attribution; extend with S3 lineage tracking + Glue catalogs before productionizing.
- **Model risk**: Admin endpoint registers metadata (provider, type, cost) enabling curated allow-lists.
- **Monitoring**: X-Ray + CloudWatch capture traces/metrics; template ready for alarms on latency, errors, and DynamoDB throttling.
- **Response**: `scripts/deploy_helpers.sh` automates smoke tests + rollback triggers to shorten MTTR.
