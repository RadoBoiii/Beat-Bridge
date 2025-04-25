"""
Track Model

This module defines the Track class used to represent a music track across different platforms.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Track:
    """
    Represents a music track with cross-platform identifiers.
    
    Attributes:
        name (str): The name/title of the track
        artist (str): The primary artist name
        album (str): The album name
        duration_ms (int): Track duration in milliseconds
        isrc (Optional[str]): International Standard Recording Code (used for cross-platform matching)
        uri (Dict[str, str]): Dictionary of platform URIs keyed by platform name
        platform_ids (Dict[str, str]): Dictionary of platform-specific IDs
        additional_artists (List[str]): List of additional artist names (beyond primary)
        release_year (Optional[int]): Year the track was released
        album_art_url (Optional[str]): URL to the album artwork
        explicit (bool): Whether the track contains explicit content
        popularity (Optional[int]): Platform-specific popularity score (0-100)
        genres (List[str]): List of genres associated with the track
        metadata (Dict[str, Any]): Additional platform-specific metadata
    """
    
    name: str
    artist: str
    album: str = ""
    duration_ms: int = 0
    isrc: Optional[str] = None
    uri: Dict[str, str] = field(default_factory=dict)
    platform_ids: Dict[str, str] = field(default_factory=dict)
    additional_artists: List[str] = field(default_factory=list)
    release_year: Optional[int] = None
    album_art_url: Optional[str] = None
    explicit: bool = False
    popularity: Optional[int] = None
    genres: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the track."""
        return f"{self.name} by {self.artist}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert track to dictionary."""
        return {
            'name': self.name,
            'artist': self.artist,
            'album': self.album,
            'duration_ms': self.duration_ms,
            'isrc': self.isrc,
            'uri': self.uri,
            'platform_ids': self.platform_ids,
            'additional_artists': self.additional_artists,
            'release_year': self.release_year,
            'album_art_url': self.album_art_url,
            'explicit': self.explicit,
            'popularity': self.popularity,
            'genres': self.genres
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Track':
        """Create track from dictionary."""
        return cls(
            name=data.get('name', ''),
            artist=data.get('artist', ''),
            album=data.get('album', ''),
            duration_ms=data.get('duration_ms', 0),
            isrc=data.get('isrc'),
            uri=data.get('uri', {}),
            platform_ids=data.get('platform_ids', {}),
            additional_artists=data.get('additional_artists', []),
            release_year=data.get('release_year'),
            album_art_url=data.get('album_art_url'),
            explicit=data.get('explicit', False),
            popularity=data.get('popularity'),
            genres=data.get('genres', []),
            metadata=data.get('metadata', {})
        )
    
    def get_artists_string(self) -> str:
        """Get string representation of all artists."""
        if not self.additional_artists:
            return self.artist
        
        artists = [self.artist] + self.additional_artists
        if len(artists) == 2:
            return f"{artists[0]} & {artists[1]}"
        
        return f"{', '.join(artists[:-1])} & {artists[-1]}"
    
    def get_search_query(self) -> str:
        """
        Get a search query string for finding this track on other platforms.
        
        Returns:
            str: A search query string combining track name and artist
        """
        return f"{self.name} {self.artist}"