"""
YouTube Music Service

This module implements the YouTubeMusicService class for interacting with the YouTube Music API.
"""

import os
import logging
import time
import json
import re
from typing import Dict, List, Optional, Tuple, Any, Union

import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from models.track import Track
from models.playlist import Playlist

logger = logging.getLogger(__name__)


class YouTubeMusicService:
    """
    Service for interacting with the YouTube Music API via YouTube Data API.
    
    Note: YouTube Music doesn't have an official API, so we use the YouTube Data API.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the YouTube Music service.
        
        Args:
            access_token: OAuth access token for user-specific operations.
        """
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.access_token = access_token
        self.youtube = None
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize YouTube client based on available credentials."""
        try:
            if self.access_token:
                # Use OAuth2 credentials for user-specific operations
                credentials = Credentials(
                    token=self.access_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=os.getenv('YOUTUBE_CLIENT_ID'),
                    client_secret=os.getenv('YOUTUBE_CLIENT_SECRET')
                )
                self.youtube = build('youtube', 'v3', credentials=credentials)
                logger.info("Initialized YouTube client with OAuth credentials")
            else:
                # Use API key for general operations
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("Initialized YouTube client with API key")
                
        except Exception as e:
            logger.error(f"Failed to initialize YouTube client: {str(e)}")
            self.youtube = None
            raise
    
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """
        Get a playlist from YouTube Music.
        
        Args:
            playlist_id: YouTube playlist ID
            
        Returns:
            Playlist object or None if not found
        """
        try:
            if not self.youtube:
                self._initialize_client()
            
            # Get playlist details
            playlist_response = self.youtube.playlists().list(
                part="snippet,contentDetails,status",
                id=playlist_id
            ).execute()
            
            if not playlist_response.get('items'):
                logger.error(f"Failed to get YouTube Music playlist: {playlist_id}")
                return None
            
            playlist_data = playlist_response['items'][0]
            
            # Get playlist metadata
            snippet = playlist_data.get('snippet', {})
            
            # Create playlist object
            playlist = Playlist(
                id=playlist_data['id'],
                name=snippet.get('title', 'Unknown Playlist'),
                description=snippet.get('description', ''),
                owner=snippet.get('channelTitle', 'Unknown'),
                platform='youtube_music',
                url=f"https://music.youtube.com/playlist?list={playlist_data['id']}",
                image_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
                is_public=playlist_data.get('status', {}).get('privacyStatus') == 'public'
            )
            
            # Get playlist items (videos)
            next_page_token = None
            
            while True:
                items_response = self.youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                
                # Process items (videos)
                for item in items_response.get('items', []):
                    # Skip non-music videos (in general playlists)
                    # YouTube Music playlists should only contain music videos
                    video_id = item.get('contentDetails', {}).get('videoId')
                    snippet = item.get('snippet', {})
                    
                    if not video_id or not snippet:
                        continue
                    
                    # Get video details (to get duration)
                    video_response = self.youtube.videos().list(
                        part="contentDetails,snippet",
                        id=video_id
                    ).execute()
                    
                    if not video_response.get('items'):
                        continue
                    
                    video_data = video_response['items'][0]
                    video_snippet = video_data.get('snippet', {})
                    
                    # Try to extract artist and title from video title
                    # Format is usually "Artist - Title" or "Artist - Title (Official Video)"
                    video_title = video_snippet.get('title', '')
                    artist, title = self._parse_video_title(video_title)
                    
                    # Convert duration from ISO format to milliseconds
                    duration_iso = video_data.get('contentDetails', {}).get('duration', 'PT0S')
                    duration_ms = self._iso_duration_to_ms(duration_iso)
                    
                    # Create Track object
                    track = Track(
                        name=title,
                        artist=artist,
                        duration_ms=duration_ms,
                        uri={'youtube_music': f"youtube:video:{video_id}"},
                        platform_ids={'youtube_music': video_id},
                        album_art_url=video_snippet.get('thumbnails', {}).get('high', {}).get('url')
                    )
                    
                    playlist.add_track(track)
                
                # Check if there are more pages
                next_page_token = items_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            logger.info(f"Retrieved YouTube Music playlist '{playlist.name}' with {len(playlist.tracks)} tracks")
            return playlist
            
        except Exception as e:
            logger.error(f"Error getting YouTube Music playlist: {str(e)}")
            return None
    
    def search_track(self, track: Track) -> Optional[Track]:
        """
        Search for a track on YouTube Music.
        
        Args:
            track: Track object to search for
            
        Returns:
            Track object with YouTube Music details or None if not found
        """
        try:
            if not self.youtube:
                self._initialize_client()
            
            # Build search query
            query = f"{track.name} {track.artist} music"
            
            # Search for videos
            search_response = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=10,
                videoEmbeddable="true",
                videoCategoryId="10"  # Music category
            ).execute()
            
            if not search_response.get('items'):
                return None
            
            # Get the first result
            video_data = search_response['items'][0]
            video_id = video_data['id']['videoId']
            snippet = video_data['snippet']
            
            # Get video details (to get duration)
            video_response = self.youtube.videos().list(
                part="contentDetails,snippet",
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return None
            
            video_details = video_response['items'][0]
            
            # Try to extract artist and title from video title
            video_title = snippet.get('title', '')
            artist, title = self._parse_video_title(video_title)
            
            # Use original track info if parsing failed
            if not artist:
                artist = track.artist
            if not title:
                title = track.name
            
            # Convert duration from ISO format to milliseconds
            duration_iso = video_details.get('contentDetails', {}).get('duration', 'PT0S')
            duration_ms = self._iso_duration_to_ms(duration_iso)
            
            # Create Track object
            return Track(
                name=title,
                artist=artist,
                duration_ms=duration_ms,
                uri={'youtube_music': f"youtube:video:{video_id}"},
                platform_ids={'youtube_music': video_id},
                album_art_url=snippet.get('thumbnails', {}).get('high', {}).get('url')
            )
            
        except Exception as e:
            logger.error(f"Error searching YouTube Music track: {str(e)}")
            return None
    
    def create_playlist(self, name: str, description: str, tracks: List[Track]) -> Optional[Playlist]:
        """
        Create a new playlist on YouTube Music.
        
        Args:
            name: Playlist name
            description: Playlist description
            tracks: List of Track objects to add
            
        Returns:
            Created Playlist object or None if creation failed
        """
        try:
            if not self.youtube or not self.access_token:
                raise ValueError("OAuth credentials required to create YouTube playlists")
            
            # Create playlist
            playlist_response = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": name,
                        "description": description
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            ).execute()
            
            if not playlist_response or 'id' not in playlist_response:
                logger.error("Failed to create YouTube Music playlist")
                return None
            
            playlist_id = playlist_response['id']
            
            # Create Playlist object
            playlist = Playlist(
                id=playlist_id,
                name=name,
                description=description,
                owner="Me",  # User's own playlist
                platform='youtube_music',
                url=f"https://music.youtube.com/playlist?list={playlist_id}",
                image_url=playlist_response.get('snippet', {}).get('thumbnails', {}).get('high', {}).get('url'),
                is_public=True
            )
            
            # Add tracks to playlist
            for track in tracks:
                video_id = track.platform_ids.get('youtube_music')
                
                if not video_id:
                    # Try to search for the track if we don't have an ID
                    found_track = self.search_track(track)
                    if found_track:
                        video_id = found_track.platform_ids.get('youtube_music')
                
                if video_id:
                    try:
                        self.youtube.playlistItems().insert(
                            part="snippet",
                            body={
                                "snippet": {
                                    "playlistId": playlist_id,
                                    "resourceId": {
                                        "kind": "youtube#video",
                                        "videoId": video_id
                                    }
                                }
                            }
                        ).execute()
                        
                        # Add track to playlist object
                        playlist.add_track(track)
                        
                    except Exception as e:
                        logger.error(f"Error adding track to YouTube playlist: {str(e)}")
            
            logger.info(f"Created YouTube Music playlist '{name}' with {len(playlist.tracks)} tracks")
            return playlist
            
        except Exception as e:
            logger.error(f"Error creating YouTube Music playlist: {str(e)}")
            return None
    
    def _parse_video_title(self, title: str) -> Tuple[str, str]:
        """
        Parse artist and track name from YouTube video title.
        
        Args:
            title: YouTube video title
            
        Returns:
            Tuple of (artist, track_name)
        """
        # Common patterns:
        # "Artist - Track"
        # "Artist - Track (Official Video)"
        # "Artist - Track [Official Video]"
        # "Artist - Track | Official Video"
        
        # Try the most common pattern first
        match = re.match(r'^(.*?)\s*[-:]\s*(.*?)(?:\s*[\(\[\|].*)?$', title)
        
        if match:
            artist = match.group(1).strip()
            track = match.group(2).strip()
            return artist, track
        
        # If no match, return the full title as the track name and empty artist
        return "", title
    
    def _iso_duration_to_ms(self, iso_duration: str) -> int:
        """
        Convert ISO 8601 duration to milliseconds.
        
        Args:
            iso_duration: Duration in ISO 8601 format (e.g., PT4M13S)
            
        Returns:
            Duration in milliseconds
        """
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        hour_match = re.search(r'(\d+)H', iso_duration)
        if hour_match:
            hours = int(hour_match.group(1))
        
        # Extract minutes
        minute_match = re.search(r'(\d+)M', iso_duration)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        # Extract seconds
        second_match = re.search(r'(\d+)S', iso_duration)
        if second_match:
            seconds = int(second_match.group(1))
        
        # Calculate total milliseconds
        total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
        
        return total_ms