from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
from users.models import UserFeedback, Media
from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import should_send_curveball, extract_filters, find_best_match
from songs.services.songGeneration import build_preferences_prompt, generate_songs_with_buffer, get_user_preferences
import logging
logger = logging.getLogger(__name__)
from constants import GENERATION_BUFFER_MULTIPLIER

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
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)
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
                    logger.info(f"[{i}] Znaleziono dopasowanie: {best_match['name']} by {best_match['artists'][0]['name']}")
                    track_id = best_match["id"]
                    track_info = spotify.get_track(track_id)

                    uri = best_match["uri"]

                    try:
                        media = Media.objects.get(spotify_uri=uri)
                        feedback_obj = UserFeedback.objects.filter(user=user, media=media).first()
                        if feedback_obj is None or feedback_obj.is_liked is None:
                            feedback_value = 0
                        else:
                            feedback_value = 1 if feedback_obj.is_liked else -1
                    except Media.DoesNotExist:
                        feedback_value = 0

                    prepared.append({
                        "title": song["title"],
                        "artist": song["artist"],
                        "uri": uri,
                        "explicit": best_match["explicit"],
                        "curveball": should_send_curveball(user, len(prepared) + 1),
                        "feedback_value": feedback_value,
                        "track_details": {
                            "id": track_info.get("id"),
                            "name": track_info.get("name"),
                            "artists": [artist["name"] for artist in track_info.get("artists", [])],
                            "album": track_info.get("album", {}).get("name"),
                            "album_type": track_info.get("album", {}).get("album_type"),
                            "markets": track_info.get("album", {}).get("available_markets"),
                            "album_cover": track_info.get("album", {}).get("images", [{}])[0].get("url"),
                            "release_date": track_info.get("album", {}).get("release_date"),
                            "duration_ms": track_info.get("duration_ms"),
                            "popularity": track_info.get("popularity"),
                            "preview_url": track_info.get("preview_url"),
                            "external_url": track_info.get("external_urls", {}).get("spotify"),
                        }
                    })
                else:
                    logger.warning(f"[{i}] Nie znaleziono dopasowania wśród {len(tracks)} wyników dla: {query}")
            except Exception as e:
                logger.error(f"[{i}] Błąd podczas wyszukiwania dla '{query}': {e}")

        return prepared[:count]


class BaseGenerateView(GenerateQueueBase):
    prompt_type = ""

    def get_prompt(self, user, data):
        raise NotImplementedError

    def post(self, request):
        user = request.user
        count = int(request.data.get("count", 0))
        if count <= 0:
            return Response(
                {"error": "count is required and must be positive"}, status=400
            )

        try:
            prompt = self.get_prompt(user, request.data)
            songs = self.generate_valid_songs(prompt, user, count)
            return Response({"message": "Generated", "songs": songs})
        except Exception as e:
            logger.exception("Unhandled exception occurred in generate endpoint")
            return Response({"error": str(e)}, status=500)


class GenerateQueueView(BaseGenerateView):
    def get_prompt(self, user, data):
        title = data.get("title")
        artist = data.get("artist")
        if not title or not artist:
            raise ValueError("title and artist are required")
        count = data.get("count")
        filter_str = extract_filters(data)
        preferences = get_user_preferences(user)

        prompt = f"""
        Podaj {count*GENERATION_BUFFER_MULTIPLIER} utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        {filter_str}

        {build_preferences_prompt(preferences)}
        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.
        Upewnij się, że wygenerowane propozycje zachowują różnorodność – unikaj powtarzania tego samego artysty w zbyt wielu utworach.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """
        return prompt


class GenerateFromTopView(BaseGenerateView):
    def get_prompt(self, user, data):
        count = data.get("count")
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
            raise ValueError("Brak danych o ulubionych utworach lub artystach")
        if not count:
            raise ValueError("count is required")

        preferences = get_user_preferences(user)

        prompt = f"""
        Na podstawie ulubionych utworów:
        {json.dumps(top_tracks, indent=2)}

        i ulubionych artystów:
        {json.dumps(top_artists, indent=2)}
        {filter_str}

        {build_preferences_prompt(preferences)}
        Podaj {count*GENERATION_BUFFER_MULTIPLIER} nowych rekomendacji muzycznych.
        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """
        return prompt


class GenerateFromArtistsView(BaseGenerateView):
    def get_prompt(self, user, data):
        artists = data.get("artists", [])
        if not artists or not isinstance(artists, list):
            raise ValueError("List of artists is required")
        count = data.get("count")
        filter_str = extract_filters(data)
        preferences = get_user_preferences(user)
        if not count:
            return Response({"error": "count is required"}, status=400)

        prompt = f"""
        Podaj {count*GENERATION_BUFFER_MULTIPLIER} utworów {filter_str}, inspirowanych twórczością artystów:
        {json.dumps(artists, indent=2)}

        {build_preferences_prompt(preferences)}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """
        return prompt


class GenerateQueueFromPromptView(BaseGenerateView):
    def get_prompt(self, user, data):
        prompt_input = data.get("prompt")
        if not prompt_input:
            raise ValueError("Prompt is required")
        count = data.get("count")
        preferences = get_user_preferences(user)
        if not count:
            return Response({"error": "count is required"}, status=400)

        prompt = f"""
        Podaj {count*GENERATION_BUFFER_MULTIPLIER} utworów pasujących do opisu:
        "{prompt_input}"

        {build_preferences_prompt(preferences)}

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """
        return prompt
