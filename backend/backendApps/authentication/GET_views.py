from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from authentication.services.spotify_service import SpotifyService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_top_artists(request):
    user = request.user  # ← pochodzi z JWT
    spotify_access_token = user.spotify_access_token

    if not spotify_access_token:
        return Response({'error': 'No Spotify token available'}, status=400)

    top_artists= SpotifyService.get_top_artists(spotify_access_token)
    return Response({'top_artists': top_artists})
