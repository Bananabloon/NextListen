from unittest.mock import patch, MagicMock
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import User, Media, UserFeedback
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


def authenticate_client():
    user = User.objects.create_user(spotify_user_id="testuser", password="testpass")
    token = AccessToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")
    return client, user


class CreateLikedPlaylistsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            spotify_user_id="playlist_user",
            password="pass",
            spotify_access_token="token123",
            spotify_refresh_token="refresh123",
        )
        token = AccessToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")

    def test_returns_400_when_no_liked_songs(self):
        response = self.client.post("/api/songs/create-liked-playlist/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    @patch("songs.views.playlistViews.create_playlist_with_uris")
    @patch("songs.views.playlistViews.SpotifyAPI")
    def test_creates_playlists_successfully(self, mock_spotify, mock_create_playlist):
        mock_create_playlist.return_value = "http://spotify.com/fake_playlist"

        media = Media.objects.create(
            spotify_uri="spotify:track:abc123",
            title="A",
            artist_name="B",
            album_name="C",
            genre=[],
            media_type=Media.SONG,
            saved_at=timezone.now(),
        )

        UserFeedback.objects.create(
            user=self.user,
            media=media,
            is_liked=True,
            source="test_case",
            feedback_at=timezone.now().date()
        )

        response = self.client.post("/api/songs/create-liked-playlist/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("playlists", response.data)


class CreatePromptPlaylistTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            spotify_user_id="prompt_user",
            password="pass",
            spotify_access_token="token123",
            spotify_refresh_token="refresh123"
        )
        token = AccessToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")

    def test_missing_fields_returns_400(self):
        response = self.client.post("/api/songs/generate-playlist-from-prompt/", {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    @patch("songs.views.playlistViews.create_playlist_with_uris")
    @patch("songs.views.playlistViews.find_best_match")
    @patch("songs.views.playlistViews.generate_songs_with_buffer")
    @patch("songs.views.playlistViews.SpotifyAPI")
    def test_creates_playlist_successfully(self, mock_spotify, mock_generate, mock_match, mock_create_playlist):
        mock_generate.return_value = ([{"title": "Song1", "artist": "Artist1"}], "prompt")
        mock_match.return_value = {"uri": "spotify:track:test123"}
        mock_create_playlist.return_value = "http://spotify.com/playlist"

        spotify_instance = MagicMock()
        spotify_instance.search.return_value = {"tracks": {"items": [{}]}}
        mock_spotify.return_value = spotify_instance

        payload = {
            "prompt": "Relaxing evening jazz",
            "name": "Jazz Vibes",
            "count": 1
        }

        response = self.client.post("/api/songs/generate-playlist-from-prompt/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("url", response.data)
