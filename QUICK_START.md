# 🚀 QUICK START - Both Services

## Start Backend (Terminal 1)

```powershell
cd central-logger
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Running at: **http://localhost:8000**

---

## Start Dashboard (Terminal 2)

```powershell
cd Tixa-Dashboard
npm run dev
```

✅ Running at: **http://localhost:3000**

---

## Generate Test Logs

```powershell
cd central-logger
.\test_quick.ps1
```

---

## Open Dashboard

Visit: **http://localhost:3000**

Automatically redirects to: **http://localhost:3000/dashboard**

---

## Quick Navigation

- **Dashboard:** Analytics overview
- **Logs:** Browse all logs
- **Click any log:** See full detail

---

## API Key

```
0CXp-UvBsS3IKQICPBQSg0kIb-8IKqykg1XsEFUtVEQ
```

---

## Troubleshooting

### Backend not responding?
```powershell
curl http://localhost:8000/health
```

### Dashboard errors?
Check `.env.local` has correct `NEXT_PUBLIC_API_KEY`

### No logs?
Run `.\test_quick.ps1` to generate sample data

---

**Both services must be running simultaneously!**
