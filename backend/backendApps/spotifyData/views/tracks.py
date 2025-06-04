from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from .profile import get_spotify_instance
import sys
sys.path.append("..")
from constants import SPOTIFY_SEARCH_URL

sys.path.append("..")


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
        return Response(
            {"error": "Failed to add track to queue", "details": error}, status=400
        )


class SpotifySearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q")
        search_type = request.query_params.get("type", "track")

        if not query or search_type not in ["track", "artist"]:
            return Response({"error": "Invalid query or type"}, status=400)

        token = request.user.spotify_access_token
        url = SPOTIFY_SEARCH_URL
        params = {"q": query, "type": search_type, "limit": 10}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return Response({"error": "Spotify API error"}, status=response.status_code)

        return Response(response.json())

class TransferPlaybackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get("device_id")
        if not device_id:
            return Response({"error": "Missing device_id"}, status=400)

        spotify = get_spotify_instance(request.user)
        success, error = spotify.transfer_playback(device_id)
        if success:
            return Response({"message": "Playback transferred successfully"})
        return Response({"error": "Failed to transfer playback", "details": error}, status=400)


class StartPlaybackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        device_id = request.data.get("device_id")
        track_uri = request.data.get("track_uri")

        if not device_id or not track_uri:
            return Response({"error": "Missing device_id or track_uri"}, status=400)

        spotify = get_spotify_instance(request.user)
        success, error = spotify.start_playback(device_id, track_uri)
        if success:
            return Response({"message": "Playback started"})
        return Response({"error": "Failed to start playback", "details": error}, status=400)
