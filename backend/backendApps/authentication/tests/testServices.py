import pytest
from unittest.mock import Mock, patch
from django.test import TestCase, override_settings
from django.conf import settings
from rest_framework.response import Response
import requests

from authentication.services.spotify_service import SpotifyService
from authentication.services.spotify_auth_service import SpotifyAuthService


class TestSpotifyService(TestCase):
    """Test cases for SpotifyService class"""

    @override_settings(
        SPOTIFY_REDIRECT_URI='http://localhost:8000/auth/callback',
        SPOTIFY_CLIENT_ID='test_client_id',
        SPOTIFY_CLIENT_SECRET='test_client_secret'
    )
    @patch('authentication.services.spotify_service.requests.post')
    def test_exchange_code_for_spotify_token_success(self, mock_post):
        """Test successful token exchange"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        code = 'test_authorization_code'
        
        # Act
        result = SpotifyService.exchange_code_for_spotify_token(code)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['access_token'], 'test_access_token')
        self.assertEqual(result['refresh_token'], 'test_refresh_token')
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                "client_id": settings.SPOTIFY_CLIENT_ID,
                "client_secret": settings.SPOTIFY_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    @patch('authentication.services.spotify_service.requests.post')
    @patch('authentication.services.spotify_service.logger')
    def test_exchange_code_for_spotify_token_failure(self, mock_logger, mock_post):
        """Test failed token exchange"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request - Invalid code'
        mock_post.return_value = mock_response
        
        code = 'invalid_code'
        
        # Act
        result = SpotifyService.exchange_code_for_spotify_token(code)
        
        # Assert
        self.assertIsNone(result)
        mock_logger.error.assert_called_once_with(
            "Failed token exchange: %s", 
            'Bad Request - Invalid code'
        )

    @patch('authentication.services.spotify_service.requests.post')
    def test_exchange_code_for_spotify_token_network_error(self, mock_post):
        """Test token exchange with network error"""
        # Arrange
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        code = 'test_code'
        
        # Act & Assert
        with self.assertRaises(requests.exceptions.RequestException):
            SpotifyService.exchange_code_for_spotify_token(code)

    @patch('authentication.services.spotify_service.requests.get')
    def test_get_user_info_success(self, mock_get):
        """Test successful user info retrieval"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'spotify_user_123',
            'display_name': 'Test User',
            'email': 'test@example.com',
            'images': [{'url': 'https://example.com/avatar.jpg'}]
        }
        mock_get.return_value = mock_response
        
        access_token = 'test_access_token'
        
        # Act
        result = SpotifyService.get_user_info(access_token)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 'spotify_user_123')
        self.assertEqual(result['display_name'], 'Test User')
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

    @patch('authentication.services.spotify_service.requests.get')
    @patch('authentication.services.spotify_service.logger')
    def test_get_user_info_failure(self, mock_logger, mock_get):
        """Test failed user info retrieval"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        access_token = 'invalid_token'
        
        # Act
        result = SpotifyService.get_user_info(access_token)
        
        # Assert
        self.assertIsNone(result)
        mock_logger.error.assert_called_once_with(
            "Failed to fetch user profile from Spotify."
        )

    @patch('authentication.services.spotify_service.requests.get')
    def test_get_user_info_network_error(self, mock_get):
        """Test user info retrieval with network error"""
        # Arrange
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        access_token = 'test_token'
        
        # Act & Assert
        with self.assertRaises(requests.exceptions.RequestException):
            SpotifyService.get_user_info(access_token)

    @patch('authentication.services.spotify_service.requests.get')
    def test_get_user_info_different_status_codes(self, mock_get):
        """Test user info retrieval with various HTTP status codes"""
        test_cases = [
            (403, None),  # Forbidden
            (404, None),  # Not Found
            (500, None),  # Internal Server Error
        ]
        
        for status_code, expected_result in test_cases:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_get.return_value = mock_response
                
                result = SpotifyService.get_user_info('test_token')
                self.assertEqual(result, expected_result)


