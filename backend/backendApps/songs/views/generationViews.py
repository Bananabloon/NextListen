from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
from spotifyData.services.spotifyClient import SpotifyAPI
from songs.utils import (
    ask_openai,
    should_send_curveball,
    # update_curveball_enjoyment,
    extract_filters,
    find_best_match,
)


class GenerateQueueBase(APIView):
    permission_classes = [IsAuthenticated]

    def add_songs_to_queue(self, user, songs, spotify, curveball_every):
        added, errors = [], []

        for idx, song in enumerate(songs):
            is_curveball = should_send_curveball(user, idx + 1)
            query = f"{song['title']} {song['artist']}"

            try:
                result = spotify.search(query=query, type="track")
                tracks = result["tracks"]["items"]
                best_match = find_best_match(tracks, song["title"], song["artist"])

                if not best_match:
                    errors.append({"song": song, "error": "No matching track found"})
                    continue

                uri = best_match["uri"]
                success, error = spotify.add_to_queue(uri)

                if success:
                    added.append(
                        {
                            "title": song["title"],
                            "artist": song["artist"],
                            "uri": uri,
                            "curveball": is_curveball,
                        }
                    )
                else:
                    errors.append({"song": song, "error": error})

            except Exception as e:
                errors.append({"song": song, "error": str(e)})

        return added, errors

    def parse_openai_json(self, content):
        content = content.strip()
        if content.startswith("```") and content.endswith("```"):
            content = "\n".join(content.split("\n")[1:-1])
        return json.loads(content)


class GenerateQueueView(GenerateQueueBase):
    def post(self, request):
        user = request.user
        title = request.data.get("title")
        artist = request.data.get("artist")
        count = int(request.data.get("count", 10))

        if not title or not artist:
            return Response({"error": "title and artist required"}, status=400)

        filter_str = extract_filters(request.data)
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

        prompt = f"""
        Podaj {count} utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        {filter_str}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            raw_response = ask_openai(
                "Jesteś ekspertem muzycznym i podajesz podobne utwory.", prompt
            )
            songs = self.parse_openai_json(raw_response)
            added, errors = self.add_songs_to_queue(
                user,
                songs,
                spotify,
                curveball_every=max(1, 50 // (user.curveball_enjoyment or 5)),
            )

            return Response(
                {"message": "Queue generated", "added": added, "errors": errors}
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class GenerateFromTopView(GenerateQueueBase):
    def post(self, request):
        user = request.user
        count = int(request.data.get("count", 10))
        filter_str = extract_filters(request.data)

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
            return Response({"error": "No top tracks or artists available"}, status=400)

        prompt = f"""
        Na podstawie ulubionych utworów:
        {json.dumps(top_tracks, indent=2)}

        i ulubionych artystów:
        {json.dumps(top_artists, indent=2)}
        {filter_str}

        Podaj {count} nowych rekomendacji muzycznych.

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            raw_response = ask_openai(
                "Jesteś ekspertem muzycznym. Generujesz nowe utwory na podstawie gustu użytkownika.",
                prompt,
            )
            songs = self.parse_openai_json(raw_response)
            added, errors = self.add_songs_to_queue(
                user,
                songs,
                spotify,
                curveball_every=max(1, 50 // (user.curveball_enjoyment or 5)),
            )

            return Response(
                {"message": "Queue from top tracks", "added": added, "errors": errors}
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class GenerateFromArtistsView(GenerateQueueBase):
    def post(self, request):
        user = request.user
        artists = request.data.get("artists", [])
        count = int(request.data.get("count", 10))

        if not artists or not isinstance(artists, list):
            return Response({"error": "List of artists is required"}, status=400)

        filter_str = extract_filters(request.data)
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

        prompt = f"""
        Podaj {count} utworów {filter_str}, inspirowanych twórczością artystów:
        {json.dumps(artists, indent=2)}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            raw_response = ask_openai(
                """Jesteś ekspertem muzycznym.
                   Generujesz nowe utwory inspirowane stylem podanych artystów i zgodne z określonym nastrojem,
                   tempem lub stylem muzycznym.""",
                prompt,
            )
            songs = self.parse_openai_json(raw_response)
            added, errors = self.add_songs_to_queue(
                user,
                songs,
                spotify,
                curveball_every=max(1, 50 // (user.curveball_enjoyment or 5)),
            )

            return Response(
                {
                    "message": "Queue generated from artists with filters",
                    "added": added,
                    "errors": errors,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)
