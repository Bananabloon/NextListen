from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import requests
from spotifyData.services.spotifyClient import SpotifyAPI
from users.models import Media, UserFeedback
from songs.utils import ask_openai, find_best_match
import json
from songs.services.songGeneration import build_preferences_prompt, generate_songs_with_buffer
import pprint
pp = pprint.PrettyPrinter(indent=2)

import sys
sys.path.append("..")
from constants import SPOTIFY_PLAYLIST_TRACKS_URL, SPOTIFY_PLAYLIST_URL

def create_playlist_with_uris(user, spotify, name, description, uris):
    spotify = SpotifyAPI(
        user.spotify_access_token,
        refresh_token=user.spotify_refresh_token,
        user=user
    )
    playlist_payload = {
        "name": name,
        "description": description,
        "public": False
    }

    user_id = spotify.get_user_profile().get("id")
    create_response = requests.post(
    SPOTIFY_PLAYLIST_URL.format(user_id=user_id),
    headers=spotify.headers,
    json=playlist_payload
)


    if create_response.status_code != 201:
        print("Failed to create playlist:", create_response.status_code, create_response.text)
        return None

    response_data = create_response.json()
    pp.pprint(response_data)

    playlist_id = response_data.get("id")
    if not playlist_id:
        print(" No playlist ID found in response!")
    else:
        print(" Playlist ID:", playlist_id)

    external_urls = response_data.get("external_urls", {})
    print(" External URLs:", external_urls)


    for i in range(0, len(uris), 100):
        chunk = uris[i:i + 100]
        add_response = requests.post(
            SPOTIFY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id),
            headers=spotify.headers,
            json={"uris": chunk}
        )
        if add_response.status_code != 201:
            print("Failed to add tracks:", add_response.status_code, add_response.text)
            return None

    # Fallback jeśli external_urls brak
    playlist_url = response_data.get("external_urls", {}).get("spotify")
    if not playlist_url and playlist_id:
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        print("Fallback playlist URL:", playlist_url)

    return playlist_url

class CreateLikedPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        spotify = SpotifyAPI(
            user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user
        )
        
        all_liked_songs = Media.objects.filter(user=user, feedback="like").exclude(spotify_uri=None)
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
            uris=all_liked_uris
        )
        if liked_playlist_url:
            created_playlists.append({"type": "all", "url": liked_playlist_url})

        if curveball_uris:
            curveball_playlist_url = self._create_playlist_with_uris(
                spotify,
                name="Liked Curveballs from App",
                description="Only curveballs you've liked in the app",
                uris=curveball_uris
            )
            if curveball_playlist_url:
                created_playlists.append({"type": "curveballs", "url": curveball_playlist_url})

        return Response({
            "message": "Playlists created successfully",
            "playlists": created_playlists
        })

    
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
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        preferences_prompt = build_preferences_prompt(preferences)
        full_prompt = f"""
        Podaj {count} utworów pasujących do opisu:
        "{prompt_input}"

        {preferences_prompt}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            songs, buffer = generate_songs_with_buffer(
                prompt=full_prompt,
                base_prompt="Jesteś ekspertem muzycznym i tworzysz playlistę do opisu.",
                count=count
            )

            if not songs:
                return Response({"error": "No valid songs returned from AI"}, status=500)

            uris = []
            for song in songs:
                query = f"{song['title']} {song['artist']}"
                result = spotify.search(query=query, type="track")
                tracks = result["tracks"]["items"]
                best_match = find_best_match(tracks, song["title"], song["artist"])
                if best_match:
                    uris.append(best_match["uri"])

            if not uris:
                return Response({"error": "No tracks found to create playlist"}, status=400)

            playlist_url = create_playlist_with_uris(
                user,
                spotify,
                name=playlist_name,
                description=f"Generated playlist for: {prompt_input}",
                uris=uris
            )
            return Response({"message": "Playlist created", "url": playlist_url})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def get_user_preferences(self, user):
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
            "explicit_content": user.allow_explicit if hasattr(user, "allow_explicit") else True
        }