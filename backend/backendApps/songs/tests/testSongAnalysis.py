from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class SongAnalysisViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(spotify_user_id="analyzer", password="testpass")
        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")

    def test_missing_title_artist_returns_400(self):
        response = self.client.post("/api/songs/analysis/", {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.data)
        self.assertIn("artist", response.data)

    @patch("songs.views.analysisViews.ask_openai")
    def test_analysis_success(self, mock_ai):
        mock_ai.return_value = {
            "tempo": "medium",
            "mood": "chill",
            "style": "lofi",
            "description": "Ambient chill track with soft beats."
        }

        response = self.client.post("/api/songs/analysis/", {
            "title": "Night Vibes",
            "artist": "LoFi Beats"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("analysis", response.data)
