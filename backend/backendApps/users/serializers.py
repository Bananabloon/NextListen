from rest_framework import serializers
from .models import Media, UserFeedback, User


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            "id",
            "spotify_uri",
            "title",
            "artist_name",
            "genres",
            "album_name",
            "media_type",
            "saved_at",
        ]


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ["id", "user", "media", "is_liked", "source", "feedback_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'spotify_user_id', 'display_name',
            'created_at', 'last_updated', 'curveball_enjoyment',
            'explicit_content_enabled'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["spotify_user_id", "display_name"]
