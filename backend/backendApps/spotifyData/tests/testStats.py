import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from users.models import UserFeedback, Media
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def media_items(db):
    media1 = Media.objects.create(
        spotify_uri="track1", title="Song 1", artist_name="Artist 1", genre="pop", album_name="Test Album", media_type="track", saved_at=timezone.now()
    )
    media2 = Media.objects.create(
        spotify_uri="track2", title="Song 2", artist_name="Artist 2", genre="rock",album_name="Test Album", media_type="track", saved_at=timezone.now()
    )
    media3 = Media.objects.create(
        spotify_uri="track3", title="Song 3", artist_name="Artist 1", genre="pop", album_name="Test Album", media_type="track", saved_at=timezone.now()
    )
    return media1, media2, media3


def test_user_stats_no_feedbacks(client):
    response = client.get("/api/spotify/user-stats/")
    assert response.status_code == 200
    assert response.data["total_feedbacks"] == 0
    assert response.data["liked"] == 0
    assert response.data["disliked"] == 0
    assert response.data["curveball_enjoyment"] == 5
    assert response.data["curveballs_total"] == 0
    assert response.data["curveballs_liked"] == 0
    assert response.data["top_genres"] == []
    assert response.data["top_artists"] == []
    assert response.data["most_common_media_type"] is None
    assert response.data["recent_top_genres"] == []


def test_user_stats_with_feedbacks(client, user, media_items):
    media1, media2, media3 = media_items
    UserFeedback.objects.create(user=user, media=media1, is_liked=True, source="recommendation", feedback_at=timezone.now())
    UserFeedback.objects.create(user=user, media=media2, is_liked=False, source="curveball", feedback_at=timezone.now())
    UserFeedback.objects.create(user=user, media=media3, is_liked=True, source="curveball", feedback_at=timezone.now())

    response = client.get("/api/spotify/user-stats/")

    assert response.status_code == 200
    assert response.data["total_feedbacks"] == 3
    assert response.data["liked"] == 2
    assert response.data["disliked"] == 1
    assert response.data["curveballs_total"] == 2
    assert response.data["curveballs_liked"] == 1

    top_genres = response.data["top_genres"]
    assert top_genres[0][0] == "pop"
    assert top_genres[0][1] == 2

    top_artists = response.data["top_artists"]
    assert top_artists[0][0] == "Artist 1"
    assert top_artists[0][1] == 2

    assert response.data["most_common_media_type"] == "track"


def test_user_stats_recent_feedbacks(client, user, media_items):
    media1, media2, _ = media_items
    old_feedback = UserFeedback.objects.create(user=user, media=media1, is_liked=True, source="recommendation", feedback_at=timezone.now())
    old_feedback.feedback_at = timezone.now() - timedelta(days=35)
    old_feedback.save()

    UserFeedback.objects.create(user=user, media=media2, is_liked=True, source="recommendation", feedback_at=timezone.now())

    response = client.get("/api/spotify/user-stats/")
    assert response.status_code == 200
    assert response.data["total_feedbacks"] == 2
    recent_top_genres = response.data["recent_top_genres"]
    assert recent_top_genres[0][0] == "rock"
    assert recent_top_genres[0][1] == 1


def test_user_stats_top_counts_limit(client, user):
    genres = ["pop", "rock", "jazz", "blues", "country", "hip-hop", "electronic"]
    for i, genre in enumerate(genres):
        media = Media.objects.create(
            spotify_uri=f"track{i}", title=f"Song {i}",
            artist_name=f"Artist {i}", genre=genre, media_type="track",
            saved_at=timezone.now()
        )
        UserFeedback.objects.create(user=user, media=media, is_liked=True, source="recommendation", feedback_at=timezone.now())

    response = client.get("/api/spotify/user-stats/")
    assert response.status_code == 200
    assert len(response.data["top_genres"]) <= 5
    assert len(response.data["top_artists"]) <= 5
    assert len(response.data["recent_top_genres"]) <= 3


def test_user_stats_curveball_filtering(client, user, media_items):
    media1, media2, media3 = media_items
    UserFeedback.objects.create(user=user, media=media1, is_liked=True, source="curveball", feedback_at=timezone.now())
    UserFeedback.objects.create(user=user, media=media2, is_liked=False, source="curveball", feedback_at=timezone.now())
    UserFeedback.objects.create(user=user, media=media3, is_liked=True, source="recommendation", feedback_at=timezone.now())

    response = client.get("/api/spotify/user-stats/")
    assert response.status_code == 200
    assert response.data["total_feedbacks"] == 3
    assert response.data["curveballs_total"] == 2
    assert response.data["curveballs_liked"] == 1


def test_user_stats_authentication_required():
    client = APIClient()
    response = client.get("/api/spotify/user-stats/")
    assert response.status_code == 401


def test_user_stats_counter_edge_cases(client, user):
    media_with_none = Media.objects.create(
        spotify_uri="track_none", title="Song None", artist_name="example", genre="pop", media_type="track", saved_at=timezone.now()
    )
    UserFeedback.objects.create(user=user, media=media_with_none, is_liked=True, source="recommendation", feedback_at=timezone.now())

    response = client.get("/api/spotify/user-stats/")
    assert response.status_code == 200
    assert response.data["total_feedbacks"] == 1
