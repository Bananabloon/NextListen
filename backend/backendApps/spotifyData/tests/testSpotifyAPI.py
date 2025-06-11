from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI

User = get_user_model()


class SpotifyAPITest(TestCase):
        
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

    def test_init(self):
        """Test SpotifyAPI initialization."""
        api = SpotifyAPI("token123")
        self.assertEqual(api.access_token, "token123")
        self.assertIsNone(api.refresh_token)
        self.assertIsNone(api.user)
        self.assertEqual(api.headers, {"Authorization": "Bearer token123"})

    def test_init_with_all_params(self):
        """Test SpotifyAPI initialization with all parameters."""
        user = Mock()
        api = SpotifyAPI("token123", "refresh123", user)
        self.assertEqual(api.access_token, "token123")
        self.assertEqual(api.refresh_token, "refresh123")
        self.assertEqual(api.user, user)

    def test_update_headers(self):
        """Test _update_headers method."""
        self.spotify_api.access_token = "new_token"
        self.spotify_api._update_headers()
        self.assertEqual(self.spotify_api.headers, {"Authorization": "Bearer new_token"})

    @patch('requests.request')
    def test_request_success(self, mock_request):
        """Test successful _request method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.spotify_api._request("GET", "/test")
        
        mock_request.assert_called_once_with(
            "GET", 
            f"{self.spotify_api.BASE_URL}/test", 
            headers=self.spotify_api.headers
        )
        self.assertEqual(result, mock_response)

    @patch('requests.request')
    def test_request_401_without_refresh_token(self, mock_request):
        """Test _request with 401 error and no refresh token."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        api = SpotifyAPI("token123")  # No refresh token
        result = api._request("GET", "/test")
        
        self.assertEqual(result.status_code, 401)
        mock_request.assert_called_once()

    @patch('requests.request')
    def test_request_401_with_refresh_token(self, mock_request):
        """Test _request with 401 error and successful token refresh."""
        # First call returns 401, second call returns 200
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_request.side_effect = [mock_response_401, mock_response_200]

        with patch.object(self.spotify_api, '_refresh_access_token') as mock_refresh:
            result = self.spotify_api._request("GET", "/test")
            
            mock_refresh.assert_called_once()
            self.assertEqual(result, mock_response_200)
            self.assertEqual(mock_request.call_count, 2)

    @patch('requests.post')
    def test_refresh_access_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new_token"}
        mock_post.return_value = mock_response

        with patch.object(settings, 'SPOTIFY_CLIENT_ID', 'client_id'), \
             patch.object(settings, 'SPOTIFY_CLIENT_SECRET', 'client_secret'):
            
            self.spotify_api._refresh_access_token()
            
            self.assertEqual(self.spotify_api.access_token, "new_token")
            self.user.save.assert_called_once()
            mock_post.assert_called_once()

    @patch('requests.post')
    def test_refresh_access_token_failure(self, mock_post):
        """Test failed token refresh."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.spotify_api._refresh_access_token()
        
        self.assertIn("Failed to refresh access token", str(context.exception))

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
    def test_get_top_artists(self, mock_get):
        """Test get_top_artists method."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        result = self.spotify_api.get_top_artists(limit=5)
        
        mock_get.assert_called_once_with("/me/top/artists?limit=5")
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
