from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ..services.spotifyClient import SpotifyAPI
from .serializers import SpotifyProfileSerializer, SpotifyTokenSerializer


def get_spotify_instance(user):
    return SpotifyAPI(
        access_token=user.spotify_access_token,
        refresh_token=user.spotify_refresh_token,
        user=user,
    )


class CurrentUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user's Spotify profile",
        description="Returns the Spotify profile information of the currently authenticated user.",
        responses=SpotifyProfileSerializer,
    )
    def get(self, request):
        spotify = get_spotify_instance(request.user)
        profile_data = spotify.get_user_profile()
        return Response(profile_data)


class SpotifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user's Spotify access token",
        description="Returns the current Spotify access token for the authenticated user.",
        responses=SpotifyTokenSerializer,
    )
    def get(self, request):
        spotify = get_spotify_instance(request.user)
        token = spotify.get_access_token()
        return Response({"access_token": token})
