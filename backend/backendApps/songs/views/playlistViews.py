from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from spotifyData.services.spotifyClient import SpotifyAPI
from users.models import Media
from songs.utils import ask_openai, find_best_match
import json

import sys

sys.path.append("..")


class CreateLikedPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

        all_liked_songs = Media.objects.filter(user=user, feedback="like").exclude(
            spotify_uri=None
        )
        liked_curveballs = all_liked_songs.filter(is_curveball=True)

        all_liked_uris = [song.spotify_uri for song in all_liked_songs]
        curveball_uris = [song.spotify_uri for song in liked_curveballs]

        if not all_liked_uris:
            return Response({"error": "No liked songs to add"}, status=400)

        user_id = spotify.get_user_profile().get("id")
        if not user_id:
            return Response({"error": "Failed to get Spotify user ID"}, status=500)

        created_playlists = []

        liked_playlist_url = self._create_playlist_with_uris(
            spotify,
            name="Liked Songs from App",
            description="All songs you've liked in the app",
            uris=all_liked_uris,
        )
        if liked_playlist_url:
            created_playlists.append({"type": "all", "url": liked_playlist_url})

        if curveball_uris:
            curveball_playlist_url = self._create_playlist_with_uris(
                spotify,
                name="Liked Curveballs from App",
                description="Only curveballs you've liked in the app",
                uris=curveball_uris,
            )
            if curveball_playlist_url:
                created_playlists.append(
                    {"type": "curveballs", "url": curveball_playlist_url}
                )

        return Response(
            {
                "message": "Playlists created successfully",
                "playlists": created_playlists,
            }
        )

    def _create_playlist_with_uris(self, spotify, name, description, uris):
        playlist_payload = {"name": name, "description": description, "public": False}

        create_response = requests.post(
            SPOTIFY_PLAYLIST_URL, headers=spotify.headers, json=playlist_payload
        )
        if create_response.status_code != 201:
            return None

        playlist_id = create_response.json().get("id")

        for i in range(0, len(uris), 100):
            chunk = uris[i : i + 100]
            add_response = requests.post(
                SPOTIFY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id),
                headers=spotify.headers,
                json={"uris": chunk},
            )
            if add_response.status_code != 201:
                return None

        return create_response.json().get("external_urls", {}).get("spotify")


class CreatePlaylistFromPromptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt_input = request.data.get("prompt")
        playlist_name = request.data.get("name")
        count = int(request.data.get("count", 15))

        if not prompt_input:
            return Response({"error": "Prompt is required"}, status=400)
        if not playlist_name:
            return Response({"error": "Playlist name is required"}, status=400)

        preferences = self.get_user_preferences(user)
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

        prompt = f"""
        Podaj {count} utworów pasujących do opisu:
        "{prompt_input}"

        Preferencje użytkownika:
        Lubi gatunki: {", ".join(preferences["liked_genres"])}
        Lubi artystów: {", ".join(preferences["liked_artists"])}
        Nie lubi gatunków: {", ".join(preferences["disliked_genres"])}
        Nie lubi artystów: {", ".join(preferences["disliked_artists"])}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            raw_response = ask_openai(
                "Jesteś ekspertem muzycznym i tworzysz playlistę do opisu.", prompt
            )
            songs = self.parse_openai_json(raw_response)

            if not songs:
                return Response(
                    {"error": "No valid songs returned from AI"}, status=500
                )

            uris = []
            for song in songs:
                query = f"{song['title']} {song['artist']}"
                result = spotify.search(query=query, type="track")
                tracks = result["tracks"]["items"]
                best_match = find_best_match(tracks, song["title"], song["artist"])
                if best_match:
                    uris.append(best_match["uri"])

            if not uris:
                return Response(
                    {"error": "No tracks found to create playlist"}, status=400
                )

            playlist_url = self._create_playlist_with_uris(
                spotify,
                name=playlist_name,
                description=f"Generated playlist for: {prompt_input}",
                uris=uris,
            )
            return Response({"message": "Playlist created", "url": playlist_url})
        except json.JSONDecodeError as e:
            return Response(
                {
                    "error": f"JSON parsing error: {str(e)}",
                    "raw_response": raw_response,
                },
                status=500,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def parse_openai_json(self, content):
        content = content.strip()
        if content.startswith("```") and content.endswith("```"):
            content = "\n".join(content.split("\n")[1:-1])

        if not content:
            raise ValueError("Empty response from OpenAI")
        return json.loads(content)

    def get_user_preferences(self, user):
        from users.models import UserFeedback

        feedbacks = UserFeedback.objects.select_related("media").filter(user=user)

        liked_genres, liked_artists, disliked_genres, disliked_artists = [], [], [], []

        for fb in feedbacks:
            if fb.is_liked:
                liked_genres.extend(fb.media.genre)
                liked_artists.append(fb.media.artist_name)
            else:
                disliked_genres.extend(fb.media.genre)
                disliked_artists.append(fb.media.artist_name)

        return {
            "liked_genres": list(set(liked_genres)),
            "liked_artists": list(set(liked_artists)),
            "disliked_genres": list(set(disliked_genres)),
            "disliked_artists": list(set(disliked_artists)),
        }
