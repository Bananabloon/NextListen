from rest_framework import serializers


class MediaSerializer(serializers.Serializer):
    spotify_uri = serializers.CharField()
    title = serializers.CharField()
    artist_name = serializers.CharField()
    album_name = serializers.CharField()
    media_type = serializers.CharField()
    saved_at = serializers.DateTimeField()
    genres = serializers.ListField(child=serializers.CharField(), required=False)


class UserFeedbackSerializer(serializers.Serializer):
    media = MediaSerializer()
    is_liked = serializers.BooleanField()
    source = serializers.CharField(required=False)


class SimilarSongsRequestSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()


class SimilarSongResponseItemSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()
    reason = serializers.CharField()


class SimilarSongsResponseSerializer(serializers.Serializer):
    results = serializers.ListSerializer(child=SimilarSongResponseItemSerializer())


class SongFeedbackSerializer(serializers.Serializer):
    spotify_uri = serializers.CharField()
    feedback = serializers.ChoiceField(choices=["like", "dislike", "none"])


class SongFeedbackResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    track_title = serializers.CharField()
    artist = serializers.CharField()
    curveball_enjoyment = serializers.FloatField()


class CreateLikedPlaylistsResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    playlists = serializers.ListSerializer(
        child=serializers.DictField(child=serializers.CharField())
    )


class PromptPlaylistRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    name = serializers.CharField()
    count = serializers.IntegerField(min_value=1)


class PromptPlaylistResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    url = serializers.URLField()


class BaseGenerateSerializer(serializers.Serializer):
    count = serializers.IntegerField(min_value=1)


class GenerateQueueSerializer(BaseGenerateSerializer):
    titles = serializers.ListField(
        child=serializers.CharField(), min_length=1
    )


class GenerateFromArtistsSerializer(BaseGenerateSerializer):
    artists = serializers.ListField(child=serializers.CharField(), allow_empty=False)


class GenerateFromPromptSerializer(BaseGenerateSerializer):
    prompt = serializers.CharField()


class SongAnalysisSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()


class SingleSongFeedbackRequestSerializer(serializers.Serializer):
    spotify_uri = serializers.CharField(required=True)


class TrackInfoSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()
    album = serializers.CharField()
    duration_ms = serializers.IntegerField()
    popularity = serializers.IntegerField()
    preview_url = serializers.URLField(allow_null=True)
    external_url = serializers.URLField()


class AllUserFeedbackSerializer(serializers.Serializer):
    spotify_uri = serializers.CharField()
    is_liked = serializers.BooleanField(allow_null=True)
    source = serializers.CharField()
    feedback_at = serializers.DateTimeField()
    spotify_data = TrackInfoSerializer()


class SingleSongFeedbackResponseSerializer(serializers.Serializer):
    spotify_uri = serializers.CharField()
    feedback_value = serializers.IntegerField()
    message = serializers.CharField(required=False)

class DiscoveryGenerateRequestSerializer(serializers.Serializer):
    genre = serializers.CharField(required=True, help_text="Genre to discover")
    count = serializers.IntegerField(
        required=False, default=10, min_value=1, max_value=50
    )

class DiscoveryGenerateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    genre = serializers.CharField()
    # songs = SongSerializer(many=True)
    errors = serializers.ListField(child=serializers.DictField())
