from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from songs.services.PromptBuilder import PromptBuilder
from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import find_best_match, ask_openai
from songs.services.songGeneration import get_user_preferences, parse_openai_json
from songs.services.songProcessing import extract_track_details
from songs.utils import should_send_curveball
from .serializers import (
    DiscoveryGenerateRequestSerializer,
    DiscoveryGenerateResponseSerializer,
)

import logging
from collections import namedtuple

logger = logging.getLogger(__name__)
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
        data = serializer.validated_data

        user = request.user
        genres = data["genres"]
        count = data.get("count", 10)

        try:
            spotify = self._get_spotify(user)
            top_artists = self._get_top_artists(spotify)
            top_tracks = self._get_top_tracks(spotify)
            preferences = get_user_preferences(user)

            prompt_builder = PromptBuilder(count=count, user_preferences=preferences)
            prompt = prompt_builder.for_discovery(top_artists, top_tracks, genres)
            base_prompt = "Jesteś ekspertem muzycznym."

            raw_response_text = ask_openai(base_prompt, prompt)
            raw_response = parse_openai_json(raw_response_text)

            if raw_response is None:
                return Response(
                    {"error": "Nie udało się sparsować odpowiedzi z OpenAI"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            match_result = self._match_songs(raw_response, spotify, user)

            response_data = {
                "message": f"Discovery songs generated for genres: {', '.join(genres)}",
                "genres": genres,
                "songs": match_result.discovered[:count],
                "errors": match_result.errors,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error generating discovery recommendations")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_spotify(self, user):
        return SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

    def _get_top_artists(self, spotify):
        data = spotify.get_top_artists(limit=10)
        return [artist["name"] for artist in data.get("items", [])]

    def _get_top_tracks(self, spotify):
        data = spotify.get_top_tracks(limit=10)
        return [
            f"{track['name']} by {track['artists'][0]['name']}"
            for track in data.get("items", [])
        ]

    def _match_songs(self, songs, spotify, user) -> MatchResult:
        discovered = []
        errors = []

        for i, song in enumerate(songs):
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

                    track_info = spotify.get_track(matched["id"])
                    track_details = extract_track_details(track_info)

                    discovered.append(
                        {
                            "title": song["title"],
                            "artist": song["artist"],
                            "uri": matched["uri"],
                            "explicit": matched.get("explicit", False),
                            "curveball": should_send_curveball(
                                user, len(discovered) + 1
                            ),
                            "track_details": track_details,
                        }
                    )
                else:
                    errors.append({"song": song, "error": "No match found"})

            except Exception as e:
                logger.exception("Error matching song")
                errors.append({"song": song, "error": str(e)})

        return MatchResult(discovered, errors)
