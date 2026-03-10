#!/bin/bash

# ChatBot SaaS - Quick Start Script
# This script sets up and runs your chatbot SaaS locally

set -e

echo "🚀 ChatBot SaaS - Quick Start"
echo "=============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 14+"
    exit 1
fi

echo "✅ Python and Node.js found"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Claude API Key - Get from https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Flask Configuration
FLASK_ENV=development
JWT_SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///chatbot_saas.db

# Frontend API URL
REACT_APP_API_URL=http://localhost:5000/api
EOF
    echo "⚠️  .env file created. Please add your Claude API key!"
    echo ""
    read -p "Do you have your Claude API key? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Get your key from: https://console.anthropic.com/account/keys"
        echo "Then update the ANTHROPIC_API_KEY in .env file"
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

# Initialize database
echo "🗄️  Initializing database..."
python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database initialized")
EOF

# Install Node dependencies
echo "📦 Installing Node dependencies..."
npm install --quiet

echo ""
echo "=============================="
echo "✅ Setup complete!"
echo ""
echo "Starting services..."
echo ""
echo "📱 Backend: http://localhost:5000"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Opening in browser in 3 seconds..."
echo ""

# Start backend in background
python3 app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
npm start &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup EXIT INT TERM

# Keep running
wait
