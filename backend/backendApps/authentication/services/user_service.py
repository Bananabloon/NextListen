from datetime import timedelta
from django.utils import timezone
from users.models import User, Artist
from rest_framework.response import Response
from .spotify_service import SpotifyService
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def create_or_update_user(user_info, access_token, refresh_token=None):
        spotify_user_id = user_info["id"]
        display_name = user_info.get("display_name", "Unknown")

        user, _ = User.objects.get_or_create(spotify_user_id=spotify_user_id)
        user.display_name = display_name
        user.spotify_access_token = access_token
        user.market = user_info.get("country")

        if refresh_token:
            user.spotify_refresh_token = refresh_token

        now = timezone.now()

        if not user.last_updated or now - user.last_updated > timedelta(days=1):
            logger.info(f"Fetching top artists for user {user.display_name}")
            UserService.fetch_and_update_top_artists(user, access_token)
            user.last_updated = now
        else:
            logger.info(f"Skipping top artist update for {user.display_name}: updated less than 24h ago")

        user.save()
        return user

    @staticmethod
    def fetch_and_update_top_artists(user, access_token): #to chyba nie powinno tutaj być
        artists = SpotifyService.get_top_artists(access_token)
        Artist.objects.filter(user=user).delete()
        for artist in artists:
            Artist.objects.create(
                user=user,
                name=artist["name"],
                spotify_uri=artist["uri"]
            )
