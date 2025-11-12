import sys
import requests
import os
import boto3
from botocore.config import Config

def main():
    if len(sys.argv) < 2:
        print("Usage: python smoke_test.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    request_id = "smoke-test-req-123"

    # 1. Test gen-text endpoint
    print("Testing /v1/gen-text...")
    try:
        response = requests.post(
            f"{base_url}/v1/gen-text",
            json={"prompt": "Summarize serverless AI in one line", "requestId": request_id},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("/v1/gen-text PASSED")
        print(response.json())
        assert "X-Amzn-Trace-Id" in response.headers or "X-Trace-Id" in response.headers
        print("Trace ID found in headers.")
    except (requests.exceptions.RequestException, AssertionError) as e:
        print(f"/v1/gen-text FAILED: {e}")
        sys.exit(1)

    # 2. Test rag-query endpoint
    print("\nTesting /v1/rag-query...")
    try:
        response = requests.post(
            f"{base_url}/v1/rag-query",
            json={"query": "What is serverless AI?", "requestId": f"{request_id}-rag"},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("/v1/rag-query PASSED")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"/v1/rag-query FAILED: {e}")
        sys.exit(1)

    # 3. Test agent-orchestrate endpoint
    print("\nTesting /v1/agent-orchestrate...")
    try:
        response = requests.post(
            f"{base_url}/v1/agent-orchestrate",
            json={"task": "Plan a trip to the moon", "requestId": f"{request_id}-agent"},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("/v1/agent-orchestrate PASSED")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"/v1/agent-orchestrate FAILED: {e}")
        sys.exit(1)


    # 4. Check DynamoDB for the created item
    print("\nChecking DynamoDB for created item...")
    try:
        # Assuming localstack is running
        endpoint_url = f"http://localhost:{os.environ.get('LOCALSTACK_EDGE_PORT', '4566')}"
        config = Config(
            region_name = os.environ.get('AWS_REGION', 'ap-south-1'),
            signature_version = 'v4',
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            }
        )
        dynamodb = boto3.client('dynamodb', endpoint_url=endpoint_url, config=config, aws_access_key_id='test', aws_secret_access_key='test')
        item = dynamodb.get_item(
            TableName='genai-prompt-dev',
            Key={'requestId': {'S': request_id}}
        )
        assert 'Item' in item
        print("DynamoDB check PASSED")
        print(item['Item'])
    except Exception as e:
        print(f"DynamoDB check FAILED: {e}")
        sys.exit(1)

    print("\nSmoke test completed successfully!")

if __name__ == "__main__":
    main()