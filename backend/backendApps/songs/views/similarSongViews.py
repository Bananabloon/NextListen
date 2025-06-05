
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import Media, UserFeedback
from songs.utils import ask_openai
from django.utils import timezone

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