from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import Media, UserFeedback
from songs.utils import update_curveball_enjoyment
from django.utils import timezone
import requests
from drf_spectacular.utils import extend_schema

from constants import SPOTIFY_TRACK_URL
from .serializers import SongFeedbackSerializer, SongFeedbackResponseSerializer


class SongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SongFeedbackSerializer,
        responses={200: SongFeedbackResponseSerializer},
        summary="Save user feedback for a song by Spotify URI",
        description=(
            "Saves user feedback (like, dislike, or none) for a song identified by its Spotify URI. "
            "If the song does not exist in the database, its metadata is fetched from Spotify and saved. "
            "Updates curveball enjoyment if applicable. "
            "Returns the status, track title, artist, and updated curveball enjoyment."
        ),
    )
    def post(self, request):
        spotify_uri = request.data.get("spotify_uri")
        feedback = request.data.get("feedback")

        if not spotify_uri or feedback not in ["like", "dislike", "none"]:
            return Response(
                {"error": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            media = Media.objects.get(spotify_uri=spotify_uri)
        except Media.DoesNotExist:
            token = request.user.spotify_access_token
            headers = {"Authorization": f"Bearer {token}"}
            track_id = spotify_uri.split(":")[-1]
            url = SPOTIFY_TRACK_URL.format(spotify_id=track_id)
            print("URI:", spotify_uri)
            print("Track ID:", track_id)
            resp = requests.get(url, headers=headers)

            if resp.status_code != 200:
                print("Spotify API error:", resp.status_code, resp.text)
                return Response(
                    {"error": "Could not fetch song data from Spotify"}, status=400
                )

            data = resp.json()
            media = Media.objects.create(
                spotify_uri=spotify_uri,
                title=data["name"],
                artist_name=data["artists"][0]["name"],
                album_name=data["album"]["name"],
                media_type=Media.SONG,
                genre=[],  # Not available via Spotify track API
                saved_at=timezone.now(),
            )

        liked = {"like": True, "dislike": False, "none": None}[feedback]

        if liked is not None:
            UserFeedback.objects.update_or_create(
                user=request.user,
                media=media,
                defaults={
                    "is_liked": liked,
                    "source": "feedback_by_uri",
                    "feedback_at": timezone.now().date(),
                },
            )

        if getattr(media, "is_curveball", False):
            update_curveball_enjoyment(request.user, liked)

        return Response(
            {
                "status": "ok",
                "track_title": media.title,
                "artist": media.artist_name,
                "curveball_enjoyment": request.user.curveball_enjoyment,
            }
        )
