from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class GetArtistViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            display_name="TestUser", spotify_user_id="test123"
        )
        self.user.spotify_access_token = "fake-access-token"
        self.user.spotify_refresh_token = "fake-refresh-token"
        self.user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_artist")
    def test_get_artist_success(self, mock_get_artist):
        mock_get_artist.return_value = {
            "id": "1tpXaFzQmEtgy8kSXWbZVr",
            "name": "Coldplay",
            "genres": ["pop", "rock"],
            "popularity": 85,
            "followers": {"total": 10000000}
        }

        response = self.client.get("/api/spotify/get-artist/?artist_id=1tpXaFzQmEtgy8kSXWbZVr")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], "1tpXaFzQmEtgy8kSXWbZVr")
        self.assertEqual(response.data["name"], "Coldplay")
        self.assertIn("genres", response.data)
        mock_get_artist.assert_called_once_with("1tpXaFzQmEtgy8kSXWbZVr")

    def test_get_artist_missing_artist_id(self):
        response = self.client.get("/api/spotify/get-artist/")
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "artist_id query parameter is required")

    def test_get_artist_empty_artist_id(self):
        response = self.client.get("/api/spotify/get-artist/?artist_id=")
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "artist_id query parameter is required")

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_artist")
    def test_get_artist_api_error(self, mock_get_artist):
        mock_get_artist.return_value = {
            "error": "Artist not found",
            "status": 404
        }

        response = self.client.get("/api/spotify/get-artist/?artist_id=invalid_id")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Failed to fetch artist")
        self.assertIn("details", response.data)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_artist")
    def test_get_artist_with_whitespace_id(self, mock_get_artist):
        mock_get_artist.return_value = {
            "id": "test_id",
            "name": "Test Artist"
        }

        response = self.client.get("/api/spotify/get-artist/?artist_id=  test_id  ")

        self.assertEqual(response.status_code, 200)

