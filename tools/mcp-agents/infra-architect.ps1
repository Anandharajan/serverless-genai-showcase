# infra-architect.ps1

# Tear down existing localstack container to ensure a clean state
docker compose -f docker-compose.localstack.yml down --remove-orphans

# Check for .env file and create if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "The .env file is missing. Creating it with default values."
    $envContent = @"
STACK_NAME=genai-showcase-dev
AWS_REGION=ap-south-1
STAGE=dev
LOCALSTACK_EDGE_PORT=4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
"@
    Set-Content -Path ".env" -Value $envContent
}

# Load environment variables from .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^(.*?)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        Set-Item -Path "env:$name" -Value $value
    }
}

# 1. Validate SAM template (SKIPPED FOR NOW)
# pip install cfn-lint
# ... cfn-lint command ...


# 2. Create LocalStack compose and start LocalStack
$composeFile = "docker-compose.localstack.yml"
docker compose --env-file .env -f $composeFile up -d

# 3. Create DynamoDB tables and secrets in LocalStack
$env:AWS_ENDPOINT_URL = "http://localhost:$($env:LOCALSTACK_EDGE_PORT)"

# Add a small delay to give localstack time to start
Start-Sleep -Seconds 15

Write-Host "--- Creating resources with Boto3 ---"
$pythonCode = @'
import boto3
import os

endpoint_url = os.environ.get('AWS_ENDPOINT_URL')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_region = os.environ.get('AWS_REGION')

dynamodb = boto3.client('dynamodb', endpoint_url=endpoint_url, region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
secretsmanager = boto3.client('secretsmanager', endpoint_url=endpoint_url, region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

try:
    dynamodb.create_table(
        TableName='genai-prompt-dev',
        AttributeDefinitions=[{'AttributeName': 'requestId', 'AttributeType': 'S'}],
        KeySchema=[{'AttributeName': 'requestId', 'KeyType': 'HASH'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print('--- Created DynamoDB table genai-prompt-dev ---')
except Exception as e:
    print(f'Error creating table genai-prompt-dev: {e}')

try:
    dynamodb.create_table(
        TableName='genai-model-dev',
        AttributeDefinitions=[{'AttributeName': 'modelId', 'AttributeType': 'S'}],
        KeySchema=[{'AttributeName': 'modelId', 'KeyType': 'HASH'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print('--- Created DynamoDB table genai-model-dev ---')
except Exception as e:
    print(f'Error creating table genai-model-dev: {e}')

try:
    secretsmanager.create_secret(
        Name='genai/provider/openai',
        SecretString='{"api_key":"mock-key"}'
    )
    print('--- Created Secret genai/provider/openai ---')
except Exception as e:
    print(f'Error creating secret genai/provider/openai: {e}')
'@
python -c $pythonCode
Write-Host "--- Boto3 script finished ---"


# 4. Emit infra checkpoint
if (-not (Test-Path "tools/checkpoints")) {
    New-Item -ItemType Directory -Path "tools/checkpoints"
}
$checkpoint = @{
    checkpoint = "infra-ready"
    PromptTable = "genai-prompt-dev"
    ModelTable = "genai-model-dev"
}
$checkpoint | ConvertTo-Json | Out-File -FilePath "tools/checkpoints/infra.json" -Encoding utf8
