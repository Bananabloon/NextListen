from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


class SpotifyDataViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            display_name="TestUser", spotify_user_id="test123"
        )
        self.user.spotify_access_token = "fake-access-token"
        self.user.spotify_refresh_token = "fake-refresh-token"
        self.user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_top_artists")
    @patch("builtins.open")
    @patch("json.load")
    def test_discovery_genres_view(
        self, mock_json_load, mock_open, mock_get_top_artists
    ):
        mock_get_top_artists.return_value = {"items": [{"genres": ["pop"]}]}
        mock_json_load.return_value = [
            {"category": "rock", "popularity": 100},
            {"category": "jazz", "popularity": 80},
        ]

        response = self.client.get("/api/spotify/discover/?count=2")

        self.assertEqual(response.status_code, 200)
        self.assertIn("genres", response.data)
        self.assertLessEqual(len(response.data["genres"]), 2)

    @patch("spotifyData.views.discovery.OpenAI")
    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_top_tracks")
    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_top_artists")
    @patch("spotifyData.services.spotifyClient.SpotifyAPI.search")
    @patch("spotifyData.services.spotifyClient.SpotifyAPI.add_to_queue")
    def test_discovery_generate_view(
        self, mock_add, mock_search, mock_artists, mock_tracks, mock_openai
    ):
        mock_artists.return_value = {"items": [{"name": "artist", "genres": ["pop"]}]}
        mock_tracks.return_value = {
            "items": [{"name": "song", "artists": [{"name": "artist"}]}]
        }

        mock_openai.return_value.chat.completions.create.return_value.choices = [
            type(
                "obj",
                (object,),
                {
                    "message": type(
                        "msg",
                        (object,),
                        {"content": '[{"title": "test", "artist": "someone"}]'},
                    )
                },
            )()
        ]
        mock_search.return_value = {"tracks": {"items": [{"uri": "spotify:track:123"}]}}
        mock_add.return_value = (True, None)

        response = self.client.post(
            "/api/spotify/discover/generate/", {"genre": "rock", "count": 1}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("songs", response.data)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_user_profile")
    def test_get_current_user_profile(self, mock_profile):
        mock_profile.return_value = {"id": "test123", "display_name": "TestUser"}
        response = self.client.get("/api/spotify/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_top_tracks")
    def test_get_top_tracks(self, mock_tracks):
        mock_tracks.return_value = {"items": []}
        response = self.client.get("/api/spotify/top-tracks/")

        self.assertEqual(response.status_code, 200)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_top_artists")
    def test_get_top_artists(self, mock_artists):
        mock_artists.return_value = {"items": []}
        response = self.client.get("/api/spotify/top-artists/")

        self.assertEqual(response.status_code, 200)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_current_playing")
    def test_get_currently_playing(self, mock_current):
        mock_current.return_value = {"is_playing": True}
        response = self.client.get("/api/spotify/currently-playing/")

        self.assertEqual(response.status_code, 200)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.add_to_queue")
    def test_add_track_to_queue(self, mock_add):
        mock_add.return_value = (True, None)
        response = self.client.post(
            "/api/spotify/queue/add/", {"track_uri": "spotify:track:abc"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    def test_add_track_to_queue_missing_uri(self):
        response = self.client.post("/api/spotify/queue/add/", {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_spotify_search_invalid(self):
        response = self.client.get("/api/spotify/search/")
        self.assertEqual(response.status_code, 400)

    @patch("requests.get")
    def test_spotify_search_valid(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"tracks": {"items": []}}

        response = self.client.get("/api/spotify/search/?q=test&type=track")
        self.assertEqual(response.status_code, 200)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.transfer_playback")
    def test_transfer_playback_success(self, mock_transfer):
        mock_transfer.return_value = (True, None)
        response = self.client.post(
            "/api/spotify/playback/transfer/", {"device_id": "device123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Playback transferred successfully")

    def test_transfer_playback_missing_device_id(self):
        response = self.client.post("/api/spotify/playback/transfer/", {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.start_playback")
    def test_start_playback_success(self, mock_start):
        mock_start.return_value = (True, None)
        response = self.client.post(
            "/api/spotify/playback/start/",
            {"device_id": "device123", "track_uri": "spotify:track:xyz"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Playback started")

    def test_start_playback_missing_fields(self):
        response = self.client.post("/api/spotify/playback/start/", {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

        response = self.client.post(
            "/api/spotify/playback/start/", {"track_uri": "spotify:track:xyz"}
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/spotify/playback/start/", {"device_id": "device123"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("requests.get")
    def test_spotify_search_artist_type(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"artists": {"items": []}}

        response = self.client.get("/api/spotify/search/?q=test&type=artist")
        self.assertEqual(response.status_code, 200)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.get_liked_tracks")
    def test_liked_tracks_view(self, mock_get_liked_tracks):
        mock_get_liked_tracks.return_value = {"items": [{"id": "1", "name": "Song"}]}
        response = self.client.get("/api/spotify/liked/?limit=1&offset=0")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.data)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.like_track")
    def test_like_track_view(self, mock_like_track):
        mock_like_track.return_value = (True, None)
        response = self.client.post("/api/spotify/liked/like/", {"track_id": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)

    @patch("spotifyData.services.spotifyClient.SpotifyAPI.remove_liked_track")
    def test_remove_liked_track_view(self, mock_remove_liked_track):
        mock_remove_liked_track.return_value = (True, None)
        response = self.client.post("/api/spotify/liked/remove/", {"track_id": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
