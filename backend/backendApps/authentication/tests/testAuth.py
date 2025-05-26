from rest_framework.test import APITestCase
from rest_framework import status


class SpotifyOAuthTests(APITestCase):
    def test_login_without_token(self):
        response = self.client.post("/auth/spotify/token-login/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "access_token required")

    def test_oauth_redirect_url(self):
        response = self.client.get("/auth/spotify/login/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.spotify.com", response.url)
