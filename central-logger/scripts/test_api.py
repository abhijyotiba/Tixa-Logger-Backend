"""
Test the logger API locally
Sends a sample log to verify everything works
"""
import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
API_KEY = "test_key_123"  # Match your .env

# Sample log payload
sample_log = {
    "environment": "production",
    "executed_at": datetime.utcnow().isoformat() + "Z",
    "workflow_version": "1.0.0",
    "ticket_id": "TICKET-TEST-001",
    "execution_time_seconds": 5.2,
    "status": "SUCCESS",
    "category": "billing_issue",
    "resolution_status": "resolved",
    "metrics": {
        "confidence": 0.95,
        "react_iterations": 3,
        "tools_used": 2,
        "nodes_executed": 5
    },
    "payload": {
        "trace": [
            {"node": "categorize", "timestamp": "2025-12-24T10:30:00Z"},
            {"node": "route", "timestamp": "2025-12-24T10:30:01Z"},
            {"node": "solve", "timestamp": "2025-12-24T10:30:05Z"}
        ],
        "final_response": "Issue resolved successfully"
    }
}

def test_health():
    """Test health endpoint"""
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_ingest():
    """Test log ingestion"""
    print("\n2. Testing log ingestion...")
    response = requests.post(
        f"{API_URL}/api/v1/logs",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        json=sample_log
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json().get("log_id")
    return None

def test_get_logs():
    """Test getting logs"""
    print("\n3. Testing get logs...")
    response = requests.get(
        f"{API_URL}/api/v1/logs?page=1&page_size=10",
        headers={"X-API-Key": API_KEY}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total logs: {data['pagination']['total']}")
    print(f"Returned: {len(data['data'])} logs")
    return response.status_code == 200

def test_metrics():
    """Test metrics endpoint"""
    print("\n4. Testing metrics...")
    response = requests.get(
        f"{API_URL}/api/v1/metrics/overview?days=7",
        headers={"X-API-Key": API_KEY}
    )
    print(f"Status: {response.status_code}")
    print(f"Metrics: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def main():
    print("=" * 60)
    print("Central Logger API Test")
    print("=" * 60)
    
    # Run tests
    health_ok = test_health()
    log_id = test_ingest()
    logs_ok = test_get_logs()
    metrics_ok = test_metrics()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Log Ingestion: {'✅' if log_id else '❌'}")
    print(f"Get Logs: {'✅' if logs_ok else '❌'}")
    print(f"Metrics: {'✅' if metrics_ok else '❌'}")
    
    if all([health_ok, log_id, logs_ok, metrics_ok]):
        print("\n🎉 All tests passed! Logger is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Test failed: {e}")
