import pytest
<<<<<<< HEAD
from unittest.mock import MagicMock
from songs.views.generationViews import GenerateFromArtistsView
from rest_framework.test import APIRequestFactory
=======
from rest_framework.test import APIClient, APIRequestFactory
from songs.views.generationViews import GenerateFromArtistsView
from users.models import UserFeedback
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        password="testpass",
        spotify_access_token="dummy",
        spotify_refresh_token="dummy",
        curveball_enjoyment=5,
    )


@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def factory():
    return APIRequestFactory()


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    # Mock SpotifyAPI
    class MockSpotify:
        def search(self, query, type):
            return {
                "tracks": {
                    "items": [
                        {
                            "name": "Teardrop",
                            "artists": [{"name": "Massive Attack"}],
                            "uri": "spotify:track:456",
                        },
                        {
                            "name": "Idioteque",
                            "artists": [{"name": "Radiohead"}],
                            "uri": "spotify:track:789",
                        },
                    ]
                }
            }

        def add_to_queue(self, uri):
            return True, None

    monkeypatch.setattr(
        "generationViews.SpotifyAPI", lambda *args, **kwargs: MockSpotify()
    )
    monkeypatch.setattr(
        "playlistViews.SpotifyAPI", lambda *args, **kwargs: MockSpotify()
    )

    # Mock OpenAI response
    monkeypatch.setattr(
        "generationViews.ask_openai",
        lambda *args, **kwargs: """
        [
            {"title": "Teardrop", "artist": "Massive Attack"},
            {"title": "Idioteque", "artist": "Radiohead"}
        ]
    """,
    )
    monkeypatch.setattr(
        "playlistViews.ask_openai",
        lambda *args, **kwargs: '[{"title": "Summer Hit", "artist": "Cool Artist"}]',
    )
>>>>>>> origin/dev


@pytest.mark.django_db
def test_generate_from_artists_success(monkeypatch):
    view = GenerateFromArtistsView.as_view()
<<<<<<< HEAD
    factory = APIRequestFactory()
    user = MagicMock()
    user.is_authenticated = True
    user.spotify_access_token = "test"
    user.spotify_refresh_token = "test"
    user.curveball_enjoyment = 5

=======
>>>>>>> origin/dev
    request = factory.post(
        "/generate",
        {
            "artists": ["Massive Attack", "Radiohead"],
            "count": 2,
            "mood": "chill",
            "tempo": "slow",
        },
        format="json",
    )
    request.user = user

<<<<<<< HEAD
    mock_spotify = MagicMock()
    monkeypatch.setattr(
        "generationViews.SpotifyAPI", lambda *args, **kwargs: mock_spotify
    )

    mock_spotify.search.return_value = {
        "tracks": {
            "items": [
                {
                    "name": "Teardrop",
                    "artists": [{"name": "Massive Attack"}],
                    "uri": "spotify:track:456",
                }
            ]
        }
    }

    mock_spotify.add_to_queue.return_value = (True, None)

    monkeypatch.setattr(
        "generationViews.ask_openai",
        lambda *args, **kwargs: """
    [
      {"title": "Teardrop", "artist": "Massive Attack"},
      {"title": "Idioteque", "artist": "Radiohead"}
    ]
    """,
    )

=======
>>>>>>> origin/dev
    response = view(request)
    assert response.status_code == 200
    assert "added" in response.data
    assert len(response.data["added"]) == 2
<<<<<<< HEAD
=======
    assert response.data["added"][0]["title"] == "Teardrop"


@pytest.mark.django_db
def test_generate_prefers_liked(user, factory):
    UserFeedback.objects.create(user=user, track_name="Teardrop")

    view = GenerateFromArtistsView.as_view()
    request = factory.post(
        "/generate", {"artists": ["Massive Attack"], "count": 2}, format="json"
    )
    request.user = user

    response = view(request)
    assert response.status_code == 200
    titles = [track["title"] for track in response.data["added"]]
    assert "Teardrop" in titles


@pytest.mark.django_db
def test_generate_queue_from_prompt(client):
    response = client.post(
        "/api/generate/queue-from-prompt/", {"prompt": "Najlepsza muzyka na lato"}
    )
    assert response.status_code == 200
    assert "added" in response.data
    assert response.data["added"][0]["title"] == "Summer Hit"
>>>>>>> origin/dev
