from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
from users.models import UserFeedback
from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import ask_openai, should_send_curveball, extract_filters, find_best_match
import logging
logging.basicConfig(level=logging.DEBUG)

class GenerateQueueBase(APIView):
    permission_classes = [IsAuthenticated]

    def get_user_preferences(self, user):
        feedbacks = UserFeedback.objects.select_related("media").filter(user=user)

        liked_genres, liked_artists = set(), set()
        disliked_genres, disliked_artists = set(), set()

        for feedback in feedbacks:
            if feedback.is_liked:
                liked_genres.update(feedback.media.genre)
                liked_artists.add(feedback.media.artist_name)
            else:
                disliked_genres.update(feedback.media.genre)
                disliked_artists.add(feedback.media.artist_name)

        return {
            "explicit_content": "Tak" if user.explicit_content_enabled else "Nie",
            "liked_genres": list(liked_genres),
            "liked_artists": list(liked_artists),
            "disliked_genres": list(disliked_genres),
            "disliked_artists": list(disliked_artists),
        }

    def parse_openai_json(self, content):
        if not isinstance(content, str) or not content.strip():
            logging.error(f"Otrzymano pustą lub nieprawidłową odpowiedź z OpenAI: {repr(content)}")
            raise ValueError("Otrzymano pustą odpowiedź z OpenAI")
        content = content.strip()

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
                        "explicit": best_match["explicit"]
                    })
            except Exception:
                continue
        return prepared, []

    def generate_valid_songs(self, prompt, user, count):
        preferences = self.get_user_preferences(user)
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        try:
            raw_response = ask_openai("Jesteś ekspertem muzycznym.", prompt)
            logging.debug(f"RAW RESPONSE: {repr(raw_response)}")
        except Exception as e:
            logging.exception("Błąd podczas pobierania danych z OpenAI")
            raise ValueError("Nie udało się pobrać odpowiedzi z OpenAI") from e

        prepared = []
        overflow = 10  # zapasowych utworów
        total = count + overflow

        for song in all_songs:
            if len(prepared) >= count:
                break
            try:
                query = f"{song['title']} {song['artist']}"
                tracks = spotify.search(query=query, type="track")["tracks"]["items"]
                best_match = find_best_match(tracks, song["title"], song["artist"])
                if best_match:
                    prepared.append({
                        "title": song["title"],
                        "artist": song["artist"],
                        "uri": best_match["uri"],
                        "explicit": best_match["explicit"],
                        "curveball": should_send_curveball(user, len(prepared) + 1)
                    })
            except Exception:
                continue

        return prepared[:count]

class BaseGenerateView(GenerateQueueBase):
    prompt_type = ""

    def get_prompt(self, user, data):
        raise NotImplementedError

    def post(self, request):
        user = request.user
        count = int(request.data.get("count", 0))
        if count <= 0:
            return Response({"error": "count is required and must be positive"}, status=400)

        try:
            prompt = self.get_prompt(user, request.data)
            songs = self.generate_valid_songs(prompt, user, count)
            return Response({"message": "Generated", "songs": songs})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class GenerateQueueView(BaseGenerateView):
    def get_prompt(self, user, data):
        title = data.get("title")
        artist = data.get("artist")
        if not title or not artist:
            raise ValueError("title and artist are required")
        count = data.get("count")
        filter_str = extract_filters(data)
        preferences = self.get_user_preferences(user)

        prompt = f"""
        Podaj {count} utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        {filter_str}

        Preferencje użytkownika:
        Lubi gatunki: {", ".join(preferences["liked_genres"])}
        Lubi artystów: {", ".join(preferences["liked_artists"])}
        Nie lubi gatunków: {", ".join(preferences["disliked_genres"])}
        Nie lubi artystów: {", ".join(preferences["disliked_artists"])}
        Czy użytkownik może dostawać explicit content? - {", ".join(preferences["explicit_content"])}
        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """
        
class GenerateFromTopView(BaseGenerateView):
    def get_prompt(self, user, data):
        count = data.get("count")
        filter_str = extract_filters(data)
        preferences = self.get_user_preferences(user)
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        top_tracks = [
            f"{t['name']} by {t['artists'][0]['name']}"
            for t in spotify.get_top_tracks().get("items", [])
        ]
        top_artists = [a["name"] for a in spotify.get_top_artists().get("items", [])]

        if not top_tracks and not top_artists:
            return Response({"error": "No top tracks or artists available"}, status=400)
        if not count:
            return Response({"error": "count is required"}, status=400)

        preferences = self.get_user_preferences(user)

        prompt = f"""
        Na podstawie ulubionych utworów:
        {json.dumps(top_tracks, indent=2)}

        i ulubionych artystów:
        {json.dumps(top_artists, indent=2)}
        {filter_str}

        Preferencje użytkownika:
        Lubi gatunki: {", ".join(preferences["liked_genres"])}
        Lubi artystów: {", ".join(preferences["liked_artists"])}
        Nie lubi gatunków: {", ".join(preferences["disliked_genres"])}
        Nie lubi artystów: {", ".join(preferences["disliked_artists"])}
        Czy użytkownik może dostawać explicit content? - {preferences["explicit_content"]}

        Podaj {count} nowych rekomendacji muzycznych.
        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

class GenerateFromArtistsView(BaseGenerateView):
    def get_prompt(self, user, data):
        artists = data.get("artists", [])
        if not artists or not isinstance(artists, list):
            raise ValueError("List of artists is required")
        count = data.get("count")
        filter_str = extract_filters(data)
        preferences = self.get_user_preferences(user)
        if not count:
            return Response({"error": "count is required"}, status=400)

        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        prompt = f"""
        Podaj {count} utworów {filter_str}, inspirowanych twórczością artystów:
        {json.dumps(artists, indent=2)}

        Preferencje użytkownika:
        Lubi gatunki: {", ".join(preferences["liked_genres"])}
        Lubi artystów: {", ".join(preferences["liked_artists"])}
        Nie lubi gatunków: {", ".join(preferences["disliked_genres"])}
        Nie lubi artystów: {", ".join(preferences["disliked_artists"])}
        Czy użytkownik może dostawać explicit content? - {preferences["explicit_content"]}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

class GenerateQueueFromPromptView(BaseGenerateView):
    def get_prompt(self, user, data):
        prompt_input = data.get("prompt")
        if not prompt_input:
            raise ValueError("Prompt is required")
        count = data.get("count")
        preferences = self.get_user_preferences(user)
        if not count:
            return Response({"error": "count is required"}, status=400)
        
        full_prompt = f"""
        Podaj {count} utworów pasujących do opisu:
        "{prompt_input}"

        Preferencje użytkownika:
        Lubi gatunki: {", ".join(preferences["liked_genres"])}
        Lubi artystów: {", ".join(preferences["liked_artists"])}
        Nie lubi gatunków: {", ".join(preferences["disliked_genres"])}
        Nie lubi artystów: {", ".join(preferences["disliked_artists"])}
        Czy użytkownik może dostawać explicit content? - {preferences["explicit_content"]}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """
