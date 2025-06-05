from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from songs.utils import ask_openai
from .serializers import SongAnalysisSerializer


class SongAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SongAnalysisSerializer,
        responses={200: None},
        summary="Analyze a song using AI",
        description=(
            "Analyzes a song based on its title and artist using AI. "
            "Returns the song's tempo (slow/medium/fast), mood (happy/sad/romantic/energetic/chill), "
            "musical style (e.g., pop, jazz, electronic), and a short description (max 2 sentences)."
        ),
    )
    def post(self, request):
        serializer = SongAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data["title"]
        artist = serializer.validated_data["artist"]

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
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
