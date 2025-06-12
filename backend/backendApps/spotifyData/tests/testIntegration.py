import pytest
from unittest.mock import patch, Mock
from songs.services.songProcessing import prepare_song_list
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase
from django.conf import settings
from spotifyData.services.spotifyClient import SpotifyAPI

User = get_user_model()

class TestMultipleEndpoints(TestCase):
    def setUp(self):
        self.access_token = "test_access_token"
        self.refresh_token = "test_refresh_token"
        self.user = Mock()
        self.spotify_api = SpotifyAPI(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            user=self.user)

    @pytest.mark.django_db
    @patch("songs.services.songProcessing.should_send_curveball", return_value=False)
    @patch("songs.services.songProcessing.Media")
    @patch("songs.services.songProcessing.UserFeedback")
    @patch("songs.services.songProcessing.SpotifyAPI")
    def test_prepare_song_list_success(mock_spotify_class, mock_feedback, mock_media, mock_curveball, dummy_user):
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

        mock_media.objects.get.return_value = Mock()
        mock_feedback.objects.filter.return_value.first.return_value = Mock(is_liked=True)

        raw_songs = [{"title": "Test Song", "artist": "Test Artist"}]
        result = prepare_song_list(dummy_user, raw_songs, count=1)

        assert len(result) == 1
        song = result[0]

        assert "track_details" in song
        track = song["track_details"]

        assert track["name"] == "Test Song"
        assert track["id"] == "track123"
        assert track["artists"] == ["Test Artist"]

    @pytest.mark.django_db
    def test_like_track_and_get_feedback(client, dummy_user):
        client.force_login(dummy_user)

        uri = "spotify:track:456"
        response = client.post("/api/spotify/liked-tracks/like/", {"uri": uri})
        assert response.status_code == 200

        feedback_response = client.post("/api/songs/feedback/update/", {
            "spotify_uri": uri,
            "is_liked": True
        })
        assert feedback_response.status_code == 200

        response = client.get("/api/songs/feedback/all-feedbacks/")
        assert response.status_code == 200
        assert any(item["spotify_uri"] == uri for item in response.data)


    @pytest.mark.django_db
    def test_generate_playlist_from_prompt(client, dummy_user):
        client.force_login(dummy_user)
        response = client.post("/api/songs/generate-playlist-from-prompt/", {
            "prompt": "Chill na wieczór",
            "count": 3
        })
        assert response.status_code == 200
        assert "playlist_url" in response.data

    @pytest.mark.django_db
    def test_generate_like_and_create_playlist(client, dummy_user):
        client.force_login(dummy_user)
        gen_resp = client.post("/api/songs/generate-from-artist/", {
            "artists": ["Massive Attack"],
            "count": 1
        })
        assert gen_resp.status_code == 200
        uri = gen_resp.data["songs"][0]["track_details"]["uri"]

        like_resp = client.post("/api/spotify/liked-tracks/like/", {"uri": uri})
        assert like_resp.status_code == 200

        playlist_resp = client.post("/api/songs/create-liked-playlist/")
        assert playlist_resp.status_code == 200
        assert "playlist_url" in playlist_resp.data
