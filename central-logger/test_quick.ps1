# Quick API Test Script

$apiKey = "0CXp-UvBsS3IKQICPBQSg0kIb-8IKqykg1XsEFUtVEQ"
$baseUrl = "http://localhost:8000"

Write-Host "`n=== Testing Central Logger API ===" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ Health Check: $($health.status)" -ForegroundColor Green
    Write-Host "   Service: $($health.service)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Ingest Log
Write-Host "`n2. Testing Log Ingestion..." -ForegroundColor Yellow
try {
    $headers = @{
        'X-API-Key' = $apiKey
        'Content-Type' = 'application/json'
    }
    
    $logData = @{
        environment = "production"
        workflow_version = "v1.0"
        ticket_id = "TEST-001"
        executed_at = "2025-12-24T12:00:00Z"
        execution_time_seconds = 1.5
        status = "SUCCESS"
        category = "info"
        metrics = @{
            cpu_usage = 45.2
            memory_mb = 512
        }
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/logs" -Method POST -Headers $headers -Body $logData
    Write-Host "✅ Log Created: $($response.id)" -ForegroundColor Green
    Write-Host "   Client: $($response.client_id)" -ForegroundColor Gray
    $logId = $response.id
} catch {
    Write-Host "❌ Log Ingestion Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Get Log by ID
Write-Host "`n3. Testing Get Log by ID..." -ForegroundColor Yellow
try {
    $log = Invoke-RestMethod -Uri "$baseUrl/api/v1/logs/$logId" -Method GET -Headers @{'X-API-Key'=$apiKey}
    Write-Host "✅ Retrieved Log: $($log.ticket_id)" -ForegroundColor Green
    Write-Host "   Status: $($log.status)" -ForegroundColor Gray
    Write-Host "   Category: $($log.category)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Get Log Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Query Logs
Write-Host "`n4. Testing Query Logs..." -ForegroundColor Yellow
try {
    $logs = Invoke-RestMethod -Uri "$baseUrl/api/v1/logs?page=1&page_size=10" -Method GET -Headers @{'X-API-Key'=$apiKey}
    Write-Host "✅ Query Logs: Found $($logs.total) total logs" -ForegroundColor Green
    Write-Host "   Page: $($logs.page)/$($logs.pages)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Query Logs Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Get Metrics
Write-Host "`n5. Testing Metrics Endpoint..." -ForegroundColor Yellow
try {
    $metrics = Invoke-RestMethod -Uri "$baseUrl/api/v1/metrics/overview" -Method GET -Headers @{'X-API-Key'=$apiKey}
    Write-Host "✅ Metrics Retrieved" -ForegroundColor Green
    Write-Host "   Total Logs: $($metrics.total_logs)" -ForegroundColor Gray
    Write-Host "   Success Rate: $($metrics.success_rate)%" -ForegroundColor Gray
    Write-Host "   Avg Execution Time: $($metrics.avg_execution_time)s" -ForegroundColor Gray
} catch {
    Write-Host "❌ Metrics Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== All Tests Complete! ===" -ForegroundColor Cyan
Write-Host "`nView API docs at: http://localhost:8000/docs" -ForegroundColor Yellow
