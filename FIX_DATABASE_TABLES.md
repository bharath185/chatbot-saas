# Fix "No such table: user" Error

**Error:** `(sqlite3.OperationalError) no such table: user`

This means the database exists but the tables don't.

---

## 🚀 Quick Fix

### Option 1: Redeploy (EASIEST - Auto-initializes)

The updated `app_new.py` auto-creates tables on startup!

```bash
# Replace old app with new one
git rm app.py
git add app_new.py  
git mv app_new.py app.py
git commit -m "Fix database initialization"
git push
```

Render auto-redeploys. 

**Check Render logs:**
```
✅ Database tables created/verified
```

Then try register again → Should work!

---

### Option 2: Manual Init (If you want to be sure)

```bash
# Run initialization script locally
python init_db.py

# You should see:
# Creating database tables...
# ✅ Database tables created successfully!
```

Then push to GitHub and redeploy.

---

## What Happened

1. ✅ app.py loaded
2. ✅ SQLite database file created
3. ❌ But NO TABLES created inside
4. ❌ When trying to query user table → ERROR

**Why?** `db.create_all()` wasn't being called at startup.

## How It's Fixed

New app_new.py has:
```python
def init_database():
    """Initialize database with all tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")

# Initialize on import (before any requests)
init_database()
```

This runs automatically when app starts → Creates all tables!

---

## ✅ Verify Tables Created

### In Render Logs

You should see:
```
✅ Database tables created/verified
```

### By Testing Register

1. Try to register in Postman
2. Should work (no more "no such table" error)
3. Should return:
```json
{
  "message": "User created successfully",
  "access_token": "...",
  "user_id": "..."
}
```

---

## What Tables Are Created

```sql
CREATE TABLE user (
  id VARCHAR(36) PRIMARY KEY,
  email VARCHAR(120) UNIQUE,
  password_hash VARCHAR(255),
  business_name VARCHAR(255),
  created_at DATETIME,
  usage_tokens INTEGER
)

CREATE TABLE chatbot (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) FOREIGN KEY,
  name VARCHAR(255),
  description TEXT,
  system_prompt TEXT,
  widget_color VARCHAR(7),
  welcome_message VARCHAR(500),
  created_at DATETIME
)

CREATE TABLE conversation (
  id VARCHAR(36) PRIMARY KEY,
  chatbot_id VARCHAR(36) FOREIGN KEY,
  visitor_id VARCHAR(36),
  created_at DATETIME
)

CREATE TABLE message (
  id VARCHAR(36) PRIMARY KEY,
  conversation_id VARCHAR(36) FOREIGN KEY,
  role VARCHAR(20),
  content TEXT,
  tokens_used INTEGER,
  created_at DATETIME
)
```

All auto-created by `db.create_all()`

---

## Testing After Fix

### Test 1: Health Check
```
GET /health
```
Should return `{"status": "healthy"}`

### Test 2: Register
```
POST /api/auth/register
{
  "email": "test@example.com",
  "password": "test123456",
  "business_name": "Test"
}
```
Should return `{"access_token": "...", ...}`

### Test 3: Create Chatbot
```
POST /api/chatbots
Headers: Authorization: Bearer {token}
{
  "name": "My Bot"
}
```
Should work!

---

## Checklist

- [ ] Replace app.py with app_new.py
- [ ] Push to GitHub
- [ ] Render auto-deploys
- [ ] Check logs for "✅ Database tables created"
- [ ] Test register in Postman
- [ ] Should get access_token (no more error!)

---

## If It Still Fails

### Check 1: Look at Render Logs

Search for:
- `Database tables created` → Success
- `OperationalError` → Still failing
- `Exception` → What error?

### Check 2: Check Database

The SQLite file exists:
- Render stores it as `chatbot_saas.db`
- But it should have tables now

### Check 3: Try Manual Init

In Render dashboard:
1. Click "Shell" tab
2. Run: `python init_db.py`
3. Should see "✅ Database tables created successfully!"

### Check 4: Restart

In Render:
1. Click your service
2. Click "Settings"
3. Scroll to "Build & Deploy"
4. Click "Clear Build Cache"
5. Click "Manual Deploy"

---

## Success Indicators

✅ Register request succeeds
✅ Get access token
✅ No "no such table" error
✅ Can create chatbots
✅ Can send messages

---

## Next Steps

Once database is fixed:
1. ✅ Test all endpoints with Postman
2. ✅ Test frontend registration
3. ✅ Create chatbot on web
4. ✅ Test chat with AI

---

**The fix is simple: Deploy app_new.py!** 🚀
