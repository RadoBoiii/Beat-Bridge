"""
BeatBridge Utilities Package

This package contains utility functions used throughout the BeatBridge application.
"""

from .auth import generate_apple_music_token, refresh_spotify_token, refresh_youtube_token
from .matching import match_tracks, match_track_by_isrc, calculate_track_similarity
from .logging import setup_logging, log_error, log_request

__all__ = [
    'generate_apple_music_token',
    'refresh_spotify_token',
    'refresh_youtube_token',
    'match_tracks',
    'match_track_by_isrc',
    'calculate_track_similarity',
    'setup_logging',
    'log_error',
    'log_request'
]