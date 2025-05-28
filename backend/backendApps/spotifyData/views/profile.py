from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..services.spotifyClient import SpotifyAPI

def get_spotify_instance(user):
    return SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

class CurrentUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spotify = get_spotify_instance(request.user)
        return Response(spotify.get_user_profile())
    
class SpotifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spotify = SpotifyAPI(
            access_token=request.user.spotify_access_token,
            refresh_token=request.user.spotify_refresh_token,
            user=request.user
        )
        token = spotify.get_access_token()
        return Response({"access_token": token})
