"""
Authentication Utilities

This module provides authentication-related utility functions for BeatBridge.
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt

logger = logging.getLogger(__name__)


def generate_apple_music_token() -> str:
    """
    Generate an Apple Music developer token for API access.
    
    Returns:
        str: JWT token for Apple Music API
    """
    try:
        team_id = os.getenv('APPLE_MUSIC_TEAM_ID')
        key_id = os.getenv('APPLE_MUSIC_KEY_ID')
        private_key_path = os.getenv('APPLE_MUSIC_PRIVATE_KEY_PATH')
        
        # Read private key
        with open(private_key_path, 'r') as file:
            private_key = file.read()
        
        # Set issue time and expiration time
        issue_time = datetime.utcnow()
        expiry_time = issue_time + timedelta(hours=12)
        
        # Create the token
        token = jwt.encode({
            'iss': team_id,  # Issuer: Team ID
            'iat': issue_time,  # Issued at
            'exp': expiry_time,  # Expiration time
        }, private_key, algorithm='ES256', headers={
            'kid': key_id,  # Key ID
            'alg': 'ES256'  # Algorithm
        })
        
        logger.info("Generated Apple Music developer token")
        return token
        
    except Exception as e:
        logger.error(f"Error generating Apple Music token: {str(e)}")
        raise


def refresh_spotify_token(refresh_token: str) -> Optional[str]:
    """
    Refresh a Spotify access token using a refresh token.
    
    Args:
        refresh_token: Spotify refresh token
        
    Returns:
        str: New access token or None if refresh failed
    """
    import base64
    import requests
    
    try:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        # Encode client ID and secret
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
        
        # Make token request
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            },
            headers={
                'Authorization': f'Basic {client_creds_b64}'
            }
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        logger.info("Successfully refreshed Spotify access token")
        return token_data.get('access_token')
        
    except Exception as e:
        logger.error(f"Error refreshing Spotify token: {str(e)}")
        return None


def refresh_youtube_token(refresh_token: str) -> Optional[str]:
    """
    Refresh a YouTube/Google access token using a refresh token.
    
    Args:
        refresh_token: Google refresh token
        
    Returns:
        str: New access token or None if refresh failed
    """
    import requests
    
    try:
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        
        # Make token request
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        logger.info("Successfully refreshed YouTube access token")
        return token_data.get('access_token')
        
    except Exception as e:
        logger.error(f"Error refreshing YouTube token: {str(e)}")
        return None


def verify_spotify_token(token: str) -> bool:
    """
    Verify if a Spotify access token is valid.
    
    Args:
        token: Spotify access token
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    import requests
    
    try:
        response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={
                'Authorization': f'Bearer {token}'
            }
        )
        
        return response.status_code == 200
        
    except Exception:
        return False


def verify_apple_music_token(token: str) -> bool:
    """
    Verify if an Apple Music user token is valid.
    
    Args:
        token: Apple Music user token
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    import requests
    
    try:
        # Generate developer token
        developer_token = generate_apple_music_token()
        
        # Make a test request to the API
        response = requests.get(
            'https://api.music.apple.com/v1/me/library/playlists',
            headers={
                'Authorization': f'Bearer {developer_token}',
                'Music-User-Token': token
            }
        )
        
        return response.status_code == 200
        
    except Exception:
        return False