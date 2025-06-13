import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI

User = get_user_model()

class SpotifyLikedTracksTest(TestCase):  
    def setUp(self):
        self.access_token = "test_access_token"
        self.refresh_token = "test_refresh_token"
        self.user = Mock()
        self.spotify_api = SpotifyAPI(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            user=self.user)
    
    @patch.object(SpotifyAPI, '_get')
    def test_get_liked_tracks_success(self, mock_get):
        """Test successful get_liked_tracks method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"track": {"id": "track1"}}]}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_liked_tracks(limit=10, offset=5)
        
        mock_get.assert_called_once_with("/me/tracks?limit=10&offset=5")
        self.assertEqual(result, {"items": [{"track": {"id": "track1"}}]})

    @patch.object(SpotifyAPI, '_get')
    def test_get_liked_tracks_default_params(self, mock_get):
        """Test get_liked_tracks method with default parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_liked_tracks()
        
        mock_get.assert_called_once_with("/me/tracks?limit=20&offset=0")
        self.assertEqual(result, {"items": []})

    @patch.object(SpotifyAPI, '_get')
    def test_get_liked_tracks_error(self, mock_get):
        """Test get_liked_tracks method with error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        result = self.spotify_api.get_liked_tracks()
        
        expected_result = {
            "error": "Spotify API error: 400",
            "response": "Bad Request",
        }
        self.assertEqual(result, expected_result)

    @patch.object(SpotifyAPI, '_put')
    def test_like_track(self, mock_put):
        """Test like_track method."""
        mock_response = Mock()
        mock_put.return_value = mock_response

        self.spotify_api.like_track("track123")
        
        expected_data = {"ids": ["track123"]}
        mock_put.assert_called_once_with("/me/tracks", json=expected_data)

    @patch.object(SpotifyAPI, '_delete')
    def test_remove_liked_track(self, mock_delete):
        """Test remove_liked_track method."""
        mock_response = Mock()
        mock_delete.return_value = mock_response

        self.spotify_api.remove_liked_track("track123")
        
        expected_data = {"ids": ["track123"]}
        mock_delete.assert_called_once_with("/me/tracks", json=expected_data)
