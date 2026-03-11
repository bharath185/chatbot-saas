"""
Customer Service Chatbot SaaS Backend - Simplified & Production Ready
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
from anthropic import Anthropic
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///chatbot_saas.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
try:
    db = SQLAlchemy(app)
    jwt = JWTManager(app)
    logger.info("✅ Database and JWT initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize database: {e}")

# Initialize Anthropic client safely
try:
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        anthropic_client = Anthropic(api_key=api_key)
        logger.info("✅ Anthropic client initialized")
    else:
        anthropic_client = None
        logger.warning("⚠️  ANTHROPIC_API_KEY not set")
except Exception as e:
    logger.error(f"❌ Failed to initialize Anthropic: {e}")
    anthropic_client = None

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    business_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usage_tokens = db.Column(db.Integer, default=0)

class Chatbot(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    system_prompt = db.Column(db.Text, default="You are a helpful customer service assistant.")
    widget_color = db.Column(db.String(7), default="#007bff")
    welcome_message = db.Column(db.String(500), default="Hello! How can I help?")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chatbot_id = db.Column(db.String(36), db.ForeignKey('chatbot.id'), nullable=False)
    visitor_id = db.Column(db.String(36))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== HEALTH ROUTES ====================

@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'ChatBot SaaS API', 'status': 'running'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'healthy', 'api': 'working'}), 200

# ==================== AUTHENTICATION ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            business_name=data.get('business_name', 'Business')
        )
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user_id': user.id
        }), 201
    except Exception as e:
        logger.error(f"Register error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
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
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== CHATBOTS ====================

@app.route('/api/chatbots', methods=['GET'])
@jwt_required()
def get_chatbots():
    try:
        user_id = get_jwt_identity()
        chatbots = Chatbot.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'created_at': c.created_at.isoformat(),
            'widget_color': c.widget_color
        } for c in chatbots]), 200
    except Exception as e:
        logger.error(f"Get chatbots error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chatbots', methods=['POST'])
@jwt_required()
def create_chatbot():
    try:
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
            welcome_message=data.get('welcome_message', 'Hello! How can I help?')
        )
        
        db.session.add(chatbot)
        db.session.commit()
        
        return jsonify({
            'id': chatbot.id,
            'name': chatbot.name,
            'message': 'Chatbot created successfully'
        }), 201
    except Exception as e:
        logger.error(f"Create chatbot error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chatbots/<chatbot_id>', methods=['GET'])
@jwt_required()
def get_chatbot(chatbot_id):
    try:
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
    except Exception as e:
        logger.error(f"Get chatbot error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== CHAT ====================

@app.route('/api/chat/<chatbot_id>', methods=['POST'])
def chat(chatbot_id):
    try:
        chatbot = Chatbot.query.filter_by(id=chatbot_id).first()
        
        if not chatbot:
            return jsonify({'error': 'Chatbot not found'}), 404
        
        data = request.get_json()
        user_message = data.get('message', '').strip()
        visitor_id = data.get('visitor_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'Message required'}), 400
        
        # Check if anthropic client is available
        if not anthropic_client:
            return jsonify({'error': 'AI service not available. Check ANTHROPIC_API_KEY.'}), 503
        
        try:
            # Call Claude API
            response = anthropic_client.messages.create(
                model='claude-3-5-sonnet-20241022',
                max_tokens=500,
                system=chatbot.system_prompt,
                messages=[{'role': 'user', 'content': user_message}]
            )
            
            assistant_response = response.content[0].text
            return jsonify({
                'response': assistant_response,
                'visitor_id': visitor_id
            }), 200
        except Exception as api_error:
            logger.error(f"Claude API error: {api_error}")
            return jsonify({'error': f'AI error: {str(api_error)}'}), 503
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== USAGE ====================

@app.route('/api/usage', methods=['GET'])
@jwt_required()
def get_usage():
    try:
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'total_tokens_used': user.usage_tokens,
            'estimated_monthly_cost': round((user.usage_tokens / 1_000_000) * 9, 2),
            'plan': 'basic'
        }), 200
    except Exception as e:
        logger.error(f"Usage error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

# ==================== INITIALIZATION ====================

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Database tables created")
        except Exception as e:
            logger.error(f"❌ Database creation error: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
