from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..services.spotifyClient import SpotifyAPI
from openai import OpenAI
from django.conf import settings
import json
from songs.utils import find_best_match

class DiscoveryGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        genre = request.data.get("genre")
        count = int(request.data.get("count", 10))

        if not genre:
            return Response({"error": "Missing 'genre' parameter"}, status=400)

        spotify = SpotifyAPI(user.spotify_access_token, refresh_token=user.spotify_refresh_token, user=user)
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        top_artists_data = spotify.get_top_artists(limit=10)
        top_tracks_data = spotify.get_top_tracks(limit=10)

        top_tracks = [f"{track['name']} by {track['artists'][0]['name']}" for track in top_tracks_data.get("items", [])]
        top_artists = [artist["name"] for artist in top_artists_data.get("items", [])]

        prompt = f"""
        Użytkownik zwykle słucha:
        Artyści: {json.dumps(top_artists, indent=2)}
        Utwory: {json.dumps(top_tracks, indent=2)}

        Teraz chce poznać nową muzykę z gatunku: {genre}

        Podaj {count} rekomendacji muzycznych w tym gatunku, w formacie JSON:
        [
          {{"title": "tytuł", "artist": "artysta"}}
        ]
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem muzycznym."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```") and raw_content.endswith("```"):
            raw_content = "\n".join(raw_content.split("\n")[1:-1])

        try:
            songs = json.loads(raw_content)
        except Exception:
            return Response({"error": "Failed to parse OpenAI response", "raw": raw_content}, status=500)

        added, errors = [], []
        for song in songs:
            query = f"{song['title']} {song['artist']}"
            search_result = spotify.search(query=query, type="track")

            try:
                matched = find_best_match(search_result["tracks"]["items"], song["title"], song["artist"])
                if matched:
                    uri = matched["uri"]
                    success, error = spotify.add_to_queue(uri)
                    if success:
                        added.append({"title": song["title"], "artist": song["artist"], "uri": uri})
                    else:
                        errors.append({"song": song, "error": error or "Could not add to queue"})
                else:
                    errors.append({"song": song, "error": "No match found"})
            except Exception as e:
                errors.append({"song": song, "error": str(e)})
        
        return Response({"message": f"Discovery queue generated for genre: {genre}", "genre": genre, "added": added, "errors": errors})
