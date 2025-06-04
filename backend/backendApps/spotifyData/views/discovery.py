from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..services.spotifyClient import SpotifyAPI
from openai import OpenAI
from django.conf import settings
import json
from songs.utils import find_best_match
from .serializers import (
    DiscoveryGenerateRequestSerializer,
    DiscoveryGenerateResponseSerializer,
)


class DiscoveryGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Generate music discovery recommendations",
        description=(
            "Generates a list of music recommendations in a selected genre, tailored to the user's listening history. "
            "Uses OpenAI to suggest new tracks and attempts to match them with Spotify tracks. "
            "Returns a list of discovered songs and any errors encountered during the process."
        ),
        request=DiscoveryGenerateRequestSerializer,
        responses=DiscoveryGenerateResponseSerializer,
    )
    def post(self, request):
        serializer = DiscoveryGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        genre = serializer.validated_data["genre"]
        count = serializer.validated_data.get("count", 10)

        user = request.user

        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        top_artists_data = spotify.get_top_artists(limit=10)
        top_tracks_data = spotify.get_top_tracks(limit=10)

        top_tracks = [
            f"{track['name']} by {track['artists'][0]['name']}"
            for track in top_tracks_data.get("items", [])
        ]
        top_artists = [artist["name"] for artist in top_artists_data.get("items", [])]

        prompt = f"""
        Użytkownik zwykle słucha:
        Artyści: {json.dumps(top_artists, indent=2, ensure_ascii=False)}
        Utwory: {json.dumps(top_tracks, indent=2, ensure_ascii=False)}

        Teraz chce poznać nową muzykę z gatunku: {genre}

        Podaj {count} rekomendacji muzycznych w tym gatunku, w formacie JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem muzycznym."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```") and raw_content.endswith("```"):
            raw_content = "\n".join(raw_content.split("\n")[1:-1])

        try:
            songs = json.loads(raw_content)
        except Exception:
            return Response(
                {"error": "Failed to parse OpenAI response", "raw": raw_content},
                status=500,
            )

        discovered, errors = [], []
        for song in songs:
            query = f"{song['title']} {song['artist']}"
            try:
                search_result = spotify.search(query=query, type="track")
                matched = find_best_match(
                    search_result["tracks"]["items"], song["title"], song["artist"]
                )

                if matched:
                    if not user.explicit_content_enabled and matched.get(
                        "explicit", False
                    ):
                        errors.append(
                            {"song": song, "error": "Explicit content not allowed"}
                        )
                        continue

                    discovered.append(
                        {
                            "title": song["title"],
                            "artist": song["artist"],
                            "uri": matched["uri"],
                            "explicit": matched.get("explicit", False),
                        }
                    )
                else:
                    errors.append({"song": song, "error": "No match found"})
            except Exception as e:
                errors.append({"song": song, "error": str(e)})

        response_data = {
            "message": f"Discovery songs generated for genre: {genre}",
            "genre": genre,
            "songs": discovered,
            "errors": errors,
        }

        response_serializer = DiscoveryGenerateResponseSerializer(response_data)
        return Response(response_serializer.data)
