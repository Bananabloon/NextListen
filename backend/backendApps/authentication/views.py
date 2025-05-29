from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authentication.services.spotify_service import SpotifyService
from authentication.services.spotify_auth_service import SpotifyAuthService

from constants import SPOTIFY_AUTHORIZE_URL

class SpotifyOAuthRedirectView(APIView):
    def get(self, request):
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
           "scope": (
                "streaming user-read-email user-read-private user-top-read user-read-playback-state "
                "user-modify-playback-state user-read-currently-playing user-read-recently-played playlist-read-private playlist-modify-private"
            )
        }
        url = f"{SPOTIFY_AUTHORIZE_URL}?{urlencode(params)}" 
        return redirect(url)

from rest_framework.response import Response

class SpotifyCallbackView(APIView): #możliwe, że refaktoryzacja, oddzielenie przesyłania JWT
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        token_data = SpotifyService.exchange_code_for_token(code)
        if not token_data:
            return Response({"error": "Failed to get access token"}, status=400)

        spotify_access_token = token_data.get("access_token")
        spotify_refresh_token = token_data.get("refresh_token")

        data, error = SpotifyAuthService.authenticate_spotify_user(spotify_access_token, spotify_refresh_token)
        if error:
            return error
        
        response = redirect(f"{settings.NGROK_URL}/callback")

        response.set_cookie(
            key='NextListen_access_token',
            value=data['access'],
            httponly=True,
            secure=True,
            max_age=1800,
            samesite='Lax', 
            path='/',

        )
        response.set_cookie(
            key='NextListen_refresh_token',
            value=data['refresh'],
            httponly=True,
            secure=True,
            max_age=7*24*1800,
            samesite='Lax',
            path='/',

        )

        return response
    
    from rest_framework.views import APIView
from rest_framework.response import Response


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated!", "user": request.user.username})
