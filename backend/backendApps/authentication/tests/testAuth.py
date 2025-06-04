from rest_framework.test import APITestCase
from ..services.user_service import UserService
from users.models import User, Media, UserFeedback
from ..services.spotify_auth_service import CustomRefreshToken
from unittest.mock import patch

class SpotifyOAuthTests(APITestCase):
    def test_login_without_token(self):
        response = self.client.post("/auth/spotify/token-login/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "access_token required")

    def test_oauth_redirect_url(self):
        response = self.client.get("/api/auth/spotify/login/")  
        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.spotify.com", response.url)

    @patch("authentication.services.spotify_service.SpotifyService.exchange_code_for_token")
    def test_invalid_code_callback_returns_400(self, mock_exchange_code):
        mock_exchange_code.return_value = None
        response = self.client.get("/api/auth/spotify/callback/?code=invalidcode")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_create_user_success(self):
        user_info = {"id": "spotify123", "displayname": "Test User", "country": "PL"}
        user = UserService.create_or_update_user(user_info, access_token="abc123")

        self.assertEqual(user.spotify_user_id, "spotify123")
        self.assertEqual(user.display_name, "Test User")
        self.assertEqual(user.market, "PL")

    def test_jwt_contains_user_data(self):
        user = User.objects.create(display_name="JWT Tester", spotify_user_id="jwt123")
        token = CustomRefreshToken.for_user(user)

        self.assertEqual(token["spotify_user_id"], "jwt123")
        self.assertEqual(token["display_name"], "JWT Tester")
        self.assertEqual(token["id"], user.id)

class DeleteAccountTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            spotify_user_id="spotify123",
            display_name="To Delete"
        )
        self.token = CustomRefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.media = Media.objects.create(
            spotify_uri="spotify:track:123",
            title="some media",
            artist_name="Test Artist",
            genre=["pop"],
            album_name="Test Album",
            media_type="song",
            saved_at="2024-01-01T00:00:00Z",
        )

        UserFeedback.objects.create(
            user=self.user,
            media=self.media,
            is_liked=True,
            source="test",
            feedback_at="2024-01-01"
        )

    def test_delete_account_removes_user_and_data(self):
        response = self.client.delete("/api/auth/delete_account/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
        self.assertEqual(UserFeedback.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Media.objects.filter(title="some media").count(), 0)

    def test_unauthenticated_delete_returns_401(self):
        self.client.credentials()
        response = self.client.delete("/api/auth/delete_account/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
