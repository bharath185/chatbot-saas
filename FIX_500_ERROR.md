# Fix 500 Internal Server Error

**Error:** Backend returning 500 instead of JSON

---

## 🔍 Check Render Logs

1. Go to Render.com dashboard
2. Click "chatbot-saas-backend" service
3. Click "Logs" tab
4. **Look for error messages** - they tell you what's wrong!

Common errors:
- `ModuleNotFoundError: No module named...` → Missing dependency
- `ANTHROPIC_API_KEY` → Missing API key (check environment variables)
- `SyntaxError` → Error in code
- `Database error` → SQLite issue

---

## ✅ Quick Fixes

### Fix 1: Check ANTHROPIC_API_KEY

**In Render dashboard:**
1. Click your service
2. Click "Environment" tab
3. Check if `ANTHROPIC_API_KEY` exists and has value
4. If missing → Add it:
   - Name: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-your-key-from-console.anthropic.com`
5. Click "Save"
6. Click "Manual Deploy"

### Fix 2: Use New Simplified App

I created a new, simpler version of app.py that handles errors better.

**Option A: Replace with new version**
```bash
# Backup old one
mv app.py app_old.py

# Use new one
cp app_new.py app.py

# Push to GitHub
git add app.py
git commit -m "Use simplified production-ready app"
git push
```

**Option B: Check if old version works**
1. Make sure ANTHROPIC_API_KEY is set
2. Click "Manual Deploy" on Render
3. Check logs again

### Fix 3: Test Health Endpoint First

Open in browser:
```
https://your-backend.onrender.com/health
```

Should see:
```json
{"status": "healthy"}
```

If this fails → Backend not starting at all
If this works → Problem is in specific endpoint

### Fix 4: Check Render Logs Carefully

Click "Logs" and look for:

```
✅ Database and JWT initialized
✅ Anthropic client initialized
```

If you see errors instead → That's your problem!

---

## 🧪 Testing Steps

### Test 1: Health Check (No Auth)
```
GET https://your-backend.onrender.com/health
```
Should return `{"status": "healthy"}`

If fails → Backend crashing on startup

### Test 2: API Health Check  
```
GET https://your-backend.onrender.com/api/health
```
Should return `{"status": "healthy", "api": "working"}`

If fails → Problem with specific route

### Test 3: Try Register in Postman
Use Postman collection to test register endpoint
If it fails → Check logs for exact error

---

## 🔧 Complete Fix Process

### Step 1: Check Environment Variables

**Required:**
- ✅ ANTHROPIC_API_KEY
- ✅ JWT_SECRET_KEY  
- ✅ FLASK_ENV = production
- ✅ DATABASE_URL = sqlite:///chatbot_saas.db

All must be set in Render Environment tab.

### Step 2: Use New App Version

Replace app.py with app_new.py:

```bash
git rm app.py
git add app_new.py
git mv app_new.py app.py
git commit -m "Fix 500 error with simplified app"
git push
```

Render auto-deploys.

### Step 3: Clear Build Cache

In Render dashboard:
1. Click your service
2. Click "Settings"
3. Scroll down to "Build & Deploy"
4. Click "Clear Build Cache"
5. Click "Manual Deploy"

### Step 4: Watch Logs

In Render logs, you should see:
```
✅ Database and JWT initialized
✅ Anthropic client initialized
Listening on 0.0.0.0:port
```

No errors = Success!

### Step 5: Test Again

1. Open health endpoint in browser
2. Should see JSON (not HTML error)
3. Try register in Postman
4. Should work!

---

## 📊 Difference: Old vs New App

| Aspect | Old | New |
|--------|-----|-----|
| Error handling | Minimal | Comprehensive |
| Logging | None | Full debug logs |
| Anthropic init | Basic | Safe with fallback |
| Database init | Simple | Error-wrapped |
| API responses | Raw | Better error messages |

New version tells you EXACTLY what's wrong via logs.

---

## 🎯 Most Likely Causes

1. **Missing ANTHROPIC_API_KEY** (90% of cases)
   - Fix: Add to Render environment

2. **Code error in routes**
   - Fix: Use new simplified app.py

3. **Database not initializing**
   - Fix: Use new app with better error handling

4. **Wrong Python version** (rare)
   - Fix: Already set in render.yaml

5. **Missing dependencies**
   - Fix: Check requirements.txt is installed

---

## If New App Still Fails

1. Check Render logs carefully
2. Look for exact error message
3. Search error message on Google
4. Check requirements.txt has all packages
5. Try minimal app (app_minimal.py)

---

## Success Indicators

✅ Health endpoint returns JSON
✅ No 500 error
✅ Logs show no errors
✅ Can register user
✅ Can create chatbot

---

## Checklist

- [ ] ANTHROPIC_API_KEY is set
- [ ] Render logs checked for errors
- [ ] Health endpoint works
- [ ] Using new app.py (or old one fixed)
- [ ] Render cache cleared
- [ ] Manual deploy done
- [ ] API returns JSON (not HTML)

**Most common fix: Set ANTHROPIC_API_KEY in Render environment!** 🔑

Then use new app.py for better error handling and logging.
