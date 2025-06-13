import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI

User = get_user_model()

class SpotifyGetTests(TestCase):  
    def setUp(self):
        self.access_token = "test_access_token"
        self.refresh_token = "test_refresh_token"
        self.user = Mock()
        self.spotify_api = SpotifyAPI(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            user=self.user)

    @patch.object(SpotifyAPI, '_get')
    def test_get_user_profile(self, mock_get):
        """Test get_user_profile method."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "user123", "display_name": "Test User"}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_user_profile()
        
        mock_get.assert_called_once_with("/me")
        self.assertEqual(result, {"id": "user123", "display_name": "Test User"})

    @patch.object(SpotifyAPI, '_get')
    def test_get_top_tracks(self, mock_get):
        """Test get_top_tracks method."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_top_tracks(limit=10)
        
        mock_get.assert_called_once_with("/me/top/tracks?limit=10")
        self.assertEqual(result, {"items": []})

    @patch.object(SpotifyAPI, '_get')
    def test_get_top_tracks_default_limit(self, mock_get):
        """Test get_top_tracks method with default limit."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_top_tracks()
        
        mock_get.assert_called_once_with("/me/top/tracks?limit=50")
        self.assertEqual(result, {"items": []})

    @patch.object(SpotifyAPI, '_get')
    def test_get_top_artists(self, mock_get):
        """Test get_top_artists method."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_top_artists(limit=5)
        
        mock_get.assert_called_once_with("/me/top/artists?limit=5")
        self.assertEqual(result, {"items": []})

    @patch.object(SpotifyAPI, '_get')
    def test_get_top_artists_default_limit(self, mock_get):
        """Test get_top_artists method with default limit."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_top_artists()
        
        mock_get.assert_called_once_with("/me/top/artists?limit=20")
        self.assertEqual(result, {"items": []})

    @patch.object(SpotifyAPI, '_get')
    def test_get_artist(self, mock_get):
        """Test get_artist method."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "artist123", "name": "Test Artist"}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_artist("artist123")
        
        mock_get.assert_called_once_with("/artists/artist123")
        self.assertEqual(result, {"id": "artist123", "name": "Test Artist"})

    @patch.object(SpotifyAPI, '_get')
    def test_get_current_playing(self, mock_get):
        """Test get_current_playing method."""
        mock_response = Mock()
        mock_response.json.return_value = {"is_playing": True}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_current_playing()
        
        mock_get.assert_called_once_with("/me/player/currently-playing")
        self.assertEqual(result, {"is_playing": True})

    @patch.object(SpotifyAPI, '_get')
    def test_get_track(self, mock_get):
        """Test get_track method."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "track123", "name": "Test Track"}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_track("track123")
        
        mock_get.assert_called_once_with("/tracks/track123")
        self.assertEqual(result, {"id": "track123", "name": "Test Track"})

    @patch.object(SpotifyAPI, '_get')
    def test_search_success(self, mock_get):
        """Test successful search method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tracks": {"items": []}}
        mock_get.return_value = mock_response

        result = self.spotify_api.search("Massive Attack")

        
        mock_get.assert_called_once_with("/search", params={"q": "Massive Attack", "type": "track", "limit": 1})
        self.assertEqual(result, {"tracks": {"items": []}})

    @patch.object(SpotifyAPI, '_get')
    def test_search_with_custom_params(self, mock_get):
        """Test search method with custom parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"artists": {"items": []}}
        mock_get.return_value = mock_response

        result = self.spotify_api.search("Radiohead", type="artist", limit=5)
        
        mock_get.assert_called_once_with("/search", params={"q": "Radiohead", "type": "artist", "limit": 5})
        self.assertEqual(result, {"artists": {"items": []}})

    @patch.object(SpotifyAPI, '_get')
    def test_search_failure(self, mock_get):
        """Test search method with API error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        result = self.spotify_api.search("test query")
        
        expected_result = {
            "error": "Spotify API error: 400",
            "response": "Bad Request",
        }
        self.assertEqual(result, expected_result)
