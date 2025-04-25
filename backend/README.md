# BeatBridge Backend Service

This is the backend service for BeatBridge, a cross-platform playlist transfer application.

## Features

- REST API for playlist conversion
- Support for multiple music platforms
- Asynchronous job processing
- Smart track matching algorithm
- Platform-specific service implementations

## Architecture

The backend service is built with:

- **Flask**: Web framework for the API
- **Redis & RQ**: For background job processing
- **Spotipy**: For Spotify API integration
- **Google API Client**: For YouTube Music API integration
- **JWT**: For Apple Music authentication

## Directory Structure

```
backend/
│
├── models/                 # Data models
│   ├── __init__.py
│   ├── track.py            # Track model
│   └── playlist.py         # Playlist model
│
├── services/               # Platform-specific services
│   ├── __init__.py
│   ├── spotify.py          # Spotify API integration
│   ├── apple_music.py      # Apple Music API integration
│   └── youtube_music.py    # YouTube Music API integration
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── auth.py             # Authentication utilities
│   ├── matching.py         # Track matching algorithms
│   └── logging.py          # Logging configuration
│
├── config.py               # Configuration settings
├── service.py              # Main service entry point
├── requirements.txt        # Python dependencies
└── Dockerfile              # Docker configuration
```

## Getting Started

### Prerequisites

- Python 3.9+
- Redis for job queue
- API keys for each music platform

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your API keys and configuration
   ```

4. Place Apple Music private key in the keys directory:
   ```bash
   mkdir -p keys
   # Copy your private key to keys/apple_music_auth_key.p8
   ```

### Running the Service

1. Start Redis:
   ```bash
   docker run -d -p 6379:6379 redis:alpine
   ```

2. Run the service:
   ```bash
   python service.py
   ```

3. For production, use Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5001 --workers 3 service:app
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t beatbridge-backend .
   ```

2. Run the container:
   ```bash
   docker run -d -p 5001:5001 \
     --env-file ../.env \
     -v $(pwd)/keys:/app/keys \
     --name beatbridge-backend \
     beatbridge-backend
   ```

## API Endpoints

### Health Check
```
GET /health
```
Returns the service status and current timestamp.

### Start Playlist Conversion
```
POST /api/convert
```
Request body:
```json
{
  "source_platform": "spotify",
  "destination_platform": "apple_music",
  "playlist_id": "37i9dQZF1DX4sWSpwq3LiO",
  "spotify_source_token": "optional_spotify_access_token"
}
```
Response:
```json
{
  "success": true,
  "message": "Conversion started",
  "job_id": "12345678-1234-5678-9012-123456789012"
}
```

### Check Conversion Status
```
GET /api/status/{job_id}
```
Response:
```json
{
  "success": true,
  "status": "processing",
  "progress": 30
}
```
Or when completed:
```json
{
  "success": true,
  "status": "completed",
  "result": {
    "success": true,
    "message": "Successfully transferred 25 tracks to apple_music. 2 tracks could not be found.",
    "playlist_id": "pl.u-123456789",
    "playlist_url": "https://music.apple.com/us/playlist/imported-playlist/pl.u-123456789",
    "source_platform": "spotify",
    "destination_platform": "apple_music",
    "source_playlist_name": "My Playlist",
    "total_tracks": 27,
    "matched_tracks": 25,
    "failed_tracks": [
      {
        "name": "Track Name",
        "artist": "Artist Name",
        "reason": "Could not find matching track"
      }
    ]
  }
}
```

## Testing

Run the unit tests:
```bash
python -m unittest discover -s tests/backend
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.