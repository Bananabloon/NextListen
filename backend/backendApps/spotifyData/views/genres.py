from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.conf import settings
import os
import json
import random
from .views_helpers import SpotifyBaseView
from .serializers import DiscoveryGenresResponseSerializer

GENRE_FILE_PATH = os.path.join(settings.BASE_DIR, "genres.json")


class DiscoveryGenresView(SpotifyBaseView):
    @extend_schema(
        summary="Get discovery genres",
        description=(
            "Returns a list of music genres for discovery, excluding genres the user already listens to. "
            "Genres are selected based on popularity and can be limited with the 'count' query parameter."
        ),
        parameters=[
            OpenApiParameter(
                name="count",
                type=int,
                required=False,
                description="Number of genres to return (default: 5)",
            )
        ],
        responses=DiscoveryGenresResponseSerializer,
    )
    def get(self, request):
        count = self.get_count_param(request)
        user_genres = self.get_user_genres(self.spotify)
        all_genres = self.load_all_genres()

        available_genres = self.filter_genres(all_genres, user_genres)
        if not available_genres:
            return Response({"genres": []})

        selected_genres = self.select_genres_by_popularity(available_genres, count)
        return Response({"genres": selected_genres})

    def get_count_param(self, request):
        try:
            count = int(request.query_params.get("count", 5))
            return max(1, count)
        except (ValueError, TypeError):
            return 5

    def get_user_genres(self, spotify):
        top_artists = spotify.get_top_artists(limit=20)
        genres = set()
        for artist in top_artists.get("items", []):
            genres.update(artist.get("genres", []))
        return genres

    def load_all_genres(self):
        with open(GENRE_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def filter_genres(self, all_genres, user_genres):
        return [g for g in all_genres if g["category"] not in user_genres]

    def select_genres_by_popularity(self, genres, count):
        sorted_genres = sorted(genres, key=lambda g: g["popularity"], reverse=True)
        chosen = random.sample(sorted_genres, min(count, len(sorted_genres)))
        return [g["category"] for g in chosen]
