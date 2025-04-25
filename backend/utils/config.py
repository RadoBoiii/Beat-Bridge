"""
Configuration Settings

This module defines configuration settings for the BeatBridge backend service.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration."""
    
    # Service settings
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # API settings
    API_PREFIX = '/api'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Redis settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Job settings
    JOB_TIMEOUT = int(os.getenv('JOB_TIMEOUT', '600'))  # 10 minutes
    JOB_RETENTION = int(os.getenv('JOB_RETENTION', '86400'))  # 24 hours
    
    # Spotify API
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
    
    # Apple Music API
    APPLE_MUSIC_TEAM_ID = os.getenv('APPLE_MUSIC_TEAM_ID')
    APPLE_MUSIC_KEY_ID = os.getenv('APPLE_MUSIC_KEY_ID')
    APPLE_MUSIC_PRIVATE_KEY_PATH = os.getenv('APPLE_MUSIC_PRIVATE_KEY_PATH')
    
    # YouTube Music API
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
    YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
    YOUTUBE_REDIRECT_URI = os.getenv('YOUTUBE_REDIRECT_URI')


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    
    # Production settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Security settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get current configuration based on environment."""
    environment = os.getenv('FLASK_ENV', 'default')
    return config.get(environment, config['default'])