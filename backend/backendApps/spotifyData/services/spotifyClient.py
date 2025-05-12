import requests
from django.contrib.auth import get_user_model

User = get_user_model()
import requests
class SpotifyAPI:
    def __init__(self, access_token, refresh_token=None, user=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user = user
        self.base_url = "https://api.spotify.com/v1"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def _get(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        print(f"[DEBUG] Wysyłam GET: {url}")
        print(f"[DEBUG] Authorization header: {self.headers.get('Authorization')}")

        try:
            response = requests.get(url, headers=self.headers)
            print(f"[DEBUG] Status odpowiedzi: {response.status_code}")
            print(f"[DEBUG] Raw response: {response.text}")  # <-- RĘCZNY print treści odpowiedzi

            if response.status_code == 401 and self.refresh_token:
                print("[DEBUG] Token wygasł. Odświeżam...")
                self.refresh_access_token()
                response = requests.get(url, headers=self.headers)
                print(f"[DEBUG] Retry status: {response.status_code}")
                print(f"[DEBUG] Retry response: {response.text}")

            try:
                json_data = response.json()
            except ValueError:
                print("[ERROR] Niepoprawny JSON w odpowiedzi.")
                return {"error": "Invalid JSON response"}

            if response.status_code >= 400:
                print(f"[ERROR] Błąd HTTP {response.status_code}: {json_data}")

            return json_data

        except requests.RequestException as e:
            print(f"[ERROR] Wyjątek przy zapytaniu: {e}")
            return {"error": str(e)}

    def get_user_profile(self):
        return self._get("/me")

    def get_top_tracks(self, limit=10):
        return self._get(f"/me/top/tracks?limit={limit}")

    def get_current_playing(self):
        return self._get("/me/player/currently-playing")
    
    def refresh_access_token(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": "<YOUR_CLIENT_ID>",
            "client_secret": "<YOUR_CLIENT_SECRET>",
        }
        response = requests.post("https://accounts.spotify.com/api/token", data=data)
        print("Response status:", response.status_code)
        print("Response JSON:", response.json())  # Debugowanie
        token_data = response.json() 
        self.access_token = token_data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        
        if self.user:
            self.user.spotifyAccessToken = self.access_token
            self.user.save()

    def get_artist(self, artist_id):
        endpoint = f"/artists/{artist_id}" 
        return self._get(endpoint)


    def get_audio_features(self, track_id):
        print(f"[DEBUG] Pobieram audio features dla track_id: {track_id}")
        print(f"[DEBUG] Obecne nagłówki: {self.headers}") 
        return self._get(f"/audio-features/{track_id}")
