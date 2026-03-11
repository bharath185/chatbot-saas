# Deploy Frontend to Vercel - SIMPLE STEPS

## ✅ You Have Everything You Need Now!

New files created:
- `index.html` - Main dashboard (Vercel will serve this)
- `vercel.json` - Configuration for Vercel
- Both are ready to deploy!

---

## 🚀 Deploy in 3 Steps

### Step 1: Update Backend URL in index.html

Open `index.html` in text editor.

Find line ~123:
```javascript
const API_URL = 'http://localhost:5000/api';
```

Replace with YOUR Render backend URL:
```javascript
const API_URL = 'https://your-backend-url.onrender.com/api';
```

Example:
```javascript
const API_URL = 'https://chatbot-saas-backend-abc123.onrender.com/api';
```

**How to get your backend URL:**
1. Go to Render.com dashboard
2. Click "chatbot-saas-backend" service
3. Look for URL at top (copy it)

---

### Step 2: Push to GitHub

```bash
git add index.html vercel.json
git commit -m "Add frontend deployment"
git push origin main
```

---

### Step 3: Deploy to Vercel

**Option A: Using GitHub (RECOMMENDED)**

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Select your GitHub repository
4. Click "Import"
5. Click "Deploy"
6. Wait 30 seconds
7. Get your URL! ✅

**Option B: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts:
# "Set up and deploy?" → yes
# "In which directory?" → .
# "Overwrite settings?" → no

# Done! You get URL
```

---

## ✅ Test Your Deployment

1. Open your Vercel URL in browser
2. You should see **Login page**
3. Click "Register"
4. Fill in:
   - Business Name: `Test Business`
   - Email: `test@example.com`
   - Password: `test123456`
5. Click "Create Account"
6. You should see **Dashboard**
7. Click "Create Chatbot"
8. You should see it appear
9. **Everything works!** 🎉

---

## If It Doesn't Work

**Error: "Cannot reach API"**
- Check API_URL is correct in index.html
- Make sure backend is running (check Render)
- Make sure it includes `/api` at the end
- Redeploy frontend

**Error: "Page not found"**
- Make sure `index.html` is in root folder
- Make sure `vercel.json` is in root folder
- Redeploy

**Error: "Blank page"**
- Check browser console (F12)
- Look for errors
- Check API_URL again

---

## Your Final URLs

After deployment you'll have:

```
Backend:  https://your-backend.onrender.com
Frontend: https://your-frontend.vercel.app
```

Share the frontend URL with customers!

---

## Next Steps

Once frontend is deployed:

1. ✅ Test it works
2. ✅ Read BUSINESS_GUIDE.md
3. ✅ Start finding customers
4. ✅ Get first paying customer in 30 days

---

**You're ready! Follow the 3 steps above and you'll be live!** 🚀
