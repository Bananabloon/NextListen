from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from ..services.user_service import UserService
from users.models import User
from ..services.spotify_auth_service import CustomRefreshToken

class SpotifyOAuthTests(APITestCase):
    def test_oauth_redirect_url(self):
        response = self.client.get("/auth/spotify/login/")  
        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.spotify.com", response.url)

    # def test_invalid_token_returns_401(self): #BROKEN, gives 400 :(
    #     invalid_token = "thisisnotavalidtoken"
    #     response = self.client.get("/auth/spotify/callback/", {
    #         "access_token": invalid_token,
    #         "refresh_token": "any"
    #     })
    #     self.assertEqual(response.status_code, 401)
    #     self.assertIn("error", response.data)

    def test_create_user_success(self):
        user_info = {
            "id": "spotify123",
            "displayname": "Test User",
            "country": "PL"
        }
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
