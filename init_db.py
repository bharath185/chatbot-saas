"""
Database initialization script
Run this once to create all tables
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def init_db():
    """Initialize database with all tables"""
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            print("\nTables created:")
            print("  - user")
            print("  - chatbot")
            print("  - conversation")
            print("  - message")
            return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == '__main__':
    success = init_db()
    sys.exit(0 if success else 1)
