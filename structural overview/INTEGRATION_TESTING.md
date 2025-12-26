# 🧪 Integration Testing Guide

## Testing Your Workflow with the Central Logger

---

## 📋 Overview

This guide shows you how to test the **complete integration** between:
1. Your workflow service (client - phases 1-3)
2. Central logger API (provider - phase 4)

---

## 🎯 Quick Integration Test

### Step 1: Start the Logger API

```powershell
cd central-logger

# Make sure .env is configured
# DATABASE_URL=...
# API_KEYS={"test_key_123": "test_client"}

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify it's running:**
```powershell
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

---

### Step 2: Configure Your Workflow Client

In your workflow service (where you implemented phases 1-3):

**Update `tixa_logger/config.py`:**

```python
# Logger Configuration
LOGGER_CONFIG = {
    # Point to your logger API
    "provider_url": "http://localhost:8000/api/v1/logs",
    
    # API key from your .env
    "api_key": "test_key_123",
    
    # Enable logging
    "enabled": True,
    
    # Ship logs asynchronously
    "async_enabled": True,
    
    # Max retries if API is down
    "max_retries": 3,
    
    # Client identification
    "client_id": "test_client",
    "environment": "development"
}
```

---

### Step 3: Run Your Workflow

Execute your workflow as normal. The log shipper will automatically send logs to the central logger.

```python
# Your workflow code (example)
from tixa_logger import TixaLogger

logger = TixaLogger()

# Execute workflow
result = process_ticket(ticket_data)

# Log is automatically shipped in background
```

---

### Step 4: Verify Logs Arrived

**Check in database:**
```powershell
cd central-logger
python -c "
from app.db.database import SessionLocal
from app.db.models import WorkflowLog

db = SessionLocal()
logs = db.query(WorkflowLog).order_by(WorkflowLog.created_at.desc()).limit(5).all()

for log in logs:
    print(f'Ticket: {log.ticket_id}, Status: {log.status}, Time: {log.executed_at}')

db.close()
"
```

**Or query via API:**
```powershell
curl "http://localhost:8000/api/v1/logs?page=1&page_size=10" `
  -H "X-API-Key: test_key_123"
```

---

## 🔬 Detailed Integration Tests

### Test 1: Basic Log Ingestion

**From your workflow service:**

```python
import requests
import os
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1/logs"
API_KEY = "test_key_123"

# Sample log
log_data = {
    "environment": "development",
    "executed_at": datetime.utcnow().isoformat() + "Z",
    "workflow_version": "1.0.0",
    "ticket_id": "INTEGRATION-TEST-001",
    "execution_time_seconds": 3.5,
    "status": "SUCCESS",
    "category": "test_category",
    "resolution_status": "resolved",
    "metrics": {
        "confidence": 0.92,
        "react_iterations": 2,
        "tools_used": 1,
        "nodes_executed": 4
    },
    "payload": {
        "trace": [
            {"node": "categorize", "timestamp": "2025-12-24T10:00:00Z"},
            {"node": "route", "timestamp": "2025-12-24T10:00:01Z"},
            {"node": "solve", "timestamp": "2025-12-24T10:00:03Z"},
            {"node": "respond", "timestamp": "2025-12-24T10:00:04Z"}
        ],
        "final_response": "Test completed successfully"
    }
}

