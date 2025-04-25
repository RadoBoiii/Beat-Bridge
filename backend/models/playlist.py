"""
Playlist Model

This module defines the Playlist class used to represent a music playlist across different platforms.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .track import Track


@dataclass
class Playlist:
    """
    Represents a music playlist with cross-platform identifiers.
    
    Attributes:
        id (str): The platform-specific ID of the playlist
        name (str): The name/title of the playlist
        description (str): The playlist description
        owner (str): The owner/creator of the playlist
        tracks (List[Track]): List of tracks in the playlist
        platform (str): The platform where this playlist exists (spotify, apple_music, etc.)
        url (Optional[str]): URL to access the playlist on its platform
        image_url (Optional[str]): URL to the playlist cover image
        is_public (bool): Whether the playlist is publicly accessible
        followers (int): Number of followers/subscribers
        collaborative (bool): Whether the playlist is collaborative
        created_at (Optional[str]): Creation date in ISO format
        metadata (Dict[str, Any]): Additional platform-specific metadata
    """
    
    id: str
    name: str
    description: str = ""
    owner: str = ""
    tracks: List[Track] = field(default_factory=list)
    platform: str = ""
    url: Optional[str] = None
    image_url: Optional[str] = None
    is_public: bool = True
    followers: int = 0
    collaborative: bool = False
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the playlist."""
        return f"{self.name} ({len(self.tracks)} tracks) on {self.platform}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert playlist to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner,
            'platform': self.platform,
            'url': self.url,
            'image_url': self.image_url,
            'is_public': self.is_public,
            'followers': self.followers,
            'collaborative': self.collaborative,
            'created_at': self.created_at,
            'track_count': len(self.tracks),
            'tracks': [track.to_dict() for track in self.tracks[:10]],  # Include first 10 tracks for preview
            'has_more_tracks': len(self.tracks) > 10
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], include_tracks: bool = True) -> 'Playlist':
        """Create playlist from dictionary."""
        playlist = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            owner=data.get('owner', ''),
            platform=data.get('platform', ''),
            url=data.get('url'),
            image_url=data.get('image_url'),
            is_public=data.get('is_public', True),
            followers=data.get('followers', 0),
            collaborative=data.get('collaborative', False),
            created_at=data.get('created_at'),
            metadata=data.get('metadata', {})
        )
        
        # Add tracks if included and present
        if include_tracks and 'tracks' in data:
            playlist.tracks = [
                Track.from_dict(track) if isinstance(track, dict) else track
                for track in data['tracks']
            ]
        
        return playlist
    
    def add_track(self, track: Track) -> None:
        """Add a track to the playlist."""
        self.tracks.append(track)
    
    def remove_track(self, track_id: str) -> bool:
        """
        Remove a track from the playlist by ID.
        
        Args:
            track_id: The platform-specific ID of the track
            
        Returns:
            bool: True if track was removed, False if not found
        """
        for i, track in enumerate(self.tracks):
            if track.platform_ids.get(self.platform) == track_id:
                self.tracks.pop(i)
                return True
        return False
    
    def get_track_count(self) -> int:
        """Get the number of tracks in the playlist."""
        return len(self.tracks)