from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import Media, UserFeedback
from songs.utils import ask_openai, update_curveball_enjoyment
from django.utils import timezone
import requests

from constants import SPOTIFY_TRACK_URL

class UserFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        media_data = request.data.get('media')
        is_liked = request.data.get('is_liked')
        source = request.data.get('source')
        
        if not media_data or is_liked is None:
            return Response(
                {"error": "Incomplete data."}, status=status.HTTP_400_BAD_REQUEST
            )

        genres = media_data.get("genres", [])

        media_obj, _ = Media.objects.get_or_create(
            spotify_uri=media_data["spotify_uri"],
            defaults={
                "title": media_data["title"],
                "artist_name": media_data["artist_name"],
                "album_name": media_data["album_name"],
                "media_type": media_data["media_type"],
                "saved_at": media_data["saved_at"],
                "genre": genres,
            },
        )

        media_obj.genre = genres
        media_obj.save(update_fields=["genre"])

        UserFeedback.objects.update_or_create(
            user=request.user,
            media=media_obj,
            defaults={
                "is_liked": is_liked,
                "source": source,
                "feedback_at": timezone.now().date(),
            },
        )

        return Response({"message": "Feedback saved."}, status=status.HTTP_200_OK)


class SongAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        artist = request.data.get("artist")

        if not title or not artist:
            return Response({"error": "title and artist are required"}, status=400)

        system_prompt = """
            Jesteś ekspertem muzycznym. Dla podanego utworu podaj:
            - tempo (slow/medium/fast)
            - nastrój (happy/sad/romantic/energetic/chill)
            - styl muzyczny (pop, jazz, electronic itd.)
            - krótki opis utworu (max 2 zdania)
            Wynik w formacie JSON.
            """

        user_prompt = f"Tytuł: {title}\nArtysta: {artist}"

        try:
            analysis = ask_openai(system_prompt, user_prompt)
            return Response({"analysis": analysis})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


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
                "Jesteś ekspertem muzycznym i rekomendujesz podobne utwory.", prompt
            )
            return Response({"results": response})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class SongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

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
                return Response({"error": "Could not fetch song data from Spotify"}, status=400)

            data = resp.json()
            media = Media.objects.create(
                spotify_uri=spotify_uri,
                title=data["name"],
                artist_name=data["artists"][0]["name"],
                album_name=data["album"]["name"],
                media_type=Media.SONG,
                genre=[],  # brak w track API
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

        return Response({
            "status": "ok",
            "track_title": media.title,
            "artist": media.artist_name,
            "curveball_enjoyment": request.user.curveball_enjoyment,
        })
    
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
