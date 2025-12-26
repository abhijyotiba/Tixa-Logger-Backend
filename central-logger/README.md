# Central Logger

> **Provider-side log collection and analytics service for workflow monitoring**

A production-ready logging infrastructure that receives, stores, and serves workflow execution logs with built-in authentication, tenant isolation, and analytics capabilities.

---

## 🏗️ Architecture

```
Client Workflow → [HTTPS] → Logger API → PostgreSQL → Dashboard
                    ↓
                 Auth + Validate + Store
```

**What this service does:**
- ✅ Accepts logs from workflow clients
- ✅ Authenticates via API keys
- ✅ Stores logs in PostgreSQL with JSONB
- ✅ Provides read APIs for dashboards
- ✅ Enforces tenant isolation

**What this service does NOT do:**
- ❌ Execute workflows
- ❌ Transform data
- ❌ Real-time streaming (yet)
- ❌ Heavy analytics (yet)

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+ (or Supabase)
- pip

### 2. Installation

```bash
# Clone or navigate to project
cd central-logger

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
# Required: DATABASE_URL, API_KEYS
```

**Example .env:**
```env
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/logger_db
SERVICE_NAME=central-logger
ENVIRONMENT=development
API_KEY_HEADER=X-API-Key
API_KEYS={"test_key_123": "client_1"}
```

### 4. Database Setup

```bash
# Initialize database tables
python -c "from app.db.database import init_db; init_db()"

# Or use Alembic for migrations (recommended for production)
alembic init migrations
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

### 5. Run the Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: `http://localhost:8000`

API docs: `http://localhost:8000/docs` (development only)

---

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| `POST` | `/api/v1/logs` | Ingest single log | API Key |
| `POST` | `/api/v1/logs/batch` | Batch ingestion | API Key |
| `GET` | `/api/v1/logs` | Query logs (paginated) | API Key |
| `GET` | `/api/v1/logs/{id}` | Get log detail | API Key |
| `GET` | `/api/v1/metrics/overview` | Dashboard metrics | API Key |
| `GET` | `/api/v1/metrics/categories` | Category breakdown | API Key |
| `GET` | `/health` | Health check | None |

### Authentication

All API endpoints (except `/health`) require an API key:

```bash
curl -X POST http://localhost:8000/api/v1/logs \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 📊 Database Schema

### `workflow_logs` table

```sql
id                       UUID PRIMARY KEY
client_id                TEXT (indexed)
environment              TEXT (indexed)
workflow_version         TEXT
ticket_id                TEXT (indexed)
executed_at              TIMESTAMPTZ (indexed)
execution_time_seconds   FLOAT
status                   TEXT (indexed)
category                 TEXT (indexed)
resolution_status        TEXT
metrics                  JSONB
payload                  JSONB
created_at               TIMESTAMPTZ (indexed)
```

**Indexes:**
- `idx_client_executed` (client_id, executed_at)
- `idx_client_status` (client_id, status)
- `idx_environment_executed` (environment, executed_at)

---

## 🔐 Security

### API Key Management

**Development:**
- Store in `.env` file
- Format: `{"key": "client_id"}`

**Production:**
- Store in database with hashing
- Rotate regularly
- Use secrets manager (AWS Secrets Manager, etc.)

### Tenant Isolation

Every query automatically filters by `client_id`:
- Clients can only see their own logs
- Enforced at service layer
- No cross-tenant data leakage

### Best Practices

- ✅ Use HTTPS in production
- ✅ Rate limit ingestion endpoint
- ✅ Monitor for unusual patterns
- ✅ Log access attempts
- ✅ Regular security audits

---

## 🧪 Testing

### Test Ingestion

```bash
# Test log ingestion
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

### Test Queries

```bash
# Get logs
curl -X GET "http://localhost:8000/api/v1/logs?page=1&page_size=10" \
  -H "X-API-Key: test_key_123"

# Get metrics
curl -X GET "http://localhost:8000/api/v1/metrics/overview?days=7" \
  -H "X-API-Key: test_key_123"
```

---

## 📦 Deployment

### Option 1: Render

1. Create PostgreSQL database on Render
2. Create Web Service
3. Set environment variables
4. Deploy from GitHub

### Option 2: Railway

1. Create PostgreSQL addon
2. Create service from repo
3. Configure environment
4. Deploy

### Option 3: Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🐛 Troubleshooting

### Database Connection Fails

- Check `DATABASE_URL` format
- Verify PostgreSQL is running
- Test connection: `psql $DATABASE_URL`

### API Returns 401

- Verify API key in `.env`
- Check `X-API-Key` header spelling
- Ensure key matches format: `{"key": "client_id"}`

### Logs Not Appearing

- Check client log shipper configuration
- Verify API endpoint URL
- Check server logs for errors
- Verify database connectivity

---

## 📈 What's Next

### Phase 4 Complete When:
- [x] API accepts logs
- [x] Authentication works
- [x] Logs stored in DB
- [x] Read endpoints functional

### Phase 5: Dashboard
- [ ] React/Next.js frontend
- [ ] Overview page
- [ ] Log list with filters
- [ ] Detailed trace viewer
- [ ] Category analytics

### Future Enhancements:
- Alerts and notifications
- Real-time streaming
- Advanced analytics
- ML-based insights
- Custom retention policies

---

## 📚 Project Structure

```
central-logger/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── api/
│   │   ├── ingest.py        # POST /logs
│   │   ├── read_logs.py     # GET /logs
│   │   └── metrics.py       # GET /metrics
│   ├── auth/
│   │   └── api_key_auth.py  # Authentication
│   ├── db/
│   │   ├── database.py      # DB connection
│   │   └── models.py        # SQLAlchemy models
│   ├── services/
│   │   └── log_service.py   # Business logic
│   └── utils/
│       └── validators.py    # Pydantic models
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🤝 Support

For questions or issues:
1. Check logs: Look at server output
2. Review documentation
3. Test with curl commands
4. Verify environment configuration

---

## ⚠️ Important Notes

- **Never commit `.env`** - Use `.env.example` as template
- **Tenant isolation is critical** - Always filter by client_id
- **Keep it simple** - Don't over-engineer early
- **Monitor performance** - Watch DB query times
- **Plan for scale** - But implement for today

---

**Built with:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic

**Status:** ✅ Phase 4 Complete - Ready for Production Testing
