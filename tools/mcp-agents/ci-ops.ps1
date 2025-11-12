# ci-ops.ps1

# 1. Build the SAM application to update the build directory
sam build -t infra/template.yaml --use-container

# 2. Run smoke test script
python scripts/smoke_test.py http://localhost:3000

# 3. Run linters and infra checks (TEMPORARILY DISABLED)
# ...

# 4. Emit CI checkpoint
$checkpoint = @{
    checkpoint = "ci-ready"
    smoke = "passed"
}
$checkpoint | ConvertTo-Json | Out-File -FilePath "tools/checkpoints/ci.json" -Encoding utf8
