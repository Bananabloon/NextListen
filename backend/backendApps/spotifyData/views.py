from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services.spotifyClient import SpotifyAPI

class CurrentUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.user.spotifyAccessToken
        refresh = request.user.spotifyRefreshToken
        data = SpotifyAPI(token, refresh_token=refresh, user=request.user).get_user_profile()
        return Response(data)

class TopTracksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.user.spotifyAccessToken
        refresh = request.user.spotifyRefreshToken
        data = SpotifyAPI(token, refresh_token=refresh, user=request.user).get_top_tracks()
        return Response(data)

class CurrentlyPlayingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.user.spotifyAccessToken
        refresh = request.user.spotifyRefreshToken
        data = SpotifyAPI(token, refresh_token=refresh, user=request.user).get_current_playing()
        return Response(data)
