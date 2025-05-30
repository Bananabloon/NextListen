from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from users.models import Media, UserFeedback
from songs.utils import (
    ask_openai,
    # should_send_curveball,
    update_curveball_enjoyment,
    # extract_filters,
)
from django.utils import timezone

from constants import SPOTYFY_TRACK_URL


class UserFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        media_data = request.data.get("media")
        is_liked = request.data.get("is_liked")
        source = request.data.get("source")

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


class SongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        song_id = request.data.get("song_id")
        feedback = request.data.get("feedback")  # "like", "dislike", "none"

        if not song_id or feedback not in ["like", "dislike", "none"]:
            return Response({"error": "Invalid input"}, status=400)

        media = get_object_or_404(Media, id=song_id)

        liked = {"like": True, "dislike": False, "none": None}[feedback]

        if liked is not None:
            UserFeedback.objects.update_or_create(
                user=request.user,
                media=media,
                defaults={
                    "is_liked": liked,
                    "source": "feedback_button",
                    "feedback_at": timezone.now().date(),
                },
            )

        if getattr(media, "is_curveball", False):
            update_curveball_enjoyment(request.user, liked)

        return Response(
            {"status": "ok", "curveball_enjoyment": request.user.curveball_enjoyment}
        )

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
            spotify_id = spotify_uri.split(":")[-1]
            headers = {"Authorization": f"Bearer {token}"}
            url = SPOTYFY_TRACK_URL
            resp = requests.get(url, headers=headers)

            if resp.status_code != 200:
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

        return Response(
            {
                "status": "ok",
                "track_title": media.title,
                "artist": media.artist_name,
                "curveball_enjoyment": request.user.curveball_enjoyment,
            }
        )
