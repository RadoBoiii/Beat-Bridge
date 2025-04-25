# Spotify to Other Music Platforms Transfer Agent
# Built with Fetch.ai uAgents Framework

from uagents import Agent, Context, Protocol
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import requests
import base64
import time
from typing import Dict, List, Optional, Any

# Define our main playlist transfer agent
playlist_transfer_agent = Agent(
    name="PlaylistTransferAgent",
    seed="your-unique-seed-here"  # Replace with a unique seed for your agent
)

# Define message protocols
class PlaylistTransferRequest:
    """Request to transfer a playlist from one platform to another"""
    source_platform: str  # e.g., "spotify"
    source_playlist_id: str
    destination_platform: str  # e.g., "apple_music", "youtube_music"
    destination_user_id: Optional[str] = None

class PlaylistTransferResponse:
    """Response after attempting to transfer a playlist"""
    success: bool
    message: str
    destination_playlist_id: Optional[str] = None
    destination_playlist_url: Optional[str] = None
    failed_tracks: List[Dict[str, str]] = []

# Create protocol for handling playlist transfers
playlist_protocol = Protocol("playlist_transfer")

@playlist_protocol.on_message(model=PlaylistTransferRequest)
async def handle_playlist_transfer(ctx: Context, sender: str, msg: PlaylistTransferRequest):
    """Handle playlist transfer requests between music platforms"""
    ctx.logger.info(f"Received playlist transfer request from {sender}")
    
    try:
        # Step 1: Extract songs from source platform (Spotify in this example)
        if msg.source_platform.lower() == "spotify":
            tracks = await extract_spotify_playlist(ctx, msg.source_playlist_id)
        else:
            raise ValueError(f"Unsupported source platform: {msg.source_platform}")
        
        # Step 2: Create playlist on destination platform
        if msg.destination_platform.lower() == "apple_music":
            result = await create_apple_music_playlist(
                ctx, 
                tracks,
                f"Imported from Spotify",
                msg.destination_user_id
            )
        elif msg.destination_platform.lower() == "youtube_music":
            result = await create_youtube_music_playlist(
                ctx, 
                tracks,
                f"Imported from Spotify",
                msg.destination_user_id
            )
        else:
            raise ValueError(f"Unsupported destination platform: {msg.destination_platform}")
        
        # Step 3: Send response with results
        await ctx.send(
            sender,
            PlaylistTransferResponse(
                success=result["success"],
                message=result["message"],
                destination_playlist_id=result.get("playlist_id"),
                destination_playlist_url=result.get("playlist_url"),
                failed_tracks=result.get("failed_tracks", [])
            )
        )
        
    except Exception as e:
        ctx.logger.error(f"Error during playlist transfer: {str(e)}")
        await ctx.send(
            sender,
            PlaylistTransferResponse(
                success=False,
                message=f"Error during playlist transfer: {str(e)}"
            )
        )

# Register the protocol with our agent
playlist_transfer_agent.include(playlist_protocol)

# ---- Platform-specific implementations ----

async def extract_spotify_playlist(ctx: Context, playlist_id: str) -> List[Dict[str, str]]:
    """Extract tracks from a Spotify playlist"""
    ctx.logger.info(f"Extracting tracks from Spotify playlist: {playlist_id}")
    
    # Set up Spotify client with proper OAuth
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-read-private"
    ))
    
    # Get playlist details
    results = sp.playlist_items(playlist_id)
    
    # Extract relevant track info
    tracks = []
    for item in results['items']:
        track = item['track']
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'spotify_uri': track['uri']
        }
        tracks.append(track_info)
        
    # Handle pagination if the playlist has more than 100 tracks
    while results['next']:
        results = sp.next(results)
        for item in results['items']:
            track = item['track']
            track_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'spotify_uri': track['uri']
            }
            tracks.append(track_info)
    
    ctx.logger.info(f"Extracted {len(tracks)} tracks from Spotify playlist")
    return tracks

async def create_apple_music_playlist(
    ctx: Context, 
    tracks: List[Dict[str, str]], 
    playlist_name: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a playlist on Apple Music with the given tracks"""
    ctx.logger.info(f"Creating Apple Music playlist with {len(tracks)} tracks")
    
    # In a real implementation, you would:
    # 1. Authenticate with Apple Music API using developer token
    # 2. Search for each track to get Apple Music IDs
    # 3. Create a new playlist
    # 4. Add all found tracks to the playlist
    
    # This is a simplified mock implementation
    # In production, you would use the Apple Music API
    
    # Mock searching for tracks on Apple Music
    found_tracks = []
    failed_tracks = []
    
    for track in tracks:
        try:
            # In production, you would search Apple Music API here
            # Mock successful match for demonstration
            found_tracks.append({
                "apple_music_id": f"mock_id_{track['name']}",
                "original_track": track
            })
        except Exception as e:
            ctx.logger.warning(f"Failed to find track {track['name']} by {track['artist']} on Apple Music: {str(e)}")
            failed_tracks.append({
                "name": track['name'],
                "artist": track['artist'],
                "reason": str(e)
            })
    
    # Mock creating a playlist
    # In production, you would call Apple Music API to create playlist and add tracks
    mock_playlist_id = f"apple_music_playlist_{int(time.time())}"
    
    return {
        "success": True,
        "message": f"Successfully created Apple Music playlist with {len(found_tracks)} tracks. {len(failed_tracks)} tracks could not be found.",
        "playlist_id": mock_playlist_id,
        "playlist_url": f"https://music.apple.com/us/playlist/{mock_playlist_id}",
        "failed_tracks": failed_tracks
    }

async def create_youtube_music_playlist(
    ctx: Context, 
    tracks: List[Dict[str, str]], 
    playlist_name: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a playlist on YouTube Music with the given tracks"""
    ctx.logger.info(f"Creating YouTube Music playlist with {len(tracks)} tracks")
    
    # In a real implementation, you would:
    # 1. Authenticate with YouTube Music API
    # 2. Search for each track to get YouTube Music IDs
    # 3. Create a new playlist
    # 4. Add all found tracks to the playlist
    
    # This is a simplified mock implementation
    # In production, you would use the YouTube API
    
    # Mock searching for tracks on YouTube Music
    found_tracks = []
    failed_tracks = []
    
    for track in tracks:
        try:
            # In production, you would search YouTube Music API here
            # Mock successful match for demonstration
            found_tracks.append({
                "youtube_music_id": f"mock_id_{track['name']}",
                "original_track": track
            })
        except Exception as e:
            ctx.logger.warning(f"Failed to find track {track['name']} by {track['artist']} on YouTube Music: {str(e)}")
            failed_tracks.append({
                "name": track['name'],
                "artist": track['artist'],
                "reason": str(e)
            })
    
    # Mock creating a playlist
    # In production, you would call YouTube Music API to create playlist and add tracks
    mock_playlist_id = f"youtube_music_playlist_{int(time.time())}"
    
    return {
        "success": True,
        "message": f"Successfully created YouTube Music playlist with {len(found_tracks)} tracks. {len(failed_tracks)} tracks could not be found.",
        "playlist_id": mock_playlist_id,
        "playlist_url": f"https://music.youtube.com/playlist?list={mock_playlist_id}",
        "failed_tracks": failed_tracks
    }

# Run the agent
if __name__ == "__main__":
    playlist_transfer_agent.run()