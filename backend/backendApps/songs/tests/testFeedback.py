import pytest
from rest_framework.test import APIClient
from users.models import User, Media, UserFeedback
from django.utils import timezone
from unittest import mock

@pytest.fixture
def user(db):
    return User.objects.create_user(
        spotify_user_id="testuser",
        password="testpass",
        spotify_access_token="dummy_token",
        spotify_refresh_token="dummy_refresh",
        curveball_enjoyment=5,
    )

@pytest.fixture
def media_instance(db):
    return Media.objects.create(
        spotify_uri="spotify:track:123",
        title="Test Song",
        artist_name="Test Artist",
        genre=["Pop"],
        album_name="Test Album",
        media_type="song",
        saved_at=timezone.now(),
    )

@pytest.fixture
def user_feedback(db, user, media_instance):
    return UserFeedback.objects.create(
        user=user,
        media=media_instance,
        is_liked=True,
        feedback_at=timezone.now(),
        source="test_source",
    )

@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
@mock.patch("songs.views.allFeedbackViews.requests.get")  
def test_all_user_feedbacks(mock_get, client, user_feedback):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "tracks": [
            {
                "id": "123",
                "name": "Mocked Song",
                "artists": [{"name": "Mocked Artist"}],
                "album": {"name": "Mocked Album"},
                "duration_ms": 123456,
                "popularity": 80,
                "preview_url": "https://mocked.preview",
                "external_urls": {"spotify": "https://open.spotify.com/track/123"},
            }
        ]
    }

    response = client.get("/api/songs/feedback/all-feedbacks/")
    
    assert response.status_code == 200
    assert "feedbacks" in response.data
    assert len(response.data["feedbacks"]) == 1
    feedback = response.data["feedbacks"][0]
    assert feedback["spotify_uri"] == "spotify:track:123"
    assert feedback["is_liked"] is True
    assert feedback["spotify_data"]["title"] == "Mocked Song"
    assert feedback["spotify_data"]["artist"] == "Mocked Artist"