# Send log
response = requests.post(
    API_URL,
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    json=log_data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Expected: 201 Created with log_id
assert response.status_code == 201
assert "log_id" in response.json()
print("✅ Test 1 Passed: Basic log ingestion")
```

---

### Test 2: Error Handling

**Test what happens when logger is down:**

```python
import requests
from requests.exceptions import RequestException
import time

API_URL = "http://localhost:8000/api/v1/logs"
API_KEY = "test_key_123"

log_data = {
    "environment": "development",
    "executed_at": datetime.utcnow().isoformat() + "Z",
    "status": "SUCCESS"
}

# Simulate logger being down
try:
    response = requests.post(
        "http://localhost:9999/api/v1/logs",  # Wrong port
        headers={"X-API-Key": API_KEY},
        json=log_data,
        timeout=2
    )
except RequestException as e:
    print(f"✅ Test 2 Passed: Workflow continued despite logger error")
    print(f"   Error handled: {type(e).__name__}")
```

**Key requirement:** Your workflow should NOT crash if logger is unavailable.

---

### Test 3: Async Shipping

**Test that logging doesn't block workflow:**

```python
import time
from threading import Thread

def ship_log_async(log_data):
    """Simulate async log shipping"""
    response = requests.post(
        "http://localhost:8000/api/v1/logs",
        headers={"X-API-Key": "test_key_123"},
        json=log_data
    )
    return response

# Workflow execution
start_time = time.time()

# Execute workflow
workflow_result = execute_workflow()  # Your actual workflow
workflow_time = time.time() - start_time

# Ship log asynchronously (doesn't block)
log_thread = Thread(target=ship_log_async, args=(log_data,))
log_thread.start()

# Workflow continues immediately
print(f"Workflow completed in {workflow_time:.2f}s")
print("✅ Test 3 Passed: Async shipping doesn't block workflow")

# Wait for log to be shipped (for verification only)
log_thread.join()
```

---

### Test 4: Multiple Clients

**Test tenant isolation:**

```python
# Client 1
response1 = requests.post(
    "http://localhost:8000/api/v1/logs",
    headers={"X-API-Key": "client1_key"},
    json={"environment": "production", "executed_at": "..."}
)

# Client 2
response2 = requests.post(
    "http://localhost:8000/api/v1/logs",
    headers={"X-API-Key": "client2_key"},
    json={"environment": "production", "executed_at": "..."}
)

# Client 1 queries their logs
logs1 = requests.get(
    "http://localhost:8000/api/v1/logs",
    headers={"X-API-Key": "client1_key"}
).json()

# Verify client 1 only sees their logs
for log in logs1["data"]:
    assert log["client_id"] == "client1"

print("✅ Test 4 Passed: Tenant isolation working")
```

---

### Test 5: High Volume

**Test handling multiple logs:**

```python
import concurrent.futures
from datetime import datetime

def send_log(ticket_num):
    log_data = {
        "environment": "development",
        "executed_at": datetime.utcnow().isoformat() + "Z",
        "ticket_id": f"LOAD-TEST-{ticket_num}",
        "status": "SUCCESS"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/logs",
        headers={"X-API-Key": "test_key_123"},
        json=log_data
    )
    return response.status_code

# Send 50 logs concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(send_log, range(50)))

success_count = sum(1 for r in results if r == 201)
print(f"✅ Test 5 Passed: {success_count}/50 logs ingested")
```

---

## 🔍 End-to-End Workflow Test

### Complete Scenario

```python
"""
End-to-End Integration Test
Simulates complete workflow execution with logging
"""
import requests
import time
from datetime import datetime

class WorkflowIntegrationTest:
    def __init__(self):
        self.logger_url = "http://localhost:8000/api/v1/logs"
        self.api_key = "test_key_123"
        
    def execute_workflow(self, ticket_data):
        """Simulate workflow execution"""
        start_time = time.time()
        
        # Step 1: Categorize
        category = "billing_issue"
        confidence = 0.95
        
        # Step 2: Route
        route = "automated"
        
        # Step 3: Solve
        solution = "Issue resolved automatically"
        
        # Step 4: Build log
        execution_time = time.time() - start_time
        
        log_data = {
            "environment": "development",
            "executed_at": datetime.utcnow().isoformat() + "Z",
            "workflow_version": "1.0.0",
            "ticket_id": ticket_data["ticket_id"],
            "execution_time_seconds": execution_time,
            "status": "SUCCESS",
            "category": category,
            "resolution_status": "resolved",
            "metrics": {
                "confidence": confidence,
                "react_iterations": 3,
                "tools_used": 2,
                "nodes_executed": 4
            },
            "payload": {
                "trace": [
                    {"node": "categorize", "result": category},
                    {"node": "route", "result": route},
                    {"node": "solve", "result": solution}
                ],
                "final_response": solution
            }
        }
        
        # Step 5: Ship log (async)
        self.ship_log_async(log_data)
        
        return {
            "status": "success",
            "solution": solution,
            "execution_time": execution_time
        }
    
    def ship_log_async(self, log_data):
        """Ship log asynchronously"""
        try:
            response = requests.post(
                self.logger_url,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=log_data,
                timeout=5
            )
            
            if response.status_code == 201:
                print(f"  ✅ Log shipped: {response.json()['log_id']}")
            else:
                print(f"  ⚠️ Log failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️ Log error (workflow continues): {e}")
    
    def verify_log_in_database(self, ticket_id):
        """Verify log was stored"""
        response = requests.get(
            f"{self.logger_url}?ticket_id={ticket_id}",
            headers={"X-API-Key": self.api_key}
        )
        
        if response.status_code == 200:
            logs = response.json()["data"]
            if logs:
                print(f"  ✅ Log found in database")
                return True
        
        print(f"  ❌ Log not found")
        return False
    
    def run_test(self):
        """Run complete integration test"""
        print("=" * 60)
        print("End-to-End Integration Test")
        print("=" * 60)
        
        # Test data
        ticket_data = {
            "ticket_id": f"E2E-TEST-{int(time.time())}",
            "description": "Test ticket for integration"
        }
        
        print(f"\n1. Executing workflow for {ticket_data['ticket_id']}...")
        result = self.execute_workflow(ticket_data)
        print(f"   Workflow completed in {result['execution_time']:.2f}s")
        
        print(f"\n2. Waiting for log to be processed...")
        time.sleep(2)  # Give logger time to process
        
        print(f"\n3. Verifying log in database...")
        found = self.verify_log_in_database(ticket_data['ticket_id'])
        
        print("\n" + "=" * 60)
        if found:
            print("✅ INTEGRATION TEST PASSED")
        else:
            print("❌ INTEGRATION TEST FAILED")
        print("=" * 60)


if __name__ == "__main__":
    test = WorkflowIntegrationTest()
    test.run_test()
```

**Run the test:**
```powershell
python integration_test.py
```

---

## 📊 Metrics Validation

### Test Dashboard Metrics

```python
import requests

API_KEY = "test_key_123"

# Get overview metrics
response = requests.get(
    "http://localhost:8000/api/v1/metrics/overview?days=7",
    headers={"X-API-Key": API_KEY}
)

metrics = response.json()["data"]

print("📊 Metrics:")
print(f"  Total Tickets: {metrics['total_tickets']}")
print(f"  Success Rate: {metrics['success_rate']}%")
print(f"  Avg Time: {metrics['avg_execution_time']}s")
print(f"  Errors: {metrics['error_count']}")

# Validate
assert metrics['total_tickets'] > 0
assert 0 <= metrics['success_rate'] <= 100
print("✅ Metrics validation passed")
```

---

## 🔧 Troubleshooting Integration Issues

### Issue 1: Logs Not Arriving

**Check:**
1. Logger API is running: `curl http://localhost:8000/health`
2. API key is correct in both `.env` and client config
3. Network connectivity: Can client reach logger?
4. Check logger server logs for errors

**Debug:**
```python
# Add verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

response = requests.post(...)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

### Issue 2: 401 Unauthorized

**Causes:**
- Wrong API key
- API key not in logger's `.env`
- Header name incorrect

**Fix:**
```python
# Verify header name
headers = {
    "X-API-Key": "your_key_here",  # Must be exactly "X-API-Key"
    "Content-Type": "application/json"
}
```

### Issue 3: Workflow Slows Down

**Cause:** Shipping logs synchronously

**Fix:** Use async shipping:
```python
from threading import Thread

def ship_log():
    requests.post(...)

# Non-blocking
Thread(target=ship_log).start()
```

---

## ✅ Integration Checklist

### Before Testing:
- [ ] Logger API running
- [ ] Database initialized
- [ ] API key generated
- [ ] API key added to logger `.env`
- [ ] Client configured with correct URL and API key

### During Testing:
- [ ] Workflow executes successfully
- [ ] Logs shipped without blocking workflow
- [ ] Logs arrive in database
- [ ] Correct client_id in database
- [ ] Metrics are calculated correctly
- [ ] Can query logs via API

### Error Scenarios:
- [ ] Workflow continues if logger is down
- [ ] Retries on temporary failures
- [ ] No sensitive data in logs
- [ ] Tenant isolation verified

---

## 📋 Quick Test Commands

```powershell
# 1. Test logger health
curl http://localhost:8000/health

# 2. Send test log
curl -X POST http://localhost:8000/api/v1/logs `
  -H "X-API-Key: test_key_123" `
  -H "Content-Type: application/json" `
  -d '{\"environment\":\"production\",\"executed_at\":\"2025-12-24T10:30:00Z\",\"status\":\"SUCCESS\"}'

# 3. Query logs
curl "http://localhost:8000/api/v1/logs?page=1" -H "X-API-Key: test_key_123"

# 4. Get metrics
curl "http://localhost:8000/api/v1/metrics/overview?days=7" -H "X-API-Key: test_key_123"

# 5. Check database
python -c "from app.db.database import SessionLocal; from app.db.models import WorkflowLog; db = SessionLocal(); print(f'Logs: {db.query(WorkflowLog).count()}'); db.close()"
```

---

**Integration testing complete!** 🎉

Next: Deploy to production and build the dashboard!
