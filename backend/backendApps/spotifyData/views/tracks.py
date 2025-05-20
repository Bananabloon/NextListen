from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..services.spotifyClient import SpotifyAPI
import requests
from django.conf import settings
from .profile import get_spotify_instance

import sys
sys.path.append("..")
from constants import SPOTYFY_SEARCH_URL

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

# class AudioFeaturesView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, track_id):
#         token = request.user.spotify_access_token
#         headers = {"Authorization": f"Bearer {token}"}
#         url = f"https://api.spotify.com/v1/audio-features/{track_id}"
#         response = requests.get(url, headers=headers)

#         if response.status_code != 200:
#             return Response({"error": "Nie udało się pobrać danych"}, status=response.status_code)

#         return Response(response.json())

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
        return Response({"error": "Failed to add track to queue", "details": error}, status=400)

class SpotifySearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q")
        search_type = request.query_params.get("type", "track")

        if not query or search_type not in ["track", "artist"]:
            return Response({"error": "Invalid query or type"}, status=400)

        token = request.user.spotify_access_token
        url = SPOTYFY_SEARCH_URL
        params = {"q": query, "type": search_type, "limit": 10}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return Response({"error": "Spotify API error"}, status=response.status_code)

        return Response(response.json())
