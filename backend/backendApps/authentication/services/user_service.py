from users.models import User
import logging

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def create_or_update_user(user_info, access_token, refresh_token=None):
        spotify_user_id = user_info["id"]
        display_name = user_info.get("displayname", "Unknown")

        user, _ = User.objects.get_or_create(spotify_user_id=spotify_user_id)
        user.display_name = display_name
        user.spotify_access_token = access_token
        user.market = user_info.get("country")
        explicit = user_info.get("explicit_content", {})
        user.explicit_content_enabled = not explicit.get("filter_enabled", False)

        if refresh_token:
            user.spotify_refresh_token = refresh_token

        user.save()
        return user
