from unittest.mock import patch, MagicMock
import pytest
from songs.services.songProcessing import prepare_song_list
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def dummy_user(db):
    return User.objects.create_user(
        spotify_user_id="testuser",
        password="testpass",
        spotify_access_token="dummy",
        spotify_refresh_token="dummy",
        curveball_enjoyment=5,
    )

@pytest.mark.django_db
@patch("songs.services.songProcessing.should_send_curveball", return_value=False)
@patch("songs.services.songProcessing.Media")
@patch("songs.services.songProcessing.UserFeedback")
@patch("songs.services.songProcessing.SpotifyAPI", autospec=True)
def test_prepare_song_list_success(mock_spotify_class, mock_feedback, mock_media, mock_curveball, dummy_user):
    mock_spotify = MagicMock()
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

    mock_media = mock_media.objects
    mock_media.get.return_value = MagicMock()

    mock_feedback.objects.filter.return_value.first.return_value = MagicMock(is_liked=True)

    raw_songs = [{"title": "Test Song", "artist": "Test Artist"}]
    result = prepare_song_list(dummy_user, raw_songs, count=1)

    assert len(result) == 1
    song = result[0]

    # Nowe asercje - dopasowane do struktury z track_details
    assert "track_details" in song
    track = song["track_details"]

    assert track["name"] == "Test Song"
    assert track["id"] == "track123"
    assert "artists" in track
    assert track["artists"] == ["Test Artist"]