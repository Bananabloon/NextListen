from django.conf import settings
import openai
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openai import OpenAI
from django.shortcuts import get_object_or_404

class SongAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        song_title = request.data.get("title")
        artist_name = request.data.get("artist")

        if not song_title or not artist_name:
            return Response({"error": "title and artist are required"}, status=400)

        prompt = f"""
        Piosenka: {song_title}
        Artysta: {artist_name}
        Opisz utwór i podaj strukturę danych wg instrukcji.
        """

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """
                Jesteś ekspertem muzycznym. Na podstawie tytułu i artysty piosenki podaj:
                - tempo (slow/medium/fast)
                - nastrój (happy/sad/romantic/energetic/chill)
                - styl muzyczny (pop, jazz, electronic itd.)
                - ogólny opis utworu (2 zdania)
                Zwróć wynik jako obiekt JSON.
                """},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        data = response.choices[0].message.content
        return Response({"analysis": data})

class SongFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        song_id = request.data.get("song_id")
        feedback = request.data.get("feedback")  # "like", "dislike", "none"

        if not song_id or feedback not in ["like", "dislike", "none"]:
            return Response({"error": "Invalid input"}, status=400)

        #AnalyzedSong - temp. (not working)
        song = get_object_or_404(AnalyzedSong, id=song_id, user=request.user)

        if song.is_curveball:
            if feedback == "like":
                request.user.curveball_enjoyment = min(10, request.user.curveball_enjoyment + 1)
            elif feedback == "dislike":
                request.user.curveball_enjoyment = max(1, request.user.curveball_enjoyment - 1)
            request.user.save()

        return Response({"status": "ok", "curveball_enjoyment": request.user.curveball_enjoyment})