class TestSpotifyAuthService(TestCase):
    """Test cases for SpotifyAuthService class"""

    @patch('authentication.services.spotify_auth_service.SpotifyService.get_user_info')
    @patch('authentication.services.spotify_auth_service.UserService.create_or_update_user')
    @patch('authentication.services.spotify_auth_service.TokenService.generate_tokens_for_user')
    def test_authenticate_spotify_user_success(self, mock_generate_tokens, 
                                               mock_create_user, mock_get_user_info):
        """Test successful Spotify user authentication"""
        # Arrange
        mock_user_info = {
            'id': 'spotify_123',
            'display_name': 'Test User',
            'email': 'test@example.com'
        }
        mock_user = Mock()
        mock_user.id = 1
        mock_tokens = {
            'access': 'jwt_access_token',
            'refresh': 'jwt_refresh_token'
        }
        
        mock_get_user_info.return_value = mock_user_info
        mock_create_user.return_value = mock_user
        mock_generate_tokens.return_value = mock_tokens
        
        spotify_access_token = 'spotify_access_token'
        spotify_refresh_token = 'spotify_refresh_token'
        
        # Act
        tokens, error_response = SpotifyAuthService.authenticate_spotify_user(
            spotify_access_token, spotify_refresh_token
        )
        
        # Assert
        self.assertIsNotNone(tokens)
        self.assertIsNone(error_response)
        self.assertEqual(tokens, mock_tokens)
        
        # Verify method calls
        mock_get_user_info.assert_called_once_with(spotify_access_token)
        mock_create_user.assert_called_once_with(
            mock_user_info, spotify_access_token, spotify_refresh_token
        )
        mock_generate_tokens.assert_called_once_with(mock_user)

    @patch('authentication.services.spotify_auth_service.SpotifyService.get_user_info')
    def test_authenticate_spotify_user_invalid_token(self, mock_get_user_info):
        """Test authentication with invalid Spotify token"""
        # Arrange
        mock_get_user_info.return_value = None
        
        spotify_access_token = 'invalid_token'
        spotify_refresh_token = 'refresh_token'
        
        # Act
        tokens, error_response = SpotifyAuthService.authenticate_spotify_user(
            spotify_access_token, spotify_refresh_token
        )
        
        # Assert
        self.assertIsNone(tokens)
        self.assertIsNotNone(error_response)
        self.assertIsInstance(error_response, Response)
        self.assertEqual(error_response.status_code, 401)
        self.assertEqual(error_response.data, {"error": "Invalid Spotify token"})

    @patch('authentication.services.spotify_auth_service.SpotifyService.get_user_info')
    @patch('authentication.services.spotify_auth_service.UserService.create_or_update_user')
    @patch('authentication.services.spotify_auth_service.TokenService.generate_tokens_for_user')
    def test_authenticate_spotify_user_user_service_error(self, mock_generate_tokens,
                                                          mock_create_user, mock_get_user_info):
        """Test authentication when UserService fails"""
        # Arrange
        mock_user_info = {'id': 'spotify_123'}
        mock_get_user_info.return_value = mock_user_info
        mock_create_user.side_effect = Exception("Database error")
        
        spotify_access_token = 'valid_token'
        spotify_refresh_token = 'refresh_token'
        
        # Act & Assert
        with self.assertRaises(Exception):
            SpotifyAuthService.authenticate_spotify_user(
                spotify_access_token, spotify_refresh_token
            )

    @patch('authentication.services.spotify_auth_service.SpotifyService.get_user_info')
    @patch('authentication.services.spotify_auth_service.UserService.create_or_update_user')
    @patch('authentication.services.spotify_auth_service.TokenService.generate_tokens_for_user')
    def test_authenticate_spotify_user_token_service_error(self, mock_generate_tokens,
                                                           mock_create_user, mock_get_user_info):
        """Test authentication when TokenService fails"""
        # Arrange
        mock_user_info = {'id': 'spotify_123'}
        mock_user = Mock()
        mock_get_user_info.return_value = mock_user_info
        mock_create_user.return_value = mock_user
        mock_generate_tokens.side_effect = Exception("Token generation error")
        
        spotify_access_token = 'valid_token'
        spotify_refresh_token = 'refresh_token'
        
        # Act & Assert
        with self.assertRaises(Exception):
            SpotifyAuthService.authenticate_spotify_user(
                spotify_access_token, spotify_refresh_token
            )

    @patch('authentication.services.spotify_auth_service.SpotifyService.get_user_info')
    @patch('authentication.services.spotify_auth_service.UserService.create_or_update_user')
    @patch('authentication.services.spotify_auth_service.TokenService.generate_tokens_for_user')
    def test_authenticate_spotify_user_with_none_values(self, mock_generate_tokens,
                                                        mock_create_user, mock_get_user_info):
        """Test authentication with None values for tokens"""
        # Arrange
        mock_user_info = {'id': 'spotify_123'}
        mock_user = Mock()
        mock_tokens = {'access': 'token', 'refresh': 'token'}
        
        mock_get_user_info.return_value = mock_user_info
        mock_create_user.return_value = mock_user
        mock_generate_tokens.return_value = mock_tokens
        
        # Act
        tokens, error_response = SpotifyAuthService.authenticate_spotify_user(
            None, None
        )
        
        # Assert - Should still call the methods with None values
        mock_get_user_info.assert_called_once_with(None)

class TestSpotifyServicePytest:
    """Pytest-style tests for SpotifyService"""

    @pytest.fixture
    def spotify_service(self):
        return SpotifyService()

    @pytest.fixture
    def mock_requests_post(self):
        with patch('authentication.services.spotify_service.requests.post') as mock:
            yield mock

    @pytest.fixture
    def mock_requests_get(self):
        with patch('authentication.services.spotify_service.requests.get') as mock:
            yield mock

    def test_exchange_code_success_pytest(self, mock_requests_post):
        """Pytest version of token exchange test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'test_token'}
        mock_requests_post.return_value = mock_response
        
        result = SpotifyService.exchange_code_for_spotify_token('test_code')
        
        assert result is not None
        assert result['access_token'] == 'test_token'

    def test_get_user_info_success_pytest(self, mock_requests_get):
        """Pytest version of user info test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'user123'}
        mock_requests_get.return_value = mock_response
        
        result = SpotifyService.get_user_info('access_token')
        
        assert result is not None
        assert result['id'] == 'user123'


if __name__ == '__main__':
    # For running with pytest
    pytest.main([__file__])