"""Test suite for the BeatBridge web application."""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the webapp directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../webapp')))

from app import app
from utils.helpers import extract_playlist_id
from utils.validators import validate_playlist_url

class BeatBridgeTestCase(unittest.TestCase):
    """Test case for the BeatBridge web application."""
    
    def setUp(self):
        """Set up test client and disable CSRF protection."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SERVER_NAME'] = 'localhost'
        self.client = app.test_client()
        
        # Create app context
        self.app_context = app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()
    
    def test_index_page(self):
        """Test the index page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BeatBridge', response.data)
    
    def test_about_page(self):
        """Test the about page loads correctly."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About BeatBridge', response.data)
    
    def test_extract_spotify_playlist_id(self):
        """Test extracting Spotify playlist IDs from URLs."""
        # Standard Spotify URL
        url = 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'
        self.assertEqual(extract_playlist_id(url, 'spotify'), '37i9dQZF1DX4sWSpwq3LiO')
        
        # URL with query parameters
        url = 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO?si=12345678'
        self.assertEqual(extract_playlist_id(url, 'spotify'), '37i9dQZF1DX4sWSpwq3LiO')
        
        # Spotify URI
        url = 'spotify:playlist:37i9dQZF1DX4sWSpwq3LiO'
        self.assertEqual(extract_playlist_id(url, 'spotify'), '37i9dQZF1DX4sWSpwq3LiO')
    
    def test_extract_apple_music_playlist_id(self):
        """Test extracting Apple Music playlist IDs from URLs."""
        # Standard Apple Music URL
        url = 'https://music.apple.com/us/playlist/top-100-global/pl.d25f5d1181894928af76c85c967f8f31'
        self.assertEqual(extract_playlist_id(url, 'apple_music'), 'pl.d25f5d1181894928af76c85c967f8f31')
    
    def test_extract_youtube_music_playlist_id(self):
        """Test extracting YouTube Music playlist IDs from URLs."""
        # Standard YouTube Music URL
        url = 'https://music.youtube.com/playlist?list=RDCLAK5uy_ktw'
        self.assertEqual(extract_playlist_id(url, 'youtube_music'), 'RDCLAK5uy_ktw')
    
    def test_validate_spotify_url(self):
        """Test validating Spotify playlist URLs."""
        # Valid URL
        url = 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'
        valid, message = validate_playlist_url(url, 'spotify')
        self.assertTrue(valid)
        
        # Invalid URL (not a playlist)
        url = 'https://open.spotify.com/album/37i9dQZF1DX4sWSpwq3LiO'
        valid, message = validate_playlist_url(url, 'spotify')
        self.assertFalse(valid)
    
    @patch('requests.post')
    def test_process_form_submission(self, mock_post):
        """Test the form submission process."""
        # Mock response for the backend API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'job_id': '12345678-1234-1234-1234-123456789012'
        }
        mock_post.return_value = mock_response
        
        # Test form submission
        response = self.client.post('/process', data={
            'source_platform': 'spotify',
            'destination_platform': 'apple_music',
            'playlist_url': 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'
        }, follow_redirects=True)
        
        # This would redirect to the OAuth page in a real scenario
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()