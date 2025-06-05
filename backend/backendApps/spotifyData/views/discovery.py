from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..services.spotifyClient import SpotifyAPI
from openai import OpenAI
from django.conf import settings
import json
from collections import namedtuple
from songs.utils import find_best_match
from .serializers import (
    DiscoveryGenerateRequestSerializer,
    DiscoveryGenerateResponseSerializer,
)


MatchResult = namedtuple("MatchResult", ["discovered", "errors"])


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

        spotify = self._get_spotify(user)
        openai_client = self._get_openai_client()

        top_artists = self._get_top_artists(spotify)
        top_tracks = self._get_top_tracks(spotify)

        prompt = self._build_prompt(top_artists, top_tracks, genre, count)
        raw_openai_response = self._query_openai(openai_client, prompt)

        songs = self._parse_openai_response(raw_openai_response)
        if songs is None:
            return Response(
                {
                    "error": "Failed to parse OpenAI response",
                    "raw": raw_openai_response,
                },
                status=500,
            )

        match_result = self._match_songs(songs, spotify, user)

        response_data = {
            "message": f"Discovery songs generated for genre: {genre}",
            "genre": genre,
            "songs": match_result.discovered,
            "errors": match_result.errors,
        }

        response_serializer = DiscoveryGenerateResponseSerializer(response_data)
        return Response(response_serializer.data)

    def _get_spotify(self, user):
        return SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

    def _get_openai_client(self):
        return OpenAI(api_key=settings.OPENAI_API_KEY)

    def _get_top_artists(self, spotify):
        data = spotify.get_top_artists(limit=10)
        return [artist["name"] for artist in data.get("items", [])]

    def _get_top_tracks(self, spotify):
        data = spotify.get_top_tracks(limit=10)
        return [
            f"{track['name']} by {track['artists'][0]['name']}"
            for track in data.get("items", [])
        ]

    def _build_prompt(self, artists, tracks, genre, count):
        return f"""
Użytkownik zwykle słucha:
Artyści: {json.dumps(artists, indent=2, ensure_ascii=False)}
Utwory: {json.dumps(tracks, indent=2, ensure_ascii=False)}

Teraz chce poznać nową muzykę z gatunku: {genre}

Podaj {count} rekomendacji muzycznych w tym gatunku, w formacie JSON:
[
  {{"title": "tytuł", "artist": "artysta"}}
]
"""

    def _query_openai(self, client, prompt):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem muzycznym."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        raw_content = response.choices[0].message.content.strip()

        # Usuń ewentualne markdownowe oznaczenia kodu
        if raw_content.startswith("```") and raw_content.endswith("```"):
            raw_content = "\n".join(raw_content.split("\n")[1:-1])
        return raw_content

    def _parse_openai_response(self, raw_content):
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            return None

    def _match_songs(self, songs, spotify, user) -> MatchResult:
        discovered = []
        errors = []

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

        return MatchResult(discovered, errors)
