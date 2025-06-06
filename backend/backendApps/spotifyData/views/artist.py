from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from .views_helpers import SpotifyBaseView

class ArtistInfoByUriView(SpotifyBaseView):
    @extend_schema(
        summary="Get artist info from URI",
        description="Fetches artist details based on Spotify artist URI.",
        request={"application/json": {"example": {"artist_uri": "spotify:artist:1tpXaFzQmEtgy8kSXWbZVr"}}},
    )
    def post(self, request):
        (artist_uri,) = self.require_fields(request.data, ["artist_uri"])

        try:
            artist_id = artist_uri.split(":")[2]
        except IndexError:
            return Response({"error": "Invalid artist URI"}, status=400)

        artist_data = self.spotify.get_artist(artist_id)

        if "error" in artist_data:
            return Response({"error": "Failed to fetch artist", "details": artist_data}, status=400)

        return Response(artist_data)
