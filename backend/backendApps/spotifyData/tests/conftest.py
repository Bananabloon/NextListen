import pytest
from unittest.mock import Mock, patch
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import Media

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        spotify_user_id="testuser",
        password="testpass",
        spotify_access_token="dummy_access_token",
        spotify_refresh_token="dummy_refresh_token",
        curveball_enjoyment=5,
    )

@pytest.fixture
def media_instance(db):
    return Media.objects.create(
        spotify_uri="spotify:track:456",
        title="Teardrop",
        artist_name="Massive Attack",
        genre="Trip-hop",
        saved_at=timezone.now()
    )

@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def mock_openai_response():
    return [
        {"title": "Teardrop", "artist": "Massive Attack"},
        {"title": "Angel", "artist": "Massive Attack"},
    ]

@pytest.fixture
def mock_spotify_api():
    with patch('spotifyData.services.spotifyClient.SpotifyAPI') as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance

        mock_instance.get_user_profile.return_value = {
            "id": "testuser",
            "display_name": "Test User"
        }
        mock_instance.like_track.return_value = None
        mock_instance.search.return_value = {
            "tracks": {
                "items": [{
                    "id": "track123",
                    "name": "Test Track",
                    "artists": [{"name": "Test Artist"}]
                }]
            }
        }
        mock_instance.get_several_tracks.return_value = [{
            "id": "track123",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}]
        }]
        
        yield mock_instance
