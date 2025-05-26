from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from spotifyData.services.spotifyClient import SpotifyAPI
from users.models import Media
from constants import SPOTIFY_PLAYLIST_TRACKS_URL, SPOTIFY_PLAYLIST_URL
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
            chunk = uris[i:i + 100]
            add_response = requests.post(
                SPOTIFY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id),
                headers=spotify.headers,
                json={"uris": chunk},
            )
            if add_response.status_code != 201:
                return None

        return create_response.json().get("external_urls", {}).get("spotify")
