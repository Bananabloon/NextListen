from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import PreferenceVector
from users.serializers import PreferenceVectorSerializer
from .services.spotifyClient import SpotifyAPI
from .services.qdrantService import upload_user_preference, create_genre_collection
from qdrant_client.http.exceptions import UnexpectedResponse
from collections import defaultdict
import numpy as np
import requests

FEATURE_KEYS = ["danceability", "energy", "valence", "tempo"]


def get_spotify_instance(user):
    return SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)


class CurrentUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spotify = get_spotify_instance(request.user)
        return Response(spotify.get_user_profile())


class TopTracksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spotify = get_spotify_instance(request.user)
        return Response(spotify.get_top_tracks())


class TopArtistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spotify = get_spotify_instance(request.user)
        return Response(spotify.get_top_artists())


class CurrentlyPlayingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spotify = get_spotify_instance(request.user)
        return Response(spotify.get_current_playing())


class GeneratePreferencesFromTopTracksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        spotify = get_spotify_instance(user)
        top_tracks = spotify.get_top_tracks(limit=10)

        if not top_tracks or "items" not in top_tracks:
            return Response({"error": "No top tracks found"}, status=400)

        genre_vectors = extract_genre_vectors(spotify, top_tracks["items"])
        saved_vectors = save_preferences(user, genre_vectors)

        return Response({"message": "Preferences updated", "vectors": saved_vectors})


class AudioFeaturesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, track_id):
        token = request.user.spotify_access_token
        if not token:
            return Response({"error": "Brak access tokena"}, status=401)

        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.spotify.com/v1/audio-features/{track_id}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Nie udało się pobrać danych"}, status=response.status_code)

        return Response(response.json())

class AddTrackToQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        track_uri = request.data.get("track_uri")
        if not track_uri:
            return Response({"error": "Missing track_uri"}, status=400)

        spotify = get_spotify_instance(request.user)
        success, error = spotify.add_to_queue(track_uri)

        if success:
            return Response({"message": "Track added to queue"}, status=200)
        else:
            return Response({"error": "Failed to add track to queue", "details": error}, status=400)
