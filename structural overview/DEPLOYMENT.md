# Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- PostgreSQL database (Supabase, Render, Railway, or self-hosted)
- Python 3.10+ runtime environment
- Domain name (optional but recommended)

---

## Option 1: Deploy to Render

### Step 1: Database Setup
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Create new PostgreSQL database
3. Copy the **Internal Database URL**

### Step 2: Web Service Setup
1. Create new **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables
Add in Render dashboard:
```
DATABASE_URL=<your_render_postgres_url>
SERVICE_NAME=central-logger
ENVIRONMENT=production
API_KEY_HEADER=X-API-Key
API_KEYS={"your_secret_key":"client_id"}
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### Step 4: Initialize Database
```bash
# Run from Render shell
python scripts/init_db.py
```

---

## Option 2: Deploy to Railway

### Step 1: Create Project
1. Go to [Railway](https://railway.app/)
2. Create new project
3. Add PostgreSQL plugin

### Step 2: Deploy Service
1. Deploy from GitHub repo
2. Railway auto-detects Python
3. Set custom start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables
Add in Railway dashboard:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SERVICE_NAME=central-logger
ENVIRONMENT=production
API_KEY_HEADER=X-API-Key
API_KEYS={"your_secret_key":"client_id"}
```

---

## Option 3: Docker Deployment

### Create Dockerfile
Already in repo root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run
```bash
# Build image
docker build -t central-logger .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e ENVIRONMENT="production" \
  -e API_KEYS='{"key":"client"}' \
  --name central-logger \
  central-logger
```

### Docker Compose
```yaml
version: '3.8'
services:
  logger:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - ENVIRONMENT=production
      - API_KEYS=${API_KEYS}
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=logger
      - POSTGRES_USER=logger
      - POSTGRES_PASSWORD=secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## Option 4: Supabase + Vercel

### Step 1: Supabase Setup
1. Create project at [Supabase](https://supabase.com/)
2. Get connection string from Settings → Database
3. Run SQL to create tables (see below)

### Step 2: Deploy API
1. Can use Vercel, Render, or Railway
2. Set `DATABASE_URL` to Supabase connection string

---

## 🗄️ Database Initialization

### SQL for Manual Setup
```sql
CREATE TABLE workflow_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id TEXT NOT NULL,
    environment TEXT NOT NULL,
    workflow_version TEXT,
    ticket_id TEXT,
    executed_at TIMESTAMPTZ NOT NULL,
    execution_time_seconds FLOAT,
    status TEXT,
    category TEXT,
    resolution_status TEXT,
    metrics JSONB,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_client_executed ON workflow_logs(client_id, executed_at);
CREATE INDEX idx_client_status ON workflow_logs(client_id, status);
CREATE INDEX idx_environment_executed ON workflow_logs(environment, executed_at);
CREATE INDEX idx_ticket_id ON workflow_logs(ticket_id);
CREATE INDEX idx_status ON workflow_logs(status);
CREATE INDEX idx_category ON workflow_logs(category);
```

---

## 🔐 Security Checklist

### Before Production:
- [ ] Change all default API keys
- [ ] Use strong, random API keys (32+ characters)
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Set `ENVIRONMENT=production`
- [ ] Remove `/docs` and `/redoc` (auto-disabled in prod)
- [ ] Use connection pooling
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Backup database regularly

### API Key Generation
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"API Key: {api_key}")
```

---

## 📊 Monitoring Setup

### Health Check Endpoint
```
GET /health
```

Configure uptime monitoring:
- [UptimeRobot](https://uptimerobot.com/)
- [Pingdom](https://www.pingdom.com/)
- [Better Uptime](https://betteruptime.com/)

### Logging
Application logs to stdout. Configure log aggregation:
- Render: Built-in logs
- Railway: Built-in logs
- Custom: Logtail, Papertrail, etc.

---

## 🧪 Production Testing

### 1. Test Health
```bash
curl https://your-api.com/health
```

### 2. Test Authentication
```bash
curl -X POST https://your-api.com/api/v1/logs \
  -H "X-API-Key: wrong_key" \
  -H "Content-Type: application/json" \
  -d '{}'
# Should return 401
```

### 3. Test Ingestion
```bash
curl -X POST https://your-api.com/api/v1/logs \
  -H "X-API-Key: your_real_key" \
  -H "Content-Type: application/json" \
  -d '{
    "environment": "production",
    "executed_at": "2025-12-24T10:30:00Z",
    "status": "SUCCESS",
    "ticket_id": "TEST-001"
  }'
# Should return 201
```

---

## 📈 Scaling Considerations

### Database
- Start with shared/hobby plan
- Upgrade when:
  - > 100 logs/minute
  - > 1M total logs
  - Query response > 500ms

### API Server
- Start with 1 instance
- Scale horizontally when:
  - CPU > 70% sustained
  - Response time > 1s
  - 503 errors occurring

### Optimization
- Add database indexes
- Use connection pooling
- Cache frequent queries
- Implement batch ingestion
- Archive old logs

---

## 🔄 Update Strategy

### Zero-Downtime Deployment
1. Deploy new version to staging
2. Test thoroughly
3. Deploy to production
4. Monitor for errors
5. Rollback if needed

### Database Migrations
Use Alembic:
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Review migration file
# Apply migration
alembic upgrade head
```

---

## 📞 Support

### Common Issues

**Issue:** Database connection fails
- Check `DATABASE_URL` format
- Verify network connectivity
- Check firewall rules

**Issue:** API returns 500
- Check server logs
- Verify database is running
- Check environment variables

**Issue:** Authentication fails
- Verify API key format in `.env`
- Check header name matches `API_KEY_HEADER`
- Ensure key-client mapping correct

---

## ✅ Launch Checklist

- [ ] Database created and initialized
- [ ] Environment variables configured
- [ ] API keys generated and stored
- [ ] Test endpoint working
- [ ] Health check responding
- [ ] CORS configured
- [ ] HTTPS enabled
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Documentation updated
- [ ] Client integration tested

---

**Ready to deploy!** 🚀

Choose your platform and follow the steps above.
