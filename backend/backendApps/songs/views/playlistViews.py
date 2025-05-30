from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from spotifyData.services.spotifyClient import SpotifyAPI
from users.models import Media, UserFeedback
from songs.utils import find_best_match, create_playlist_with_uris
from songs.services.songGeneration import build_preferences_prompt, generate_songs_with_buffer
import logging
logger = logging.getLogger(__name__)
from constants import GENERATION_BUFFER_MULTIPLIER

class CreateLikedPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)
        
        liked = Media.objects.filter(user=user, feedback="like").exclude(spotify_uri=None)
        curveballs = liked.filter(is_curveball=True)

        if not liked.exists():
            return Response({"error": "No liked songs"}, status=400)

        all_uris = [m.spotify_uri for m in liked]
        curveball_uris = [m.spotify_uri for m in curveballs]

        playlists = []

        try:
            url = create_playlist_with_uris(user, spotify, "Liked Songs from App", "All liked songs", all_uris)
            playlists.append({"type": "all", "url": url})

            if curveball_uris:
                url = create_playlist_with_uris(user, spotify, "Liked Curveballs from App", "Curveballs you liked", curveball_uris)
                playlists.append({"type": "curveballs", "url": url})

            return Response({"message": "Playlists created", "playlists": playlists})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    
class CreatePlaylistFromPromptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt_input = request.data.get("prompt")
        playlist_name = request.data.get("name")
        count = int(request.data.get("count", 0))

        if not prompt_input or not playlist_name or count <= 0:
            return Response({"error": "prompt, name and positive count are required"}, status=400)

        preferences = self._get_user_preferences(user)
        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)

        preferences_prompt = build_preferences_prompt(preferences)
        full_prompt = f"""
        Podaj {count*GENERATION_BUFFER_MULTIPLIER} utworów pasujących do opisu:
        "{prompt_input}"

        {preferences_prompt}

        Tylko utwory i artyści, którzy rzeczywiście istnieją i są dostępni na Spotify.

        Format JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        try:
            songs, _ = generate_songs_with_buffer(
                prompt=full_prompt,
                base_prompt="Jesteś ekspertem muzycznym i tworzysz playlistę do opisu.",
                count=count
            )

            uris = []
            for song in songs:
                query = f"{song['title']} {song['artist']}"
                try:
                    result = spotify.search(query=query, type="track")
                    best_match = find_best_match(result["tracks"]["items"], song["title"], song["artist"])
                    if best_match:
                        uris.append(best_match["uri"])
                except Exception as e:
                    logger.warning(f"Search failed for {query}: {str(e)}")
                    continue

            if not uris:
                return Response({"error": "No tracks found to create playlist"}, status=400)

            playlist_url = create_playlist_with_uris(
                user=user,
                spotify=spotify,
                name=playlist_name,
                description=f"Generated playlist for: {prompt_input}",
                uris=uris
            )
            return Response({"message": "Playlist created", "url": playlist_url})

        except Exception as e:
            logger.exception("Playlist generation failed")
            return Response({"error": str(e)}, status=500)

    def _get_user_preferences(self, user):
        feedbacks = UserFeedback.objects.select_related("media").filter(user=user)

        liked_genres, liked_artists, disliked_genres, disliked_artists = set(), set(), set(), set()

        for fb in feedbacks:
            if fb.is_liked:
                liked_genres.update(fb.media.genre)
                liked_artists.add(fb.media.artist_name)
            else:
                disliked_genres.update(fb.media.genre)
                disliked_artists.add(fb.media.artist_name)

        return {
            "liked_genres": list(liked_genres),
            "liked_artists": list(liked_artists),
            "disliked_genres": list(disliked_genres),
            "disliked_artists": list(disliked_artists),
            "explicit_content": getattr(user, "allow_explicit", True)
        }