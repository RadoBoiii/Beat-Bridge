"""
Apple Music Service

This module implements the AppleMusicService class for interacting with the Apple Music API.
"""

import os
import logging
import time
import json
from typing import Dict, List, Optional, Tuple, Any, Union

import requests
import jwt
from datetime import datetime, timedelta

from models.track import Track
from models.playlist import Playlist

logger = logging.getLogger(__name__)


class AppleMusicService:
    """
    Service for interacting with the Apple Music API.
    """
    
    def __init__(self, developer_token: str, user_token: Optional[str] = None):
        """
        Initialize the Apple Music service.
        
        Args:
            developer_token: Apple Music developer token (JWT)
            user_token: User Music User Token (optional, for user-specific operations)
        """
        self.developer_token = developer_token
        self.user_token = user_token
        self.base_url = "https://api.music.apple.com/v1"
        self.storefront = "us"  # Default storefront
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                     data: Optional[Dict[str, Any]] = None, user_token: bool = False) -> Optional[Dict[str, Any]]:
        """
        Make a request to the Apple Music API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Body data for POST requests
            user_token: Whether to include the user token in the request
            
        Returns:
            Response data or None if request failed
        """
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.developer_token}",
            "Content-Type": "application/json"
        }
        
        if user_token and self.user_token:
            headers["Music-User-Token"] = self.user_token
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error making Apple Music API request: {str(e)}")
            return None
        
        except Exception as e:
            logger.error(f"Error making Apple Music API request: {str(e)}")
            return None
    
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """
        Get a playlist from Apple Music.
        
        Args:
            playlist_id: Apple Music playlist ID
            
        Returns:
            Playlist object or None if not found
        """
        try:
            # Apple Music playlist IDs start with 'pl.'
            if not playlist_id.startswith('pl.'):
                playlist_id = f"pl.{playlist_id}"
            
            # Get playlist details
            endpoint = f"catalog/{self.storefront}/playlists/{playlist_id}"
            response = self._make_request("GET", endpoint, params={"include": "tracks"})
            
            if not response or 'data' not in response:
                logger.error(f"Failed to get Apple Music playlist: {playlist_id}")
                return None
            
            playlist_data = response['data'][0] if response.get('data') else None
            
            if not playlist_data:
                logger.error(f"No data returned for Apple Music playlist: {playlist_id}")
                return None
            
            # Get playlist attributes
            attributes = playlist_data.get('attributes', {})
            
            # Create playlist object
            playlist = Playlist(
                id=playlist_data['id'],
                name=attributes.get('name', 'Unknown Playlist'),
                description=attributes.get('description', {}).get('standard', ''),
                owner=attributes.get('curatorName', 'Apple Music'),
                platform='apple_music',
                url=attributes.get('url'),
                image_url=attributes.get('artwork', {}).get('url'),
                is_public=True  # Apple Music playlists are always public
            )
            
            # Get tracks from relationships
            relationships = playlist_data.get('relationships', {})
            tracks_data = relationships.get('tracks', {}).get('data', [])
            
            # Convert tracks to Track objects
            for track_data in tracks_data:
                attrs = track_data.get('attributes', {})
                
                # Skip if no attributes
                if not attrs:
                    continue
                
                # Create Track object
                track = Track(
                    name=attrs.get('name', 'Unknown Track'),
                    artist=attrs.get('artistName', 'Unknown Artist'),
                    album=attrs.get('albumName', ''),
                    duration_ms=int(attrs.get('durationInMillis', 0)),
                    isrc=attrs.get('isrc'),
                    uri={'apple_music': f"apple_music:track:{track_data.get('id')}"},
                    platform_ids={'apple_music': track_data.get('id')},
                    release_year=int(attrs.get('releaseDate', '0000')[:4]) 
                        if attrs.get('releaseDate') else None,
                    album_art_url=attrs.get('artwork', {}).get('url'),
                    explicit=attrs.get('contentRating') == 'explicit'
                )
                
                playlist.add_track(track)
            
            logger.info(f"Retrieved Apple Music playlist '{playlist.name}' with {len(playlist.tracks)} tracks")
            return playlist
            
        except Exception as e:
            logger.error(f"Error getting Apple Music playlist: {str(e)}")
            return None
    
    def search_track(self, track: Track) -> Optional[Track]:
        """
        Search for a track on Apple Music.
        
        Args:
            track: Track object to search for
            
        Returns:
            Track object with Apple Music details or None if not found
        """
        try:
            # Try to find by ISRC first (most accurate)
            if track.isrc:
                query = f"isrc:{track.isrc}"
                endpoint = f"catalog/{self.storefront}/songs"
                response = self._make_request("GET", endpoint, params={
                    "filter[isrc]": track.isrc,
                    "limit": 1
                })
                
                if response and response.get('data'):
                    track_data = response['data'][0]
                    return self._apple_music_track_to_track(track_data)
            
            # Try by track name and artist
            query = f"{track.name} {track.artist}"
            endpoint = f"catalog/{self.storefront}/search"
            response = self._make_request("GET", endpoint, params={
                "term": query,
                "types": "songs",
                "limit": 10
            })
            
            # Find best match
            if response and response.get('results', {}).get('songs', {}).get('data'):
                songs = response['results']['songs']['data']
                
                for song in songs:
                    attrs = song.get('attributes', {})
                    
                    # Check if this is a good match
                    if (attrs.get('name', '').lower() == track.name.lower() and
                            attrs.get('artistName', '').lower() == track.artist.lower()):
                        return self._apple_music_track_to_track(song)
                
                # If no exact match, return the first result
                return self._apple_music_track_to_track(songs[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching Apple Music track: {str(e)}")
            return None
    
    def create_playlist(self, name: str, description: str, tracks: List[Track]) -> Optional[Playlist]:
        """
        Create a new playlist on Apple Music.
        
        Args:
            name: Playlist name
            description: Playlist description
            tracks: List of Track objects to add
            
        Returns:
            Created Playlist object or None if creation failed
        """
        try:
            if not self.user_token:
                raise ValueError("User token required to create Apple Music playlists")
            
            # Create playlist
            endpoint = f"me/library/playlists"
            
            # Get track IDs
            track_ids = []
            for track in tracks:
                track_id = track.platform_ids.get('apple_music')
                if track_id:
                    track_ids.append({
                        "id": track_id,
                        "type": "songs"
                    })
            
            # Prepare data
            data = {
                "attributes": {
                    "name": name,
                    "description": description
                },
                "relationships": {
                    "tracks": {
                        "data": track_ids
                    }
                }
            }
            
            # Make request
            response = self._make_request("POST", endpoint, data=data, user_token=True)
            
            if not response or 'data' not in response:
                logger.error(f"Failed to create Apple Music playlist")
                return None
            
            playlist_data = response['data'][0] if response.get('data') else None
            
            if not playlist_data:
                logger.error(f"No data returned for created Apple Music playlist")
                return None
            
            # Create Playlist object
            playlist = Playlist(
                id=playlist_data['id'],
                name=name,
                description=description,
                owner="Me",  # User's own playlist
                platform='apple_music',
                url=None,  # Apple Music API doesn't return a URL for created playlists
                is_public=True
            )
            
            # Add tracks to playlist object
            playlist.tracks = tracks
            
            logger.info(f"Created Apple Music playlist '{name}' with {len(tracks)} tracks")
            return playlist
            
        except Exception as e:
            logger.error(f"Error creating Apple Music playlist: {str(e)}")
            return None
    
    def _apple_music_track_to_track(self, track_data: Dict[str, Any]) -> Track:
        """
        Convert Apple Music track data to Track object.
        
        Args:
            track_data: Apple Music track data dictionary
            
        Returns:
            Track object
        """
        attrs = track_data.get('attributes', {})
        
        return Track(
            name=attrs.get('name', 'Unknown Track'),
            artist=attrs.get('artistName', 'Unknown Artist'),
            album=attrs.get('albumName', ''),
            duration_ms=int(attrs.get('durationInMillis', 0)),
            isrc=attrs.get('isrc'),
            uri={'apple_music': f"apple_music:track:{track_data.get('id')}"},
            platform_ids={'apple_music': track_data.get('id')},
            release_year=int(attrs.get('releaseDate', '0000')[:4]) 
                if attrs.get('releaseDate') else None,
            album_art_url=attrs.get('artwork', {}).get('url'),
            explicit=attrs.get('contentRating') == 'explicit'
        )