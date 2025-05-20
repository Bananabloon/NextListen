import requests
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
import sys
sys.path.append("..")
from constants import SPOTIFY_PROFILE_URL, SPOTIFY_TOKEN_URL, SPOTIFY_QUEUE_URL

class SpotifyAPI:
    BASE_URL = SPOTIFY_PROFILE_URL
    TOKEN_URL = SPOTIFY_TOKEN_URL

    def __init__(self, access_token, refresh_token=None, user=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user = user
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def _get(self, endpoint: str):
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 401 and self.refresh_token:
            self._refresh_access_token()
            response = requests.get(url, headers=self.headers)

        try:
            return response.json()
        except Exception:
            return {"error": "Invalid JSON response from Spotify"}

    def _refresh_access_token(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        }

        response = requests.post(self.TOKEN_URL, data=data)
        if response.status_code != 200:
            raise Exception("Failed to refresh access token")

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

        if self.user:
            self.user.spotifyAccessToken = self.access_token
            self.user.save()

            

    def add_to_queue(self, track_uri):
        if not self.access_token:
            return False, {"error": "Missing access token"}

        url = SPOTIFY_QUEUE_URL
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"uri": track_uri}

        response = requests.post(url, headers=headers, params=params)

        if response.status_code in [200, 204]:
            return True, None
        try:
            return False, response.json()
        except Exception:
            return False, {"error": "Unexpected response", "status": response.status_code}


    def get_user_profile(self):
        return self._get("/me")

    def get_top_tracks(self, limit=50):
        return self._get(f"/me/top/tracks?limit={limit}")

    def get_top_artists(self, limit=20):
        return self._get(f"/me/top/artists?limit={limit}")

    def get_current_playing(self):
        return self._get("/me/player/currently-playing")

    def get_artist(self, artist_id: str):
        return self._get(f"/artists/{artist_id}")

    def get_audio_features(self, track_id: str):
        return self._get(f"/audio-features/{track_id}")

    def search(self, query, type="track", limit=1):
        url = f"{self.BASE_URL}/search"
        params = {
            "q": query,
            "type": type,
            "limit": limit
        }
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 401 and self.refresh_token:
            self._refresh_access_token()
            response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            return {"error": f"Spotify API error: {response.status_code}", "response": response.text}

        return response.json()
