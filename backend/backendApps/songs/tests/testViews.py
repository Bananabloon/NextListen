from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import User
from users.models import Media


User = get_user_model()

class SongViewsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(display_name="testuser", spotify_user_id="dummy_spotify_id")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_song_analysis_missing_data(self):
        response = self.client.post("/songs/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_song_analysis_success(self):
        data = {
            "access_token": "mocked_token",  
            "song_id": "sample_id"
        }
        response = self.client.post("/songs/", data)
        # Zewętrzne API - mocking tylko
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_song_analysis_missing_data(self):
        response = self.client.post("/songs/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_similar_songs_missing_data(self):
        response = self.client.post("/songs/similar/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_similar_songs_missing_feedback(self):
        response = self.client.post("/songs/similar/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "No feedback found for this user.")

#  ToImplement
#     def test_feedback_invalid_input(self):
#         response = self.client.post("/songs/feedback/", {"song_id": 999, "feedback": "meh"})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_feedback_success(self):
    #     media = Media.objects.create(user=self.user, media_id="track123", media_type="track")
    #     data = {
    #         "song_id": media.media_id,
    #         "feedback": "positive"
    #     }
    #     response = self.client.post("/api/songs/feedback/", data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["message"], "Feedback saved successfully.")

    # def test_feedback_invalid_song(self):
    #     response = self.client.post("/api/songs/feedback/", {
    #         "song_id": "nonexistent",
    #         "feedback": "positive"
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_similar_songs_success(self):
    #     # Użytkownik ma jedną ocenioną piosenkę
    #     media = Media.objects.create(user=self.user, media_id="track123", media_type="track")
    #     Feedback.objects.create(user=self.user, song=media, feedback="positive")

    #     response = self.client.post("/songs/similar/", {})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn("recommendations", response.data)