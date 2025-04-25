"""
Track Matching Utilities

This module provides utilities for matching tracks between different music platforms.
"""

import logging
import time
from typing import Dict, List, Tuple, Optional, Any

from models.track import Track
from services.spotify import SpotifyService
from services.apple_music import AppleMusicService
from services.youtube_music import YouTubeMusicService

logger = logging.getLogger(__name__)


def match_tracks(tracks: List[Track], destination_service: Any) -> Tuple[List[Track], List[Track]]:
    """
    Match tracks from one platform to another.
    
    Args:
        tracks: List of Track objects to match
        destination_service: Service for the destination platform
        
    Returns:
        Tuple of (matched_tracks, failed_tracks)
    """
    matched_tracks = []
    failed_tracks = []
    
    logger.info(f"Matching {len(tracks)} tracks to destination platform")
    
    for index, track in enumerate(tracks):
        logger.debug(f"Matching track {index+1}/{len(tracks)}: {track.name} by {track.artist}")
        
        # Try to find match on destination platform
        match = destination_service.search_track(track)
        
        if match:
            # Update original track with destination platform details
            track.uri.update(match.uri)
            track.platform_ids.update(match.platform_ids)
            
            # Add to matched tracks
            matched_tracks.append(track)
            
            logger.debug(f"Found match for '{track.name}' by {track.artist}")
        else:
            # Add to failed tracks
            failed_tracks.append(track)
            
            logger.debug(f"No match found for '{track.name}' by {track.artist}")
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.1)
    
    logger.info(f"Matched {len(matched_tracks)}/{len(tracks)} tracks")
    return matched_tracks, failed_tracks


def match_track_by_isrc(track: Track, destination_service: Any) -> Optional[Track]:
    """
    Match a track by ISRC code (most accurate method).
    
    Args:
        track: Track object to match
        destination_service: Service for the destination platform
        
    Returns:
        Matched Track object or None if no match
    """
    if not track.isrc:
        return None
    
    return destination_service.search_track(track)


def calculate_track_similarity(track1: Track, track2: Track) -> float:
    """
    Calculate similarity score between two tracks (0.0 to 1.0).
    
    Args:
        track1: First Track object
        track2: Second Track object
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    # Start with base score
    score = 0.0
    total_weight = 0.0
    
    # Compare track names (highest weight)
    name_weight = 0.5
    if track1.name.lower() == track2.name.lower():
        score += name_weight
    elif track1.name.lower() in track2.name.lower() or track2.name.lower() in track1.name.lower():
        score += name_weight * 0.8
    total_weight += name_weight
    
    # Compare artist names
    artist_weight = 0.3
    if track1.artist.lower() == track2.artist.lower():
        score += artist_weight
    elif track1.artist.lower() in track2.artist.lower() or track2.artist.lower() in track1.artist.lower():
        score += artist_weight * 0.8
    total_weight += artist_weight
    
    # Compare album names
    album_weight = 0.1
    if track1.album and track2.album and (track1.album.lower() == track2.album.lower()):
        score += album_weight
    elif track1.album and track2.album and (track1.album.lower() in track2.album.lower() or track2.album.lower() in track1.album.lower()):
        score += album_weight * 0.8
    total_weight += album_weight
    
    # Compare duration (if both are available)
    duration_weight = 0.1
    if track1.duration_ms > 0 and track2.duration_ms > 0:
        # Calculate duration difference percentage
        diff_percentage = abs(track1.duration_ms - track2.duration_ms) / max(track1.duration_ms, track2.duration_ms)
        
        # Score based on similarity (lower difference is better)
        if diff_percentage < 0.05:  # Less than 5% difference
            score += duration_weight
        elif diff_percentage < 0.1:  # Less than 10% difference
            score += duration_weight * 0.8
        elif diff_percentage < 0.2:  # Less than 20% difference
            score += duration_weight * 0.5
        
        total_weight += duration_weight
    
    # Normalize score by total weight
    return score / total_weight if total_weight > 0 else 0.0


def find_best_match(track: Track, candidates: List[Track]) -> Optional[Track]:
    """
    Find the best matching track from a list of candidates.
    
    Args:
        track: Track to match
        candidates: List of candidate Track objects
        
    Returns:
        Best matching Track or None if no good match
    """
    best_match = None
    best_score = 0.0
    
    for candidate in candidates:
        score = calculate_track_similarity(track, candidate)
        
        if score > best_score:
            best_score = score
            best_match = candidate
    
    # Only return a match if it's good enough
    if best_score >= 0.8:
        return best_match
    
    return None


def deduplicate_tracks(tracks: List[Track]) -> List[Track]:
    """
    Remove duplicate tracks from a list.
    
    Args:
        tracks: List of Track objects
        
    Returns:
        List of unique Track objects
    """
    unique_tracks = []
    seen_ids = set()
    
    for track in tracks:
        # Create a unique ID based on name and artist
        unique_id = f"{track.name.lower()}|{track.artist.lower()}"
        
        if unique_id not in seen_ids:
            seen_ids.add(unique_id)
            unique_tracks.append(track)
    
    return unique_tracks