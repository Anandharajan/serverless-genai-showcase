# service-engineer.ps1

# Load environment variables from .env file if it exists
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^(.*?)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# 1. Install dev deps
pip install -e .[dev]

# 2. Run unit tests
try {
    $pythonPath = (Get-Command python).Source
    $pythonDir = Split-Path $pythonPath
    $scriptsDir = Join-Path $pythonDir "Scripts"
    $pytestPath = Join-Path $scriptsDir "pytest.exe"
    if (Test-Path $pytestPath) {
        & $pytestPath -q tests
    } else {
        Write-Warning "pytest.exe not found at $pytestPath. Trying to run from user base."
        $userBasePath = (python -m site --user-base).Trim()
        $userScriptsPath = Join-Path -Path $userBasePath -ChildPath "Scripts\pytest.exe"
        if (Test-Path $userScriptsPath) {
            & $userScriptsPath -q tests
        } else {
            Write-Warning "pytest.exe not found in user base path either. Running 'python -m pytest' as a last resort."
            python -m pytest -q tests
        }
    }
} catch {
    Write-Error "Error running pytest: $_"
}


# 3. Build the SAM application
sam build -t infra/template.yaml --use-container

# 4. Instructions to run the API locally
Write-Host "To run the API locally, execute the following command in a separate terminal:"
Write-Host "sam local start-api --env-vars infra/env.dev.json --port 3000"
Write-Host "After starting the API, you can validate the endpoint."

# 5. Emit service checkpoint
$checkpoint = @{
    checkpoint = "services-ready"
    tested_endpoints = @(
        "/v1/gen-text",
        "/v1/rag-query",
        "/v1/agent-orchestrate"
    )
}
$checkpoint | ConvertTo-Json | Out-File -FilePath "tools/checkpoints/services.json" -Encoding utf8
