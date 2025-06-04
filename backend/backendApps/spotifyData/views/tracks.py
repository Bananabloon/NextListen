from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from drf_spectacular.utils import extend_schema
from .profile import get_spotify_instance
from constants import SPOTIFY_SEARCH_URL


class SpotifyBaseView(APIView):
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.spotify = get_spotify_instance(request.user)


class TopTracksView(SpotifyBaseView):
    @extend_schema(
        summary="Get user's top tracks",
        description="Returns a list of the user's most listened tracks on Spotify.",
    )
    def get(self, request):
        return Response(self.spotify.get_top_tracks())


class TopArtistsView(SpotifyBaseView):
    @extend_schema(
        summary="Get user's top artists",
        description="Returns a list of the user's most listened artists on Spotify.",
    )
    def get(self, request):
        return Response(self.spotify.get_top_artists())


class CurrentlyPlayingView(SpotifyBaseView):
    @extend_schema(
        summary="Get currently playing track",
        description="Returns information about the track currently playing on Spotify.",
    )
    def get(self, request):
        return Response(self.spotify.get_current_playing())


class AddTrackToQueueView(SpotifyBaseView):
    @extend_schema(
        summary="Add track to queue",
        description="Adds the specified track to the user's Spotify playback queue.",
        request={"application/json": {"example": {"track_uri": "spotify:track:xyz"}}},
    )
    def post(self, request):
        track_uri = request.data.get("track_uri")
        if not track_uri:
            return Response({"error": "Missing track_uri"}, status=400)

        success, error = self.spotify.add_to_queue(track_uri)
        if success:
            return Response({"message": "Track added to queue"})
        return Response(
            {"error": "Failed to add track to queue", "details": error}, status=400
        )


class SpotifySearchView(SpotifyBaseView):
    @extend_schema(
        summary="Search tracks or artists",
        description="Searches for tracks or artists on Spotify based on a text query.",
        parameters=[
            {
                "name": "q",
                "required": True,
                "description": "Search phrase",
                "in": "query",
                "type": "string",
            },
            {
                "name": "type",
                "required": False,
                "description": "Search type: track or artist",
                "in": "query",
                "type": "string",
            },
        ],
    )
    def get(self, request):
        query = request.query_params.get("q")
        search_type = request.query_params.get("type", "track")

        if not query or search_type not in ["track", "artist"]:
            return Response({"error": "Invalid query or type"}, status=400)

        token = request.user.spotify_access_token
        params = {"q": query, "type": search_type, "limit": 10}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)

        if response.status_code != 200:
            return Response({"error": "Spotify API error"}, status=response.status_code)

        return Response(response.json())


class TransferPlaybackView(SpotifyBaseView):
    @extend_schema(
        summary="Transfer playback",
        description="Transfers playback to the selected Spotify device.",
        request={"application/json": {"example": {"device_id": "abc123"}}},
    )
    def post(self, request):
        device_id = request.data.get("device_id")
        if not device_id:
            return Response({"error": "Missing device_id"}, status=400)

        success, error = self.spotify.transfer_playback(device_id)
        if success:
            return Response({"message": "Playback transferred successfully"})
        return Response(
            {"error": "Failed to transfer playback", "details": error}, status=400
        )


class StartPlaybackView(SpotifyBaseView):
    @extend_schema(
        summary="Start playback of a track",
        description="Starts playback of the selected track on the specified Spotify device.",
        request={
            "application/json": {
                "example": {"device_id": "abc123", "track_uri": "spotify:track:xyz"}
            }
        },
    )
    def post(self, request):
        device_id = request.data.get("device_id")
        track_uri = request.data.get("track_uri")

        if not device_id or not track_uri:
            return Response({"error": "Missing device_id or track_uri"}, status=400)

        success, error = self.spotify.start_playback(device_id, track_uri)
        if success:
            return Response({"message": "Playback started"})
        return Response(
            {"error": "Failed to start playback", "details": error}, status=400
        )
