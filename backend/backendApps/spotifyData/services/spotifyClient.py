import sys
import time
import logging
import requests

from django.contrib.auth import get_user_model
from django.conf import settings
from constants import SPOTIFY_API_BASE_URL, SPOTIFY_TOKEN_URL, SPOTIFY_QUEUE_URL

logger = logging.getLogger(__name__)
User = get_user_model()
sys.path.append("..")


class SpotifyAPI:
    BASE_URL = SPOTIFY_API_BASE_URL
    TOKEN_URL = SPOTIFY_TOKEN_URL

    def __init__(self, access_token, refresh_token=None, user=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user = user
        self._update_headers()

    def _update_headers(self):
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)

        if response.status_code == 401 and self.refresh_token:
            self._refresh_access_token()
            response = requests.request(method, url, headers=self.headers, **kwargs)

        return response

    def _get(self, endpoint, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def _put(self, endpoint, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def _delete(self, endpoint, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)

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
        self._update_headers()

        if self.user:
            self.user.spotifyAccessToken = self.access_token
            self.user.save()

    def get_user_profile(self):
        return self._get("/me").json()

    def get_top_tracks(self, limit=50):
        return self._get(f"/me/top/tracks?limit={limit}").json()

    def get_top_artists(self, limit=20):
        return self._get(f"/me/top/artists?limit={limit}").json()

    def get_artist(self, artist_id):
        return self._get(f"/artists/{artist_id}").json()

    def get_current_playing(self):
        return self._get("/me/player/currently-playing").json()

    def get_track(self, track_id):
        return self._get(f"/tracks/{track_id}").json()

    def search(self, query, type="track", limit=1):
        params = {"q": query, "type": type, "limit": limit}
        response = self._get("/search", params=params)

        if response.status_code != 200:
            return {
                "error": f"Spotify API error: {response.status_code}",
                "response": response.text,
            }

        return response.json()

    def get_several_tracks(self, track_ids):
        params = {"ids": ",".join(track_ids)}

        for attempt in range(2):
            response = self._get("/tracks", params=params)

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

    def add_to_queue(self, track_uri):
        params = {"uri": track_uri}
        response = requests.post(SPOTIFY_QUEUE_URL, headers=self.headers, params=params)

        if response.status_code in [200, 204]:
            return True, None

        try:
            return False, response.json()
        except Exception:
            return False, {"error": "Unexpected response", "status": response.status_code}

    def start_playback(self, device_id, track_uri):
        data = {"uris": [track_uri], "offset": {"position": 0}}
        params = {"device_id": device_id}
        response = self._put("/me/player/play", params=params, json=data)
        return response.status_code in [204, 202], response.text

    def transfer_playback(self, device_id, play=True):
        data = {"device_ids": [device_id], "play": play}
        response = self._put("/me/player", json=data)
        return response.status_code == 204, response.text

    def pause_playback(self):
        response = self._put("/me/player/pause")
        return response.status_code in [204, 202], response.text

    def get_liked_tracks(self, limit=20, offset=0):
        response = self._get(f"/me/tracks?limit={limit}&offset={offset}")
        if response.status_code != 200:
            return {
                "error": f"Spotify API error: {response.status_code}",
                "response": response.text,
            }
        return response.json()

    def like_track(self, track_id):
        data = {"ids": [track_id]}
        self._put("/me/tracks", json=data)

    def remove_liked_track(self, track_id):
        data = {"ids": [track_id]}
        self._delete("/me/tracks", json=data)

    def get_access_token(self):
        if not self.access_token:
            raise Exception("Brak access tokena.")
        return self.access_token
