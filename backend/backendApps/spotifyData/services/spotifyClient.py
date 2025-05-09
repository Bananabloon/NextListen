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
        r = requests.get(url, headers=self.headers)
        print(f"Zapytanie: {url}")
        print("Odpowiedź status:", r.status_code)
        print("Odpowiedź JSON:", r.json())  # Debugowanie
        if r.status_code == 401 and self.refresh_token:
            print("Access token expired, attempting refresh...")
            self.refresh_access_token()
            r = requests.get(url, headers=self.headers)  
        return r.json()
    
    def get_user_profile(self):
        return self._get("/me")

    def get_top_tracks(self):
        return self._get("/me/top/tracks")

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
