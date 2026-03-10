"""
Customer Service Chatbot SaaS Backend
This is the Flask backend that handles:
- User registration and authentication
- Chatbot creation and management
- Chat message handling with Claude API
- Usage tracking for billing
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, timedelta
from anthropic import Anthropic
import uuid

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///chatbot_saas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Initialize Anthropic client - handle API key safely
api_key = os.environ.get('ANTHROPIC_API_KEY')
if api_key:
    anthropic_client = Anthropic(api_key=api_key)
else:
    anthropic_client = None

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for SaaS customers"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    business_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    plan = db.Column(db.String(50), default='free')  # free, basic, pro
    usage_tokens = db.Column(db.Integer, default=0)  # Track token usage
    chatbots = db.relationship('Chatbot', backref='owner', lazy=True, cascade='all, delete-orphan')

class Chatbot(db.Model):
    """Chatbot configuration model"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    system_prompt = db.Column(db.Text, default="You are a helpful customer service assistant.")
    widget_color = db.Column(db.String(7), default="#007bff")
    welcome_message = db.Column(db.String(500), default="Hello! How can I help you today?")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    conversations = db.relationship('Conversation', backref='chatbot', lazy=True, cascade='all, delete-orphan')

class Conversation(db.Model):
    """Conversation/chat session model"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chatbot_id = db.Column(db.String(36), db.ForeignKey('chatbot.id'), nullable=False)
    visitor_id = db.Column(db.String(36))  # Anonymous visitor ID
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    """Individual message in a conversation"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new SaaS customer"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        business_name=data.get('business_name', 'New Business')
    )
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'user_id': user.id
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login SaaS customer"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'access_token': access_token,
        'user_id': user.id,
        'business_name': user.business_name
    }), 200

# ==================== CHATBOT MANAGEMENT ROUTES ====================

@app.route('/api/chatbots', methods=['GET'])
@jwt_required()
def get_chatbots():
    """Get all chatbots for current user"""
    user_id = get_jwt_identity()
    chatbots = Chatbot.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'created_at': c.created_at.isoformat(),
        'widget_color': c.widget_color
    } for c in chatbots]), 200

@app.route('/api/chatbots', methods=['POST'])
@jwt_required()
def create_chatbot():
    """Create new chatbot"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Chatbot name required'}), 400
    
    chatbot = Chatbot(
        user_id=user_id,
        name=data['name'],
        description=data.get('description', ''),
        system_prompt=data.get('system_prompt', 'You are a helpful customer service assistant.'),
        widget_color=data.get('widget_color', '#007bff'),
        welcome_message=data.get('welcome_message', 'Hello! How can I help you today?')
    )
    
    db.session.add(chatbot)
    db.session.commit()
    
    return jsonify({
        'id': chatbot.id,
        'name': chatbot.name,
        'message': 'Chatbot created successfully'
    }), 201

@app.route('/api/chatbots/<chatbot_id>', methods=['GET'])
@jwt_required()
def get_chatbot(chatbot_id):
    """Get chatbot details"""
    user_id = get_jwt_identity()
    chatbot = Chatbot.query.filter_by(id=chatbot_id, user_id=user_id).first()
    
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    return jsonify({
        'id': chatbot.id,
        'name': chatbot.name,
        'description': chatbot.description,
        'system_prompt': chatbot.system_prompt,
        'widget_color': chatbot.widget_color,
        'welcome_message': chatbot.welcome_message,
        'created_at': chatbot.created_at.isoformat()
    }), 200

@app.route('/api/chatbots/<chatbot_id>', methods=['PUT'])
@jwt_required()
def update_chatbot(chatbot_id):
    """Update chatbot configuration"""
    user_id = get_jwt_identity()
    chatbot = Chatbot.query.filter_by(id=chatbot_id, user_id=user_id).first()
    
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    data = request.get_json()
    chatbot.name = data.get('name', chatbot.name)
    chatbot.description = data.get('description', chatbot.description)
    chatbot.system_prompt = data.get('system_prompt', chatbot.system_prompt)
    chatbot.widget_color = data.get('widget_color', chatbot.widget_color)
    chatbot.welcome_message = data.get('welcome_message', chatbot.welcome_message)
    
    db.session.commit()
    
    return jsonify({'message': 'Chatbot updated successfully'}), 200

# ==================== CHAT/MESSAGE ROUTES ====================

@app.route('/api/chat/<chatbot_id>', methods=['POST'])
def chat(chatbot_id):
    """Send message to chatbot (public endpoint for embedded widget)"""
    chatbot = Chatbot.query.filter_by(id=chatbot_id).first()
    
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')
    visitor_id = data.get('visitor_id', str(uuid.uuid4()))
    
    if not user_message:
        return jsonify({'error': 'Message required'}), 400
    
    # Get or create conversation
    if conversation_id:
        conversation = Conversation.query.filter_by(id=conversation_id).first()
    else:
        conversation = Conversation(chatbot_id=chatbot_id, visitor_id=visitor_id)
        db.session.add(conversation)
        db.session.flush()
    
    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role='user',
        content=user_message
    )
    db.session.add(user_msg)
    db.session.flush()
    
    # Get conversation history for context
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
    
    # Prepare messages for Claude API
    api_messages = []
    for msg in messages:
        api_messages.append({
            'role': msg.role,
            'content': msg.content
        })
    
    try:
        # Check if API key is configured
        if not anthropic_client:
            return jsonify({'error': 'Claude API key not configured. Contact administrator.'}), 500
        
        # Call Claude API
        response = anthropic_client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=500,
            system=chatbot.system_prompt,
            messages=api_messages
        )
        
        assistant_response = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        
        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role='assistant',
            content=assistant_response,
            tokens_used=tokens_used
        )
        db.session.add(assistant_msg)
        
        # Update user's token usage
        user = User.query.filter_by(id=chatbot.user_id).first()
        if user:
            user.usage_tokens += tokens_used
        
        db.session.commit()
        
        return jsonify({
            'response': assistant_response,
            'conversation_id': conversation.id,
            'visitor_id': visitor_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

# ==================== ANALYTICS ROUTES ====================

@app.route('/api/analytics/<chatbot_id>', methods=['GET'])
@jwt_required()
def get_analytics(chatbot_id):
    """Get chatbot analytics"""
    user_id = get_jwt_identity()
    chatbot = Chatbot.query.filter_by(id=chatbot_id, user_id=user_id).first()
    
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    conversations = Conversation.query.filter_by(chatbot_id=chatbot_id).all()
    total_messages = Message.query.join(Conversation).filter(
        Conversation.chatbot_id == chatbot_id
    ).count()
    
    total_tokens = db.session.query(db.func.sum(Message.tokens_used)).filter(
        Message.conversation_id.in_([c.id for c in conversations])
    ).scalar() or 0
    
    return jsonify({
        'total_conversations': len(conversations),
        'total_messages': total_messages,
        'total_tokens_used': total_tokens
    }), 200

# ==================== USAGE & BILLING ROUTES ====================

@app.route('/api/usage', methods=['GET'])
@jwt_required()
def get_usage():
    """Get user's token usage for billing"""
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Estimate cost based on Sonnet pricing: $3 per 1M input, $15 per 1M output
    # Rough average: $9 per 1M tokens
    estimated_cost = (user.usage_tokens / 1_000_000) * 9
    
    return jsonify({
        'total_tokens_used': user.usage_tokens,
        'estimated_monthly_cost': round(estimated_cost, 2),
        'plan': user.plan,
        'free_tier_limit': 1_000_000  # 1M tokens free per month
    }), 200

