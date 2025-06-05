from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import Media, UserFeedback
import requests

class AllUserFeedbacksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        feedbacks = UserFeedback.objects.filter(user=request.user).select_related('media')
        spotify_uris = [fb.media.spotify_uri for fb in feedbacks]

        if not spotify_uris:
            return Response({"feedbacks": []})

        # Podział paczek po max 50 URI (limit Spotify)
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        token = request.user.spotify_access_token
        headers = {"Authorization": f"Bearer {token}"}

        all_track_info = {}
        for chunk_uris in chunks(spotify_uris, 50):
            ids_param = ",".join(chunk_uris)
            url = f"https://api.spotify.com/v1/tracks?ids={ids_param}"
            resp = requests.get(url, headers=headers)

            if resp.status_code != 200:
                return Response({"error": "Spotify API error", "details": resp.json()}, status=400)

            data = resp.json().get("tracks", [])
            for track in data:
                all_track_info[track["uri"]] = {
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

            feedback_list.append({
                "spotify_uri": spotify_uri,
                "is_liked": fb.is_liked,
                "source": fb.source,
                "feedback_at": fb.feedback_at,
                "spotify_data": track_info
            })

        return Response({"feedbacks": feedback_list})

class SingleSongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spotify_uri = request.query_params.get("spotify_uri")

        if not spotify_uri:
            return Response({
                "error": "spotify_uri is required",
                "expected_format": {"spotify_uri": "<Spotify track URI>"}
            }, status=400)

        try:
            media = Media.objects.get(spotify_uri=spotify_uri)
            feedback = UserFeedback.objects.filter(user=request.user, media=media).first()

            value = 0 if feedback is None or feedback.is_liked is None else (1 if feedback.is_liked else -1)

            return Response({
                "spotify_uri": spotify_uri,
                "feedback_value": value
            })

        except Media.DoesNotExist:
            return Response({
                "spotify_uri": spotify_uri,
                "feedback_value": 0,
                "message": "No feedback found for this track."
            })
 