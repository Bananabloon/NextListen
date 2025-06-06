from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from .views_helpers import SpotifyBaseView
from .serializers import LikeTrackSerializer, RemoveLikedTrackSerializer


class LikedTracksView(SpotifyBaseView):
    @extend_schema(
        summary="Get user's liked tracks",
        description="Returns a list of tracks liked by the current user on Spotify.",
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
        summary="Like a track",
        description="Adds a track to the user's liked tracks on Spotify.",
        request=LikeTrackSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = LikeTrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        track_id = serializer.validated_data["track_id"]
        self.spotify.like_track(track_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveLikedTrackView(SpotifyBaseView):
    @extend_schema(
        summary="Remove a track from liked tracks",
        description="Removes a track from the user's liked tracks on Spotify.",
        request=RemoveLikedTrackSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = RemoveLikedTrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        track_id = serializer.validated_data["track_id"]
        self.spotify.remove_liked_track(track_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
