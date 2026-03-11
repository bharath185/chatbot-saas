# "Failed to Fetch" Error - Troubleshooting

**Error:** "Connection error: Failed to fetch"

This means your frontend can't reach your backend API.

---

## ✅ Quick Fix Checklist

### 1. Check Your Backend URL

**In index.html, line ~123:**
```javascript
const API_URL = 'http://localhost:5000/api';
```

**This should be YOUR Render backend URL:**
```javascript
const API_URL = 'https://chatbot-saas-backend-abc123.onrender.com/api';
```

**How to find your backend URL:**
1. Go to Render.com
2. Click "chatbot-saas-backend" service
3. Look for "URL" at the top
4. Copy it completely
5. Make sure it ends with `/api`

---

### 2. Test Backend is Running

**Open in browser (directly):**
```
https://your-backend-url.onrender.com/api/health
```

You should see:
```
{"status": "healthy"}
```

If you see error → backend is down or wrong URL

---

### 3. Check CORS is Enabled

Backend should allow requests from anywhere.

**In app.py (already fixed):**
```python
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
})
```

This is already set! Just need to redeploy.

---

## 🔧 Step-by-Step Fix

### Step 1: Update Backend URL in index.html

Find line 123:
```javascript
const API_URL = 'http://localhost:5000/api';
```

Replace with YOUR actual Render URL (with /api at end):
```javascript
const API_URL = 'https://your-render-url.onrender.com/api';
```

**Example:**
```javascript
const API_URL = 'https://chatbot-saas-backend-12345.onrender.com/api';
```

### Step 2: Redeploy Backend (app.py)

The CORS fix is now in app.py. You need to redeploy:

```bash
# In your project with app.py
git add app.py
git commit -m "Fix CORS for production"
git push origin main
```

Render auto-redeploys automatically (watch your Render dashboard).

### Step 3: Redeploy Frontend (index.html)

```bash
# After updating index.html with correct API URL
git add index.html
git commit -m "Fix backend API URL"
git push origin main
```

Vercel auto-redeploys (watch your Vercel dashboard).

### Step 4: Test Again

1. Open your frontend URL
2. Open browser console (F12 → Console)
3. Try to login
4. You should see in console:
   ```
   API URL: https://your-backend.onrender.com/api
   Calling: https://your-backend.onrender.com/api/auth/login
   Response status: 200
   Response data: {...}
   ```

If you see errors → check the exact error message

---

## 🔍 Debugging

### Open Browser Console (F12)

When you try to login, look for:

**Good logs:**
```
API URL: https://your-backend.onrender.com/api
Calling: https://your-backend.onrender.com/api/auth/login
Response status: 200
Response data: {access_token: "..."}
```

**Bad logs:**
```
Fetch error: TypeError: Failed to fetch
```

**What to check:**
1. Is the URL correct?
2. Does backend respond to `/api/health`?
3. Is backend running on Render?

---

## Common Issues & Fixes

### Issue 1: Wrong API URL

**Error:** Fetch error
**Cause:** API_URL is incorrect
**Fix:** Copy exact URL from Render, check `/api` at end

### Issue 2: Backend is Down

**Error:** Fetch error
**Cause:** Backend crashed or not running
**Fix:** 
1. Go to Render.com dashboard
2. Click your service
3. Check status (should say "Running")
4. Check logs for errors
5. If errors, check your ANTHROPIC_API_KEY is set

### Issue 3: CORS Blocked

**Error:** In browser console you see CORS error
**Cause:** Backend doesn't allow frontend domain
**Fix:** Already fixed in updated app.py, just redeploy

### Issue 4: Using Localhost

**Error:** "Failed to fetch" on production frontend
**Cause:** Frontend is on Vercel but API_URL is localhost
**Fix:** Change API_URL to your Render backend, NOT localhost

---

## ✅ Verification

After fixes, you should see:

```
Frontend (Vercel): https://your-frontend.vercel.app ✅
Backend (Render): https://your-backend.onrender.com ✅
API calls working ✅
Can login ✅
Can create chatbot ✅
```

---

## Quick Test Commands

### Test Backend Health
```bash
curl https://your-backend.onrender.com/api/health
```

Should return: `{"status":"healthy"}`

### Test CORS
```bash
curl -X OPTIONS https://your-backend.onrender.com/api/auth/login \
  -H "Origin: https://your-frontend.vercel.app"
```

Should NOT give CORS error.

---

## If Still Stuck

1. Check the exact error message in browser console
2. Make sure API_URL in index.html is EXACTLY your Render URL
3. Make sure it ends with `/api`
4. Make sure backend is running (check Render logs)
5. Redeploy both backend and frontend

---

**Most common issue: Wrong API_URL in index.html!**
**Double-check it matches your actual Render backend URL!** 🔍