# ==================== SETUP & HEALTH ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/embed/<chatbot_id>', methods=['GET'])
def get_embed_code(chatbot_id):
    """Get embed code for customer to use on their website"""
    chatbot = Chatbot.query.filter_by(id=chatbot_id).first()
    
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    embed_code = f"""
<!-- Chatbot Widget -->
<script>
(function() {{
    const chatbotId = '{chatbot_id}';
    const apiUrl = '{request.host_url}api';
    const color = '{chatbot.widget_color}';
    const welcomeMsg = '{chatbot.welcome_message}';
    
    // Create widget
    const widget = document.createElement('div');
    widget.id = 'chatbot-widget';
    widget.innerHTML = `
        <div style="position: fixed; bottom: 20px; right: 20px; width: 400px; height: 500px; border-radius: 10px; box-shadow: 0 5px 40px rgba(0,0,0,0.16); display: flex; flex-direction: column; background: white; z-index: 9999;">
            <div style="background: ${{color}}; color: white; padding: 20px; border-radius: 10px 10px 0 0; font-weight: bold;">Customer Support</div>
            <div id="chatbot-messages" style="flex: 1; overflow-y: auto; padding: 20px;"></div>
            <div style="display: flex; padding: 10px; border-top: 1px solid #ddd;">
                <input type="text" id="chatbot-input" placeholder="Type message..." style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"/>
                <button id="chatbot-send" style="margin-left: 10px; padding: 10px 20px; background: ${{color}}; color: white; border: none; border-radius: 5px; cursor: pointer;">Send</button>
            </div>
        </div>
    `;
    document.body.appendChild(widget);
    
    // Show welcome message
    const messagesDiv = document.getElementById('chatbot-messages');
    const welcomeDiv = document.createElement('div');
    welcomeDiv.style.cssText = 'background: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;';
    welcomeDiv.textContent = welcomeMsg;
    messagesDiv.appendChild(welcomeDiv);
    
    // Handle messages
    let conversationId = null;
    const visitorId = localStorage.getItem('chatbot-visitor-id') || '{str(uuid.uuid4())}';
    localStorage.setItem('chatbot-visitor-id', visitorId);
    
    document.getElementById('chatbot-send').addEventListener('click', async () => {{
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        if (!message) return;
        
        // Show user message
        const userDiv = document.createElement('div');
        userDiv.style.cssText = 'text-align: right; background: ${{color}}; color: white; padding: 10px; border-radius: 5px; margin: 10px 0;';
        userDiv.textContent = message;
        messagesDiv.appendChild(userDiv);
        input.value = '';
        
        // Send to API
        const response = await fetch(`${{apiUrl}}/chat/${{chatbotId}}`, {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                message: message,
                conversation_id: conversationId,
                visitor_id: visitorId
            }})
        }});
        
        const data = await response.json();
        conversationId = data.conversation_id;
        
        // Show bot response
        const botDiv = document.createElement('div');
        botDiv.style.cssText = 'background: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;';
        botDiv.textContent = data.response;
        messagesDiv.appendChild(botDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }});
}})();
</script>
"""
    return jsonify({'embed_code': embed_code}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
