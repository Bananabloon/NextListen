from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import extract_filters, find_best_match
from songs.services.songProcessing import prepare_song_list, get_spotify
from songs.services.generationPipeline import generate_recommendations
from songs.services.songGeneration import (
    build_preferences_prompt,
    generate_songs_with_buffer,
    get_user_preferences,
)
from constants import GENERATION_BUFFER_MULTIPLIER
from .serializers import (
    GenerateQueueSerializer,
    GenerateFromArtistsSerializer,
    GenerateFromPromptSerializer,
    BaseGenerateSerializer,
)

import json
import logging

logger = logging.getLogger(__name__)


class GenerateQueueBase(APIView):
    permission_classes = [IsAuthenticated]

    def prepare_song_list_only(self, user, songs, spotify):
        prepared = []
        for song in songs:
            query = f"{song['title']} {song['artist']}"
            try:
                tracks = spotify.search(query=query, type="track")["tracks"]["items"]
                best_match = find_best_match(tracks, song["title"], song["artist"])
                if best_match:
                    prepared.append({
                        "title": song["title"],
                        "artist": song["artist"],
                        "uri": best_match["uri"],
                        "explicit": best_match["explicit"],
                    })
            except Exception:
                continue
        return prepared, []

    def generate_valid_songs(self, prompt, user, count):
        base_prompt = "Jesteś ekspertem muzycznym."
        try:
            all_songs, _ = generate_songs_with_buffer(
                prompt, base_prompt, int(count * GENERATION_BUFFER_MULTIPLIER)
            )
        except Exception as e:
            raise ValueError("Nie udało się pobrać odpowiedzi z OpenAI") from e

        return prepare_song_list(user, all_songs, count)


class BaseGenerateView(GenerateQueueBase):
    serializer_class = None  

    def get_prompt(self, user, data):
        raise NotImplementedError("get_prompt must be implemented in subclasses.")

    @extend_schema(
        summary="Generate recommendations",
        description="Base endpoint for generating song recommendations.",
        request=None,  # override in subclasses
        responses=None,
    )
    def post(self, request):
        if self.serializer_class is None:
            return Response({"error": "Serializer not defined."}, status=500)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        count = data["count"]

        try:
            prompt = self.get_prompt(request.user, data)
            songs = generate_recommendations(request.user, prompt, count)
            return Response({"message": "Generated", "songs": songs})
        except Exception as e:
            logger.exception("Unhandled exception in generation view")
            return Response({"error": str(e)}, status=500)


class GenerateQueueView(BaseGenerateView):
    serializer_class = GenerateQueueSerializer

    @extend_schema(
        summary="Generates a list of recommended songs similar to a given title and artist. "
            "You can provide additional filters (e.g., genre, year). "
            "Returns a list of songs with Spotify metadata and user feedback if available.",
        request=GenerateQueueSerializer,
        responses=None,
    )
    def post(self, request):
        return super().post(request)

    def get_prompt(self, user, data):
        title = data["title"]
        artist = data["artist"]
        count = data["count"]
        filter_str = extract_filters(data)
        preferences = get_user_preferences(user)

        return f"""
        Podaj {count * GENERATION_BUFFER_MULTIPLIER} utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        {filter_str}

        {build_preferences_prompt(preferences)}
        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.
        Unikaj zbyt częstego powtarzania tego samego artysty w generowanych utworach.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """


class GenerateFromTopView(BaseGenerateView):
    serializer_class = BaseGenerateSerializer

    @extend_schema(
        summary="Generate recommendations from selected artists",
        description=(
            "Generates a list of recommended songs inspired by a list of selected artists. "
            "You can provide additional filters (e.g., genre, year). "
            "Returns a list of recommended songs with Spotify metadata."),
        request=BaseGenerateSerializer,
        responses=None,
    )
    def post(self, request):
        return super().post(request)

    def get_prompt(self, user, data):
        count = data["count"]
        filter_str = extract_filters(data)
        preferences = get_user_preferences(user)
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

        top_tracks = [
            f"{t['name']} by {t['artists'][0]['name']}"
            for t in spotify.get_top_tracks().get("items", [])
        ]
        top_artists = [a["name"] for a in spotify.get_top_artists().get("items", [])]

        if not top_tracks and not top_artists:
            raise ValueError("No data about favorite tracks or artists")

        return f"""
        Na podstawie ulubionych utworów:
        {json.dumps(top_tracks, indent=2)}

        i ulubionych artystów:
        {json.dumps(top_artists, indent=2)}
        {filter_str}

        {build_preferences_prompt(preferences)}
        Podaj {count * GENERATION_BUFFER_MULTIPLIER} nowych rekomendacji muzycznych.
        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """


class GenerateFromArtistsView(BaseGenerateView):
    serializer_class = GenerateFromArtistsSerializer

    @extend_schema(
        summary="Generate recommendations from a text prompt",
        description=(
            "Generates a list of recommended songs based on a free-form text prompt describing the desired mood"
            ", style, or theme. "
            "Returns a list of recommended songs with Spotify metadata."
        ),
        responses=None,
    )
    def post(self, request):
        return super().post(request)

    def get_prompt(self, user, data):
        artists = data["artists"]
        count = data["count"]
        filter_str = extract_filters(data)
        preferences = get_user_preferences(user)

        return f"""
        Podaj {count * GENERATION_BUFFER_MULTIPLIER} utworów {filter_str}, inspirowanych twórczością artystów:
        {json.dumps(artists, indent=2)}

        {build_preferences_prompt(preferences)}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """


class GenerateQueueFromPromptView(BaseGenerateView):
    serializer_class = GenerateFromPromptSerializer

    @extend_schema(
        summary="Generate recommendations from selected artists",
        description=(
            "Generates a list of recommended songs inspired by a list of selected artists. "
            "You can provide additional filters (e.g., genre, year). "
            "Returns a list of recommended songs with Spotify metadata."),
        request=GenerateFromPromptSerializer,
        responses=None,
    )
    def post(self, request):
        return super().post(request)

    def get_prompt(self, user, data):
        prompt_input = data["prompt"]
        count = data["count"]
        preferences = get_user_preferences(user)

        return f"""
        Podaj {count * GENERATION_BUFFER_MULTIPLIER} utworów pasujących do opisu:
        "{prompt_input}"

        {build_preferences_prompt(preferences)}

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """
