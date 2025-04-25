"""
BeatBridge Services Package

This package contains the service implementations for different music platforms.
"""

from .spotify import SpotifyService
from .apple_music import AppleMusicService
from .youtube_music import YouTubeMusicService

__all__ = ['SpotifyService', 'AppleMusicService', 'YouTubeMusicService']