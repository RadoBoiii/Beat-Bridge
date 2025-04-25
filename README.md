# BeatBridge

BeatBridge is a cross-platform playlist transfer service that allows users to move playlists between different music streaming platforms like Spotify, Apple Music, and YouTube Music.

## Features

- Transfer playlists between multiple music platforms
- No account creation needed
- Automatic track matching across platforms
- Detailed conversion reports
- User-friendly interface

## Supported Platforms

- Spotify
- Apple Music
- YouTube Music
- More platforms coming soon!

## Project Structure

The project is divided into two main components:

1. **Frontend (webapp/)**: Flask application that provides the user interface
2. **Backend (backend/)**: Conversion service that handles the actual playlist transfers

## Requirements

- Python 3.9+
- Docker and Docker Compose (for deployment)
- API keys for supported music platforms

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/beatbridge.git
   cd beatbridge
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies for both components:
   ```bash
   cd webapp
   pip install -r requirements.txt
   cd ../backend
   pip install -r requirements.txt
   cd ..
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Run the development servers:
   ```bash
   # Terminal 1 - Frontend
   cd webapp
   flask run --port=5000

   # Terminal 2 - Backend
   cd backend
   flask run --port=5001
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Docker Deployment

1. Make sure Docker and Docker Compose are installed on your server

2. Configure your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. Build and run the containers:
   ```bash
   docker-compose up -d
   ```

4. The application will be available at `http://localhost:5000`

## API Keys Setup

For this application to work, you'll need to register as a developer with each music platform:

### Spotify
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new application
3. Set the redirect URI to `http://yourdomain.com/spotify-callback`
4. Copy the Client ID and Client Secret to your `.env` file

### Apple Music
1. Enroll in the [Apple Developer Program](https://developer.apple.com/programs/)
2. Create a MusicKit identifier in the developer console
3. Create a private key and download the `.p8` file
4. Copy the Team ID, Key ID, and place the private key file in the `keys/` directory

### YouTube Music
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project and enable the YouTube Data API v3
3. Create OAuth 2.0 credentials
4. Set the redirect URI to `http://yourdomain.com/youtube-callback`
5. Copy the Client ID and Client Secret to your `.env` file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Fetch.ai](https://fetch.ai/) technology
- Utilizes the Spotify, Apple Music, and YouTube Music APIs
- Inspired by similar tools like Soundiiz and SongShift