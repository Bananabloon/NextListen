import pytest
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
