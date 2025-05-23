from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import UserFeedback, User, Media
from django.utils import timezone
from datetime import date
User = get_user_model()

class SongViewsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(display_name="testuser", spotify_user_id="dummy_spotify_id")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_song_analysis_missing_data(self):
        response = self.client.post("/songs/analysis/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_song_analysis_success(self):
        data = {
            "access_token": "mocked_token",  
            "song_id": "sample_id"
        }
        response = self.client.post("/songs/analysis/", data)
        # Zewętrzne API - mocking tylko
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_similar_songs_missing_data(self):
        response = self.client.post("/songs/similar/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_feedback_invalid_input(self):
        response = self.client.post("/songs/feedback/", {"song_id": 999, "feedback": "meh"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_feedback_success(self):
        media = Media.objects.create(
            spotify_uri="track123",
            title="Some Track",
            artist_name="Some Artist",
            genre=[],
            album_name="Some Album",
            media_type=Media.SONG,
            saved_at=timezone.now()
        )

        data = {
            "song_id": media.id,
            "feedback": "positive"
        }
        response = self.client.post("/songs/feedback/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Feedback saved successfully.")


    def test_feedback_invalid_song(self):
        response = self.client.post("/songs/feedback/", {
            "song_id": "nonexistent",
            "feedback": "positive"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_similar_songs_success(self):
        media = Media.objects.create(
            spotify_uri="track123",
            title="Some Track",
            artist_name="Some Artist",
            genre=["pop"],
            album_name="Some Album",
            media_type=Media.SONG,
            saved_at=timezone.now()
        )

        UserFeedback.objects.create(
            user=self.user,
            media=media,
            is_liked=True,
            source="test",
            feedback_at=timezone.now()
        )

        response = self.client.post("/songs/similar/", {
            "title": "Some Track",
            "artist": "Some Artist"
        })


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recommendations", response.data)


    def test_similar_songs_missing_feedback(self):
        response = self.client.post("/songs/similar/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "title and artist are required")
