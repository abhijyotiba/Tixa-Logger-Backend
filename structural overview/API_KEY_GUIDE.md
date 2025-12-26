# 🔐 API Key Management Guide

## Complete API Key Workflow

### 🎯 Overview

```
YOU (Provider)                          CLIENT (Workflow Owner)
      │                                        │
      │  1. Generate API Key                   │
      ├────────────────────────────────────────┤
      │                                        │
      │  2. Share API Key Securely            │
      │     (Email, Dashboard, etc.)          │
      ├───────────────────────────────────────▶│
      │                                        │
      │                                        │  3. Store in .env
      │                                        │     API_KEY=xyz123
      │                                        │
      │  4. Client sends logs with API key    │
      │     X-API-Key: xyz123                 │
      │ ◀──────────────────────────────────────┤
      │                                        │
      │  5. Validate & Resolve client_id      │
      │     xyz123 → client_abc               │
      │                                        │
      │  6. Store log with client_id          │
      │     (tenant isolation)                │
```

---

## 🔑 Part 1: Generating API Keys (YOU - Provider Side)

### Method 1: Python Script (Recommended)

Create a file: `scripts/generate_api_key.py`

```python
import secrets
import json

def generate_api_key():
    """Generate a cryptographically secure API key"""
    return secrets.token_urlsafe(32)

def main():
    print("=" * 60)
    print("API Key Generator")
    print("=" * 60)
    
    # Get client details
    client_id = input("\nEnter client_id (e.g., 'acme_corp'): ").strip()
    
    if not client_id:
        print("Error: client_id is required")
        return
    
    # Generate key
    api_key = generate_api_key()
    
    print("\n" + "=" * 60)
    print("✅ API Key Generated Successfully!")
    print("=" * 60)
    print(f"\nClient ID: {client_id}")
    print(f"API Key:   {api_key}")
    print("\n" + "=" * 60)
    print("IMPORTANT: Save this information securely!")
    print("=" * 60)
    
    # Show .env format
    print("\n📝 Add to your .env file:")
    print("-" * 60)
    print(f'API_KEYS={{"...", "{api_key}": "{client_id}"}}')
    print("-" * 60)
    
    # Show client format
    print("\n📧 Send to client:")
    print("-" * 60)
    print(f"API Endpoint: https://your-logger-api.com/api/v1/logs")
    print(f"API Key: {api_key}")
    print(f"Header: X-API-Key: {api_key}")
    print("-" * 60)

if __name__ == "__main__":
    main()
```

**Run it:**
```powershell
cd central-logger
python scripts\generate_api_key.py
```

### Method 2: PowerShell One-Liner

```powershell
# Generate secure random key
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
$apiKey = [Convert]::ToBase64String($bytes) -replace '\+','-' -replace '/','_' -replace '=',''
Write-Host "API Key: $apiKey"
```

### Method 3: Python One-Liner

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📝 Part 2: Storing API Keys (YOU - Provider Side)

### Development: Use .env File

**Edit `.env`:**
```env
# API Keys: Map API key → client_id
API_KEYS={
    "abc123_dev_key": "client_demo",
    "xyz789_real_key": "acme_corp",
    "def456_another": "widget_co"
}
```

⚠️ **Important:** This is for development only!

### Production: Use Database (Recommended)

**Step 1:** Create API keys table

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key TEXT UNIQUE NOT NULL,
    client_id TEXT NOT NULL,
    client_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
);

CREATE INDEX idx_api_key ON api_keys(api_key);
CREATE INDEX idx_client_id ON api_keys(client_id);
```

**Step 2:** Update authentication to use database

I'll create a production-ready version in the code.

---

## 🔒 Part 3: API Key Validation (Automatic)

### How It Works

When a client sends a request:

```http
POST /api/v1/logs HTTP/1.1
Host: your-logger-api.com
X-API-Key: xyz789_real_key
Content-Type: application/json

{
  "environment": "production",
  "executed_at": "2025-12-24T10:30:00Z",
  ...
}
```

**Validation Flow:**

1. **Extract Header:** FastAPI gets `X-API-Key` from request
2. **Lookup:** Check if key exists in `API_KEYS` (or database)
3. **Resolve:** Get corresponding `client_id`
4. **Validate:** If not found → 401 Unauthorized
5. **Continue:** If valid → request proceeds with `client_id`

**Code (Already Implemented):**
```python
# app/auth/api_key_auth.py
def get_current_client(api_key: str = Header(..., alias="X-API-Key")) -> str:
    client_id = api_keys.get(api_key)
    if not client_id:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return client_id
```

---

## 📤 Part 4: Distributing API Keys to Clients

### Option 1: Email

```
Subject: Your Logger API Credentials

Hi [Client Name],

Your logging API credentials are ready:

Endpoint: https://your-logger-api.com/api/v1/logs
API Key: xyz789_real_key
Client ID: acme_corp

Setup Instructions:
1. Add to your .env file:
   LOGGER_API_URL=https://your-logger-api.com/api/v1/logs
   LOGGER_API_KEY=xyz789_real_key

2. Use the header in requests:
   X-API-Key: xyz789_real_key

Documentation: https://docs.your-logger.com

⚠️ Keep this key secure and never commit it to version control.

