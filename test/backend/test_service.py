"""
Test suite for the BeatBridge backend service.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from service import app
from models.track import Track
from models.playlist import Playlist


class BeatBridgeBackendTestCase(unittest.TestCase):
    """Test case for the BeatBridge backend service."""
    
    def setUp(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')
        self.assertIn('timestamp', data)
    
    @patch('service.process_conversion')
    def test_convert_playlist(self, mock_process):
        """Test the playlist conversion endpoint."""
        # Mock the process_conversion function
        mock_process.return_value = None
        
        # Test request
        request_data = {
            'source_platform': 'spotify',
            'destination_platform': 'apple_music',
            'playlist_id': '37i9dQZF1DX4sWSpwq3LiO'
        }
        
        response = self.client.post(
            '/api/convert',
            json=request_data,
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('job_id', data)
        
        # Verify process_conversion was called (in a background thread)
        self.assertTrue(mock_process.called)
    
    def test_convert_playlist_missing_field(self):
        """Test the playlist conversion endpoint with missing field."""
        # Test request with missing field
        request_data = {
            'source_platform': 'spotify',
            'playlist_id': '37i9dQZF1DX4sWSpwq3LiO'
            # Missing destination_platform
        }
        
        response = self.client.post(
            '/api/convert',
            json=request_data,
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('destination_platform', data['message'])
    
    def test_get_job_status_not_found(self):
        """Test the job status endpoint with non-existent job ID."""
        response = self.client.get('/api/status/non_existent_job_id')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('not found', data['message'])
    
    def test_track_model(self):
        """Test the Track model."""
        # Create a track
        track = Track(
            name='Test Track',
            artist='Test Artist',
            album='Test Album',
            duration_ms=120000,
            isrc='USRC12345678',
            uri={'spotify': 'spotify:track:1234567890'},
            platform_ids={'spotify': '1234567890'}
        )
        
        # Test string representation
        self.assertEqual(str(track), 'Test Track by Test Artist')
        
        # Test to_dict method
        track_dict = track.to_dict()
        self.assertEqual(track_dict['name'], 'Test Track')
        self.assertEqual(track_dict['artist'], 'Test Artist')
        self.assertEqual(track_dict['album'], 'Test Album')
        self.assertEqual(track_dict['duration_ms'], 120000)
        self.assertEqual(track_dict['isrc'], 'USRC12345678')
        self.assertEqual(track_dict['uri']['spotify'], 'spotify:track:1234567890')
        self.assertEqual(track_dict['platform_ids']['spotify'], '1234567890')
        
        # Test from_dict method
        new_track = Track.from_dict(track_dict)
        self.assertEqual(new_track.name, 'Test Track')
        self.assertEqual(new_track.artist, 'Test Artist')
        self.assertEqual(new_track.album, 'Test Album')
        self.assertEqual(new_track.duration_ms, 120000)
        self.assertEqual(new_track.isrc, 'USRC12345678')
        self.assertEqual(new_track.uri['spotify'], 'spotify:track:1234567890')
        self.assertEqual(new_track.platform_ids['spotify'], '1234567890')
    
    def test_playlist_model(self):
        """Test the Playlist model."""
        # Create a playlist
        playlist = Playlist(
            id='playlist123',
            name='Test Playlist',
            description='Test Description',
            owner='Test Owner',
            platform='spotify',
            url='https://open.spotify.com/playlist/playlist123'
        )
        
        # Add tracks
        playlist.add_track(Track(name='Track 1', artist='Artist 1'))
        playlist.add_track(Track(name='Track 2', artist='Artist 2'))
        
        # Test string representation
        self.assertEqual(str(playlist), 'Test Playlist (2 tracks) on spotify')
        
        # Test to_dict method
        playlist_dict = playlist.to_dict()
        self.assertEqual(playlist_dict['id'], 'playlist123')
        self.assertEqual(playlist_dict['name'], 'Test Playlist')
        self.assertEqual(playlist_dict['description'], 'Test Description')
        self.assertEqual(playlist_dict['owner'], 'Test Owner')
        self.assertEqual(playlist_dict['platform'], 'spotify')
        self.assertEqual(playlist_dict['url'], 'https://open.spotify.com/playlist/playlist123')
        self.assertEqual(playlist_dict['track_count'], 2)
        
        # Test track management
        self.assertEqual(playlist.get_track_count(), 2)


if __name__ == '__main__':
    unittest.main()