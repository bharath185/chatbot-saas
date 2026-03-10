# Payment Integration Guide (Razorpay)

This guide shows you how to add payments to your SaaS so customers can actually pay you.

---

## Why Razorpay?

✅ India-native (easiest for Indian customers)
✅ Simple integration (5 minutes)
✅ Low fees (2% for UPI, 2.9% for cards)
✅ Automatic settlements
✅ Great documentation

**Alternative:** Stripe (works globally, slightly more complex)

---

## Setup (10 Minutes)

### Step 1: Create Razorpay Account

1. Go to https://razorpay.com
2. Click "Sign Up"
3. Fill email + password
4. Verify email
5. Business details (your name, Bengaluru)
6. Phone verification
7. You're in! Dashboard ready.

### Step 2: Get API Keys

```
Dashboard → Settings → API Keys

Copy:
- Key ID: rzp_live_xxxxxxxxxxxxx
- Key Secret: Keep it secret! (Don't commit to GitHub)
```

### Step 3: Add to .env File

```env
RAZORPAY_KEY=rzp_live_xxxxxxxxxxxxx
RAZORPAY_SECRET=your-secret-key-here
```

---

## Backend Implementation

### Option 1: Simple (Recommended for Start)

Add to your `app.py`:

```python
import razorpay
import os
from datetime import datetime

# Initialize Razorpay
razorpay_client = razorpay.Client(auth=(
    os.getenv('RAZORPAY_KEY'),
    os.getenv('RAZORPAY_SECRET')
))

# ==================== PAYMENT ROUTES ====================

@app.route('/api/payment/create', methods=['POST'])
@jwt_required()
def create_payment_order():
    """Create payment order for plan upgrade"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    plan = data.get('plan')  # 'basic', 'pro', 'enterprise'
    
    # Define prices in paise (₹100 = 10000 paise)
    plans = {
        'basic': 500000,      # ₹5,000
        'pro': 1000000,       # ₹10,000
        'enterprise': 1500000 # ₹15,000
    }
    
    if plan not in plans:
        return jsonify({'error': 'Invalid plan'}), 400
    
    try:
        # Create order on Razorpay
        order = razorpay_client.order.create({
            'amount': plans[plan],
            'currency': 'INR',
            'receipt': f'order_{user_id}_{datetime.now().timestamp()}',
            'notes': {
                'user_id': user_id,
                'plan': plan
            }
        })
        
        return jsonify({
            'order_id': order['id'],
            'amount': order['amount'],
            'amount_display': f"₹{order['amount']/100}",
            'key': os.getenv('RAZORPAY_KEY')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payment/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """Verify payment signature and activate plan"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    payment_id = data.get('razorpay_payment_id')
    order_id = data.get('razorpay_order_id')
    signature = data.get('razorpay_signature')
    plan = data.get('plan')
    
    try:
        # Verify signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Signature verified! Update user's plan
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.plan = plan
        user.plan_renewal = datetime.utcnow() + timedelta(days=30)
        user.payment_id = payment_id
        
        db.session.commit()
        
        # Send confirmation email (optional)
        # send_confirmation_email(user.email, plan)
        
        return jsonify({
            'success': True,
            'message': f'Plan upgraded to {plan}!',
            'plan': plan
        }), 200
        
    except razorpay.BadRequestsError as e:
        return jsonify({'error': 'Payment verification failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/payment/status/<order_id>', methods=['GET'])
@jwt_required()
def check_payment_status(order_id):
    """Check if payment was successful"""
    try:
        order = razorpay_client.order.fetch(order_id)
        return jsonify({
            'order_id': order['id'],
            'status': order['status'],
            'amount': order['amount'],
            'amount_paid': order.get('amount_paid', 0)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/plan', methods=['GET'])
@jwt_required()
def get_user_plan():
    """Get current user's plan"""
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Calculate days until renewal
    if hasattr(user, 'plan_renewal'):
        days_left = (user.plan_renewal - datetime.utcnow()).days
    else:
        days_left = 0
    
    return jsonify({
        'plan': user.plan,
        'days_until_renewal': max(0, days_left),
        'usage_tokens': user.usage_tokens,
        'created_at': user.created_at.isoformat()
    }), 200
```

