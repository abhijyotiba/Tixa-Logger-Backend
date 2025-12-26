# 🎯 Central Logger - Complete Setup Guide

## Quick Start (5 Minutes)

### 1️⃣ Install Dependencies
```powershell
cd central-logger
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Configure Environment
```powershell
# Copy template
copy .env.example .env

# Edit .env (use your PostgreSQL URL)
notepad .env
```

**Minimum .env configuration:**
```env
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/logger_db
API_KEYS={"test_key_123": "client_1"}
ENVIRONMENT=development
```

### 3️⃣ Setup Database
```powershell
# Option A: Using provided script
python scripts\init_db.py

# Option B: Using Python directly
python -c "from app.db.database import init_db; init_db()"
```

### 4️⃣ Run the Server
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5️⃣ Test the API
```powershell
# In a new terminal
python scripts\test_api.py
```

**Done!** 🎉 Your logger is running at `http://localhost:8000`

---

## 📋 What You Get

### ✅ Complete Backend API
- **Log Ingestion:** `POST /api/v1/logs`
- **Query Logs:** `GET /api/v1/logs`
- **Log Detail:** `GET /api/v1/logs/{id}`
- **Metrics:** `GET /api/v1/metrics/overview`
- **Category Stats:** `GET /api/v1/metrics/categories`
- **Health Check:** `GET /health`

### ✅ Security Built-In
- API key authentication
- Tenant isolation (client-based filtering)
- CORS protection
- Error handling
- Input validation

### ✅ Production Ready
- PostgreSQL with JSONB support
- Indexed queries for performance
- Pagination
- Flexible schema (evolves with your needs)
- Docker support
- Deployment guides

---

## 🔌 Integrate with Your Workflow

### Update Your Client (Workflow App)

In your workflow's log shipper configuration:

```python
# tixa_logger/config.py
LOGGER_CONFIG = {
    "provider_url": "http://localhost:8000/api/v1/logs",  # Your logger URL
    "api_key": "test_key_123",  # API key from .env
    "enabled": True
}
```

That's it! Your workflow will now send logs to the central logger.

---

## 🗂️ Project Structure

```
central-logger/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── api/
│   │   ├── ingest.py          # POST /logs (write)
│   │   ├── read_logs.py       # GET /logs (read)
│   │   └── metrics.py         # GET /metrics (analytics)
│   ├── auth/
│   │   └── api_key_auth.py    # API key validation
│   ├── db/
│   │   ├── database.py        # DB connection
│   │   └── models.py          # SQLAlchemy models
│   ├── services/
│   │   └── log_service.py     # Business logic
│   └── utils/
│       └── validators.py      # Pydantic schemas
├── scripts/
│   ├── init_db.py             # Database setup
│   └── test_api.py            # API testing
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── README.md
└── DEPLOYMENT.md
```

---

## 🎮 Usage Examples

### Ingest a Log
```bash
curl -X POST http://localhost:8000/api/v1/logs \
  -H "X-API-Key: test_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "production",
    "executed_at": "2025-12-24T10:30:00Z",
    "ticket_id": "TICKET-123",
    "status": "SUCCESS",
    "execution_time_seconds": 5.2,
    "category": "billing_issue",
    "metrics": {"confidence": 0.95},
    "payload": {"trace": []}
  }'
```

### Query Logs
```bash
curl "http://localhost:8000/api/v1/logs?status=SUCCESS&page=1&page_size=10" \
  -H "X-API-Key: test_key_123"
```

### Get Metrics
```bash
curl "http://localhost:8000/api/v1/metrics/overview?days=7" \
  -H "X-API-Key: test_key_123"
```

---

## 🐳 Docker Quick Start

### Option 1: Docker Compose (Easiest)
```powershell
# Start everything (logger + postgres)
docker-compose up -d

# Initialize database
docker-compose exec logger python scripts/init_db.py

# View logs
docker-compose logs -f logger

# Stop
docker-compose down
```

### Option 2: Docker Only
```powershell
# Build
docker build -t central-logger .

# Run (requires external database)
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e API_KEYS='{"key":"client"}' \
  central-logger
```

