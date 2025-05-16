from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import redirect

from rest_framework.views import APIView
from rest_framework.response import Response

from authentication.services.spotify_service import SpotifyService
from authentication.services.spotify_auth_service import SpotifyAuthService

class SpotifyLoginView(APIView):
    def post(self, request):
        spotify_access_token = request.data.get("access_token")
        if not spotify_access_token:
            return Response({"error": "spotify_access_token required"}, status=400)

        data, error = SpotifyAuthService.authenticate_spotify_user(spotify_access_token)
        if error:
            return error
        return Response(data)

class SpotifyOAuthRedirectView(APIView):
    def get(self, request):
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": (
                "user-read-email user-read-private user-top-read user-read-playback-state "
                "user-modify-playback-state user-read-currently-playing user-read-recently-played"
            )
        }
        url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        return redirect(url)

class SpotifyCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        token_data = SpotifyService.exchange_code_for_token(code)
        if not token_data:
            return Response({"error": "Failed to get access token"}, status=400)

        spotify_access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        data, error = SpotifyAuthService.authenticate_spotify_user(spotify_access_token, refresh_token)
        if error:
            return error
        return Response(data)
