from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from ..services.spotifyClient import SpotifyAPI


class SpotifyBaseView(APIView):
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.spotify = self.get_spotify_instance(request.user)

    @staticmethod
    def get_spotify_instance(user):
        return SpotifyAPI(
            access_token=user.spotify_access_token,
            refresh_token=user.spotify_refresh_token,
            user=user,
        )

    def require_fields(self, data, fields):
        missing = [f for f in fields if not data.get(f)]
        if missing:
            raise ValidationError({f: "This field is required." for f in missing})
        return [data[f] for f in fields]

    def respond_action(self, success, error, message, status_ok=200, status_err=400):
        return Response(
            {"message": message} if success else {"error": message, "details": error},
            status=status_ok if success else status_err,
        )