---

## 📊 Database Schema

### Main Table: `workflow_logs`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `client_id` | TEXT | Tenant identifier |
| `environment` | TEXT | prod/staging/dev |
| `ticket_id` | TEXT | Workflow ticket ID |
| `executed_at` | TIMESTAMP | Execution time |
| `execution_time_seconds` | FLOAT | Duration |
| `status` | TEXT | SUCCESS/ERROR/FAILED |
| `category` | TEXT | Ticket category |
| `metrics` | JSONB | Flexible metrics |
| `payload` | JSONB | Full trace data |
| `created_at` | TIMESTAMP | Log created time |

**Indexes:**
- `(client_id, executed_at)` - Time-series queries
- `(client_id, status)` - Status filtering
- `ticket_id`, `status`, `category` - Individual lookups

---

## 🔐 Security Configuration

### Generate Strong API Keys
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Configure API Keys
In `.env`:
```env
# Development: Simple dictionary
API_KEYS={"test_key_123": "client_1", "abc456def": "client_2"}

# Production: Move to database or secrets manager
```

### CORS Configuration
In `.env`:
```env
# Development
ALLOWED_ORIGINS=["http://localhost:3000"]

# Production
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

---

## 🧪 Testing

### Automated Tests
```powershell
python scripts\test_api.py
```

### Manual Testing
1. **Health Check:**
   ```powershell
   curl http://localhost:8000/health
   ```

2. **API Documentation:**
   Visit `http://localhost:8000/docs` (development only)

3. **Database Verification:**
   ```sql
   SELECT COUNT(*) FROM workflow_logs;
   SELECT * FROM workflow_logs ORDER BY created_at DESC LIMIT 10;
   ```

---

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides:
- **Render** - Easiest managed deployment
- **Railway** - Auto-scaling, pay-per-use
- **Docker** - Self-hosted
- **Supabase** - Managed PostgreSQL

### Quick Deploy to Render
1. Push code to GitHub
2. Create PostgreSQL database on Render
3. Create Web Service from repo
4. Set environment variables
5. Deploy!

---

## 📈 What's Next?

### ✅ Phase 4 Complete
- [x] Log ingestion API
- [x] Authentication
- [x] Database storage
- [x] Read endpoints
- [x] Metrics API

### 🎯 Phase 5: Dashboard (Next Step)
- [ ] React/Next.js frontend
- [ ] Overview metrics page
- [ ] Log list with filters
- [ ] Detailed trace viewer
- [ ] Category analytics charts

### 🔮 Future Enhancements
- Real-time log streaming
- Alerting system
- Advanced analytics
- ML-based insights
- Custom retention policies
- Log archival

---

## 🆘 Troubleshooting

### Server Won't Start
```powershell
# Check Python version
python --version  # Need 3.10+

# Check dependencies
pip list | findstr fastapi

# Check environment
type .env
```

### Database Connection Fails
```powershell
# Test connection
python -c "from app.db.database import engine; engine.connect()"

# Check DATABASE_URL format
# postgresql+psycopg://user:pass@host:port/dbname
```

### API Returns 401
- Verify API key in `.env` matches request header
- Check header name: `X-API-Key` (case-sensitive)
- Ensure API_KEYS format: `{"key": "client_id"}`

### Logs Not Showing
- Check client log shipper is enabled
- Verify API endpoint URL is correct
- Check server logs for errors
- Verify database has rows: `SELECT COUNT(*) FROM workflow_logs;`

---

## 📞 Need Help?

1. Check [README.md](README.md) for full documentation
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
3. Check server logs: Look at terminal output
4. Test with curl: Use examples above
5. Verify database: Query workflow_logs table

---

## 🎉 Success Indicators

Your logger is working correctly when:
- ✅ Server starts without errors
- ✅ Health check returns 200
- ✅ Log ingestion returns 201
- ✅ Logs appear in database
- ✅ Metrics return valid data
- ✅ Client workflow continues if logger is down

---

**Status:** ✅ Phase 4 Complete - Production Ready

**Built with:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic

**Next:** Build the dashboard (Phase 5) to visualize your logs!
