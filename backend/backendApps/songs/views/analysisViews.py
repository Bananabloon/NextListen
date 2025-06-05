from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from songs.utils import ask_openai

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