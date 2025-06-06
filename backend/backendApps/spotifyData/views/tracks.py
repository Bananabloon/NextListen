from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
import requests
from constants import SPOTIFY_SEARCH_URL
from .views_helpers import SpotifyBaseView
from difflib import SequenceMatcher

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


from difflib import SequenceMatcher

class SpotifySearchView(SpotifyBaseView):
    @extend_schema(
        summary="Search tracks or artists",
        description="Search on Spotify.",
        parameters=[
            OpenApiParameter(name="q", required=True, description="Search phrase", type=str),
            OpenApiParameter(name="type", required=False, description="Search type: track or artist", type=str),
            OpenApiParameter(name="artist", required=False, description="Artist name (optional, improves accuracy)", type=str),
        ],
    )
    def get(self, request):
        query = request.query_params.get("q")
        search_type = request.query_params.get("type", "track")
        artist_filter = request.query_params.get("artist")

        if not query or search_type not in ["track", "artist"]:
            return Response({"error": "Invalid query or type"}, status=400)

        token = request.user.spotify_access_token
        headers = {"Authorization": f"Bearer {token}"}

        if search_type == "artist":
            query = f'artist:"{query}"'
        elif search_type == "track":
            query_parts = [f'track:"{query}"']
            if artist_filter:
                query_parts.append(f'artist:"{artist_filter}"')
            query = " ".join(query_parts)

        params = {"q": query, "type": search_type, "limit": 20}

        response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)
        if response.status_code != 200:
            return Response({"error": "Spotify API error"}, status=response.status_code)

        data = response.json()

        if search_type == "track" and "tracks" in data:
            original_query = request.query_params.get("q", "").lower()

            def similarity_score(track):
                name = track.get("name", "").lower()
                return SequenceMatcher(None, name, original_query).ratio()

            sorted_items = sorted(data["tracks"]["items"], key=similarity_score, reverse=True)
            data["tracks"]["items"] = sorted_items

        return Response(data)
    
class TransferPlaybackView(SpotifyBaseView):
    @extend_schema(
        summary="Transfer playback",
        description="Switch Spotify playback to selected device. Pauses current playback first.",
        request={"application/json": {"example": {"device_id": "abc123"}}},
    )
    def post(self, request):
        (device_id,) = self.require_fields(request.data, ["device_id"])
        
        paused, pause_response = self.spotify.pause_playback()
        if not paused:
            return Response({"error": "Failed to pause playback", "detail": pause_response}, status=400)
        
        success, transfer_response = self.spotify.transfer_playback(device_id)
        if not success:
            return Response({"error": "Failed to transfer playback", "detail": transfer_response}, status=400)

        return self.respond_action(True, transfer_response, message="Playback transferred successfully")

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
