# import pytest
# from unittest.mock import patch, MagicMock
# from songs.services.songProcessing import prepare_song_list
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @pytest.fixture
# def dummy_user(db):
#     return User.objects.create_user(
#         spotify_user_id="testuser",
#         password="testpass",
#         spotify_access_token="dummy",
#         spotify_refresh_token="dummy",
#         curveball_enjoyment=5,
#     )

# @pytest.mark.django_db
# @patch("songs.services.songProcessing.should_send_curveball", return_value=False)
# @patch("songs.services.songProcessing.Media")
# @patch("songs.services.songProcessing.UserFeedback")
# @patch("songs.services.songProcessing.SpotifyAPI", autospec=True)
# def test_prepare_song_list_success(mock_spotify_class, mock_feedback, mock_media, mock_curveball, dummy_user):
#     mock_spotify = MagicMock()
#     mock_spotify.search.return_value = {
#         "tracks": {
#             "items": [{
#                 "name": "Test Song",
#                 "artists": [{"name": "Test Artist"}],
#                 "explicit": False,
#                 "id": "track123",
#                 "uri": "spotify:track:test"
#             }]
#         }
#     }
#     mock_spotify.get_several_tracks.return_value = {
#         "tracks": [{
#             "id": "track123",
#             "uri": "spotify:track:test",
#             "name": "Test Song",
#             "artists": [{"name": "Test Artist"}],
#             "album": {
#                 "name": "Test Album",
#                 "album_type": "album",
#                 "available_markets": ["US", "PL"],
#                 "images": [{"url": "http://image"}],
#                 "release_date": "2022-01-01"
#             },
#             "duration_ms": 180000,
#             "popularity": 80,
#             "preview_url": "http://preview",
#             "external_urls": {"spotify": "http://spotify"}
#         }]
#     }
#     mock_spotify_class.return_value = mock_spotify

#     mock_media = mock_media.objects
#     mock_media.get.return_value = MagicMock()

#     mock_feedback.objects.filter.return_value.first.return_value = MagicMock(is_liked=True)

#     raw_songs = [{"title": "Test Song", "artist": "Test Artist"}]
#     result = prepare_song_list(dummy_user, raw_songs, count=1)

#     assert len(result) == 1
#     song = result[0]

#     assert "track_details" in song
#     track = song["track_details"]

#     assert track["name"] == "Test Song"
#     assert track["id"] == "track123"
#     assert "artists" in track
#     assert track["artists"] == ["Test Artist"]

# @pytest.mark.django_db
# def test_like_track_and_get_feedback(client):
#     uri = "spotify:track:456"

#     response = client.post("/api/spotify/liked-tracks/like/", {"uri": uri})
#     assert response.status_code == 200

#     feedback_response = client.post("/api/songs/feedback/update/", {
#         "spotify_uri": uri,
#         "is_liked": True
#     })
#     assert feedback_response.status_code == 200

#     response = client.get("/api/songs/feedback/all-feedbacks/")
#     assert response.status_code == 200
#     assert any(item["spotify_uri"] == uri for item in response.data)

# @pytest.mark.django_db
# def test_generate_playlist_from_prompt(client):
#     response = client.post("/api/songs/generate-playlist-from-prompt/", {
#         "prompt": "Chill na wieczór",
#         "count": 3
#     })
#     assert response.status_code == 200
#     assert "playlist_url" in response.data

# @pytest.mark.django_db
# def test_generate_like_and_create_playlist(client):
#     gen_resp = client.post("/api/songs/generate-from-artist/", {
#         "artists": ["Massive Attack"],
#         "count": 1
#     })
#     assert gen_resp.status_code == 200
#     uri = gen_resp.data["songs"][0]["track_details"]["uri"]

#     like_resp = client.post("/api/spotify/liked-tracks/like/", {"uri": uri})
#     assert like_resp.status_code == 200

#     playlist_resp = client.post("/api/songs/create-liked-playlist/")
#     assert playlist_resp.status_code == 200
#     assert "playlist_url" in playlist_resp.data

# @pytest.mark.django_db
# def test_analyze_song(client):
#     response = client.post("/api/songs/analysis/", {
#         "title": "Teardrop",
#         "artist": "Massive Attack"
#     })
#     assert response.status_code == 200
#     assert "analysis" in response.data

# @pytest.mark.django_db
# def test_get_spotify_profile(client):
#     response = client.get("/api/spotify/profile/")
#     assert response.status_code == 200
#     assert "id" in response.data or "display_name" in response.data
