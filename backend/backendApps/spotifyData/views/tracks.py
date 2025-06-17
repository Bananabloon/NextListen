from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
import requests
import os
import json
from django.conf import settings
from constants import SPOTIFY_SEARCH_URL
from .views_helpers import SpotifyBaseView
from difflib import SequenceMatcher

GENRE_FILE_PATH = os.path.join(settings.BASE_DIR, "genres.json")


class TopTracksView(SpotifyBaseView):
    @extend_schema(summary="Get user's top tracks", description="Most listened tracks.")
    def get(self, request):
        return Response(self.spotify.get_top_tracks())


class TopArtistsView(SpotifyBaseView):
    @extend_schema(
        summary="Get user's top artists", description="Most listened artists."
    )
    def get(self, request):
        return Response(self.spotify.get_top_artists())


class CurrentlyPlayingView(SpotifyBaseView):
    @extend_schema(
        summary="Get currently playing track", description="Track currently playing."
    )
    def get(self, request):
        return Response(self.spotify.get_current_playing())


class AddTrackToQueueView(SpotifyBaseView):
    @extend_schema(
        summary="Add track to queue",
        description="Adds a track to the user's Spotify queue.",
        request={"application/json": {"example": {"track_uri": "spotify:track:xyz"}}},
    )
    def post(self, request):
        (track_uri,) = self.require_fields(request.data, ["track_uri"])
        return self.respond_action(
            *self.spotify.add_to_queue(track_uri), message="Track added to queue"
        )


class SpotifySearchView(SpotifyBaseView):
    @extend_schema(
        summary="Search tracks, artists, or genres",
        description="Search on Spotify or local genres.",
        parameters=[
            OpenApiParameter(
                name="q", required=True, description="Search phrase", type=str
            ),
            OpenApiParameter(
                name="type",
                required=False,
                description="Search type: track, artist, or genre",
                type=str,
            ),
            OpenApiParameter(
                name="artist",
                required=False,
                description="Artist name (optional, improves accuracy)",
                type=str,
            ),
        ],
    )
    def get(self, request):
        query = request.query_params.get("q")
        search_type = request.query_params.get("type", "track")
        artist_filter = request.query_params.get("artist")

        if not query or search_type not in ["track", "artist", "genre"]:
            return Response(
                {"error": "Invalid query or type. Allowed types: track, artist, genre"},
                status=400,
            )

        if search_type == "genre":
            return self._search_genres(query)

        token = request.user.spotify_access_token
        headers = {"Authorization": f"Bearer {token}"}

        if search_type == "artist":
            query = f'artist:"{query}"'
        elif search_type == "track":
            query_parts = [f'track:"{query}"']
            if artist_filter:
                query_parts.append(f'artist:"{artist_filter}"')
            query = " ".join(query_parts)

        params = {"q": query, "type": search_type, "limit": 20}

        response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)
        if response.status_code != 200:
            return Response({"error": "Spotify API error"}, status=response.status_code)

        data = response.json()

        if search_type == "track" and "tracks" in data:
            original_query = request.query_params.get("q", "").lower()

            def similarity_score(track):
                name = track.get("name", "").lower()
                return SequenceMatcher(None, name, original_query).ratio()

            sorted_items = sorted(
                data["tracks"]["items"], key=similarity_score, reverse=True
            )
            data["tracks"]["items"] = sorted_items

        return Response(data)

    def _search_genres(self, query):
        """Search for genres in the local genres.json file"""
        try:
            with open(GENRE_FILE_PATH, "r", encoding="utf-8") as file:
                genres_data = json.load(file)

            if isinstance(genres_data, dict) and "genres" in genres_data:
                genres = genres_data["genres"]
            elif isinstance(genres_data, list):
                genres = genres_data
            else:
                return Response({"error": "Invalid genres file format"}, status=500)

            query_lower = query.lower()

            matching_genres = []
            for genre in genres:
                if isinstance(genre, str):
                    genre_name = genre
                    popularity = None
                elif isinstance(genre, dict):
                    genre_name = genre.get("category", "")
                    popularity = genre.get("popularity")
                else:
                    continue

                if query_lower in genre_name.lower():
                    similarity = SequenceMatcher(
                        None, genre_name.lower(), query_lower
                    ).ratio()
                    matching_genres.append(
                        {
                            "name": genre_name,
                            "similarity": similarity,
                            "type": "genre",
                            "uri": popularity,
                        }
                    )

            matching_genres.sort(key=lambda x: x["similarity"], reverse=True)
            matching_genres = matching_genres[:20]

            response_data = {
                "genres": {
                    "items": [
                        {"name": genre["name"], "type": "genre", "uri": genre["uri"]}
                        for genre in matching_genres
                    ],
                    "total": len(matching_genres),
                }
            }

            return Response(response_data)

        except FileNotFoundError:
            return Response({"error": "Genres file not found"}, status=500)
        except json.JSONDecodeError:
            return Response({"error": "Error decoding genres file"}, status=500)


class TransferPlaybackView(SpotifyBaseView):
    @extend_schema(
        summary="Transfer playback",
        description="Switch Spotify playback to selected device. Pauses current playback first.",
        request={"application/json": {"example": {"device_id": "abc123"}}},
    )
    def post(self, request):
        (device_id,) = self.require_fields(request.data, ["device_id"])

        paused, pause_response = self.spotify.pause_playback()
        if not paused:
            return Response(
                {"error": "Failed to pause playback", "detail": pause_response},
                status=400,
            )

        success, transfer_response = self.spotify.transfer_playback(device_id)
        if not success:
            return Response(
                {"error": "Failed to transfer playback", "detail": transfer_response},
                status=400,
            )

        return self.respond_action(
            True, transfer_response, message="Playback transferred successfully"
        )


class StartPlaybackView(SpotifyBaseView):
    @extend_schema(
        summary="Start playback of a track",
        description="Starts playback on selected device.",
        request={
            "application/json": {
                "example": {"device_id": "abc123", "track_uri": "spotify:track:xyz"}
            }
        },
    )
    def post(self, request):
        device_id, track_uri = self.require_fields(
            request.data, ["device_id", "track_uri"]
        )
        return self.respond_action(
            *self.spotify.start_playback(device_id, track_uri),
            message="Playback started",
        )
