import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI

User = get_user_model()

class SpotifyQueueTest(TestCase):
        
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.access_token = "test_access_token"
        self.refresh_token = "test_refresh_token"
        self.user = Mock()
        self.spotify_api = SpotifyAPI(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            user=self.user
        )
    
    @patch('requests.post')
    def test_add_to_queue_success(self, mock_post):
        """Test successful add_to_queue method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        success, error = self.spotify_api.add_to_queue("spotify:track:123")
        
        self.assertTrue(success)
        self.assertIsNone(error)
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_add_to_queue_success_204(self, mock_post):
        """Test add_to_queue method with 204 status code."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        success, error = self.spotify_api.add_to_queue("spotify:track:123")
        
        self.assertTrue(success)
        self.assertIsNone(error)

    @patch('requests.post')
    def test_add_to_queue_error_with_json(self, mock_post):
        """Test add_to_queue method with error response containing JSON."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"status": 400, "message": "Bad request"}}
        mock_post.return_value = mock_response

        success, error = self.spotify_api.add_to_queue("spotify:track:123")
        
        self.assertFalse(success)
        self.assertEqual(error, {"error": {"status": 400, "message": "Bad request"}})

    @patch('requests.post')
    def test_add_to_queue_error_without_json(self, mock_post):
        """Test add_to_queue method with error response that can't be parsed as JSON."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_post.return_value = mock_response

        success, error = self.spotify_api.add_to_queue("spotify:track:123")
        
        self.assertFalse(success)
        self.assertEqual(error, {"error": "Unexpected response", "status": 500})
