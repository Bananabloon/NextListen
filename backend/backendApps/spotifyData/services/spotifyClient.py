import requests
from django.contrib.auth import get_user_model
from django.conf import settings
import sys
import time
import logging
logger = logging.getLogger(__name__)

from constants import SPOTIFY_API_BASE_URL, SPOTIFY_TOKEN_URL, SPOTIFY_QUEUE_URL

User = get_user_model()


sys.path.append("..")


class SpotifyAPI:
    BASE_URL = SPOTIFY_API_BASE_URL
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
            return False, {
                "error": "Unexpected response",
                "status": response.status_code,
            }

    def get_user_profile(self):
        return self._get("/me")

    def get_top_tracks(self, limit=50):
        return self._get(f"/me/top/tracks?limit={limit}")

    def get_top_artists(self, limit=20):
        return self._get(f"/me/top/artists?limit={limit}")

    def get_artist(self, endpoint: str):
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers)
        try:
            return response.json()
        except Exception:
            print("SPOTIFY RAW RESPONSE:", response.text)  # Dodaj to!
            return {
                "error": "Invalid JSON response from Spotify",
                "raw": response.text,
                "status": response.status_code,
            }

    def get_current_playing(self):
        return self._get("/me/player/currently-playing")

    def get_track(self, track_id):
        response = requests.get(
            f"https://api.spotify.com/v1/tracks/{track_id}", headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to get track info: {response.status_code} - {response.text}"
            )
        return response.json()

    def search(self, query, type="track", limit=1):
        url = f"{self.BASE_URL}/search"
        params = {"q": query, "type": type, "limit": limit}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 401 and self.refresh_token:
            self._refresh_access_token()
            response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            return {
                "error": f"Spotify API error: {response.status_code}",
                "response": response.text,
            }

        return response.json()

    def get_access_token(self):
        if not self.access_token:
            raise Exception("Brak access tokena.")

        return self.access_token

    def transfer_playback(self, device_id: str, play: bool = True):
        url = "https://api.spotify.com/v1/me/player"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"device_ids": [device_id], "play": play}
        response = requests.put(url, headers=headers, json=data)
        return response.status_code == 204, response.text

    def start_playback(self, device_id: str, track_uri: str):
        url = "https://api.spotify.com/v1/me/player/play"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"uris": [track_uri], "offset": {"position": 0}}
        params = {"device_id": device_id}
        response = requests.put(url, headers=headers, params=params, json=data)
        return response.status_code in [204, 202], response.text

    def pause_playback(self):
        url = f"{self.BASE_URL}/me/player/pause"
        response = requests.put(url, headers=self.headers)
        return response.status_code in [204, 202], response.text

    def get_several_tracks(self, track_ids):
        url = f"{self.BASE_URL}/tracks"
        params = {"ids": ",".join(track_ids)}

        for attempt in range(2):  
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                return response.json().get("tracks", [])

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                continue 

            if response.status_code == 401 and self.refresh_token:
                self._refresh_access_token()
                continue 

            raise Exception(f"Failed to get tracks info: {response.status_code} - {response.text}")

        raise Exception("Rate limited again or failed after retry")

    def get_liked_tracks(self, limit=20, offset=0):
        url = f"{self.BASE_URL}/me/tracks?limit={limit}&offset={offset}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return {
                "error": f"Spotify API error: {response.status_code}",
                "response": response.text,
            }

        return response.json()

    def like_track(self, track_id: str):
        url = f"{self.BASE_URL}/me/tracks"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"ids": [track_id]}
        requests.put(url, headers=headers, json=data)

    def remove_liked_track(self, track_id: str):
        url = f"{self.BASE_URL}/me/tracks"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"ids": [track_id]}
        requests.delete(url, headers=headers, json=data)
