# Customer Service Chatbot SaaS - Complete Setup Guide

## Overview

This is a **production-ready SaaS platform** that lets you:
- Create and manage chatbots for customers
- Embed chatbots on customer websites
- Charge customers ₹5,000-15,000/month per chatbot
- Track usage and scale revenue automatically

**Revenue Model:**
- Basic Plan: ₹5,000/month (1 chatbot, 100k tokens/month)
- Pro Plan: ₹10,000/month (5 chatbots, 500k tokens/month)
- Enterprise: ₹15,000+/month (unlimited)

---

## Architecture Overview

```
┌─────────────────┐
│  Customer's     │
│  Website        │
└────────┬────────┘
         │
         │ Embed Widget
         ↓
┌─────────────────┐      ┌──────────────────┐
│  Chatbot        │─────→│  Flask Backend   │
│  Widget         │      │  (app.py)        │
└─────────────────┘      └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ↓             ↓             ↓
                ┌─────────┐  ┌────────┐   ┌──────────┐
                │ SQLite  │  │ Claude │   │ Payment  │
                │ Database│  │ API    │   │ Gateway  │
                └─────────┘  └────────┘   └──────────┘
```

---

## Installation & Setup

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install flask flask-cors flask-sqlalchemy flask-jwt-extended anthropic python-dotenv

# Install Node.js dependencies (for React frontend)
npm install
```

### Step 2: Set Up Environment Variables

Create a `.env` file in your project root:

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxx

# Flask
FLASK_ENV=production
JWT_SECRET_KEY=your-super-secret-key-change-this

# Database (can use SQLite or PostgreSQL)
DATABASE_URL=sqlite:///chatbot_saas.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/chatbot_saas

# Payment Gateway (optional, add later)
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxx

# Frontend API URL
REACT_APP_API_URL=http://localhost:5000/api
```

### Step 3: Get Claude API Keys

1. Go to https://console.anthropic.com
2. Sign up/login
3. Click "API Keys" 
4. Create new API key
5. Copy and paste in `.env` file

**Free credits included!** New users get free trial credits to test the API.

### Step 4: Run Locally

```bash
# Terminal 1: Start Flask backend
python app.py
# Server runs on http://localhost:5000

# Terminal 2: Start React frontend
npm start
# Frontend runs on http://localhost:3000
```

---

## Deployment Guide

### Option A: Deploy on Render (Free + Paid)

**Backend Deployment:**

1. Push code to GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect GitHub repo
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:** Add all from `.env`
6. Click "Create Web Service"

**Cost:** Free tier ($0) or paid ($7+/month)

### Option B: Deploy on Railway (Simple)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Add services:
   - Add `PostgreSQL` service (production database)
   - Railway auto-detects Python/Node
5. Add environment variables
6. Deploy!

**Cost:** Pay-as-you-go ($5+ per service)

### Option C: Deploy on AWS/DigitalOcean (Scalable)

1. Create EC2/Droplet instance
2. Install: `Python, Node.js, PostgreSQL, Nginx`
3. Clone repo, install dependencies
4. Use `systemd` to run Flask as service
5. Use Nginx as reverse proxy
6. Use Let's Encrypt for SSL

---

## Database Setup

### Using SQLite (Dev/Small Scale)

Already configured! Just runs locally.

```bash
# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Upgrade to PostgreSQL (Production)

1. Install PostgreSQL locally or use cloud service (Railway, AWS RDS, Heroku Postgres)
2. Update `.env`:
   ```
   DATABASE_URL=postgresql://username:password@host:5432/chatbot_saas
   ```
3. Install package: `pip install psycopg2`
4. Run: `python app.py` (creates tables automatically)

---

## Payment Integration (Add Revenue)

### Option 1: Razorpay (Best for India)

```python
# Add to app.py
import razorpay

client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))

@app.route('/api/payment/create', methods=['POST'])
@jwt_required()
def create_payment():
    user_id = get_jwt_identity()
    plan = request.json['plan']  # 'basic', 'pro', 'enterprise'
    
    # Define plan amounts
    plans = {
        'basic': 500000,  # ₹5,000
        'pro': 1000000,   # ₹10,000
        'enterprise': 1500000  # ₹15,000
    }
    
    payment = client.order.create({
        'amount': plans[plan],
        'currency': 'INR',
        'receipt': f'receipt_{user_id}'
    })
    
    return jsonify({
        'order_id': payment['id'],
        'amount': payment['amount']
    })

@app.route('/api/payment/verify', methods=['POST'])
def verify_payment():
    data = request.json
    client.utility.verify_payment_signature({
        'razorpay_order_id': data['order_id'],
        'razorpay_payment_id': data['payment_id'],
        'razorpay_signature': data['signature']
    })
    
    # Update user plan to paid
    user = User.query.filter_by(id=data['user_id']).first()
    user.plan = data['plan']
    db.session.commit()
    
    return jsonify({'success': True})
