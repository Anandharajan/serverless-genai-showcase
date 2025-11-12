#!/usr/bin/env bash
set -euo pipefail

# Helper functions invoked by Codex/GitHub workflows.

STACK_NAME=${STACK_NAME:-genai-showcase}
STAGE=${STAGE:-dev}

function ensure_stack() {
  sam deploy \
    --stack-name "${STACK_NAME}" \
    --template-file infra/template.yaml \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --parameter-overrides StageName="${STAGE}"
}

function publish_dashboard() {
  aws cloudwatch put-dashboard \
    --dashboard-name "${STACK_NAME}-${STAGE}" \
    --dashboard-body file://cloudwatch-dashboard.json
}

function smoke() {
  ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text)
  curl -s "${ENDPOINT}/text" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"prompt":"hello","mode":"completion"}'
}

case "${1:-}" in
  ensure-stack) ensure_stack ;;
  dashboard) publish_dashboard ;;
  smoke) smoke ;;
  *)
    echo "Usage: $0 {ensure-stack|dashboard|smoke}"
    exit 1
    ;;
esac
