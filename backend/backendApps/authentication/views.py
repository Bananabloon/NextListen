from django.conf import settings
from django.shortcuts import redirect
from urllib.parse import urlencode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework.request import Request

from users.models import User

class SpotifyLoginView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "access_token required"}, status=400)

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)

        if response.status_code != 200:
            return Response({"error": "Invalid Spotify token"}, status=401)

        profile = response.json()
        spotify_id = profile["id"]
        display_name = profile.get("display_name", "Unknown")

        user, created = User.objects.get_or_create(
            spotifyUserId=spotify_id,
            defaults={"displayName": display_name}
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "spotifyUserId": user.spotifyUserId,
                "displayName": user.displayName
            }
        })

class SpotifyOAuthRedirectView(APIView):
    def get(self, request):
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": "user-read-email user-read-private",
        }
        url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        return redirect(url)
    
class SpotifyCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post("https://accounts.spotify.com/api/token", data=payload, headers=headers)
        print(response.status_code, response.json()) #Debug
        if response.status_code != 200:
            return Response({"error": "Failed to get access token"}, status=400)

        access_token = response.json()["access_token"]

        fake_request = Request(request._request)
        fake_request._full_data = {"access_token": access_token}
        return SpotifyLoginView().post(fake_request)
    
    


