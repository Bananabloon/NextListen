import logging
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class TokenService:
    @staticmethod
    def generate_tokens_for_user(user):
        refresh = CustomRefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def set_cookie_access_token(response, access):
        response.set_cookie(
            key="NextListen_access_token",
            value=access,
            httponly=True,
            secure=True,
            max_age=1800,
            samesite="Lax",
            path="/",
        )

    @staticmethod
    def set_cookie_refresh_token(response, refresh):
        response.set_cookie(
            key="NextListen_refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            max_age=7 * 24 * 3600,
            samesite="Lax",
            path="/",
        )


class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["id"] = user.id
        token["spotify_user_id"] = user.spotify_user_id
        token["display_name"] = user.display_name
        return token