Questions? Reply to this email.
```

### Option 2: Self-Service Dashboard (Future)

Build a dashboard where clients can:
- Generate their own API keys
- View usage statistics
- Rotate keys
- Deactivate old keys

### Option 3: Secrets Manager

For enterprise clients:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault

---

## 🧪 Part 5: Testing API Key Validation

### Test 1: Valid API Key (Should Work)

```powershell
curl -X POST http://localhost:8000/api/v1/logs `
  -H "X-API-Key: abc123_dev_key" `
  -H "Content-Type: application/json" `
  -d '{
    "environment": "production",
    "executed_at": "2025-12-24T10:30:00Z",
    "status": "SUCCESS"
  }'

# Expected: 201 Created
```

### Test 2: Invalid API Key (Should Fail)

```powershell
curl -X POST http://localhost:8000/api/v1/logs `
  -H "X-API-Key: wrong_key_12345" `
  -H "Content-Type: application/json" `
  -d '{
    "environment": "production",
    "executed_at": "2025-12-24T10:30:00Z",
    "status": "SUCCESS"
  }'

# Expected: 401 Unauthorized
```

### Test 3: Missing API Key (Should Fail)

```powershell
curl -X POST http://localhost:8000/api/v1/logs `
  -H "Content-Type: application/json" `
  -d '{
    "environment": "production",
    "executed_at": "2025-12-24T10:30:00Z",
    "status": "SUCCESS"
  }'

# Expected: 401 Unauthorized
```

---

## 🔄 Part 6: API Key Lifecycle

### Creation
1. Provider generates key
2. Maps key → client_id
3. Adds to .env or database
4. Sends to client securely

### Usage
1. Client includes in every request
2. Provider validates on every request
3. Logs stored with client_id
4. Tenant isolation enforced

### Rotation
1. Generate new key
2. Give client grace period (both keys work)
3. Client updates their systems
4. Deactivate old key

### Revocation
1. Remove from .env or set `is_active=false` in DB
2. Client requests immediately fail with 401
3. Generate new key if needed

---

## 🏢 Part 7: Multi-Tenant Setup

### Example: 3 Clients

**.env Configuration:**
```env
API_KEYS={
    "key_acme_abc123": "acme_corp",
    "key_widget_xyz789": "widget_co",
    "key_demo_def456": "demo_client"
}
```

### Data Isolation

When `acme_corp` queries logs:
```sql
SELECT * FROM workflow_logs WHERE client_id = 'acme_corp'
```

They **never** see data from `widget_co` or `demo_client`.

---

## 🔐 Security Best Practices

### DO:
✅ Generate keys with `secrets.token_urlsafe(32)`
✅ Use HTTPS in production
✅ Store keys in environment variables
✅ Rotate keys periodically (every 90 days)
✅ Use different keys per client
✅ Log authentication attempts
✅ Implement rate limiting

### DON'T:
❌ Hardcode API keys in code
❌ Commit API keys to Git
❌ Share keys between clients
❌ Use weak/predictable keys
❌ Store keys in plain text in database
❌ Use HTTP in production

---

## 📊 Part 8: Monitoring API Key Usage

### Track in Database

Add to `api_keys` table:
```sql
-- Update last_used_at on every successful auth
UPDATE api_keys 
SET last_used_at = NOW() 
WHERE api_key = ?;

-- Track usage
SELECT 
    client_id,
    COUNT(*) as request_count,
    MAX(last_used_at) as last_activity
FROM api_keys
GROUP BY client_id;
```

### Alert on Suspicious Activity

- Multiple failed auth attempts
- API key used from unusual IP
- Sudden spike in requests
- Inactive key suddenly active

---

## 🚀 Quick Start Summary

### For You (Provider):

1. **Generate API key:**
   ```powershell
   python scripts\generate_api_key.py
   ```

2. **Add to .env:**
   ```env
   API_KEYS={"generated_key": "client_id"}
   ```

3. **Restart server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

4. **Send to client:**
   - API endpoint URL
   - API key
   - Documentation

### For Client:

1. **Receive API key from you**

2. **Add to their .env:**
   ```env
   LOGGER_API_URL=https://your-logger.com/api/v1/logs
   LOGGER_API_KEY=their_api_key_here
   ```

3. **Use in requests:**
   ```python
   headers = {"X-API-Key": os.getenv("LOGGER_API_KEY")}
   requests.post(url, headers=headers, json=log_data)
   ```

---

## 🆘 Troubleshooting

### Client Gets 401

**Possible causes:**
1. API key not in your `.env` file
2. Typo in API key
3. Header name wrong (must be `X-API-Key`)
4. Server not restarted after .env change

**Debug:**
```python
# Add logging to auth module
logger.info(f"Received API key: {api_key[:8]}...")
logger.info(f"Available keys: {list(API_KEYS.keys())}")
```

### Keys Not Loading

Check `.env` format:
```env
# ✅ Correct
API_KEYS={"key1": "client1", "key2": "client2"}

# ❌ Wrong
API_KEYS=key1:client1,key2:client2
```

---

## 📋 Checklist

### Before Giving API Key to Client:
- [ ] Key generated with secure method
- [ ] Key added to `.env` or database
- [ ] Server restarted
- [ ] Key tested with curl/test script
- [ ] Documentation prepared
- [ ] Secure transmission method chosen

### Client Setup Checklist:
- [ ] API key received
- [ ] API key stored in .env
- [ ] Never committed to Git
- [ ] Test request successful
- [ ] Error handling implemented
- [ ] Async shipping configured

---

**Need help?** See the integration testing guide next!
