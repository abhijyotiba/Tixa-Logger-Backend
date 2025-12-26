# 🗄️ Database Setup Guide

## Complete Database Setup for Central Logger

---

## 📋 Overview

You need a PostgreSQL database with:
- **One main table:** `workflow_logs`
- **Indexes** for performance
- **JSONB support** for flexible log storage

---

## 🎯 Quick Setup Options

### Option 1: Supabase (Easiest - Recommended for Testing)

**Free tier includes:**
- 500MB database
- PostgreSQL with JSONB
- Automatic backups
- Web interface

**Steps:**

1. **Create Account:**
   - Go to [supabase.com](https://supabase.com)
   - Sign up (free)

2. **Create Project:**
   - Click "New Project"
   - Choose name, password, region
   - Wait ~2 minutes for setup

3. **Get Connection String:**
   - Go to Settings → Database
   - Copy "Connection string" (URI format)
   - Example: `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`

4. **Convert for SQLAlchemy:**
   ```
   Original:  postgresql://postgres:pass@host:5432/postgres
   For .env:  postgresql+psycopg://postgres:pass@host:5432/postgres
   ```

5. **Add to .env:**
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:your_password@db.xxx.supabase.co:5432/postgres
   ```

6. **Initialize Tables:**
   ```powershell
   python scripts\init_db.py
   ```

✅ **Done!** Your database is ready.

---

### Option 2: Local PostgreSQL

**Install PostgreSQL:**

**Windows:**
1. Download from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer
3. Set password (remember it!)
4. Default port: 5432

**Or use Docker:**
```powershell
docker run -d `
  --name postgres-logger `
  -e POSTGRES_DB=logger_db `
  -e POSTGRES_USER=logger `
  -e POSTGRES_PASSWORD=secret123 `
  -p 5432:5432 `
  postgres:14-alpine
```

**Connection string:**
```env
DATABASE_URL=postgresql+psycopg://logger:secret123@localhost:5432/logger_db
```

**Initialize:**
```powershell
python scripts\init_db.py
```

---

### Option 3: Docker Compose (Local Development)

**Already configured!** Just run:

```powershell
cd central-logger
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Logger API on port 8000

**Initialize database:**
```powershell
docker-compose exec logger python scripts/init_db.py
```

**Check logs:**
```powershell
docker-compose logs -f
```

**Stop:**
```powershell
docker-compose down
```

**Stop and delete data:**
```powershell
docker-compose down -v
```

---

### Option 4: Render.com (Production)

**Free tier includes:**
- PostgreSQL database
- 1GB storage
- Automatic backups

**Steps:**

1. **Sign up:** [render.com](https://render.com)

2. **Create PostgreSQL:**
   - Dashboard → New → PostgreSQL
   - Choose free tier
   - Wait for provisioning

3. **Get Connection Info:**
   - Click on database
   - Copy "Internal Database URL"

4. **Add to .env:**
   ```env
   DATABASE_URL=<paste_internal_url_here>
   ```

5. **Initialize:**
   ```powershell
   python scripts\init_db.py
   ```

---

### Option 5: Railway (Modern Alternative)

**Steps:**

1. **Sign up:** [railway.app](https://railway.app)

2. **Create Project:**
   - New Project → Provision PostgreSQL

3. **Get Connection String:**
   - Click PostgreSQL service
   - Copy `DATABASE_URL`

4. **Add to .env:**
   ```env
   DATABASE_URL=<railway_database_url>
   ```

5. **Initialize:**
   ```powershell
   python scripts\init_db.py
   ```

---

## 🗂️ Database Schema

### Main Table: `workflow_logs`

```sql
CREATE TABLE workflow_logs (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tenant Isolation
    client_id TEXT NOT NULL,
    environment TEXT NOT NULL,
    workflow_version TEXT,
    
    -- Execution Metadata
    ticket_id TEXT,
    executed_at TIMESTAMPTZ NOT NULL,
    execution_time_seconds FLOAT,
    
    -- Status & Classification
    status TEXT,
    category TEXT,
    resolution_status TEXT,
    
    -- Flexible JSON Storage
    metrics JSONB,    -- Performance metrics, confidence, etc.
    payload JSONB,    -- Full trace, ReACT iterations, tools
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes (Critical for Performance)

```sql
-- Most common queries: by client and time
CREATE INDEX idx_client_executed 
ON workflow_logs(client_id, executed_at);

-- Filter by status
CREATE INDEX idx_client_status 
ON workflow_logs(client_id, status);

-- Environment filtering
CREATE INDEX idx_environment_executed 
ON workflow_logs(environment, executed_at);

-- Quick lookups
CREATE INDEX idx_ticket_id ON workflow_logs(ticket_id);
CREATE INDEX idx_status ON workflow_logs(status);
CREATE INDEX idx_category ON workflow_logs(category);
```

---

## 🚀 Initialize Database (Automated)

### Method 1: Use the Script (Recommended)

```powershell
cd central-logger
python scripts\init_db.py
```

**What it does:**
- Connects to database using `DATABASE_URL` from `.env`
- Creates `workflow_logs` table
- Creates all indexes
- Reports success/failure

**Expected output:**
```
Initializing database tables...
✅ Database initialized successfully!
Tables created: workflow_logs
```

### Method 2: Manual SQL

**Connect to database:**
```powershell
# Get connection string from .env
$env_content = Get-Content .env
$db_url = ($env_content | Select-String "DATABASE_URL").ToString().Split("=")[1]

# Connect using psql
psql $db_url
```

**Run SQL:**
```sql
-- Create table
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

-- Create indexes
CREATE INDEX idx_client_executed ON workflow_logs(client_id, executed_at);
CREATE INDEX idx_client_status ON workflow_logs(client_id, status);
CREATE INDEX idx_environment_executed ON workflow_logs(environment, executed_at);
CREATE INDEX idx_ticket_id ON workflow_logs(ticket_id);
CREATE INDEX idx_status ON workflow_logs(status);
CREATE INDEX idx_category ON workflow_logs(category);

-- Verify
\dt
\d workflow_logs
```

---

## ✅ Verify Database Setup

### Test 1: Check Connection

```powershell
python -c "from app.db.database import engine; engine.connect(); print('✅ Connected!')"
```

### Test 2: Check Tables

```powershell
python -c "from app.db.database import engine; print(engine.table_names())"
```

### Test 3: Insert Test Data

```powershell
python -c "
from app.db.database import SessionLocal
from app.db.models import WorkflowLog
from datetime import datetime

db = SessionLocal()
log = WorkflowLog(
    client_id='test_client',
    environment='development',
    ticket_id='TEST-001',
    executed_at=datetime.utcnow(),
    status='SUCCESS'
)
db.add(log)
db.commit()
print('✅ Test log created!')
db.close()
"
```

### Test 4: Query Data

```powershell
python -c "
from app.db.database import SessionLocal
from app.db.models import WorkflowLog

db = SessionLocal()
count = db.query(WorkflowLog).count()
print(f'✅ Logs in database: {count}')
db.close()
"
```

---

## 🔍 Useful Database Queries

### Check Total Logs

```sql
SELECT COUNT(*) FROM workflow_logs;
```

### View Recent Logs

```sql
SELECT 
    id, 
    client_id, 
    ticket_id, 
    status, 
    executed_at 
FROM workflow_logs 
ORDER BY executed_at DESC 
LIMIT 10;
```

### Logs by Client

```sql
SELECT 
    client_id,
    COUNT(*) as total_logs,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as success_count,
    COUNT(CASE WHEN status = 'ERROR' THEN 1 END) as error_count
FROM workflow_logs
GROUP BY client_id;
```

### Logs by Environment

```sql
SELECT 
    environment,
    COUNT(*) as total,
    AVG(execution_time_seconds) as avg_time
FROM workflow_logs
GROUP BY environment;
```

### Recent Errors

```sql
SELECT 
    ticket_id,
    category,
    executed_at,
    payload->>'error' as error_message
FROM workflow_logs
WHERE status = 'ERROR'
ORDER BY executed_at DESC
LIMIT 20;
```

### JSONB Query Example

```sql
-- Get logs with high confidence
SELECT 
    ticket_id,
    metrics->>'confidence' as confidence,
    metrics->>'react_iterations' as iterations
FROM workflow_logs
WHERE (metrics->>'confidence')::float > 0.9
ORDER BY executed_at DESC;
```

---

## 🛠️ Database Management

### Backup

**PostgreSQL dump:**
```powershell
pg_dump -U username -h host -d database_name > backup.sql
```

**Restore:**
```powershell
psql -U username -h host -d database_name < backup.sql
```

### Clean Old Logs

```sql
-- Delete logs older than 90 days
DELETE FROM workflow_logs 
WHERE created_at < NOW() - INTERVAL '90 days';
```

### Vacuum (Optimize)

```sql
VACUUM ANALYZE workflow_logs;
```

---

## 📊 Monitoring Database

### Check Database Size

```sql
SELECT 
    pg_size_pretty(pg_database_size(current_database())) as size;
```

### Check Table Size

```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('workflow_logs')) as total_size,
    pg_size_pretty(pg_relation_size('workflow_logs')) as table_size,
    pg_size_pretty(pg_total_relation_size('workflow_logs') - pg_relation_size('workflow_logs')) as index_size;
```

### Active Connections

```sql
SELECT 
    count(*) as connections 
FROM pg_stat_activity;
```

### Slow Queries

```sql
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 🆘 Troubleshooting

### Error: "could not connect to server"

**Causes:**
- Database not running
- Wrong host/port
- Firewall blocking

**Fix:**
```powershell
# Test connection
Test-NetConnection -ComputerName db.xxx.supabase.co -Port 5432

# Check DATABASE_URL format
# Should be: postgresql+psycopg://user:pass@host:5432/dbname
```

### Error: "relation does not exist"

**Cause:** Tables not created

**Fix:**
```powershell
python scripts\init_db.py
```

### Error: "psycopg not installed"

**Fix:**
```powershell
pip install "psycopg[binary]==3.1.18"
```

### Error: "FATAL: password authentication failed"

**Cause:** Wrong username or password

**Fix:**
- Double-check DATABASE_URL
- Ensure password is URL-encoded if it has special characters
  - Replace `@` with `%40`
  - Replace `#` with `%23`
  - Replace `%` with `%25`

---

## 📋 Setup Checklist

- [ ] PostgreSQL database created
- [ ] Connection string obtained
- [ ] DATABASE_URL added to .env
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tables created (`python scripts\init_db.py`)
- [ ] Connection tested
- [ ] Sample log inserted successfully
- [ ] Can query logs

---

## 🎯 Quick Commands Reference

```powershell
# Initialize database
python scripts\init_db.py

# Test connection
python -c "from app.db.database import engine; engine.connect(); print('OK')"

# Count logs
python -c "from app.db.database import SessionLocal; from app.db.models import WorkflowLog; db = SessionLocal(); print(db.query(WorkflowLog).count())"

# Docker Compose
docker-compose up -d                          # Start
docker-compose exec logger python scripts/init_db.py  # Init DB
docker-compose down                           # Stop
```

---

**Your database is now ready to receive logs!** 🎉
