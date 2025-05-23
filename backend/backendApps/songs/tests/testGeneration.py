import pytest
from unittest.mock import MagicMock
from songs.views.generationViews import GenerateFromArtistsView
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser

@pytest.mark.django_db
def test_generate_from_artists_success(monkeypatch):
    view = GenerateFromArtistsView.as_view()
    factory = APIRequestFactory()
    user = MagicMock()
    user.is_authenticated = True
    user.spotify_access_token = "test"
    user.spotify_refresh_token = "test"
    user.curveball_enjoyment = 5

    request = factory.post("/generate", {
        "artists": ["Massive Attack", "Radiohead"],
        "count": 2,
        "mood": "chill",
        "tempo": "slow"
    }, format="json")
    request.user = user

    mock_spotify = MagicMock()
    monkeypatch.setattr("generationViews.SpotifyAPI", lambda *args, **kwargs: mock_spotify)

    mock_spotify.search.return_value = {
        "tracks": {
            "items": [
                {
                    "name": "Teardrop",
                    "artists": [{"name": "Massive Attack"}],
                    "uri": "spotify:track:456"
                }
            ]
        }
    }

    mock_spotify.add_to_queue.return_value = (True, None)

    monkeypatch.setattr("generationViews.ask_openai", lambda *args, **kwargs: """
    [
      {"title": "Teardrop", "artist": "Massive Attack"},
      {"title": "Idioteque", "artist": "Radiohead"}
    ]
    """)

    response = view(request)
    assert response.status_code == 200
    assert "added" in response.data
    assert len(response.data["added"]) == 2
    
    @pytest.mark.django_db
    def test_generate_prefers_liked(monkeypatch):
        view = GenerateFromArtistsView.as_view()
        factory = APIRequestFactory()
        user = MagicMock()
        user.is_authenticated = True
        user.spotify_access_token = "test"
        user.spotify_refresh_token = "test"
        user.curveball_enjoyment = 5

        # Dodajemy polubiony utwór
        LikedTrack.objects.create(user=user, track_name="Teardrop")

        request = factory.post("/generate", {
            "artists": ["Massive Attack"],
            "count": 2
        }, format="json")
        request.user = user

        mock_spotify = MagicMock()
        monkeypatch.setattr("generationViews.SpotifyAPI", lambda *args, **kwargs: mock_spotify)

        mock_spotify.search.return_value = {
            "tracks": {
                "items": [
                    {"name": "Teardrop", "artists": [{"name": "Massive Attack"}], "uri": "spotify:track:456"}
                ]
            }
        }

        mock_spotify.add_to_queue.return_value = (True, None)

        monkeypatch.setattr("generationViews.ask_openai", lambda *args, **kwargs: """
        [
        {"title": "Teardrop", "artist": "Massive Attack"},
        {"title": "Some Song", "artist": "Some Artist"}
        ]
        """)

        response = view(request)
        assert response.status_code == 200
        assert any(song["title"] == "Teardrop" for song in response.data["added"])

