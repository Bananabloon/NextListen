import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI

User = get_user_model()

class SpotifyPlaybackViewsTest(TestCase):
        
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
    
    @patch.object(SpotifyAPI, '_put')
    def test_start_playback_success(self, mock_put):
        """Test successful start_playback method."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_put.return_value = mock_response

        success, response_text = self.spotify_api.start_playback("device123", "spotify:track:123")
        
        expected_data = {"uris": ["spotify:track:123"], "offset": {"position": 0}}
        expected_params = {"device_id": "device123"}
        
        mock_put.assert_called_once_with("/me/player/play", params=expected_params, json=expected_data)
        self.assertTrue(success)
        self.assertEqual(response_text, "")

    @patch.object(SpotifyAPI, '_put')
    def test_start_playback_error(self, mock_put):
        """Test start_playback method with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_put.return_value = mock_response

        success, response_text = self.spotify_api.start_playback("device123", "spotify:track:123")
        
        self.assertFalse(success)
        self.assertEqual(response_text, "Bad Request")

    @patch.object(SpotifyAPI, '_put')
    def test_transfer_playback_success(self, mock_put):
        """Test successful transfer_playback method."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_put.return_value = mock_response

        success, response_text = self.spotify_api.transfer_playback("device123", play=False)
        
        expected_data = {"device_ids": ["device123"], "play": False}
        mock_put.assert_called_once_with("/me/player", json=expected_data)
        self.assertTrue(success)
        self.assertEqual(response_text, "")

    @patch.object(SpotifyAPI, '_put')
    def test_transfer_playback_default_play(self, mock_put):
        """Test transfer_playback method with default play parameter."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_put.return_value = mock_response

        success, response_text = self.spotify_api.transfer_playback("device123")
        
        expected_data = {"device_ids": ["device123"], "play": True}
        mock_put.assert_called_once_with("/me/player", json=expected_data)
        self.assertTrue(success)

    @patch.object(SpotifyAPI, '_put')
    def test_transfer_playback_error(self, mock_put):
        """Test transfer_playback method with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_put.return_value = mock_response

        success, response_text = self.spotify_api.transfer_playback("device123")
        
        self.assertFalse(success)
        self.assertEqual(response_text, "Bad Request")

    @patch.object(SpotifyAPI, '_put')
    def test_pause_playback_success(self, mock_put):
        """Test successful pause_playback method."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_put.return_value = mock_response

        success, response_text = self.spotify_api.pause_playback()
        
        mock_put.assert_called_once_with("/me/player/pause")
        self.assertTrue(success)
        self.assertEqual(response_text, "")

    @patch.object(SpotifyAPI, '_put')
    def test_pause_playback_error(self, mock_put):
        """Test pause_playback method with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_put.return_value = mock_response

        success, response_text = self.spotify_api.pause_playback()
        
        self.assertFalse(success)
        self.assertEqual(response_text, "Bad Request")

    def test_get_access_token_success(self):
        """Test successful get_access_token method."""
        result = self.spotify_api.get_access_token()
        self.assertEqual(result, self.access_token)

    def test_get_access_token_no_token(self):
        """Test get_access_token method with no access token."""
        api = SpotifyAPI(None)
        
        with self.assertRaises(Exception) as context:
            api.get_access_token()
        
        self.assertIn("Brak access tokena", str(context.exception))