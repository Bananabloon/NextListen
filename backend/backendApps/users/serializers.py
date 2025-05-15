from rest_framework import serializers
from .models import Genre, PreferenceVector, Media, UserFeedback, User


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class PreferenceVectorSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()

    class Meta:
        model = PreferenceVector
        fields = ['id', 'genre', 'preferences']


class MediaSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()

    class Meta:
        model = Media
        fields = [
            'id', 'spotify_uri', 'title', 'artist_name',
            'genre', 'album_name', 'media_type', 'saved_at'
        ]


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ['id', 'user', 'media', 'is_liked', 'source', 'feedback_at']


class UserSerializer(serializers.ModelSerializer):
    preference_vectors = PreferenceVectorSerializer(source='preferencevector_set', many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'spotify_user_id', 'display_name',
            'created_at', 'last_updated', 'curveball_enjoyment',
            'preference_vectors'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['spotify_user_id', 'display_name']
