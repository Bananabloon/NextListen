from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from .views_helpers import SpotifyBaseView
from .serializers import LikeTrackSerializer, RemoveLikedTrackSerializer


def parse_spotify_uris_to_ids(uris_string):
    uris = [u.strip() for u in uris_string.split(",") if u.strip()]
    ids = []
    for uri in uris:
        if uri.startswith("spotify:track:"):
            ids.append(uri.split(":")[-1])
        else:
            ids.append(uri)
    return ids


class LikedTracksView(SpotifyBaseView):
    @extend_schema(
        summary="Get user's saved tracks",
        description="Returns a list of tracks saved by the current user on Spotify.",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                required=False,
                description="Number of tracks to return (default: 20)",
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                required=False,
                description="Offset for pagination (default: 0)",
            ),
        ],
    )
    def get(self, request):
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))
        return Response(self.spotify.get_liked_tracks(limit=limit, offset=offset))


class LikeTrackView(SpotifyBaseView):
    @extend_schema(
        summary="Save a track",
        description="Adds a track to the user's saved tracks on Spotify.",
        request=LikeTrackSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = LikeTrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        track_uri = serializer.validated_data["track_uri"]
        track_id = parse_spotify_uris_to_ids(track_uri)[0]
        self.spotify.like_track(track_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveLikedTrackView(SpotifyBaseView):
    @extend_schema(
        summary="Remove a track from saved tracks",
        description="Removes a track from the user's saved tracks on Spotify.",
        request=RemoveLikedTrackSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = RemoveLikedTrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        track_uri = serializer.validated_data["track_uri"]
        track_id = parse_spotify_uris_to_ids(track_uri)[0]
        self.spotify.remove_liked_track(track_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AreTracksLikedView(SpotifyBaseView):
    @extend_schema(
        summary="Check if track(s) are saved",
        description="Checks if given track URIs or IDs are saved by the current user on Spotify.",
        parameters=[
            OpenApiParameter(
                name="uris",
                type=str,
                required=True,
                description="Comma-separated list of Spotify track URIs or IDs (max 50)",
            ),
        ],
        responses={200: None},
    )
    def get(self, request):
        uris = request.query_params.get("uris")
        if not uris:
            return Response(
                {"error": "Missing 'uris' query parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        id_list = parse_spotify_uris_to_ids(uris)
        ids_param = ",".join(id_list)
        result = self.spotify.are_tracks_liked(ids_param)
        uri_list = [u.strip() for u in uris.split(",") if u.strip()]
        liked_map = {uri: liked for uri, liked in zip(uri_list, result)}
        return Response(liked_map)
