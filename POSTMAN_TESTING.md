# Test Backend with Postman

## 📥 Import Collection

### Step 1: Download Postman

Go to https://www.postman.com/downloads/ and install Postman

### Step 2: Import Collection

1. Open Postman
2. Click **"File"** → **"Import"**
3. Select **`ChatBot_SaaS_API.postman_collection.json`** (from outputs folder)
4. Click **"Import"**

---

## ⚙️ Setup Variables

### Step 1: Set BASE_URL

1. In Postman, click **"Collections"** tab (left sidebar)
2. Find **"ChatBot SaaS API"**
3. Click the **"..."** menu
4. Click **"Edit"**
5. Go to **"Variables"** tab
6. Find `BASE_URL`
7. Change Value to your Render backend URL:
   ```
   https://your-backend.onrender.com
   ```

**Example:**
```
https://chatbot-saas-backend-12345.onrender.com
```

### Step 2: Done!

Now all requests will use your backend URL automatically.

---

## 🧪 Test Steps

### Test 1: Health Check

1. In Postman, click **"Collections"** → **"ChatBot SaaS API"** → **"Health Check"** → **"Health"**
2. Click **"Send"**
3. You should see:
   ```json
   {
     "status": "healthy"
   }
   ```

**If you see error:**
- Backend is down
- Wrong URL
- Check Render logs

### Test 2: Register Account

1. Click **"Collections"** → **"ChatBot SaaS API"** → **"Authentication"** → **"Register"**
2. Click **"Send"**
3. You should get a response with `access_token`

**Response looks like:**
```json
{
  "message": "User created successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "12345-abc"
}
```

### Test 3: Copy Token

1. Copy the `access_token` from response
2. In Postman, go to **"Variables"**
3. Click **"Collections"** tab
4. Find **"ChatBot SaaS API"**
5. Find `TOKEN` variable
6. Paste your token in **"Current Value"**
7. Save

### Test 4: Get Chatbots

1. Click **"Collections"** → **"ChatBot SaaS API"** → **"Chatbots"** → **"Get All Chatbots"**
2. Click **"Send"**
3. Should see empty array (no chatbots yet):
   ```json
   []
   ```

### Test 5: Create Chatbot

1. Click **"Collections"** → **"ChatBot SaaS API"** → **"Chatbots"** → **"Create Chatbot"**
2. Click **"Send"**
3. You should get back new chatbot with ID:
   ```json
   {
     "id": "chatbot-123-abc",
     "name": "Customer Support Bot",
     "message": "Chatbot created successfully"
   }
   ```

### Test 6: Copy Chatbot ID

1. Copy the `id` from response
2. Go to Postman **"Variables"**
3. Find `CHATBOT_ID`
4. Paste the ID
5. Save

### Test 7: Get Chatbots Again

1. Click **"Get All Chatbots"**
2. Click **"Send"**
3. Now should see your chatbot in the list

### Test 8: Send Message to Chatbot

1. Click **"Chat"** → **"Send Message (Public - No Auth)"**
2. Click **"Send"**
3. Should get AI response from Claude!

---

## ✅ Success Indicators

If all these work:
- ✅ Health check returns 200
- ✅ Register creates account
- ✅ Get chatbots returns list
- ✅ Create chatbot works
- ✅ Send message gets AI response

**Then your backend is 100% working!** 🎉

---

## 🔍 Troubleshooting

### Error: Connection refused
- Backend is down
- Wrong URL
- Check Render status

### Error: 401 Unauthorized
- Token is missing or expired
- Make sure TOKEN variable is set
- Register again to get new token

### Error: 404 Not Found
- Endpoint doesn't exist
- Check URL spelling
- Make sure CHATBOT_ID is set

### Error: 500 Internal Server Error
- Backend crashed
- Check Render logs
- Check ANTHROPIC_API_KEY is set

---

## 📝 Notes

- **Health Check** - No auth needed
- **Register/Login** - No auth needed
- **All other endpoints** - Need TOKEN in header
- **Chat** - No auth needed (public)
- **Variables** - Use {{VARIABLE_NAME}} in Postman

---

## 🚀 What This Proves

If you can test all these endpoints in Postman:
- Backend is running ✅
- Database is working ✅
- Authentication works ✅
- Claude API is connected ✅
- CORS is configured ✅

Then your backend is **production-ready!**

---

## Next: Test Frontend

Once backend tests pass:
1. Test frontend can connect
2. Try creating account on web
3. Try creating chatbot on web
4. Try chatting with chatbot

---

**Download the Postman collection and test!** 🚀
