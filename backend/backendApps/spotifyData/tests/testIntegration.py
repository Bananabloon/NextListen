import pytest
from unittest.mock import patch, Mock
from songs.services.songProcessing import prepare_song_list
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI
from authentication.services.spotify_service import SpotifyService
from authentication.services.spotify_auth_service import SpotifyAuthService
from django.urls import reverse
User = get_user_model()

class TestMultipleEndpoints(APITestCase):
    def setUp(self):
        self.access_token = "test_access_token"
        self.refresh_token = "test_refresh_token"
        self.user = User.objects.create_user(
            spotify_user_id='testuser'
        )
        self.spotify_api = SpotifyAPI(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            user=self.user)

    @pytest.mark.django_db
    @patch("songs.services.songProcessing.should_send_curveball", return_value=False)
    @patch("songs.services.songProcessing.Media")
    @patch("songs.services.songProcessing.UserFeedback")
    @patch("songs.services.songProcessing.SpotifyAPI")
    def test_prepare_song_list_success(self, mock_spotify_class, mock_feedback, mock_media, mock_curveball):
        mock_spotify = Mock()
        mock_spotify.search.return_value = {
            "tracks": {
                "items": [{
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "explicit": False,
                    "id": "track123",
                    "uri": "spotify:track:test"
                }]
            }
        }
        mock_spotify.get_several_tracks.return_value = {
            "tracks": [{
                "id": "track123",
                "uri": "spotify:track:test",
                "name": "Test Song",
                "artists": [{"name": "Test Artist"}],
                "album": {
                    "name": "Test Album",
                    "album_type": "album",
                    "available_markets": ["US", "PL"],
                    "images": [{"url": "http://image"}],
                    "release_date": "2022-01-01"
                },
                "duration_ms": 180000,
                "popularity": 80,
                "preview_url": "http://preview",
                "external_urls": {"spotify": "http://spotify"}
            }]
        }
        mock_spotify_class.return_value = mock_spotify

        mock_media_instance = Mock()
        mock_media.objects.get_or_create.return_value = (mock_media_instance, True)
        mock_media.objects.get.return_value = mock_media_instance
        
        mock_feedback_instance = Mock(feedback_value=1)
        mock_feedback.objects.filter.return_value.first.return_value = mock_feedback_instance

        raw_songs = [{"title": "Test Song", "artist": "Test Artist"}]
        result = prepare_song_list(self.user, raw_songs, count=1)

        self.assertGreater(len(result), 0)
        if len(result) > 0:
            song = result[0]
            self.assertIn("track_details", song)
            track = song["track_details"]
            self.assertEqual(track["name"], "Test Song")
            self.assertEqual(track["id"], "track123")

