from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import Media, UserFeedback
from drf_spectacular.utils import extend_schema
from .serializers import (
    SingleSongFeedbackRequestSerializer,
    SingleSongFeedbackResponseSerializer,
    AllUserFeedbackSerializer,
    TrackInfoSerializer,
)
import requests


class AllUserFeedbacksView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get all user feedbacks with Spotify track info",
        description=(
            "Returns a list of all feedback entries for the authenticated user, "
            "including detailed Spotify track information for each feedback."
        ),
        responses={200: AllUserFeedbackSerializer(many=True)},
    )
    def get(self, request):
        feedbacks = UserFeedback.objects.filter(user=request.user).select_related(
            "media"
        )
        spotify_uris = [fb.media.spotify_uri for fb in feedbacks]

        if not spotify_uris:
            return Response({"feedbacks": []})

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i : i + n]

        token = request.user.spotify_access_token
        headers = {"Authorization": f"Bearer {token}"}

        track_ids = [uri.split(":")[-1] for uri in spotify_uris] 
        all_track_info = {}

        for chunk_ids in chunks(track_ids, 50):
            ids_param = ",".join(chunk_ids)
            url = f"https://api.spotify.com/v1/tracks?ids={ids_param}"
            resp = requests.get(url, headers=headers)

            if resp.status_code != 200:
                return Response(
                    {"error": "Spotify API error", "details": resp.json()}, status=400
                )

            data = resp.json().get("tracks", [])
            for track in data:
                full_uri = f"spotify:track:{track['id']}"
                all_track_info[full_uri] = {
                    "title": track["name"],
                    "artist": ", ".join([a["name"] for a in track["artists"]]),
                    "album": track["album"]["name"],
                    "duration_ms": track["duration_ms"],
                    "popularity": track["popularity"],
                    "preview_url": track["preview_url"],
                    "external_url": track["external_urls"]["spotify"],
                }


        feedback_list = []
        for fb in feedbacks:
            spotify_uri = fb.media.spotify_uri
            track_info = all_track_info.get(spotify_uri, {})

            track_info_serializer = TrackInfoSerializer(data=track_info)
            if track_info and track_info_serializer.is_valid():
                spotify_data = track_info_serializer.data
            else:
                spotify_data = {}

            feedback_data = {
                "spotify_uri": spotify_uri,
                "is_liked": fb.is_liked,
                "source": fb.source,
                "feedback_at": fb.feedback_at,
                "spotify_data": spotify_data,
            }

            feedback_serializer = AllUserFeedbackSerializer(data=feedback_data)
            if feedback_serializer.is_valid():
                feedback_list.append(feedback_serializer.data)
            else:
                feedback_list.append(feedback_data)

        return Response({"feedbacks": feedback_list})


class SingleSongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get feedback for a single song",
        description=(
            "Returns the feedback value (like/dislike/none) for a single song identified by its Spotify URI, "
            "for the authenticated user."
        ),
        request=SingleSongFeedbackRequestSerializer,
        responses={200: SingleSongFeedbackResponseSerializer},
    )
    def get(self, request):
        serializer = SingleSongFeedbackRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        spotify_uri = serializer.validated_data["spotify_uri"]

        try:
            media = Media.objects.get(spotify_uri=spotify_uri)
            feedback = UserFeedback.objects.filter(
                user=request.user, media=media
            ).first()
            value = (
                0
                if feedback is None or feedback.is_liked is None
                else (1 if feedback.is_liked else -1)
            )
            response_data = {"spotify_uri": spotify_uri, "feedback_value": value}
        except Media.DoesNotExist:
            response_data = {
                "spotify_uri": spotify_uri,
                "feedback_value": 0,
                "message": "No feedback found for this track.",
            }

        response_serializer = SingleSongFeedbackResponseSerializer(response_data)
        return Response(response_serializer.data)
