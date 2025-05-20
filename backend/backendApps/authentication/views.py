import logging
import requests
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone

from ..constants import SPOTIFY_PROFILE_URL, SPOTIFY_TOP_ARTISTS_URL, SPOTIFY_AUTHORIZE_URL, SPOTIFY_TOKEN_URL

from users.models import Artist
from users.models import User

logger = logging.getLogger(__name__)

class SpotifyLoginView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "access_token required"}, status=400)

        user_info = self._get_user_profile(access_token)
        if user_info is None:
            return Response({"error": "Invalid Spotify token"}, status=401)

        spotify_id = user_info["id"]
        display_name = user_info.get("display_name", "Unknown")

        user, _ = User.objects.get_or_create(
            spotify_user_id=spotify_id,
            defaults={"display_name": display_name}
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "spotify_user_id": user.spotify_user_id,
                "display_name": user.display_name
            }
        })

    def _get_user_profile(self, access_token):
        response = requests.get(
            SPOTIFY_PROFILE_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            logger.warning("Spotify token invalid or expired.")
            return None
        return response.json()


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
        url = f"{SPOTIFY_AUTHORIZE_URL}?{urlencode(params)}"
        return redirect(url)


class SpotifyCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        token_data = self._exchange_code_for_token(code)
        if not token_data:
            return Response({"error": "Failed to get access token"}, status=400)

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")

        user_info = self._get_user_info(access_token)
        if not user_info:
            return Response({"error": "Failed to fetch user info"}, status=400)

        user = self._create_or_update_user(user_info, access_token, refresh_token)

        fake_request = Request(request._request)
        fake_request._full_data = {"access_token": access_token}
        return SpotifyLoginView().post(fake_request)

    def _exchange_code_for_token(self, code):
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=headers)

        if response.status_code != 200:
            logger.error("Failed token exchange: %s", response.text)
            return None

        return response.json()

    def _get_user_info(self, access_token):
        response = requests.get(
            SPOTIFY_PROFILE_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            logger.error("Failed to fetch user profile from Spotify.")
            return None
        return response.json()


    def _create_or_update_user(self, user_info, access_token, refresh_token):
        spotify_user_id = user_info["id"]
        display_name = user_info.get("display_name", "Unknown")

        user, _ = User.objects.get_or_create(spotify_user_id=spotify_user_id)
        user.display_name = display_name
        user.spotify_access_token = access_token
        user.market = user_info.get("country")

        if refresh_token:
            user.spotify_refresh_token = refresh_token

        now = timezone.now()

        if not user.last_updated or now - user.last_updated > timedelta(days=1):
            logger.info(f"Fetching top artists for user {user.display_name}")
            self.fetch_and_update_top_artists(user, access_token)
            user.last_updated = now
        else:
            logger.info(f"Skipping top artist update for {user.display_name}: updated less than 24h ago")

        user.save()
        return user


    def fetch_and_update_top_artists(self, user, access_token):
        url = SPOTIFY_TOP_ARTISTS_URL
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Failed to fetch top artists: {response.status_code} {response.text}")
            return

        data = response.json()
        artists = data.get("items", [])

        Artist.objects.filter(user=user).delete()

        for _, artist in enumerate(artists, start=1):
            Artist.objects.create(
                user=user,
                name=artist["name"],
                spotify_uri=artist["uri"],
            )
