from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from users.models import UserFeedback, Media
from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import should_send_curveball, extract_filters, find_best_match
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
        """
        Matches a list of song dicts (with title and artist) to Spotify tracks and returns a prepared list
        with Spotify metadata (uri, explicit flag).
        """
        prepared = []
        for song in songs:
            query = f"{song['title']} {song['artist']}"
            try:
                tracks = spotify.search(query=query, type="track")["tracks"]["items"]
                best_match = find_best_match(tracks, song["title"], song["artist"])
                if best_match:
                    prepared.append(
                        {
                            "title": song["title"],
                            "artist": song["artist"],
                            "uri": best_match["uri"],
                            "explicit": best_match["explicit"],
                        }
                    )
            except Exception:
                continue
        return prepared, []

    def generate_valid_songs(self, prompt, user, count):
        """
        Generates a list of valid songs using OpenAI and matches them to Spotify tracks.
        Returns a list of prepared songs with Spotify metadata and user feedback if available.
        """
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )
        base_prompt = "Jesteś ekspertem muzycznym."
        multiplier = GENERATION_BUFFER_MULTIPLIER
        requested_total_count = int(count * multiplier)

        try:
            all_songs, _ = generate_songs_with_buffer(
                prompt, base_prompt, requested_total_count
            )
        except Exception as e:
            raise ValueError("Nie udało się pobrać odpowiedzi z OpenAI") from e

        prepared = []

        for i, song in enumerate(all_songs):
            if len(prepared) >= count:
                break

            query = f"{song['title']} {song['artist']}"
            try:
                tracks = spotify.search(query=query, type="track")["tracks"]["items"]
                if not tracks:
                    logger.warning(f"[{i}] Brak wyników z Spotify dla: {query}")
                    continue

                best_match = find_best_match(tracks, song["title"], song["artist"])
                if best_match:
                    logger.info(
                        f"[{i}] Znaleziono dopasowanie: {best_match['name']} by {best_match['artists'][0]['name']}"
                    )
                    track_id = best_match["id"]
                    track_info = spotify.get_track(track_id)
                    uri = best_match["uri"]

                    try:
                        media = Media.objects.get(spotify_uri=uri)
                        feedback_obj = UserFeedback.objects.filter(
                            user=user, media=media
                        ).first()
                        feedback_value = (
                            1
                            if feedback_obj.is_liked
                            else -1
                            if feedback_obj and feedback_obj.is_liked is not None
                            else 0
                        )
                    except Media.DoesNotExist:
                        feedback_value = 0

                    prepared.append(
                        {
                            "title": song["title"],
                            "artist": song["artist"],
                            "uri": uri,
                            "explicit": best_match["explicit"],
                            "curveball": should_send_curveball(user, len(prepared) + 1),
                            "feedback_value": feedback_value,
                            "track_details": {
                                "id": track_info.get("id"),
                                "name": track_info.get("name"),
                                "artists": [
                                    artist["name"]
                                    for artist in track_info.get("artists", [])
                                ],
                                "album": track_info.get("album", {}).get("name"),
                                "album_type": track_info.get("album", {}).get(
                                    "album_type"
                                ),
                                "markets": track_info.get("album", {}).get(
                                    "available_markets"
                                ),
                                "album_cover": track_info.get("album", {})
                                .get("images", [{}])[0]
                                .get("url"),
                                "release_date": track_info.get("album", {}).get(
                                    "release_date"
                                ),
                                "duration_ms": track_info.get("duration_ms"),
                                "popularity": track_info.get("popularity"),
                                "preview_url": track_info.get("preview_url"),
                                "external_url": track_info.get("external_urls", {}).get(
                                    "spotify"
                                ),
                            },
                        }
                    )
                else:
                    logger.warning(
                        f"[{i}] Nie znaleziono dopasowania wśród {len(tracks)} wyników dla: {query}"
                    )
            except Exception as e:
                logger.error(f"[{i}] Błąd podczas wyszukiwania dla '{query}': {e}")

        return prepared[:count]


class BaseGenerateView(GenerateQueueBase):
    prompt_type = ""

    def get_prompt(self, user, data):
        """
        Should be implemented by subclasses to return a prompt string for song generation.
        """
        raise NotImplementedError

    @extend_schema(
        summary="Generate recommendations (base endpoint)",
        description="Base endpoint for generating song recommendations. Should not be used directly.",
        request=BaseGenerateSerializer,
        responses=None,
    )
    def post(self, request):
        """
        Handles POST requests for generating recommendations using the implemented prompt.
        """
        user = request.user
        serializer = BaseGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        count = serializer.validated_data["count"]

        try:
            prompt = self.get_prompt(user, request.data)
            songs = self.generate_valid_songs(prompt, user, count)
            return Response({"message": "Generated", "songs": songs})
        except Exception as e:
            logger.exception("Unhandled exception occurred in generate endpoint")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GenerateQueueView(BaseGenerateView):
    @extend_schema(
        summary="Generate queue based on a song",
        description=(
            "Generates a list of recommended songs similar to a given title and artist. "
            "You can provide additional filters (e.g., genre, year). "
            "Returns a list of songs with Spotify metadata and user feedback if available."
        ),
        request=GenerateQueueSerializer,
        responses=None,
    )
    def post(self, request):
        serializer = GenerateQueueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        return super().post(request)

    def get_prompt(self, user, data):
        """
        Builds a prompt for generating songs similar to a given title and artist.
        """
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
        Upewnij się, że wygenerowane propozycje zachowują różnorodność –
        unikaj powtarzania tego samego artysty w zbyt wielu utworach.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """


class GenerateFromTopView(BaseGenerateView):
    @extend_schema(
        summary="Generate recommendations from user's top tracks and artists",
        description=(
            "Generates music recommendations based on the user's top tracks and artists on Spotify. "
            "You can provide additional filters (e.g., genre, year). "
            "Returns a list of recommended songs with Spotify metadata."
        ),
        request=BaseGenerateSerializer,
        responses=None,
    )
    def post(self, request):
        serializer = BaseGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        return super().post(request)

    def get_prompt(self, user, data):
        """
        Builds a prompt for generating songs based on user's top tracks and artists.
        """
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
    @extend_schema(
        summary="Generate recommendations from selected artists",
        description=(
            "Generates a list of recommended songs inspired by a list of selected artists. "
            "You can provide additional filters (e.g., genre, year). "
            "Returns a list of recommended songs with Spotify metadata."
        ),
        request=GenerateFromArtistsSerializer,
        responses=None,
    )
    def post(self, request):
        serializer = GenerateFromArtistsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        return super().post(request)

    def get_prompt(self, user, data):
        """
        Builds a prompt for generating songs inspired by selected artists.
        """
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
    @extend_schema(
        summary="Generate recommendations from a text prompt",
        description=(
            "Generates a list of recommended songs based on a free-form text prompt describing the desired mood"
            ", style, or theme. "
            "Returns a list of recommended songs with Spotify metadata."
        ),
        request=GenerateFromPromptSerializer,
        responses=None,
    )
    def post(self, request):
        serializer = GenerateFromPromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        return super().post(request)

    def get_prompt(self, user, data):
        """
        Builds a prompt for generating songs based on a free-form text prompt.
        """
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
