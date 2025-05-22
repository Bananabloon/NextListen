import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class SpotifyService:
    @staticmethod
    def exchange_code_for_token(code: str):
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post("https://accounts.spotify.com/api/token", data=payload, headers=headers)
        if response.status_code != 200:
            logger.error("Failed token exchange: %s", response.text)
            return None
        return response.json()

    @staticmethod
    def get_user_info(spotify_access_token: str):
        response = requests.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {spotify_access_token}"}
        )
        if response.status_code != 200:
            logger.error("Failed to fetch user profile from Spotify.")
            return None
        return response.json()

    @staticmethod
    def get_top_artists(access_token: str): #to też nie powinno tutaj być raczej
        url = "https://api.spotify.com/v1/me/top/artists?limit=50"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch top artists: {response.status_code} {response.text}")
            return []
        data = response.json()
        return data.get("items", [])
