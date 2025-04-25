import re
from urllib.parse import urlparse

def validate_playlist_url(url, platform):
    """
    Validate that a URL is a valid playlist URL for the given platform
    
    Args:
        url (str): The playlist URL to validate
        platform (str): The platform identifier (spotify, apple_music, youtube_music)
        
    Returns:
        tuple: (is_valid, message) - A boolean indicating if the URL is valid and an error message if not
    """
    if not url:
        return False, "Please enter a playlist URL."
    
    # Basic URL validation
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False, "Invalid URL format. Please enter a complete URL."
    except Exception:
        return False, "Invalid URL format. Please check the URL and try again."
    
    # Platform-specific validation
    if platform == 'spotify':
        return validate_spotify_url(url)
    elif platform == 'apple_music':
        return validate_apple_music_url(url)
    elif platform == 'youtube_music':
        return validate_youtube_music_url(url)
    else:
        return False, f"Unsupported platform: {platform}"

def validate_spotify_url(url):
    """
    Validate a Spotify playlist URL
    
    Args:
        url (str): The playlist URL to validate
        
    Returns:
        tuple: (is_valid, message) - A boolean indicating if the URL is valid and an error message if not
    """
    # Check if URL is from Spotify domain
    if 'spotify.com' not in url and 'spotify:' not in url:
        return False, "This doesn't appear to be a Spotify URL. Please enter a URL from open.spotify.com."
    
    # Check if URL is a playlist
    if 'playlist' not in url:
        return False, "This doesn't appear to be a playlist URL. Please enter a Spotify playlist URL."
    
    # Check for playlist ID presence
    if 'spotify.com/playlist/' in url:
        match = re.search(r'spotify\.com/playlist/([a-zA-Z0-9]+)', url)
        if not match:
            return False, "Could not find a valid playlist ID in the URL. Please check the URL and try again."
    elif 'spotify:playlist:' in url:
        match = re.search(r'spotify:playlist:([a-zA-Z0-9]+)', url)
        if not match:
            return False, "Could not find a valid playlist ID in the URI. Please use a URL from the Spotify web player."
    else:
        return False, "This doesn't appear to be a valid Spotify playlist URL. Please enter a URL from the Spotify web player."
    
    return True, ""

def validate_apple_music_url(url):
    """
    Validate an Apple Music playlist URL
    
    Args:
        url (str): The playlist URL to validate
        
    Returns:
        tuple: (is_valid, message) - A boolean indicating if the URL is valid and an error message if not
    """
    # Check if URL is from Apple Music domain
    if 'music.apple.com' not in url:
        return False, "This doesn't appear to be an Apple Music URL. Please enter a URL from music.apple.com."
    
    # Check if URL is a playlist
    if '/playlist/' not in url:
        return False, "This doesn't appear to be a playlist URL. Please enter an Apple Music playlist URL."
    
    # Check for a valid playlist ID format
    match = re.search(r'music\.apple\.com/.+/playlist/.+/(pl\.[a-zA-Z0-9]+)', url)
    if not match:
        # Try alternative format
        match = re.search(r'music\.apple\.com/.+/playlist/.+/([a-zA-Z0-9\.]+)', url)
        if not match:
            return False, "Could not find a valid playlist ID in the URL. Please check the URL and try again."
    
    return True, ""

def validate_youtube_music_url(url):
    """
    Validate a YouTube Music playlist URL
    
    Args:
        url (str): The playlist URL to validate
        
    Returns:
        tuple: (is_valid, message) - A boolean indicating if the URL is valid and an error message if not
    """
    # Check if URL is from YouTube Music domain
    if 'music.youtube.com' not in url:
        return False, "This doesn't appear to be a YouTube Music URL. Please enter a URL from music.youtube.com."
    
    # Check if URL contains a list parameter
    if 'list=' not in url:
        return False, "This doesn't appear to be a playlist URL. Please enter a YouTube Music playlist URL."
    
    # Check for a valid playlist ID format
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    if not match:
        return False, "Could not find a valid playlist ID in the URL. Please check the URL and try again."
    
    return True, ""

def validate_email(email):
    """
    Validate email address format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
        
    # Simple regex pattern for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, message) - A boolean indicating if the password is valid and an error message if not
    """
    if not password:
        return False, "Password is required."
        
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
        
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
        
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
        
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
        
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
        
    return True, ""