### Step 2: Update User Model

```python
class User(db.Model):
    """Updated User model with payment fields"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    business_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Payment fields
    plan = db.Column(db.String(50), default='free')  # free, basic, pro, enterprise
    plan_renewal = db.Column(db.DateTime)  # When subscription renews
    payment_id = db.Column(db.String(255))  # Last payment ID
    
    usage_tokens = db.Column(db.Integer, default=0)
    chatbots = db.relationship('Chatbot', backref='owner', lazy=True, cascade='all, delete-orphan')
```

---

## Frontend Implementation

### Add to React Dashboard

```jsx
// Add to ChatbotSaaS.jsx

const [showPaymentModal, setShowPaymentModal] = useState(false);
const [selectedPlan, setSelectedPlan] = useState(null);

// Payment function
const handlePayment = async (plan) => {
  setSelectedPlan(plan);
  
  try {
    // 1. Create order
    const orderResponse = await fetch(`${API_URL}/payment/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ plan })
    });
    
    const order = await orderResponse.json();
    
    // 2. Load Razorpay script
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    script.onload = () => {
      // 3. Open payment modal
      const options = {
        key: order.key,
        order_id: order.order_id,
        amount: order.amount,
        currency: 'INR',
        name: 'ChatBot SaaS',
        description: `Subscribe to ${plan} plan`,
        handler: async (response) => {
          // 4. Verify payment
          const verifyResponse = await fetch(`${API_URL}/payment/verify`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              plan: plan
            })
          });
          
          const result = await verifyResponse.json();
          if (result.success) {
            alert(`✅ Welcome to ${plan} plan!`);
            setShowPaymentModal(false);
            // Refresh user plan
            fetchUserPlan();
          }
        },
        prefill: {
          email: email
        }
      };
      
      const razorpay = new window.Razorpay(options);
      razorpay.open();
    };
    document.body.appendChild(script);
    
  } catch (err) {
    alert('Payment error: ' + err.message);
  }
};

// Add Pricing Section to Dashboard
const PricingSection = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-8">
    {/* Basic Plan */}
    <div className="border-2 border-blue-500 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-2">Basic</h3>
      <p className="text-3xl font-bold text-blue-600 mb-4">₹5,000/mo</p>
      <ul className="space-y-2 mb-6">
        <li>✅ 1 chatbot</li>
        <li>✅ 100k conversations</li>
        <li>✅ Email support</li>
        <li>✅ Custom widget</li>
      </ul>
      <button
        onClick={() => handlePayment('basic')}
        className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold hover:bg-blue-700"
      >
        Subscribe Now
      </button>
    </div>
    
    {/* Pro Plan */}
    <div className="border-2 border-purple-500 rounded-lg p-6 relative">
      <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-purple-500 text-white px-4 py-1 rounded-full text-sm">
        Popular
      </div>
      <h3 className="text-xl font-bold mb-2">Pro</h3>
      <p className="text-3xl font-bold text-purple-600 mb-4">₹10,000/mo</p>
      <ul className="space-y-2 mb-6">
        <li>✅ 5 chatbots</li>
        <li>✅ 500k conversations</li>
        <li>✅ Priority support</li>
        <li>✅ Analytics dashboard</li>
      </ul>
      <button
        onClick={() => handlePayment('pro')}
        className="w-full bg-purple-600 text-white py-2 rounded-lg font-bold hover:bg-purple-700"
      >
        Subscribe Now
      </button>
    </div>
    
    {/* Enterprise Plan */}
    <div className="border-2 border-green-500 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-2">Enterprise</h3>
      <p className="text-3xl font-bold text-green-600 mb-4">Custom</p>
      <ul className="space-y-2 mb-6">
        <li>✅ Unlimited chatbots</li>
        <li>✅ Unlimited conversations</li>
        <li>✅ Dedicated support</li>
        <li>✅ Custom integrations</li>
      </ul>
      <button
        className="w-full bg-green-600 text-white py-2 rounded-lg font-bold hover:bg-green-700"
        onClick={() => alert('Contact: sales@chatbotsaas.com')}
      >
        Contact Sales
      </button>
    </div>
  </div>
);
```

---

## Installation

```bash
# Install Razorpay SDK
pip install razorpay

