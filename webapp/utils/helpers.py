import re
import json
import requests
from urllib.parse import urlparse, parse_qs

def extract_playlist_id(url, platform):
    """
    Extract platform-specific playlist ID from a URL
    
    Args:
        url (str): The playlist URL
        platform (str): The platform identifier (spotify, apple_music, youtube_music)
        
    Returns:
        str: The extracted playlist ID or None if not found
    """
    if not url:
        return None
        
    if platform == 'spotify':
        # Spotify format: https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO?si=...
        match = re.search(r'spotify\.com/playlist/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
            
        # Alternative format: spotify:playlist:37i9dQZF1DX4sWSpwq3LiO
        match = re.search(r'spotify:playlist:([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
            
    elif platform == 'apple_music':
        # Apple Music format: https://music.apple.com/us/playlist/top-100-global/pl.d25f5d1181894928af76c85c967f8f31
        match = re.search(r'music\.apple\.com/.+/playlist/.+/(pl\.[a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
            
        # Alternative format with just the ID
        match = re.search(r'music\.apple\.com/.+/playlist/.+/([a-zA-Z0-9\.]+)', url)
        if match:
            return match.group(1)
            
    elif platform == 'youtube_music':
        # YouTube Music format: https://music.youtube.com/playlist?list=RDCLAK5uy_ktw...
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        if 'list' in query_params:
            return query_params['list'][0]
    
    return None

def get_platform_name(platform_id):
    """
    Get user-friendly platform name from platform ID
    
    Args:
        platform_id (str): The platform identifier (spotify, apple_music, youtube_music)
        
    Returns:
        str: User-friendly platform name
    """
    platform_names = {
        'spotify': 'Spotify',
        'apple_music': 'Apple Music',
        'youtube_music': 'YouTube Music',
        'deezer': 'Deezer',
        'tidal': 'TIDAL',
        'amazon_music': 'Amazon Music'
    }
    
    return platform_names.get(platform_id, platform_id.title())

def format_artist_name(artists):
    """
    Format a list of artists into a string
    
    Args:
        artists (list): List of artist dictionaries or names
        
    Returns:
        str: Formatted artist string (e.g., "Artist1, Artist2 & Artist3")
    """
    if not artists:
        return "Unknown Artist"
        
    if isinstance(artists[0], dict) and 'name' in artists[0]:
        artist_names = [artist['name'] for artist in artists]
    else:
        artist_names = artists
        
    if len(artist_names) == 1:
        return artist_names[0]
    elif len(artist_names) == 2:
        return f"{artist_names[0]} & {artist_names[1]}"
    else:
        return f"{', '.join(artist_names[:-1])} & {artist_names[-1]}"

def truncate_string(text, max_length=50):
    """
    Truncate a string to a maximum length and add ellipsis
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated string
    """
    if not text or len(text) <= max_length:
        return text
        
    return text[:max_length-3] + '...'

def get_platform_icon(platform_id):
    """
    Get CSS class for platform icon
    
    Args:
        platform_id (str): The platform identifier
        
    Returns:
        str: CSS class for the platform icon
    """
    icon_classes = {
        'spotify': 'fab fa-spotify',
        'apple_music': 'fab fa-apple',
        'youtube_music': 'fab fa-youtube',
        'deezer': 'fas fa-music',
        'tidal': 'fas fa-wave-square',
        'amazon_music': 'fab fa-amazon'
    }
    
    return icon_classes.get(platform_id, 'fas fa-music')

def get_playlist_details(playlist_url, platform, token=None):
    """
    Get basic details about a playlist for display purposes
    This is a simplified mock implementation
    
    Args:
        playlist_url (str): The playlist URL
        platform (str): The platform identifier
        token (str, optional): Authentication token if needed
        
    Returns:
        dict: Playlist details (name, owner, image_url)
    """
    # Mock implementation - in production, this would make API calls
    playlist_id = extract_playlist_id(playlist_url, platform)
    
    if not playlist_id:
        return {
            'name': 'Unknown Playlist',
            'owner': 'Unknown',
            'image_url': '/static/img/default_playlist.png'
        }
    
    # This is just a placeholder - in production, you would fetch real data
    return {
        'name': f"Playlist {playlist_id[:8]}...",
        'owner': 'BeatBridge User',
        'image_url': '/static/img/default_playlist.png'
    }