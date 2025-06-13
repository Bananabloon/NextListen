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

    # @pytest.mark.django_db
    # @patch('songs.views.saveFeedbackViews.UserFeedback.objects')
    # @patch('songs.views.saveFeedbackViews.Media.objects')
    # def test_like_track_and_get_feedback(self, mock_media_objects, mock_feedback_objects):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_media_instance = Mock()
    #     mock_media_objects.get_or_create.return_value = (mock_media_instance, True)
        
    #     mock_feedback_instance = Mock()
    #     mock_feedback_instance.spotify_uri = "spotify:track:456"
    #     mock_feedback_instance.feedback_value = 1
    #     mock_feedback_instance.user = self.user
    #     mock_feedback_objects.get_or_create.return_value = (mock_feedback_instance, True)
    #     mock_feedback_objects.filter.return_value.all.return_value = [mock_feedback_instance]

    #     uri = "spotify:track:456"
    #     response = self.client.post("/api/songs/feedback/update/", {
    #         "spotify_uri": uri,
    #         "feedback_value": 1
    #     }, format='json')
                
    #     if response.status_code != 200:
    #         print(f"Feedback response status: {response.status_code}")
    #         print(f"Feedback response data: {response.data}")
        
    #     self.assertEqual(response.status_code, 200)

    #     response = self.client.get("/api/songs/feedback/all-feedbacks/")
    #     self.assertEqual(response.status_code, 200)

    # @pytest.mark.django_db
    # @patch('songs.services.generationPipeline.prepare_song_list')
    # @patch('songs.views.saveFeedbackViews.UserFeedback.objects')
    # @patch('songs.views.saveFeedbackViews.Media.objects')
    # @patch('songs.views.playlistViews.create_playlist')
    # def test_generate_like_and_create_playlist(self, mock_create_playlist, mock_media_objects, mock_feedback_objects, mock_generate):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_generate.return_value = [{
    #         "track_details": {
    #             "name": "Teardrop",
    #             "artists": [{"name": "Massive Attack"}],
    #             "uri": "spotify:track:test123",
    #             "id": "test123"
    #         }
    #     }]
        
    #     mock_media_instance = Mock()
    #     mock_media_objects.get_or_create.return_value = (mock_media_instance, True)
    #     mock_feedback_instance = Mock()
    #     mock_feedback_objects.get_or_create.return_value = (mock_feedback_instance, True)
        
    #     mock_create_playlist.return_value = {
    #         'playlist_url': 'https://open.spotify.com/playlist/liked123',
    #         'playlist_id': 'liked123'
    #     }

    #     gen_resp = self.client.post("/api/songs/generate-from-artist/", {
    #         "artists": ["Massive Attack"],
    #         "count": 1
    #     })
    #     self.assertEqual(gen_resp.status_code, 200)
        
    #     uri = "spotify:track:test123"
    #     like_resp = self.client.post("/api/songs/feedback/update/", {
    #         "spotify_uri": uri,
    #         "feedback_value": 1
    #     }, format='json')
    #     self.assertEqual(like_resp.status_code, 200)

    #     playlist_resp = self.client.post("/api/songs/create-liked-playlist/")
    #     self.assertEqual(playlist_resp.status_code, 200)
    #     self.assertIn("playlist_url", playlist_resp.data)

    # @patch('authentication.services.spotify_service.requests.post')
    # @patch('authentication.services.spotify_service.requests.get')
    # @patch('authentication.services.spotify_auth_service.UserService.create_or_update_user')
    # @patch('authentication.services.spotify_auth_service.TokenService.generate_tokens_for_user')
    # def test_full_spotify_auth_flow(self, mock_generate_tokens, mock_create_user,
    #                                mock_get_request, mock_post_request):
    #     mock_token_response = Mock()
    #     mock_token_response.status_code = 200
    #     mock_token_response.json.return_value = {
    #         'access_token': 'spotify_access_token',
    #         'refresh_token': 'spotify_refresh_token'
    #     }
    #     mock_post_request.return_value = mock_token_response
        
    #     mock_user_response = Mock()
    #     mock_user_response.status_code = 200
    #     mock_user_response.json.return_value = {
    #         'id': 'spotify_user_123',
    #         'display_name': 'Integration Test User'
    #     }
    #     mock_get_request.return_value = mock_user_response
        
    #     mock_user = Mock()
    #     mock_tokens = {'access': 'jwt_token', 'refresh': 'jwt_refresh'}
    #     mock_create_user.return_value = mock_user
    #     mock_generate_tokens.return_value = mock_tokens
        
    #     token_data = SpotifyService.exchange_code_for_spotify_token('auth_code')
        
    #     user_tokens, error = SpotifyAuthService.authenticate_spotify_user(
    #         token_data['access_token'], 
    #         token_data['refresh_token']
    #     )
        
    #     self.assertIsNotNone(token_data)
    #     self.assertIsNotNone(user_tokens)
    #     self.assertIsNone(error)
    #     self.assertEqual(user_tokens, mock_tokens)

    # @pytest.mark.django_db
    # @patch('spotifyData.services.spotifyClient.SpotifyAPI')
    # def test_spotify_profile_and_top_tracks_integration(self, mock_get_spotify_api, mock_spotify_api):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_spotify_instance = Mock()
    #     mock_get_spotify_api.return_value = mock_spotify_instance
        
    #     mock_spotify_instance.get_current_user_profile.return_value = {
    #         'display_name': 'Test User',
    #         'access_token': 'token'
    #     }
        
    #     mock_spotify_instance.get_user_top_tracks.return_value = {
    #         'items': [{
    #             'id': 'track1',
    #             'name': 'Top Track 1',
    #             'artists': [{'name': 'Artist 1'}]
    #         }]
    #     }
        
    #     profile_resp = self.client.get("/api/spotify/profile/")
    #     self.assertEqual(profile_resp.status_code, 200)
        
    #     top_tracks_resp = self.client.get("/api/spotify/top-tracks/")
    #     self.assertEqual(top_tracks_resp.status_code, 200)
        
    #     self.assertIn('display_name', profile_resp.data)
    #     self.assertIn('items', top_tracks_resp.data)

    # @pytest.mark.django_db
    # @patch('spotifyData.services.spotifyClient.SpotifyAPI')
    # def test_search_and_save_track_integration(self, mock_get_spotify_api):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_spotify_instance = Mock()
    #     mock_get_spotify_api.return_value = mock_spotify_instance
        
    #     mock_spotify_instance.search.return_value = {
    #         'tracks': {
    #             'items': [{
    #                 'id': 'search_track_1',
    #                 'name': 'Search Result',
    #                 'artists': [{'name': 'Search Artist'}]
    #             }]
    #         }
    #     }
        
    #     mock_spotify_instance.like_track.return_value = (True, None)
        
    #     search_resp = self.client.get("/api/spotify/search/", {
    #         'q': 'test song',
    #         'type': 'track'
    #     })
    #     self.assertEqual(search_resp.status_code, 200)
        
    #     save_resp = self.client.post("/api/spotify/saved-tracks/save/", {
    #         'track_id': 'search_track_1'
    #     })
    #     self.assertEqual(save_resp.status_code, 204)

    # @pytest.mark.django_db
    # @patch('songs.views.generationViews.prepare_song_list')
    # @patch('spotifyData.services.spotifyClient.SpotifyAPI')
    # def test_genre_discovery_and_analysis_flow(self, mock_spotify_api, mock_generate_service):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_spotify_instance = Mock()
    #     mock_spotify_api.return_value = mock_spotify_instance
        
    #     mock_spotify_instance.search.return_value = {
    #         "tracks": {
    #             "items": [{
    #                 "id": "jazz123",
    #                 "name": "Take Five",
    #                 "artists": [{"name": "The Dave Brubeck Quartet"}],
    #                 "uri": "spotify:track:jazz123"
    #             }]
    #         }
    #     }
        
    #     mock_generate_service.return_value = [{
    #         "track_details": {
    #             "name": "Jazz Track",
    #             "artists": [{"name": "Jazz Artist"}],
    #             "uri": "spotify:track:jazz123",
    #             "id": "jazz123"
    #         }
    #     }]
        
    #     mock_spotify_instance.get_track_audio_features.return_value = {
    #         'danceability': 0.8,
    #         'energy': 0.6,
    #         'valence': 0.7
    #     }
        
    #     genre_resp = self.client.post("/api/songs/generate-from-genre/", {
    #         "genres": ["jazz"],
    #         "count": 1
    #     })
    #     self.assertEqual(genre_resp.status_code, 200)
        
    #     analysis_resp = self.client.post("/api/songs/analysis/", {
    #         "track_id": "jazz123"
    #     })
    #     self.assertEqual(analysis_resp.status_code, 200)

    # @pytest.mark.django_db
    # @patch('spotifyData.services.spotifyClient.SpotifyAPI')
    # def test_playback_control_integration(self, mock_get_spotify_api, mock_spotify_api):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_spotify_instance = Mock()
    #     mock_get_spotify_api.return_value = mock_spotify_instance
        
    #     mock_spotify_instance.start_playback.return_value = (True, None)
    #     mock_spotify_instance.add_to_queue.return_value = (True, None)
    #     mock_spotify_instance.get_currently_playing.return_value = {
    #         'item': {
    #             'id': 'current_track',
    #             'name': 'Currently Playing'
    #         }
    #     }
        
    #     playback_resp = self.client.post("/api/spotify/playback/start/", {
    #         'track_uri': 'spotify:track:test123',
    #         'device_id': 'abc123'
    #     })
    #     self.assertEqual(playback_resp.status_code, 200)
        
    #     queue_resp = self.client.post("/api/spotify/queue/add/", {
    #         'track_uri': 'spotify:track:queue123'
    #     })
    #     self.assertEqual(queue_resp.status_code, 200)
        
    #     current_resp = self.client.get("/api/spotify/currently-playing/")
    #     self.assertEqual(current_resp.status_code, 200)

    # @pytest.mark.django_db
    # @patch('songs.views.similarSongViews')
    # @patch('songs.views.generationViews.prepare_song_list')
    # def test_song_similarity_and_generation_flow(self, mock_generate_service, mock_similar_service):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_similar_service.return_value = [{
    #         "title": "Similar Song",
    #         "artist": "Similar Artist",
    #         "similarity_score": 0.85
    #     }]
        
    #     mock_generate_service.return_value = [{
    #         "track_details": {
    #             "name": "Generated Song",
    #             "artists": [{"name": "Generated Artist"}],
    #             "uri": "spotify:track:gen123",
    #             "id": "gen123"
    #         }
    #     }]
        
    #     similar_resp = self.client.post("/api/songs/similar/", {
    #         "title": "Test Song",
    #         "artist": "Test Artist"
    #     })
    #     self.assertEqual(similar_resp.status_code, 200)
        
    #     generate_resp = self.client.post("/api/songs/generate-from-song/", {
    #         "songs": [{"title": "Test Song - please generate random songs", "artist": "Test Artist"}],
    #         "count": 1
    #     })
    #     self.assertEqual(generate_resp.status_code, 200)

    # @pytest.mark.django_db
    # def test_user_data_management_flow(self):
    #     self.client.force_authenticate(user=self.user)
        
    #     stats_resp = self.client.get("/api/spotify/user-stats/")
    #     self.assertIn(stats_resp.status_code, [200, 404, 500])

    #     delete_data_resp = self.client.delete("/api/auth/spotify/delete-user-data/")
    #     self.assertEqual(delete_data_resp.status_code, 200)
        
    #     delete_tokens_resp = self.client.delete("/api/auth/spotify/delete-tokens/")
    #     self.assertEqual(delete_tokens_resp.status_code, 200)

    # @pytest.mark.django_db
    # @patch('authentication.services.spotify_service.SpotifyService.refresh_access_token')
    # def test_token_refresh_flow(self, mock_refresh):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_refresh.return_value = {
    #         'access_token': 'new_access_token',
    #         'refresh_token': 'new_refresh_token'
    #     }
        
    #     refresh_resp = self.client.post("/api/auth/spotify/refresh-token/")
    #     self.assertEqual(refresh_resp.status_code, 200)

    # @pytest.mark.django_db
    # @patch('songs.views.generationViews.prepare_song_list')
    # def test_multiple_endpoints_with_real_user_flow(self, mock_generate):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_generate.return_value = [{
    #         "track_details": {
    #             "name": "Top Track",
    #             "artists": [{"name": "Top Artist"}],
    #             "uri": "spotify:track:top123",
    #             "id": "top123"
    #         }
    #     }]
        
    #     response = self.client.post("/api/songs/generate-from-top/", {
    #         "count": 1
    #     }, format='json')
        
    #     if response.status_code != 200:
    #         print(f"Generate from top response status: {response.status_code}")
    #         print(f"Generate from top response data: {response.data}")
        
    #     self.assertEqual(response.status_code, 200)
    #     self.assertGreater(len(response.data), 0)

    # @pytest.mark.django_db 
    # @patch('songs.views.playlistViews.create_playlist')
    # @patch('songs.views.saveFeedbackViews.UserFeedback.objects')
    # @patch('songs.views.saveFeedbackViews.Media.objects')
    # def test_feedback_and_playlist_creation_flow(self, mock_media_objects, mock_feedback_objects, mock_create_playlist):
    #     self.client.force_authenticate(user=self.user)
        
    #     mock_media_objects.get_or_create.return_value = (Mock(), True)
    #     mock_feedback_objects.get_or_create.return_value = (Mock(), True)
    #     mock_create_playlist.return_value = {
    #         'playlist_url': 'https://open.spotify.com/playlist/test123'
    #     }

    #     uris = ["spotify:track:1", "spotify:track:2", "spotify:track:3"]
    #     for uri in uris:
    #         response = self.client.post("/api/songs/feedback/update/", {
    #             "spotify_uri": uri,
    #             "feedback_value": 1
    #         }, format='json')
            
    #         if response.status_code != 200:
    #             print(f"Feedback loop response status: {response.status_code}")
    #             print(f"Feedback loop response data: {response.data}")
            
    #         self.assertEqual(response.status_code, 200)
        
    #     playlist_response = self.client.post("/api/songs/create-liked-playlist/", format='json')
        
    #     if playlist_response.status_code != 200:
    #         print(f"Playlist creation response status: {playlist_response.status_code}")
    #         print(f"Playlist creation response data: {playlist_response.data}")
        
    #     self.assertEqual(playlist_response.status_code, 200)
    #     self.assertIn("playlist_url", playlist_response.data)