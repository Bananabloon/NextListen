from rest_framework import serializers
from .models import Genre, PreferenceVector, Media, UserFeedback, User

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genreName']


class PreferenceVectorSerializer(serializers.ModelSerializer):
    genreName = GenreSerializer()

    class Meta:
        model = PreferenceVector
        fields = ['id', 'genreName', 'preferences']


class MediaSerializer(serializers.ModelSerializer):
    genreName = GenreSerializer()

    class Meta:
        model = Media
        fields = ['id', 'spotifyMediaURI', 'title', 'artistName', 'genreName',
                  'albumName', 'typeOfMedia', 'savedAt']


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ['id', 'user', 'media', 'isLiked', 'source', 'feedbackAt']


class UserSerializer(serializers.ModelSerializer):
    preference_vectors = PreferenceVectorSerializer(source='preferencevector_set', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'spotifyUserId', 'displayName', 'createdAt', 'lastUpdated', 'curveballEnjoyment', 'preference_vectors']



class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['spotifyUserId', 'displayName']
