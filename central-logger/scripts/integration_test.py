"""
Complete Integration Test
Tests the full workflow from client to logger to database
"""
import requests
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class IntegrationTest:
    """Complete integration test suite"""
    
    def __init__(self, logger_url="http://localhost:8000", api_key="test_key_123"):
        self.logger_url = logger_url
        self.api_key = api_key
        self.tests_passed = 0
        self.tests_failed = 0
    
    def log_test(self, name, passed, message=""):
        """Log test result"""
        if passed:
            print(f"  ✅ {name}")
            if message:
                print(f"     {message}")
            self.tests_passed += 1
        else:
            print(f"  ❌ {name}")
            if message:
                print(f"     {message}")
            self.tests_failed += 1
    
    def test_health_check(self):
        """Test 1: Health Check"""
        print("\n1️⃣  Testing Health Check...")
        try:
            response = requests.get(f"{self.logger_url}/health", timeout=5)
            passed = response.status_code == 200
            self.log_test(
                "Health check",
                passed,
                f"Status: {response.status_code}"
            )
            return passed
        except Exception as e:
            self.log_test("Health check", False, f"Error: {e}")
            return False
    
    def test_log_ingestion(self):
        """Test 2: Log Ingestion"""
        print("\n2️⃣  Testing Log Ingestion...")
        
        log_data = {
            "environment": "development",
            "executed_at": datetime.utcnow().isoformat() + "Z",
            "workflow_version": "1.0.0",
            "ticket_id": f"INTEGRATION-{int(time.time())}",
            "execution_time_seconds": 3.5,
            "status": "SUCCESS",
            "category": "integration_test",
            "resolution_status": "resolved",
            "metrics": {
                "confidence": 0.95,
                "react_iterations": 3,
                "tools_used": 2,
                "nodes_executed": 5
            },
            "payload": {
                "trace": [
                    {"node": "categorize", "timestamp": datetime.utcnow().isoformat()},
                    {"node": "route", "timestamp": datetime.utcnow().isoformat()},
                    {"node": "solve", "timestamp": datetime.utcnow().isoformat()}
                ],
                "final_response": "Integration test completed successfully"
            }
        }
        
        try:
            response = requests.post(
                f"{self.logger_url}/api/v1/logs",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=log_data,
                timeout=10
            )
            
            passed = response.status_code == 201
            self.log_test(
                "Log ingestion",
                passed,
                f"Status: {response.status_code}, Response: {response.json()}"
            )
            
            if passed:
                return log_data["ticket_id"], response.json().get("log_id")
            return None, None
            
        except Exception as e:
            self.log_test("Log ingestion", False, f"Error: {e}")
            return None, None
    
    def test_authentication(self):
        """Test 3: Authentication"""
        print("\n3️⃣  Testing Authentication...")
        
        # Test with wrong API key
        try:
            response = requests.post(
                f"{self.logger_url}/api/v1/logs",
                headers={
                    "X-API-Key": "wrong_key_123",
                    "Content-Type": "application/json"
                },
                json={
                    "environment": "development",
                    "executed_at": datetime.utcnow().isoformat() + "Z",
                    "status": "SUCCESS"
                },
                timeout=5
            )
            
            passed = response.status_code == 401
            self.log_test(
                "Invalid API key rejected",
                passed,
                f"Status: {response.status_code} (expected 401)"
            )
            
        except Exception as e:
            self.log_test("Authentication test", False, f"Error: {e}")
    
    def test_query_logs(self, ticket_id):
        """Test 4: Query Logs"""
        print("\n4️⃣  Testing Log Queries...")
        
        if not ticket_id:
            self.log_test("Query logs", False, "No ticket_id to query")
            return
        
        # Wait a moment for DB to be ready
        time.sleep(1)
        
        try:
            # Query by ticket_id
            response = requests.get(
                f"{self.logger_url}/api/v1/logs?ticket_id={ticket_id}",
                headers={"X-API-Key": self.api_key},
                timeout=10
            )
            
            passed = response.status_code == 200
            data = response.json() if passed else {}
            
            if passed and data.get("data"):
                found = any(log["ticket_id"] == ticket_id for log in data["data"])
                self.log_test(
                    "Query logs by ticket_id",
                    found,
                    f"Found {len(data['data'])} log(s)"
                )
            else:
                self.log_test(
                    "Query logs by ticket_id",
                    passed,
                    f"Status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Query logs", False, f"Error: {e}")
    
    def test_metrics(self):
        """Test 5: Metrics"""
        print("\n5️⃣  Testing Metrics...")
        
        try:
            response = requests.get(
                f"{self.logger_url}/api/v1/metrics/overview?days=7",
                headers={"X-API-Key": self.api_key},
                timeout=10
            )
            
            passed = response.status_code == 200
            
            if passed:
                metrics = response.json()["data"]
                print(f"     Total Tickets: {metrics['total_tickets']}")
                print(f"     Success Rate: {metrics['success_rate']}%")
                print(f"     Avg Time: {metrics['avg_execution_time']}s")
                print(f"     Errors: {metrics['error_count']}")
                
                # Validate metrics structure
                valid = all(key in metrics for key in [
                    'total_tickets', 'success_rate', 'avg_execution_time', 'error_count'
                ])
                
                self.log_test(
                    "Metrics endpoint",
                    valid,
                    "All expected metrics present"
                )
            else:
                self.log_test("Metrics endpoint", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Metrics endpoint", False, f"Error: {e}")
    
    def test_batch_ingestion(self):
        """Test 6: Batch Ingestion"""
        print("\n6️⃣  Testing Batch Ingestion...")
        
        logs = []
        for i in range(5):
            logs.append({
                "environment": "development",
                "executed_at": datetime.utcnow().isoformat() + "Z",
                "ticket_id": f"BATCH-{int(time.time())}-{i}",
                "status": "SUCCESS" if i % 2 == 0 else "ERROR",
                "execution_time_seconds": 2.5 + i * 0.5
            })
        
        try:
            response = requests.post(
                f"{self.logger_url}/api/v1/logs/batch",
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=logs,
                timeout=15
            )
            
            passed = response.status_code == 201
            
            if passed:
                result = response.json()
                self.log_test(
                    "Batch ingestion",
                    result.get("count") == 5,
                    f"Ingested {result.get('count', 0)}/5 logs"
                )
            else:
                self.log_test("Batch ingestion", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Batch ingestion", False, f"Error: {e}")
    
    def test_database_verification(self):
        """Test 7: Database Verification"""
        print("\n7️⃣  Testing Database Connection...")
        
        try:
            from app.db.database import SessionLocal
            from app.db.models import WorkflowLog
            
            db = SessionLocal()
            count = db.query(WorkflowLog).count()
            db.close()
            
            passed = count > 0
            self.log_test(
                "Database verification",
                passed,
                f"Found {count} log(s) in database"
            )
            
        except Exception as e:
            self.log_test("Database verification", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 70)
        print(" " * 20 + "INTEGRATION TEST SUITE")
        print("=" * 70)
        print(f"\nLogger URL: {self.logger_url}")
        print(f"API Key: {self.api_key[:10]}...")
        
        # Run tests
        if not self.test_health_check():
            print("\n❌ Logger API is not responding. Please start the server:")
            print("   uvicorn app.main:app --reload")
            return
        
        ticket_id, log_id = self.test_log_ingestion()
        self.test_authentication()
        self.test_query_logs(ticket_id)
        self.test_metrics()
        self.test_batch_ingestion()
        self.test_database_verification()
        
        # Summary
        print("\n" + "=" * 70)
        print(" " * 25 + "TEST SUMMARY")
        print("=" * 70)
        print(f"  ✅ Passed: {self.tests_passed}")
        print(f"  ❌ Failed: {self.tests_failed}")
        print(f"  📊 Total:  {self.tests_passed + self.tests_failed}")
        
        if self.tests_failed == 0:
            print("\n  🎉 ALL TESTS PASSED! Integration is working correctly.")
        else:
            print(f"\n  ⚠️  {self.tests_failed} test(s) failed. Check output above for details.")
        
        print("=" * 70)
        
        return self.tests_failed == 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Integration Test Suite")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Logger API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--api-key",
        default="test_key_123",
        help="API key for authentication (default: test_key_123)"
    )
    
    args = parser.parse_args()
    
    test = IntegrationTest(logger_url=args.url, api_key=args.api_key)
    success = test.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
