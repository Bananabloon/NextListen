from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import PreferenceVector
from users.serializers import PreferenceVectorSerializer
from .services.spotifyClient import SpotifyAPI
from django.db.models import JSONField
from django.db import models
import numpy as np
from collections import defaultdict
from .services.qdrantService import upload_user_preference, create_genre_collection  
from qdrant_client.http.exceptions import UnexpectedResponse
import requests

FEATURE_KEYS = ["danceability", "energy", "valence", "tempo"]

class CurrentUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.user.spotifyAccessToken
        refresh = request.user.spotifyRefreshToken
        data = SpotifyAPI(token, refresh_token=refresh, user=request.user).get_user_profile()
        return Response(data)

class TopTracksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.user.spotifyAccessToken
        refresh = request.user.spotifyRefreshToken
        data = SpotifyAPI(token, refresh_token=refresh, user=request.user).get_top_tracks()
        return Response(data)

class CurrentlyPlayingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.user.spotifyAccessToken
        refresh = request.user.spotifyRefreshToken
        data = SpotifyAPI(token, refresh_token=refresh, user=request.user).get_current_playing()
        return Response(data)

class GeneratePreferencesFromTopTracksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        token = user.spotifyAccessToken
        refresh = user.spotifyRefreshToken

        spotify = SpotifyAPI(token, refresh_token=refresh, user=user)
        top_tracks = spotify.get_top_tracks(10)

        if not top_tracks or "items" not in top_tracks:
            return Response({"error": "No top tracks found"}, status=400)

        genre_vectors = defaultdict(list)

        for track in top_tracks["items"]:
            track_id = track["id"]
            artists = track["artists"]
            artist_id = artists[0]["id"]

            print(f"Pobieram dane dla artysty: {artist_id}")
            artist_data = spotify.get_artist(artist_id)
            print(f"Genres dla {artist_data.get('name')}: {artist_data.get('genres', [])}")
            genres = artist_data.get("genres", [])
            if not genres:
                genres = ["unknown"]

            print(f"Utwór: {track['name']} | Artysta: {artists[0]['name']} | Gatunki: {genres}")  # Debugowanie

            if not genres:
                print(f"Brak gatunków dla {track['name']} ({artist_id})")
                continue

            audio_features = spotify.get_audio_features(track_id)
            print(f"Utwór: {track['name']} | Audio Features: {audio_features}") # Debugowanie
            if not audio_features:
                continue

            feature_vector = {
                k: audio_features.get(k, 0.0)  
                for k in FEATURE_KEYS
                if k in audio_features
            }

            for genre in genres:
                genre_vectors[genre].append(feature_vector)

        result = []
        for genre, vectors in genre_vectors.items():
            if not vectors:
                continue
            if "error" in audio_features:
                continue
            averaged = {
                k: float(np.mean([v[k] for v in vectors])) for k in FEATURE_KEYS
            }

            vector_obj, _ = PreferenceVector.objects.update_or_create(
                user=user,
                genreName=genre,
                defaults={"preferences": averaged}
            )

            try:
                create_genre_collection(genre)
            except UnexpectedResponse:
                pass 

            upload_user_preference(user.id, genre, averaged)

            result.append(PreferenceVectorSerializer(vector_obj).data)
    
        return Response({"message": "Preferences updated", "vectors": result})
    
class AudioFeaturesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, track_id):
        access_token = request.user.spotifyAccessToken  # Pobranie tokena użytkownika

        if not access_token:
            return Response({"error": "Brak access tokena"}, status=401)

        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.spotify.com/v1/audio-features/{track_id}"

        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return Response({"error": "Nie udało się pobrać danych"}, status=response.status_code)

        return Response(response.json())
