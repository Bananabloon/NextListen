from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .spotify_service import SpotifyService
from .user_service import UserService
from .token_service import TokenService

class SpotifyAuthService:
    @staticmethod
    def authenticate_spotify_user(spotify_access_token, spotify_refresh_token):
        user_info = SpotifyService.get_user_info(spotify_access_token)
        if not user_info:
            return None, Response({"error": "Invalid Spotify token"}, status=401)

     
        user = UserService.create_or_update_user(user_info, spotify_access_token, spotify_refresh_token)
        tokens = TokenService.generate_tokens_for_user(user)

        return tokens, None
