from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..services.spotifyClient import SpotifyAPI
import os
import json
import random
from django.conf import settings

GENRE_FILE_PATH = os.path.join(settings.BASE_DIR, "genres.json")


class DiscoveryGenresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        count = int(request.query_params.get("count", 5))
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

        top_artists = spotify.get_top_artists(limit=20)
        user_genres = set()
        for artist in top_artists.get("items", []):
            user_genres.update(artist.get("genres", []))

        with open(GENRE_FILE_PATH, "r", encoding="utf-8") as f:
            all_genres = json.load(f)

        available_genres = [
            g["category"] for g in all_genres if g["category"] not in user_genres
        ]

        if not available_genres:
            return Response({"message": "No new genres to discover"}, status=200)

        weighted_genres = sorted(
            [g for g in all_genres if g["category"] in available_genres],
            key=lambda x: x["popularity"],
            reverse=True,
        )

        random_genres = random.sample(weighted_genres, min(count, len(weighted_genres)))
        result = [g["category"] for g in random_genres]

        return Response({"genres": result})
