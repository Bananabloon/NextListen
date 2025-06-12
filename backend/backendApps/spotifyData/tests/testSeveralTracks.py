import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI

User = get_user_model()

class SpotifySeveralTracksTest(TestCase):
    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_success(self, mock_get):
        """Test successful get_several_tracks method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tracks": [{"id": "track1"}, {"id": "track2"}]}
        mock_get.return_value = mock_response

        track_ids = ["track1", "track2", "track3"]
        result = self.spotify_api.get_several_tracks(track_ids)

        mock_get.assert_called_once_with("/tracks", params={"ids": "track1,track2,track3"})
        self.assertEqual(result, [{"id": "track1"}, {"id": "track2"}])

    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_with_mocked_response(self, mock_get):
        """Test get_several_tracks with properly mocked response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tracks": [
                {"id": "track1", "name": "Test Track 1"},
                {"id": "track2", "name": "Test Track 2"}
            ]
        }
        mock_get.return_value = mock_response

        track_ids = ["track1", "track2"]
        result = self.spotify_api.get_several_tracks(track_ids)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "track1")
        self.assertEqual(result[1]["id"], "track2")

    @patch('time.sleep')
    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_rate_limited_then_success(self, mock_get, mock_sleep):
        """Test get_several_tracks with rate limiting then success."""
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "2"}
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"tracks": [{"id": "track1"}]}
        
        mock_get.side_effect = [mock_response_429, mock_response_200]
    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_error(self, mock_get):
        """Test get_several_tracks with non-recoverable error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        track_ids = ["track1"]
        
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_several_tracks(track_ids)
        
        self.assertIn("Failed to get tracks info", str(context.exception))
        self.assertIn("500", str(context.exception))

    @patch('time.sleep')
    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_rate_limited_twice(self, mock_get, mock_sleep):
        """Test get_several_tracks with rate limiting twice."""
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "1"}
        
        mock_get.return_value = mock_response_429

        track_ids = ["track1"]
        
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_several_tracks(track_ids)
        
        self.assertIn("Rate limited again or failed after retry", str(context.exception))
        self.assertEqual(mock_get.call_count, 2)
        track_ids = ["track1"]
        result = self.spotify_api.get_several_tracks(track_ids)

        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once_with(2)
        self.assertEqual(result, [{"id": "track1"}])

    @patch('time.sleep')
    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_rate_limited_no_retry_after_header(self, mock_get, mock_sleep):
        """Test get_several_tracks with rate limiting and no Retry-After header."""
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {}
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"tracks": []}
        
        mock_get.side_effect = [mock_response_429, mock_response_200]

        track_ids = ["track1"]
        result = self.spotify_api.get_several_tracks(track_ids)

        mock_sleep.assert_called_once_with(1)  
        self.assertEqual(result, [])

    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_401_with_refresh(self, mock_get):
        """Test get_several_tracks with 401 error and token refresh."""
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"tracks": []}
        
        mock_get.side_effect = [mock_response_401, mock_response_200]

        with patch.object(self.spotify_api, '_refresh_access_token') as mock_refresh:
            track_ids = ["track1"]
            result = self.spotify_api.get_several_tracks(track_ids)

            mock_refresh.assert_called_once()
            self.assertEqual(result, [])

    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_error(self, mock_get):
        """Test get_several_tracks with non-recoverable error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        track_ids = ["track1"]
        
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_several_tracks(track_ids)
        
        self.assertIn("Failed to get tracks info", str(context.exception))
        self.assertIn("500", str(context.exception))

    @patch('time.sleep')
    @patch.object(SpotifyAPI, '_get')
    def test_get_several_tracks_rate_limited_twice(self, mock_get, mock_sleep):
        """Test get_several_tracks with rate limiting twice."""
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "1"}
        
        mock_get.return_value = mock_response_429

        track_ids = ["track1"]
        
        with self.assertRaises(Exception) as context:
            self.spotify_api.get_several_tracks(track_ids)
        
        self.assertIn("Rate limited again or failed after retry", str(context.exception))
        self.assertEqual(mock_get.call_count, 2)