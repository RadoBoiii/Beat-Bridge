"""Database initialization script for BeatBridge."""

import os
from dotenv import load_dotenv
from flask import Flask
from models import db

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask application for database initialization."""
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///beatbridge.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    return app

if __name__ == '__main__':
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")