from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
import requests
from constants import SPOTIFY_SEARCH_URL
from .views_helpers import SpotifyBaseView


class TopTracksView(SpotifyBaseView):
    @extend_schema(summary="Get user's top tracks", description="Most listened tracks.")
    def get(self, request):
        return Response(self.spotify.get_top_tracks())


class TopArtistsView(SpotifyBaseView):
    @extend_schema(
        summary="Get user's top artists", description="Most listened artists."
    )
    def get(self, request):
        return Response(self.spotify.get_top_artists())


class CurrentlyPlayingView(SpotifyBaseView):
    @extend_schema(
        summary="Get currently playing track", description="Track currently playing."
    )
    def get(self, request):
        return Response(self.spotify.get_current_playing())


class AddTrackToQueueView(SpotifyBaseView):
    @extend_schema(
        summary="Add track to queue",
        description="Adds a track to the user's Spotify queue.",
        request={"application/json": {"example": {"track_uri": "spotify:track:xyz"}}},
    )
    def post(self, request):
        (track_uri,) = self.require_fields(request.data, ["track_uri"])
        return self.respond_action(
            *self.spotify.add_to_queue(track_uri), message="Track added to queue"
        )


class SpotifySearchView(SpotifyBaseView):
    @extend_schema(
        summary="Search tracks or artists",
        description="Search on Spotify.",
        parameters=[
            OpenApiParameter(
                name="q", required=True, description="Search phrase", type=str
            ),
            OpenApiParameter(
                name="type",
                required=False,
                description="Search type: track or artist",
                type=str,
            ),
        ],
    )
    def get(self, request):
        query = request.query_params.get("q")
        search_type = request.query_params.get("type", "track")

        if not query or search_type not in ["track", "artist"]:
            return Response({"error": "Invalid query or type"}, status=400)

        token = request.user.spotify_access_token
        headers = {"Authorization": f"Bearer {token}"}
        params = {"q": query, "type": search_type, "limit": 10}

        response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)
        if response.status_code != 200:
            return Response({"error": "Spotify API error"}, status=response.status_code)

        return Response(response.json())


class TransferPlaybackView(SpotifyBaseView):
    @extend_schema(
        summary="Transfer playback",
        description="Switch Spotify playback to selected device.",
        request={"application/json": {"example": {"device_id": "abc123"}}},
    )
    def post(self, request):
        (device_id,) = self.require_fields(request.data, ["device_id"])
        return self.respond_action(
            *self.spotify.transfer_playback(device_id),
            message="Playback transferred successfully",
        )


class StartPlaybackView(SpotifyBaseView):
    @extend_schema(
        summary="Start playback of a track",
        description="Starts playback on selected device.",
        request={
            "application/json": {
                "example": {"device_id": "abc123", "track_uri": "spotify:track:xyz"}
            }
        },
    )
    def post(self, request):
        device_id, track_uri = self.require_fields(
            request.data, ["device_id", "track_uri"]
        )
        return self.respond_action(
            *self.spotify.start_playback(device_id, track_uri),
            message="Playback started",
        )