# Add to requirements.txt
echo "razorpay==1.4.0" >> requirements.txt
```

---

## Testing Payments

**Razorpay provides test cards:**

```
Card Number: 4111 1111 1111 1111
Expiry: 12/25
CVV: 123
```

In test mode, any amount works. Payment auto-succeeds!

---

## Webhook Setup (Advanced)

For automatic recurring billing:

```python
@app.route('/api/webhooks/razorpay', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhook for renewals"""
    
    # Verify webhook signature (important for security!)
    secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
    body = request.data.decode()
    
    # Verify signature
    webhook_signature = request.headers.get('X-Razorpay-Signature')
    
    # On successful payment:
    # - Extend user's subscription by 30 days
    # - Reset token limit
    # - Send renewal confirmation email
    
    return jsonify({'status': 'ok'}), 200
```

---

## Email Confirmation (Optional but Nice)

```python
from flask_mail import Mail, Message

mail = Mail(app)

def send_confirmation_email(email, plan):
    msg = Message(
        'Welcome to ChatBot SaaS!',
        sender='noreply@chatbotsaas.com',
        recipients=[email]
    )
    msg.body = f"""
    Welcome to {plan.upper()} plan!
    
    Your subscription is active and your chatbots are ready.
    
    Next steps:
    1. Log in to dashboard
    2. Create your first chatbot
    3. Get embed code
    4. Add to your website
    
    Questions? Email us at support@chatbotsaas.com
    """
    
    mail.send(msg)
```

---

## Monitoring Payments

Track these metrics:

```python
# Dashboard endpoint to show payment analytics
@app.route('/api/admin/revenue', methods=['GET'])
@jwt_required()
def get_revenue_stats():
    """Admin endpoint: show total revenue"""
    
    # Only for admin
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if user.email != 'your-admin-email@gmail.com':
        return jsonify({'error': 'Unauthorized'}), 403
    
    basic_count = User.query.filter_by(plan='basic').count()
    pro_count = User.query.filter_by(plan='pro').count()
    
    monthly_revenue = (basic_count * 5000) + (pro_count * 10000)
    
    return jsonify({
        'total_users': User.query.count(),
        'basic_users': basic_count,
        'pro_users': pro_count,
        'monthly_recurring_revenue': monthly_revenue
    }), 200
```

---

## Going Live

**Checklist before accepting real payments:**

- [ ] Change from test keys to live keys
- [ ] Update .env with live RAZORPAY_KEY and RAZORPAY_SECRET
- [ ] Test payment with real card (use ₹1 to minimize risk)
- [ ] Verify payment shows in Razorpay dashboard
- [ ] Set up webhook for automatic renewals
- [ ] Create Terms of Service mentioning billing
- [ ] Set up refund policy
- [ ] Create support email for payment issues

---

## Sample Monthly Revenue Tracker

```
Month 1: 2 customers × ₹5,000 = ₹10,000
Month 2: 5 customers × ₹7,500 avg = ₹37,500
Month 3: 10 customers × ₹7,500 avg = ₹75,000
Month 6: 20 customers × ₹8,000 avg = ₹160,000
Month 12: 50 customers × ₹8,500 avg = ₹425,000
```

**Year 1 total revenue: ₹900,000+**

---

## Support

- Razorpay Docs: https://razorpay.com/docs
- Test API calls: https://razorpay.com/docs/api/orders/
- Webhook setup: https://razorpay.com/docs/webhooks/

Good luck! 🚀
