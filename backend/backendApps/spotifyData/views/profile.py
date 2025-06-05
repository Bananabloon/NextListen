from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .views_helpers import SpotifyBaseView
from .serializers import SpotifyProfileSerializer, SpotifyTokenSerializer


class CurrentUserProfileView(SpotifyBaseView):
    @extend_schema(
        summary="Get current user's Spotify profile",
        description="Returns the Spotify profile information of the currently authenticated user.",
        responses=SpotifyProfileSerializer,
    )
    def get(self, request):
        return Response(self.spotify.get_user_profile())


class SpotifyTokenView(SpotifyBaseView):
    @extend_schema(
        summary="Get current user's Spotify access token",
        description="Returns the current Spotify access token for the authenticated user.",
        responses=SpotifyTokenSerializer,
    )
    def get(self, request):
        return Response({"access_token": self.spotify.get_access_token()})
