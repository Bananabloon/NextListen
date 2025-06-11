from unittest.mock import patch
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import UserFeedback, User, Media
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


def authenticate_client():
    user = User.objects.create_user(spotify_user_id="testuser", password="testpass")
    token = AccessToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")
    return client, user


class SimilarSongsViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(spotify_user_id="similar_user", password="pass")
        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")

    def test_missing_data_returns_400(self):
        response = self.client.post("/api/songs/similar/", {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("title and artist are required", response.data["error"])

    @patch("songs.views.similarSongViews.ask_openai")
    def test_similar_songs_success(self, mock_ai):
        mock_ai.return_value = [
            {"title": "Track A", "artist": "Artist A", "reason": "similar mood"},
            {"title": "Track B", "artist": "Artist B", "reason": "similar style"},
        ]

        response = self.client.post("/api/songs/similar/", {
            "title": "Test Song",
            "artist": "Test Artist"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 2)
