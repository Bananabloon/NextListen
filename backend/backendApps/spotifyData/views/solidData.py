from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .views_helpers import SpotifyBaseView


class GetArtistView(SpotifyBaseView):
    @extend_schema(
        summary="Get artist info by ID",
        description="Fetches artist details based on Spotify artist ID.",
        parameters=[
            OpenApiParameter(
                "artist_id",
                str,
                required=True,
                description="Spotify artist ID (e.g. 1tpXaFzQmEtgy8kSXWbZVr)",
            )
        ],
        responses={200: None},
    )
    def get(self, request):
        artist_id = request.query_params.get("artist_id")
        if not artist_id:
            return Response(
                {"error": "artist_id query parameter is required"}, status=400
            )

        artist_data = self.spotify.get_artist(artist_id)
        if "error" in artist_data:
            return Response(
                {"error": "Failed to fetch artist", "details": artist_data}, status=400
            )

        return Response(artist_data)
