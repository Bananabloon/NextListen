from django.conf import settings
import openai
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openai import OpenAI
from django.shortcuts import get_object_or_404
import json
import random
import requests
from spotifyData.services.spotifyClient import SpotifyAPI
from users.models import Media
from .utils import ask_openai, should_send_curveball, update_curveball_enjoyment

import sys
sys.path.append("..")
from constants import SPOTIFY_PLAYLIST_TRACKS_URL, SPOTIFY_PLAYLIST_URL

class SongAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        artist = request.data.get("artist")

        if not title or not artist:
            return Response({"error": "title and artist are required"}, status=400)

        system_prompt = (
            """
            Jesteś ekspertem muzycznym. Dla podanego utworu podaj:
            - tempo (slow/medium/fast)
            - nastrój (happy/sad/romantic/energetic/chill)
            - styl muzyczny (pop, jazz, electronic itd.)
            - krótki opis utworu (max 2 zdania)
            Wynik w formacie JSON.
            """
        )

        user_prompt = f"Tytuł: {title}\nArtysta: {artist}"

        try:
            analysis = ask_openai(system_prompt, user_prompt)
            return Response({"analysis": analysis})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class SongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        song_id = request.data.get("song_id")
        feedback = request.data.get("feedback")  # "like", "dislike", "none"

        if not song_id or feedback not in ["like", "dislike", "none"]:
            return Response({"error": "Invalid input"}, status=400)

        song = get_object_or_404(Media, id=song_id, user=request.user)

        if song.is_curveball:
            liked = {"like": True, "dislike": False, "none": None}[feedback]
            update_curveball_enjoyment(request.user, liked)

        return Response({"status": "ok", "curveball_enjoyment": request.user.curveball_enjoyment})


class SimilarSongsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        artist = request.data.get("artist")

        if not title or not artist:
            return Response({"error": "title and artist are required"}, status=400)

        prompt = f"""
        Podaj 5 utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        Zwróć listę w formacie JSON:
        [
          {{"title": "tytuł", "artist": "artysta", "reason": "krótka przyczyna podobieństwa"}},
          ...
        ]
        """

        try:
            response = ask_openai(
                "Jesteś ekspertem muzycznym i rekomendujesz podobne utwory.",
                prompt
            )
            return Response({"results": response})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class GenerateQueueBase(APIView):
    permission_classes = [IsAuthenticated]

    def add_songs_to_queue(self, user, songs, spotify, curveball_every):
        added, errors = [], []

        for idx, song in enumerate(songs):
            is_curveball = should_send_curveball(user, idx + 1)
            query = f"{song['title']} {song['artist']}"
            try:
                result = spotify.search(query=query, type="track")
                uri = result["tracks"]["items"][0]["uri"]
                success, error = spotify.add_to_queue(uri)
                if success:
                    added.append({"title": song["title"], "artist": song["artist"], "uri": uri, "curveball": is_curveball})
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


from songs.utils import ask_openai, should_send_curveball, update_curveball_enjoyment, extract_filters

class GenerateQueueView(GenerateQueueBase):
    def post(self, request):
        user = request.user
        title = request.data.get("title")
        artist = request.data.get("artist")
        count = int(request.data.get("count", 10))

        if not title or not artist:
            return Response({"error": "title and artist required"}, status=400)

        filter_str = extract_filters(request.data)
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        prompt = f"""
        Podaj {count} utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        {filter_str}

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            raw_response = ask_openai("Jesteś ekspertem muzycznym i podajesz podobne utwory.", prompt)
            songs = self.parse_openai_json(raw_response)
            added, errors = self.add_songs_to_queue(
                user, songs, spotify,
                curveball_every=max(1, 50 // (user.curveball_enjoyment or 5))
            )

            return Response({"message": "Queue generated", "added": added, "errors": errors})
        except Exception as e:
            return Response({"error": str(e)}, status=500)



class GenerateFromTopView(GenerateQueueBase):
    def post(self, request):
        user = request.user
        count = int(request.data.get("count", 10))
        filter_str = extract_filters(request.data)

        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        top_tracks = [f"{t['name']} by {t['artists'][0]['name']}" for t in spotify.get_top_tracks().get("items", [])]
        top_artists = [a["name"] for a in spotify.get_top_artists().get("items", [])]

        if not top_tracks and not top_artists:
            return Response({"error": "No top tracks or artists available"}, status=400)

        prompt = f"""
        Na podstawie ulubionych utworów:
        {json.dumps(top_tracks, indent=2)}

        i ulubionych artystów:
        {json.dumps(top_artists, indent=2)}
        {filter_str}

        Podaj {count} nowych rekomendacji muzycznych w formacie JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            raw_response = ask_openai("Jesteś ekspertem muzycznym. Generujesz nowe utwory na podstawie gustu użytkownika.", prompt)
            songs = self.parse_openai_json(raw_response)
            added, errors = self.add_songs_to_queue(
                user, songs, spotify,
                curveball_every=max(1, 50 // (user.curveball_enjoyment or 5))
            )

            return Response({"message": "Queue from top tracks", "added": added, "errors": errors})
        except Exception as e:
            return Response({"error": str(e)}, status=500)



class CreateLikedPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)
        liked_songs = Media.objects.filter(user=user, feedback="like").exclude(spotify_uri=None)

        uris = [song.spotify_uri for song in liked_songs]
        if not uris:
            return Response({"error": "No liked songs to add"}, status=400)

        user_id = spotify.get_user_profile().get("id")
        if not user_id:
            return Response({"error": "Failed to get Spotify user ID"}, status=500)

        playlist_payload = {
            "name": "Liked Songs from App",
            "description": "Playlist of liked songs from the app",
            "public": False
        }

        create_response = requests.post(SPOTIFY_PLAYLIST_URL, headers=spotify.headers, json=playlist_payload)
        if create_response.status_code != 201:
            return Response({"error": "Failed to create playlist"}, status=500)

        playlist_id = create_response.json().get("id")
        for i in range(0, len(uris), 100):
            chunk = uris[i:i + 100]
            add_response = requests.post(
                SPOTIFY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id),
                headers=spotify.headers,
                json={"uris": chunk}
            )
            if add_response.status_code != 201:
                return Response({"error": "Failed to add tracks", "details": add_response.json()}, status=500)

        return Response({
            "message": "Playlist created and tracks added",
            "playlist_url": create_response.json().get("external_urls", {}).get("spotify")
        })

class GenerateFromArtistsView(GenerateQueueBase):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        artists = request.data.get("artists", [])
        count = int(request.data.get("count", 10))

        if not artists or not isinstance(artists, list):
            return Response({"error": "List of artists is required"}, status=400)

        filter_str = extract_filters(request.data)
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        prompt = f"""
        Podaj {count} utworów{filter_str}, inspirowanych twórczością artystów:
        {json.dumps(artists, indent=2)}

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            raw_response = ask_openai(
                "Jesteś ekspertem muzycznym. Generujesz nowe utwory inspirowane stylem podanych artystów i zgodne z określonym nastrojem, tempem lub stylem muzycznym.",
                prompt
            )
            songs = self.parse_openai_json(raw_response)
            added, errors = self.add_songs_to_queue(
                user, songs, spotify,
                curveball_every=max(1, 50 // (user.curveball_enjoyment or 5))
            )

            return Response({
                "message": "Queue generated from artists with filters",
                "added": added,
                "errors": errors
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
