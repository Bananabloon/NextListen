import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI
from rest_framework.test import APIClient
from users.models import Media, User
from django.utils import timezone

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        spotify_user_id="testuser",
        password="testpass",
        spotify_access_token="dummy_access_token",
        spotify_refresh_token="dummy_refresh_token",
        curveball_enjoyment=5,
    )

@pytest.fixture
def media_instance(db):
    return Media.objects.create(
        spotify_uri="spotify:track:456",
        title="Teardrop",
        artist_name="Massive Attack",
        genre="Trip-hop",
        saved_at=timezone.now()
    )

@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response for playlist generation"""
    return [
        {"title": "Teardrop", "artist": "Massive Attack"},
        {"title": "Angel", "artist": "Massive Attack"},
    ]

@pytest.fixture
def mock_spotify_api():
    with patch('spotifyData.services.spotifyClient.SpotifyAPI') as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        mock_instance.get_user_profile.return_value = {
            "id": "testuser",
            "display_name": "Test User"
        }
        mock_instance.like_track.return_value = None
        mock_instance.search.return_value = {
            "tracks": {
                "items": [{
                    "id": "track123",
                    "name": "Test Track",
                    "artists": [{"name": "Test Artist"}]
                }]
            }
        }
        mock_instance.get_several_tracks.return_value = [{
            "id": "track123",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}]
        }]
        
        yield mock_instance

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
        
        api = SpotifyAPI("token123")  
        result = api._request("GET", "/test")
        
        self.assertEqual(result.status_code, 401)
        mock_request.assert_called_once()

    @patch('requests.request')
    def test_request_401_with_refresh_token(self, mock_request):
        """Test _request with 401 error and successful token refresh."""
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

    @patch('requests.request')
    def test_request_with_kwargs(self, mock_request):
        """Test _request method with additional kwargs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        params = {"limit": 10}
        json_data = {"test": "data"}
        
        result = self.spotify_api._request("POST", "/test", params=params, json=json_data)
        
        mock_request.assert_called_once_with(
            "POST",
            f"{self.spotify_api.BASE_URL}/test",
            headers=self.spotify_api.headers,
            params=params,
            json=json_data
        )
        self.assertEqual(result, mock_response)

    @patch.object(SpotifyAPI, '_request')
    def test_get_method(self, mock_request):
        """Test _get method."""
        mock_response = Mock()
        mock_request.return_value = mock_response
        
        result = self.spotify_api._get("/test", params={"limit": 10})
        
        mock_request.assert_called_once_with("GET", "/test", params={"limit": 10})
        self.assertEqual(result, mock_response)

    @patch.object(SpotifyAPI, '_request')
    def test_post_method(self, mock_request):
        """Test _post method."""
        mock_response = Mock()
        mock_request.return_value = mock_response
        
        result = self.spotify_api._post("/test", json={"data": "test"})
        
        mock_request.assert_called_once_with("POST", "/test", json={"data": "test"})
        self.assertEqual(result, mock_response)

    @patch.object(SpotifyAPI, '_request')
    def test_put_method(self, mock_request):
        """Test _put method."""
        mock_response = Mock()
        mock_request.return_value = mock_response
        
        result = self.spotify_api._put("/test", json={"data": "test"})
        
        mock_request.assert_called_once_with("PUT", "/test", json={"data": "test"})
        self.assertEqual(result, mock_response)

    @patch.object(SpotifyAPI, '_request')
    def test_delete_method(self, mock_request):
        """Test _delete method."""
        mock_response = Mock()
        mock_request.return_value = mock_response
        
        result = self.spotify_api._delete("/test", json={"data": "test"})
        
        mock_request.assert_called_once_with("DELETE", "/test", json={"data": "test"})
        self.assertEqual(result, mock_response)

    @patch('requests.post')
    def test_refresh_access_token_failure_handling(self, mock_post):
        """Test that refresh token failures are handled gracefully in tests"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid refresh token"
        mock_post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.spotify_api._refresh_access_token()
        
        self.assertIn("Failed to refresh access token", str(context.exception))

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
    def test_refresh_access_token_success_without_user(self, mock_post):
        """Test successful token refresh without user."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new_token"}
        mock_post.return_value = mock_response

        api = SpotifyAPI("token123", "refresh123") 
        
        with patch.object(settings, 'SPOTIFY_CLIENT_ID', 'client_id'), \
             patch.object(settings, 'SPOTIFY_CLIENT_SECRET', 'client_secret'):
            
            api._refresh_access_token()
            
            self.assertEqual(api.access_token, "new_token")

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

