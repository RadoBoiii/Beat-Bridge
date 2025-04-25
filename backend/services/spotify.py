"""
Spotify Service

This module implements the SpotifyService class for interacting with the Spotify Web API.
"""

import os
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Union

import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from models.track import Track
from models.playlist import Playlist

logger = logging.getLogger(__name__)


class SpotifyService:
    """
    Service for interacting with the Spotify Web API.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Spotify service.
        
        Args:
            access_token: OAuth access token for user-specific operations.
                          If not provided, uses client credentials flow.
        """
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.access_token = access_token
        self.sp = None
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Spotify client based on available credentials."""
        try:
            if self.access_token:
                # Use provided access token for user-specific operations
                self.sp = spotipy.Spotify(auth=self.access_token)
                logger.info("Initialized Spotify client with user access token")
            else:
                # Use client credentials for general operations
                auth_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                logger.info("Initialized Spotify client with client credentials")
                
            # Test the client
            self.sp.current_user() if self.access_token else self.sp.recommendation_genre_seeds()
            
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {str(e)}")
            self.sp = None
            raise
    
    def _handle_pagination(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle Spotify API pagination.
        
        Args:
            results: Initial response from Spotify API
            
        Returns:
            List of items from all pages
        """
        items = results['items']
        
        # Continue fetching if there are more pages
        while results['next']:
            results = self.sp.next(results)
            items.extend(results['items'])
        
        return items
    
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """
        Get a playlist from Spotify.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            Playlist object or None if not found
        """
        try:
            if not self.sp:
                self._initialize_client()
            
            # Get playlist details
            playlist_data = self.sp.playlist(playlist_id)
            
            # Create playlist object
            playlist = Playlist(
                id=playlist_data['id'],
                name=playlist_data['name'],
                description=playlist_data.get('description', ''),
                owner=playlist_data['owner']['display_name'],
                platform='spotify',
                url=playlist_data['external_urls'].get('spotify'),
                image_url=playlist_data['images'][0]['url'] if playlist_data.get('images') else None,
                is_public=playlist_data.get('public', True),
                followers=playlist_data.get('followers', {}).get('total', 0),
                collaborative=playlist_data.get('collaborative', False)
            )
            
            # Get all tracks (handle pagination)
            track_items = self._handle_pagination(playlist_data['tracks'])
            
            # Convert tracks to Track objects
            for item in track_items:
                if not item.get('track'):
                    continue
                    
                track_data = item['track']
                
                # Skip local files or tracks without IDs (can't be transferred)
                if track_data.get('is_local') or not track_data.get('id'):
                    continue
                
                # Create Track object
                track = Track(
                    name=track_data['name'],
                    artist=track_data['artists'][0]['name'] if track_data.get('artists') else 'Unknown',
                    album=track_data['album']['name'] if track_data.get('album') else '',
                    duration_ms=track_data.get('duration_ms', 0),
                    isrc=track_data.get('external_ids', {}).get('isrc'),
                    uri={'spotify': track_data['uri']},
                    platform_ids={'spotify': track_data['id']},
                    additional_artists=[
                        artist['name'] for artist in track_data.get('artists', [])[1:]
                    ],
                    release_year=int(track_data.get('album', {}).get('release_date', '0000')[:4]) 
                        if track_data.get('album', {}).get('release_date') else None,
                    album_art_url=track_data.get('album', {}).get('images', [{}])[0].get('url') 
                        if track_data.get('album', {}).get('images') else None,
                    explicit=track_data.get('explicit', False),
                    popularity=track_data.get('popularity')
                )
                
                playlist.add_track(track)
            
            logger.info(f"Retrieved Spotify playlist '{playlist.name}' with {len(playlist.tracks)} tracks")
            return playlist
            
        except Exception as e:
            logger.error(f"Error getting Spotify playlist: {str(e)}")
            return None
    
    def search_track(self, track: Track) -> Optional[Track]:
        """
        Search for a track on Spotify.
        
        Args:
            track: Track object to search for
            
        Returns:
            Track object with Spotify details or None if not found
        """
        try:
            if not self.sp:
                self._initialize_client()
            
            # Try to find by ISRC first (most accurate)
            if track.isrc:
                query = f"isrc:{track.isrc}"
                results = self.sp.search(q=query, type='track', limit=1)
                
                if results['tracks']['items']:
                    track_data = results['tracks']['items'][0]
                    return self._spotify_track_to_track(track_data)
            
            # Try by track name and artist
            query = f"track:{track.name} artist:{track.artist}"
            results = self.sp.search(q=query, type='track', limit=10)
            
            # Find best match
            if results['tracks']['items']:
                for track_data in results['tracks']['items']:
                    # Check if this is a good match
                    if (track_data['name'].lower() == track.name.lower() and
                            track_data['artists'][0]['name'].lower() == track.artist.lower()):
                        return self._spotify_track_to_track(track_data)
                
                # If no exact match, return the first result
                return self._spotify_track_to_track(results['tracks']['items'][0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching Spotify track: {str(e)}")
            return None
    
    def create_playlist(self, name: str, description: str, tracks: List[Track]) -> Optional[Playlist]:
        """
        Create a new playlist on Spotify.
        
        Args:
            name: Playlist name
            description: Playlist description
            tracks: List of Track objects to add
            
        Returns:
            Created Playlist object or None if creation failed
        """
        try:
            if not self.sp or not self.access_token:
                raise ValueError("User access token required to create playlists")
            
            # Get current user
            user_data = self.sp.current_user()
            user_id = user_data['id']
            
            # Create empty playlist
            playlist_data = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=True,
                description=description
            )
            
            # Create Playlist object
            playlist = Playlist(
                id=playlist_data['id'],
                name=playlist_data['name'],
                description=playlist_data.get('description', ''),
                owner=user_id,
                platform='spotify',
                url=playlist_data['external_urls'].get('spotify'),
                is_public=True
            )
            
            # Add tracks to playlist (in batches of 100)
            track_uris = []
            
            for track in tracks:
                uri = track.uri.get('spotify')
                if uri:
                    track_uris.append(uri)
                    playlist.add_track(track)
            
            # Add tracks in batches
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i:i+100]
                self.sp.playlist_add_items(playlist_data['id'], batch)
            
            logger.info(f"Created Spotify playlist '{name}' with {len(track_uris)} tracks")
            return playlist
            
        except Exception as e:
            logger.error(f"Error creating Spotify playlist: {str(e)}")
            return None
    
    def _spotify_track_to_track(self, track_data: Dict[str, Any]) -> Track:
        """
        Convert Spotify track data to Track object.
        
        Args:
            track_data: Spotify track data dictionary
            
        Returns:
            Track object
        """
        return Track(
            name=track_data['name'],
            artist=track_data['artists'][0]['name'] if track_data.get('artists') else 'Unknown',
            album=track_data['album']['name'] if track_data.get('album') else '',
            duration_ms=track_data.get('duration_ms', 0),
            isrc=track_data.get('external_ids', {}).get('isrc'),
            uri={'spotify': track_data['uri']},
            platform_ids={'spotify': track_data['id']},
            additional_artists=[
                artist['name'] for artist in track_data.get('artists', [])[1:]
            ],
            release_year=int(track_data.get('album', {}).get('release_date', '0000')[:4]) 
                if track_data.get('album', {}).get('release_date') else None,
            album_art_url=track_data.get('album', {}).get('images', [{}])[0].get('url') 
                if track_data.get('album', {}).get('images') else None,
            explicit=track_data.get('explicit', False),
            popularity=track_data.get('popularity')
        )