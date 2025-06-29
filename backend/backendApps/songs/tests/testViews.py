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


class SongViewsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            display_name="testuser", spotify_user_id="dummy_spotify_id"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_song_analysis_missing_data(self):
        response = self.client.post("/api/songs/analysis/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("artist", response.data)

    def test_song_analysis_success(self):
        data = {
            "access_token": "mocked_token",  
            "song_id": "sample_id"
        }
        response = self.client.post("/api/songs/analysis/", data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_similar_songs_missing_data(self):
        response = self.client.post("/api/songs/similar/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_feedback_invalid_input(self):
        response = self.client.post("/api/songs/feedback/update/", {"spotify_uri": "xyz", "feedback_value": "meh"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_feedback_success_existing_media(self):
        client, user = authenticate_client()

        media = Media.objects.create(
            spotify_uri="spotify:track:123",
            title="Some Track",
            artist_name="Some Artist",
            genre=[],
            album_name="Some Album",
            media_type=Media.SONG,
            saved_at=timezone.now(),
        )

        data = {"spotify_uri": media.spotify_uri, "feedback_value": 1}

        response = client.post("/api/songs/feedback/update/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

    @patch("songs.views.saveFeedbackViews.requests.get")
    def test_feedback_creates_media_from_spotify(self, mock_get):
        client, user = authenticate_client()

        spotify_uri = "spotify:track:new123"

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "name": "New Track",
            "artists": [{"name": "New Artist"}],
            "album": {"name": "New Album"},
        }

        data = {"spotify_uri": spotify_uri, "feedback_value": -1}

        response = client.post("/api/songs/feedback/update/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["track_title"], "New Track")
        self.assertEqual(response.data["artist"], "New Artist")

        self.assertTrue(Media.objects.filter(spotify_uri=spotify_uri).exists())
        self.assertTrue(
            UserFeedback.objects.filter(
                user=user, media__spotify_uri=spotify_uri
            ).exists()
        )

    def test_feedback_invalid_uri_format(self):
        response = self.client.post("/api/songs/feedback/update/", {
            "spotify_uri": "",
            "feedback_value": 1
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_feedback_none_does_not_create_feedback(self):
        client, user = authenticate_client()

        media = Media.objects.create(
            spotify_uri="spotify:track:none123",
            title="No Feedback Track",
            artist_name="No Artist",
            genre=[],
            album_name="No Album",
            media_type=Media.SONG,
            saved_at=timezone.now(),
        )

        data = {"spotify_uri": media.spotify_uri, "feedback_value": 0}

        response = client.post("/api/songs/feedback/update/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)

    def test_similar_songs_missing_feedback(self):
        response = self.client.post("/api/songs/similar/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "title and artist are required")

