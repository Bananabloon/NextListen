import pytest
from rest_framework.test import APIClient, APIRequestFactory
from songs.views.generationViews import GenerateFromArtistsView
from users.models import UserFeedback, Media, User
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from songs.views.discoveryGenerationViews import DiscoveryGenerateView
import json
from django.utils import timezone
from rest_framework.test import force_authenticate

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        spotify_user_id="testuser",
        password="testpass",
        spotify_access_token="dummy",
        spotify_refresh_token="dummy",
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
def factory():
    return APIRequestFactory()


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    class MockSpotify:
        def search(self, query, *args, **kwargs):
            return {
                "tracks": {
                    "items": [
                        {
                            "name": "Teardrop",
                            "artists": [{"name": "Massive Attack"}],
                            "uri": "spotify:track:456",
                            "explicit": False,
                            "id": "track456",
                        },
                        {
                            "name": "Idioteque",
                            "artists": [{"name": "Radiohead"}],
                            "uri": "spotify:track:789",
                            "explicit": True,
                            "id": "track789",
                        },
                    ]
                }
            }

        def get_several_tracks(self, track_ids):
            tracks = []
            for track_id in track_ids:
                if track_id == "track456":
                    tracks.append({
                        "id": track_id,
                        "name": "Teardrop",
                        "artists": [{"name": "Massive Attack"}],
                        "explicit": False,
                        "album": {
                            "name": "Mezzanine",
                            "album_type": "album",
                            "available_markets": ["US", "PL"],
                            "images": [{"url": "http://image.com/teardrop"}],
                            "release_date": "1998-04-20"
                        },
                        "duration_ms": 329000,
                        "popularity": 85,
                        "preview_url": "http://preview.com/teardrop",
                        "external_urls": {"spotify": "http://spotify.com/teardrop"}
                    })
                else:
                    tracks.append({
                        "id": track_id,
                        "name": f"Mock Track {track_id}",
                        "artists": [{"name": "Mock Artist"}],
                        "explicit": False,
                        "album": {
                            "name": "Mock Album",
                            "album_type": "album",
                            "available_markets": ["US", "PL"],
                            "images": [{"url": "http://image.com/mock"}],
                            "release_date": "2022-01-01"
                        },
                        "duration_ms": 180000,
                        "popularity": 80,
                        "preview_url": "http://preview.com/mock",
                        "external_urls": {"spotify": "http://spotify.com/mock"}
                    })
            
            return {"tracks": tracks}
            
        def get_top_artists(self, limit=10):
            return {"items": [{"name": "Mock Artist", "genres": ["pop"]}]}
        
        def get_top_tracks(self, limit=10):
            return {"items": [{"name": "Mock Track", "artists": [{"name": "Mock Artist"}]}]}

        def add_to_queue(self, uri):
            return True, None

    monkeypatch.setattr(
        "songs.views.generationViews.SpotifyAPI", lambda *args, **kwargs: MockSpotify()
    )
    monkeypatch.setattr(
        "songs.views.playlistViews.SpotifyAPI", lambda *args, **kwargs: MockSpotify()
    )
    monkeypatch.setattr(
        "songs.services.songProcessing.SpotifyAPI", lambda *args, **kwargs: MockSpotify()
    )
    monkeypatch.setattr(
        "songs.views.discoveryGenerationViews.SpotifyAPI", lambda *args, **kwargs: MockSpotify())

    def mock_ask_openai(*args, **kwargs):
        return '''json
    [
    {"title": "Teardrop", "artist": "Massive Attack"},
    {"title": "Idioteque", "artist": "Radiohead"}
    ]
    '''

    monkeypatch.setattr("songs.utils.ask_openai", mock_ask_openai)


@pytest.mark.django_db
def test_generate_from_artists_success(client):  
    response = client.post("/api/songs/generate-from-artist/", {
        "artists": ["Massive Attack", "Radiohead"],
        "count": 5,
        "mood": "chill",
        "tempo": "slow"
    }, format="json")

    assert response.status_code == 200
    assert "songs" in response.data
    assert len(response.data["songs"]) >= 1 
    first_song = response.data["songs"][0]
    assert "name" in first_song or "title" in first_song  
    song_name = first_song.get("name") or first_song.get("title")
    assert song_name is not None


@pytest.mark.django_db
def test_generate_prefers_liked(user, factory, media_instance):
    UserFeedback.objects.create(user=user, media=media_instance, is_liked=True, feedback_at="2024-01-01")

    view = GenerateFromArtistsView.as_view()
    request = factory.post("/api/songs/generate-from-artist/", {
        "artists": ["Massive Attack"],
        "count": 5
    }, format="json")
    force_authenticate(request, user=user)

    response = view(request)
    assert response.status_code == 200
    assert "songs" in response.data
    names = []
    for track in response.data["songs"]:
        name = track.get("name") or track.get("title")
        if name:
            names.append(name)
    
    assert "Teardrop" in names


@pytest.mark.django_db
def test_generate_queue_from_prompt(client):
    response = client.post(
        "/api/songs/generate-from-prompt/", {"prompt": "Najlepsza muzyka na lato", "count": 5}
    )
    assert response.status_code == 200
    assert "songs" in response.data
    assert len(response.data["songs"]) >= 0  

@pytest.mark.django_db
def test_discovery_generate_view(client):
    response = client.post("/api/songs/generate-from-genre/", {"genre": "rock", "count": 5})

    assert response.status_code == 200
    assert "songs" in response.data
    assert isinstance(response.data["songs"], list)
    if response.data["songs"]:
        first_song = response.data["songs"][0]
        assert any(field in first_song for field in ["name", "title"])