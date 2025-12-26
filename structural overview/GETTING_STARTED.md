# 🚀 Getting Started - Complete Walkthrough

## Your Complete Guide to Setting Up and Testing the Central Logger

---

## 📋 What You'll Do

1. **Set up the database** (5 minutes)
2. **Generate API keys** (2 minutes)
3. **Start the logger API** (1 minute)
4. **Test everything works** (3 minutes)
5. **Integrate with your workflow** (5 minutes)

**Total time: ~15 minutes** ⏱️

---

## 🎯 Step 1: Database Setup

### Option A: Supabase (Recommended for Quick Start)

1. **Go to [supabase.com](https://supabase.com)** and sign up (free)

2. **Create a new project:**
   - Project name: `central-logger`
   - Database password: Choose a strong password
   - Region: Closest to you

3. **Wait ~2 minutes** for database to be ready

4. **Get connection string:**
   - Go to **Settings → Database**
   - Find "Connection string" → URI
   - Copy it (looks like: `postgresql://postgres:...@db.xxx.supabase.co:5432/postgres`)

5. **Add to your `.env` file:**
   ```powershell
   cd central-logger
   copy .env.example .env
   notepad .env
   ```

  Edit the file:
  ```env
  DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@db.xxx.supabase.co:5432/postgres
  API_KEYS={"test_key_123": "test_client"}
  ```

   ⚠️ **Important:** Use `+psycopg` after `postgresql`

### Option B: Local PostgreSQL (If you have it installed)

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/logger_db
API_KEYS={"test_key_123": "test_client"}
```

### Option C: Docker (Everything in one command)

```powershell
cd central-logger
docker-compose up -d
```

Then skip to Step 3! ✨

---

## 🎯 Step 2: Initialize Database

```powershell
cd central-logger

# Make sure you're in the right directory
pwd

# Install dependencies (if not done yet)
pip install -r requirements.txt

# Initialize database
python scripts\init_db.py
```

**Expected output:**
```
Initializing database tables...
✅ Database initialized successfully!
Tables created: workflow_logs
```

❌ **If you get an error:**
- Check your `DATABASE_URL` in `.env`
- Make sure database is running
- Check connection with: `python -c "from app.db.database import engine; engine.connect(); print('OK')"`

---

## 🎯 Step 3: Generate API Keys

```powershell
# Generate API key for your client
python scripts\generate_api_key.py
```

**Follow the prompts:**
```
Client ID: my_workflow_client
Client Name: My Workflow Service
```

**The script will:**
- Generate a secure API key
- Show you the key (save it!)
- Offer to update `.env` automatically (say yes!)

**Example output:**
```
✅ API Key Generated Successfully!

Client ID:   my_workflow_client
API Key:     Xh2k9_LmPqR8v3W7nY4tZ1aC5dE6fG-HiJkLmNoPqRsT

📝 Your updated .env configuration:
API_KEYS={"Xh2k9_LmPqR8v3W7nY4tZ1aC5dE6fG-HiJkLmNoPqRsT": "my_workflow_client"}

💾 Automatically update .env file? (y/N): y
```

✅ **Save the API key** - you'll give this to your workflow client

---

## 🎯 Step 4: Start the Logger API

```powershell
cd central-logger

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting central-logger in development mode
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

🎉 **Your logger is now running!**

**Keep this terminal open** - it needs to stay running

---

## 🎯 Step 5: Test Everything

Open a **new terminal** and run:

```powershell
cd central-logger
python scripts\integration_test.py
```

**This will test:**
- ✅ Health check
- ✅ Log ingestion
- ✅ Authentication
- ✅ Querying logs
- ✅ Metrics
- ✅ Batch ingestion
- ✅ Database verification

**Expected output:**
```
======================================================================
                     INTEGRATION TEST SUITE
======================================================================

1️⃣  Testing Health Check...
  ✅ Health check
     Status: 200

2️⃣  Testing Log Ingestion...
  ✅ Log ingestion
     Status: 201, Response: {'status': 'success', 'log_id': '...'}

[... more tests ...]

======================================================================
                        TEST SUMMARY
======================================================================
  ✅ Passed: 7
  ❌ Failed: 0
  📊 Total:  7

  🎉 ALL TESTS PASSED! Integration is working correctly.
======================================================================
```

---

## 🎯 Step 6: Manual Testing (Optional but Recommended)

### Test 1: Health Check

```powershell
curl http://localhost:8000/health
```

**Expected:**
```json
{"status":"healthy","service":"central-logger","environment":"development"}
```

### Test 2: Send a Log

```powershell
curl -X POST http://localhost:8000/api/v1/logs `
  -H "X-API-Key: test_key_123" `
  -H "Content-Type: application/json" `
  -d '{
    "environment": "production",
    "executed_at": "2025-12-24T10:30:00Z",
    "ticket_id": "MANUAL-TEST-001",
    "status": "SUCCESS",
    "execution_time_seconds": 3.5,
    "category": "test",
    "metrics": {"confidence": 0.95},
    "payload": {"trace": []}
  }'
