from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.shortcuts import redirect
from urllib.parse import urlencode
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.models import Media, UserFeedback

from .services.spotify_service import SpotifyService
from .services.spotify_auth_service import SpotifyAuthService
from .services.token_service import TokenService, CustomRefreshToken
from constants import SPOTIFY_AUTHORIZE_URL
from django.conf import settings


from .serializers import (
    TokenRefreshResponseSerializer,
    ErrorSerializer,
    EmptyRequestSerializer,
)


class SpotifyOAuthRedirectView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Redirect to Spotify OAuth",
        description="Redirects the user to Spotify's authorization URL.",
        responses={302: OpenApiResponse(description="Redirect to Spotify OAuth")},
    )
    def get(self, request):
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "scope": (
                "streaming user-read-email user-read-private user-top-read user-read-playback-state "
                "user-modify-playback-state user-read-currently-playing user-read-recently-played"
            ),
            "show_dialog": True,
        }
        url = f"{SPOTIFY_AUTHORIZE_URL}?{urlencode(params)}"
        return redirect(url)


class SpotifyCallbackView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Handle Spotify Callback",
        description="Handles Spotify's OAuth callback with authorization code.",
        responses={
            302: OpenApiResponse(
                description="Redirect to frontend with tokens set in cookies"
            ),
            400: ErrorSerializer,
        },
    )
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            return Response({"error": "No code provided"}, status=400)

        token_data = SpotifyService.exchange_code_for_spotify_token(code)
        if not token_data:
            return Response({"error": "Failed to get access token"}, status=400)

        spotify_access_token = token_data.get("access_token")
        spotify_refresh_token = token_data.get("refresh_token")

        data, error = SpotifyAuthService.authenticate_spotify_user(
            spotify_access_token, spotify_refresh_token
        )
        if error:
            return error

        response = redirect(f"{settings.NGROK_URL}/callback")
        TokenService.set_cookie_access_token(response, data["access"])
        TokenService.set_cookie_refresh_token(response, data["refresh"])
        return response


class RefreshAccessToken(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Refresh access token",
        description="Refreshes the access token using the refresh token stored in cookies.",
        request=EmptyRequestSerializer,
        responses={
            200: TokenRefreshResponseSerializer,
            400: ErrorSerializer,
            401: ErrorSerializer,
        },
    )
    def post(self, request):
        refresh_token_str = request.COOKIES.get("NextListen_refresh_token")
        if not refresh_token_str:
            return Response(
                {"detail": "No refresh token provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = CustomRefreshToken(refresh_token_str)
            new_access_token = refresh.access_token

            response = Response({"access": str(new_access_token)})

            TokenService.set_cookie_access_token(response, str(new_access_token))
            return response

        except (TokenError, InvalidToken):
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class DeleteTokens(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Delete auth cookies",
        description="Deletes the access and refresh tokens from cookies.",
        request=EmptyRequestSerializer,
        responses={200: OpenApiResponse(description="Tokens deleted")},
    )
    def post(self, request):
        response = Response(
            {"detail": "Tokens deleted successfully."}, status=status.HTTP_200_OK
        )
        TokenService.delete_cookie_access_token(response)
        TokenService.delete_cookie_refresh_token(response)
        return response


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        media_ids = UserFeedback.objects.filter(user=user).values_list(
            "media_id", flat=True
        )
        Media.objects.filter(id__in=media_ids).delete()
        UserFeedback.objects.filter(user=user).delete()

        user.delete()

        response = Response(
            {"detail": "Account and related data deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )
        TokenService.delete_cookie_access_token(response)
        TokenService.delete_cookie_refresh_token(response)

        return response


class DeleteUserDataView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user

        media_ids = UserFeedback.objects.filter(user=user).values_list(
            "media_id", flat=True
        )
        Media.objects.filter(id__in=media_ids).delete()
        UserFeedback.objects.filter(user=user).delete()

        return Response({"detail": "User data deleted."}, status=status.HTTP_200_OK)