```

Install: `pip install razorpay`

### Option 2: Stripe

Similar implementation using `stripe` package

---

## Getting Your First Customers

### Marketing Strategy (₹0 budget)

1. **Create landing page** using template (Webflow, etc.)
2. **Demo video**: Record your chatbot in action (2 min)
3. **Social media**: Post on LinkedIn, Twitter, Instagram
4. **Local outreach**: Email local restaurants, shops, service businesses
5. **Product Hunt**: Launch and get feedback
6. **Referral program**: Give ₹500 commission per customer

### Sample Pitch

```
"We provide AI chatbots for your business that handle customer support 24/7.

✅ 5-minute setup
✅ Works on WhatsApp, Website, or Messenger
✅ Saves 10 hours/week on customer support
✅ ₹5,000-15,000/month

Try free for 7 days"
```

### Sales Targets

| Month | Customers | Revenue |
|-------|-----------|---------|
| Month 1 | 2 | ₹10,000 |
| Month 2 | 5 | ₹35,000 |
| Month 3 | 10 | ₹80,000 |
| Month 6 | 25 | ₹200,000+ |

---

## Scaling Your Revenue

### Phase 1 (Month 1-3): Validation
- Get 5-10 paying customers
- Refine product based on feedback
- Build feature requests list

### Phase 2 (Month 3-6): Growth
- Hire contractor to handle customer support
- Add more features (analytics, training, integrations)
- Improve conversion (landing page, demo videos)
- Target goal: 20-30 customers, ₹150k-200k/month

### Phase 3 (Month 6+): Scale
- Add team members (2-3 people)
- Build integrations (Zapier, Make.com)
- Create marketplace for templates
- Target: 100+ customers, ₹500k+/month

---

## Cost Analysis

| Item | Cost | Notes |
|------|------|-------|
| Claude API | ₹500-5,000/month | Pay-as-you-go ($3-15 per 1M tokens) |
| Hosting | ₹300-3,000/month | Render/Railway free-paid options |
| Database | ₹0-2,000/month | SQLite free, PostgreSQL paid |
| Domain | ₹500/year | Namecheap, GoDaddy |
| Email | ₹0-1,000/month | SendGrid free tier, Gmail |
| **Total** | **₹1,500-11,000/month** | Very scalable! |

**Example Revenue at 10 customers:**
- Revenue: 10 × ₹7,500 (avg) = ₹75,000
- Costs: ₹5,000
- **Profit: ₹70,000/month** ✅

---

## Monitoring & Analytics

### Track Key Metrics

```python
# In your dashboard, show:
- Total customers
- Monthly recurring revenue (MRR)
- Customer acquisition cost (CAC)
- Token usage per customer
- Churn rate
```

### Performance Checklist

- [ ] API response time < 500ms
- [ ] 99.9% uptime
- [ ] Customer support < 24hr response
- [ ] Bug fixes within 48 hours
- [ ] Monthly feature updates

---

## Troubleshooting

### Claude API Errors

**Error: "Rate limit exceeded"**
→ You hit free tier limits. Add payment method or upgrade plan.

**Error: "Invalid API key"**
→ Check `.env` file, make sure key is correct

**Error: "Connection timeout"**
→ Check internet, try again. Claude API has 99.9% uptime.

### Database Errors

**Error: "Database locked" (SQLite)**
→ Normal for multiple requests. Switch to PostgreSQL for production.

**Error: "Connection refused" (PostgreSQL)**
→ Make sure PostgreSQL is running: `sudo systemctl start postgresql`

---

## Security Checklist

- [ ] Change `JWT_SECRET_KEY` in production
- [ ] Use HTTPS only (Let's Encrypt free SSL)
- [ ] Enable CORS for specific domains only
- [ ] Hash all passwords (already done with Werkzeug)
- [ ] Validate all user inputs
- [ ] Rate limit API endpoints
- [ ] Keep API keys in environment variables (never commit)
- [ ] Regular security updates

---

## Next Steps

1. **Deploy backend** on Render/Railway
2. **Deploy frontend** on Vercel/Netlify
3. **Get Razorpay account** for payments
4. **Create landing page**
5. **Find first 3 customers** (family, friends, local business)
6. **Get feedback & iterate**
7. **Scale** 🚀

---

## Support & Questions

- Claude API Docs: https://docs.claude.com
- Flask Docs: https://flask.palletsprojects.com
- Render Docs: https://render.com/docs
- Razorpay Docs: https://razorpay.com/docs

---

## Revenue Roadmap

```
Your Goal: ₹10k/month extra income

Timeline:
Month 1: 2 customers = ₹10,000/month
Month 2: 5 customers = ₹35,000/month  
Month 3: 10 customers = ₹75,000/month
Month 6: 25 customers = ₹150,000+/month

After 6 months, you can:
- Quit your current job and run this full-time
- Hire someone to help
- Scale to ₹500k+/month
```

**You can do this.** Start small, get first customer, scale. 💪

---

Generated: March 2025
Version: 1.0
