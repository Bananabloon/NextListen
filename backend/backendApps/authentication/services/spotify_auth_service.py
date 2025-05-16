from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .spotify_service import SpotifyService
from .user_service import UserService

class SpotifyAuthService:
    @staticmethod
    def authenticate_spotify_user(spotify_access_token, refresh_token=None):
        user_info = SpotifyService.get_user_info(spotify_access_token)
        if not user_info:
            return None, Response({"error": "Invalid Spotify token"}, status=401)

     
        user = UserService.create_or_update_user(user_info, spotify_access_token, refresh_token)

        jwt_refresh_token = RefreshToken.for_user(user)
        jwt_access_token = jwt_refresh_token.access_token

        return {
            "access": str(jwt_access_token),
            "refresh": str(jwt_refresh_token),
            "user": {
                "id": user.id,
                "spotify_user_id": user.spotify_user_id,
                "display_name": user.display_name
            }
        }, None
