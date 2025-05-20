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

import sys
sys.path.append("..")
from constants import SPOTIFY_PLAYLIST_TRACKS_URL, SPOTIFY_PLAYLIST_URL

class SongAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        song_title = request.data.get("title")
        artist_name = request.data.get("artist")

        if not song_title or not artist_name:
            return Response({"error": "title and artist are required"}, status=400)

        prompt = f"""
        Piosenka: {song_title}
        Artysta: {artist_name}
        Opisz utwór i podaj strukturę danych wg instrukcji.
        """

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                Jesteś ekspertem muzycznym. Na podstawie tytułu i artysty piosenki podaj:
                - tempo (slow/medium/fast)
                - nastrój (happy/sad/romantic/energetic/chill)
                - styl muzyczny (pop, jazz, electronic itd.)
                - ogólny opis utworu (2 zdania)
                Zwróć wynik jako obiekt JSON.
                """},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        data = response.choices[0].message.content
        return Response({"analysis": data})

class SongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        song_id = request.data.get("song_id")
        feedback = request.data.get("feedback")  # "like", "dislike", "none"

        if not song_id or feedback not in ["like", "dislike", "none"]:
            return Response({"error": "Invalid input"}, status=400)

        song = get_object_or_404(Media, id=song_id, user=request.user)

        if song.is_curveball:
            if feedback == "like":
                request.user.curveball_enjoyment = min(10, request.user.curveball_enjoyment + 1)
            elif feedback == "dislike":
                request.user.curveball_enjoyment = max(1, request.user.curveball_enjoyment - 1)
            request.user.save()

        return Response({"status": "ok", "curveball_enjoyment": request.user.curveball_enjoyment})

class SimilarSongsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        artist = request.data.get("artist")

        if not title or not artist:
            return Response({"error": "title and artist are required"}, status=400)

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

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

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem muzycznym i rekomendujesz podobne utwory."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return Response({"results": response.choices[0].message.content})

class GenerateQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        title = request.data.get("title")
        artist = request.data.get("artist")
        num_tracks = request.data.get("count", 10)

        if not title or not artist:
            return Response({"error": "title and artist required"}, status=400)

        # Ustawienia curveballi
        enjoyment = user.curveball_enjoyment or 5
        curveball_every = max(1, 50 // enjoyment)

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        prompt = f"""
        Podaj {num_tracks} utworów podobnych do:
        Tytuł: {title}
        Artysta: {artist}
        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem muzycznym i podajesz podobne utwory."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        raw_content = response.choices[0].message.content.strip()

        if raw_content.startswith("```") and raw_content.endswith("```"):
            raw_content = "\n".join(raw_content.split("\n")[1:-1])

        try:
            songs = json.loads(raw_content)
        except Exception as e:
            return Response({
                "error": "Failed to parse OpenAI response",
                "raw": response.choices[0].message.content
            }, status=500)
        
        added = []
        errors = []

        for idx, song in enumerate(songs):
            is_curveball = (idx + 1) % curveball_every == 0
            query = f"{song['title']} {song['artist']}"
            search_result = spotify.search(query=query, type="track")

            try:
                first_track = search_result["tracks"]["items"][0]
                uri = first_track["uri"]
                success, error = spotify.add_to_queue(uri)
                if success:
                    added.append({"title": song["title"], "artist": song["artist"], "uri": uri, "curveball": is_curveball})
                else:
                    errors.append({"song": song, "error": error})
            except Exception as e:
                errors.append({"song": song, "error": str(e)})

        return Response({
            "message": "Queue generated",
            "curveball_every": curveball_every,
            "added": added,
            "errors": errors
        })
    
class CreateLikedPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        liked_songs = Media.objects.filter(user=user, feedback="like").exclude(spotify_uri=None)
        uris = [song.spotify_uri for song in liked_songs]

        if not uris:
            return Response({"error": "No liked songs to add"}, status=400)

        user_profile = spotify.get_user_profile()
        user_id = user_profile.get("id")

        if not user_id:
            return Response({"error": "Failed to get Spotify user ID"}, status=500)

        playlist_data = {
            "name": "My Favorite Curveballs",
            "description": "Playlist of liked curveballs from the app",
            "public": False
        }

        create_response = requests.post(
            SPOTIFY_PLAYLIST_URL,
            headers=spotify.headers,
            json=playlist_data
        )

        if create_response.status_code != 201:
            return Response({"error": "Failed to create playlist"}, status=500)

        playlist = create_response.json()
        playlist_id = playlist["id"]

        chunk_size = 100
        for i in range(0, len(uris), chunk_size):
            chunk = uris[i:i + chunk_size]
            add_response = requests.post(
                SPOTIFY_PLAYLIST_TRACKS_URL,
                headers=spotify.headers,
                json={"uris": chunk}
            )
            if add_response.status_code != 201:
                return Response({"error": "Failed to add tracks", "details": add_response.json()}, status=500)

        return Response({
            "message": "Playlist created and tracks added",
            "playlist_url": playlist.get("external_urls", {}).get("spotify")
        })

class GenerateFromTopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        count = int(request.data.get("count", 10))
        enjoyment = user.curveball_enjoyment or 5
        curveball_every = max(1, 50 // enjoyment)

        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        top_tracks_data = spotify.get_top_tracks(limit=10)
        top_artists_data = spotify.get_top_artists(limit=5)

        top_tracks = [f"{track['name']} by {track['artists'][0]['name']}" for track in top_tracks_data.get("items", [])]
        top_artists = [artist["name"] for artist in top_artists_data.get("items", [])]

        if not top_tracks and not top_artists:
            return Response({"error": "No top tracks or artists available"}, status=400)

        prompt = f"""
        Na podstawie ulubionych utworów:
        {json.dumps(top_tracks, indent=2)}

        i ulubionych artystów:
        {json.dumps(top_artists, indent=2)}

        Podaj {count} nowych rekomendacji muzycznych w formacie JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem muzycznym. Generujesz nowe utwory dla użytkownika na podstawie jego gustu."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        raw_content = response.choices[0].message.content.strip()

        if raw_content.startswith("```") and raw_content.endswith("```"):
            raw_content = "\n".join(raw_content.split("\n")[1:-1])

        try:
            songs = json.loads(raw_content)
        except Exception as e:
            return Response({
                "error": "Failed to parse OpenAI response",
                "raw": response.choices[0].message.content
            }, status=500)

        added = []
        errors = []

        for idx, song in enumerate(songs):
            is_curveball = (idx + 1) % curveball_every == 0
            query = f"{song['title']} {song['artist']}"
            search_result = spotify.search(query=query, type="track")

            try:
                first_track = search_result["tracks"]["items"][0]
                uri = first_track["uri"]
                success, error = spotify.add_to_queue(uri)
                if success:
                    added.append({"title": song["title"], "artist": song["artist"], "uri": uri, "curveball": is_curveball})
                else:
                    errors.append({"song": song, "error": error})
            except Exception as e:
                errors.append({"song": song, "error": str(e)})

        return Response({
            "message": "Queue generated based on top tracks",
            "curveball_every": curveball_every,
            "added": added,
            "errors": errors
        })
