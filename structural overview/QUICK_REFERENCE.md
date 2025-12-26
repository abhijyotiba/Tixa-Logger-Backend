# Central Logger - Quick Reference

## 🚀 Start Server
```powershell
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🐳 Docker Commands
```powershell
# Start everything
docker-compose up -d

# Initialize database
docker-compose exec logger python scripts/init_db.py

# View logs
docker-compose logs -f logger

# Stop
docker-compose down
```

## 🧪 Test Commands
```powershell
# Automated test
python scripts\test_api.py

# Health check
curl http://localhost:8000/health

# Ingest log
curl -X POST http://localhost:8000/api/v1/logs -H "X-API-Key: test_key_123" -H "Content-Type: application/json" -d "{\"environment\":\"production\",\"executed_at\":\"2025-12-24T10:30:00Z\",\"status\":\"SUCCESS\"}"

# Get logs
curl http://localhost:8000/api/v1/logs?page=1 -H "X-API-Key: test_key_123"

# Get metrics
curl http://localhost:8000/api/v1/metrics/overview?days=7 -H "X-API-Key: test_key_123"
```

## 📊 Database Commands
```powershell
# Initialize
python scripts\init_db.py

# Connect to DB
psql $DATABASE_URL

# Check logs
SELECT COUNT(*) FROM workflow_logs;
SELECT * FROM workflow_logs ORDER BY created_at DESC LIMIT 5;
```

## 🔐 Generate API Key
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📁 Key Files
- `app/main.py` - Main application
- `app/api/ingest.py` - Log ingestion
- `app/api/read_logs.py` - Query logs
- `app/api/metrics.py` - Analytics
- `app/db/models.py` - Database schema
- `.env` - Configuration

## 🔗 URLs
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs` (dev only)
- Health: `http://localhost:8000/health`

## 🆘 Troubleshooting
```powershell
# Check Python version
python --version

# Check dependencies
pip list

# Test database connection
python -c "from app.db.database import engine; engine.connect()"

# View environment
type .env
```