```

**Expected:**
```json
{"status":"success","log_id":"...","message":"Log ingested successfully"}
```

### Test 3: Query Logs

```powershell
curl "http://localhost:8000/api/v1/logs?page=1&page_size=5" `
  -H "X-API-Key: test_key_123"
```

**Expected:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 5,
    "total": 2,
    "pages": 1
  }
}
```

### Test 4: Get Metrics

```powershell
curl "http://localhost:8000/api/v1/metrics/overview?days=7" `
  -H "X-API-Key: test_key_123"
```

**Expected:**
```json
{
  "data": {
    "total_tickets": 2,
    "success_rate": 100.0,
    "avg_execution_time": 3.5,
    "error_count": 0
  }
}
```

---

## 🎯 Step 7: Integrate with Your Workflow

### In Your Workflow Service

1. **Install the client library** (if you have one, or use requests):
   ```powershell
   pip install requests
   ```

2. **Add configuration:**
   ```python
   # config.py or .env in your workflow service
   LOGGER_API_URL = "http://localhost:8000/api/v1/logs"
   LOGGER_API_KEY = "your_api_key_here"  # From Step 3
   ```

3. **Send logs from your workflow:**
   ```python
   import requests
   import os
   from datetime import datetime
   
   def ship_log(log_data):
       """Ship log to central logger"""
       try:
           response = requests.post(
               os.getenv("LOGGER_API_URL"),
               headers={
                   "X-API-Key": os.getenv("LOGGER_API_KEY"),
                   "Content-Type": "application/json"
               },
               json=log_data,
               timeout=5
           )
           
           if response.status_code == 201:
               print(f"✅ Log shipped: {response.json()['log_id']}")
           else:
               print(f"⚠️ Log failed: {response.status_code}")
               
       except Exception as e:
           # Important: Don't crash workflow if logger fails
           print(f"⚠️ Logger unavailable: {e}")
   
   # Usage in your workflow
   log_data = {
       "environment": "production",
       "executed_at": datetime.utcnow().isoformat() + "Z",
       "ticket_id": ticket_id,
       "status": "SUCCESS",
       "execution_time_seconds": execution_time,
       "category": category,
       "metrics": {...},
       "payload": {...}
   }
   
   # Ship async (don't block workflow)
   from threading import Thread
   Thread(target=ship_log, args=(log_data,)).start()
   ```

---

## ✅ Verification Checklist

After completing all steps:

- [ ] Database created and initialized
- [ ] `.env` file configured with DATABASE_URL
- [ ] API key generated
- [ ] Logger API running on port 8000
- [ ] Health check returns 200
- [ ] Can ingest logs (test with curl)
- [ ] Can query logs
- [ ] Metrics endpoint works
- [ ] Integration test passes
- [ ] Workflow client configured

---

## 🎉 You're Done!

Your central logger is now:
- ✅ Running and accepting logs
- ✅ Storing logs in PostgreSQL
- ✅ Providing APIs for queries and metrics
- ✅ Ready for integration with your workflow

---

## 🔥 Quick Commands Reference

```powershell
# Start logger API
uvicorn app.main:app --reload

# Run integration tests
python scripts\integration_test.py

# Generate API key
python scripts\generate_api_key.py

# Check health
curl http://localhost:8000/health

# View logs in database
python -c "from app.db.database import SessionLocal; from app.db.models import WorkflowLog; db = SessionLocal(); logs = db.query(WorkflowLog).limit(5).all(); [print(f'{l.ticket_id}: {l.status}') for l in logs]"

# Count logs
python -c "from app.db.database import SessionLocal; from app.db.models import WorkflowLog; db = SessionLocal(); print(f'Total logs: {db.query(WorkflowLog).count()}')"
```

---

## 🆘 Troubleshooting

### "Cannot connect to database"
- Check `DATABASE_URL` in `.env`
- Verify database is running
- Test: `python -c "from app.db.database import engine; engine.connect()"`

### "Table does not exist"
- Run: `python scripts\init_db.py`

### "401 Unauthorized"
- Check API key in request matches `.env`
- Header must be exactly: `X-API-Key`

### "Logger not responding"
- Make sure server is running: `uvicorn app.main:app --reload`
- Check port 8000 is not in use

---

## 📚 Next Steps

Now that your logger is running:

1. **Deploy to production:**
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for Render, Railway, or Docker deployment

2. **Build the dashboard (Phase 5):**
   - Create React/Next.js frontend
   - Display metrics, log lists, and trace views

3. **Monitor and scale:**
   - Set up uptime monitoring
   - Add alerts
   - Scale horizontally as needed

---

## 📖 Documentation

- **[API_KEY_GUIDE.md](API_KEY_GUIDE.md)** - Complete API key management
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Detailed database setup
- **[INTEGRATION_TESTING.md](INTEGRATION_TESTING.md)** - Testing workflows
- **[README.md](README.md)** - Full project documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment

---

**🎊 Congratulations! Your logging infrastructure is ready!**

Questions? Check the documentation above or reach out for help.
