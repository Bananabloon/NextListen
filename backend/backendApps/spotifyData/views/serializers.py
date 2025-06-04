from rest_framework import serializers


class AddTrackToQueueSerializer(serializers.Serializer):
    track_uri = serializers.CharField(help_text="URI of the track to add to the queue")


class StartPlaybackSerializer(serializers.Serializer):
    device_id = serializers.CharField(help_text="ID of the device to start playback on")
    track_uri = serializers.CharField(help_text="URI of the track to play")


class TransferPlaybackSerializer(serializers.Serializer):
    device_id = serializers.CharField(
        help_text="ID of the device to transfer playback to"
    )


class SpotifySearchSerializer(serializers.Serializer):
    q = serializers.CharField(help_text="Search query")
    type = serializers.ChoiceField(choices=["track", "artist"], help_text="Search type")


class GenreStatSerializer(serializers.Serializer):
    genre = serializers.CharField()
    count = serializers.IntegerField()


class ArtistStatSerializer(serializers.Serializer):
    artist = serializers.CharField()
    count = serializers.IntegerField()


class UserStatsResponseSerializer(serializers.Serializer):
    total_feedbacks = serializers.IntegerField()
    liked = serializers.IntegerField()
    disliked = serializers.IntegerField()
    curveball_enjoyment = serializers.FloatField()
    curveballs_total = serializers.IntegerField()
    curveballs_liked = serializers.IntegerField()
    top_genres = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )
    top_artists = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )
    most_common_media_type = serializers.CharField(allow_null=True)
    recent_top_genres = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )


class SpotifyProfileSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    email = serializers.EmailField()
    id = serializers.CharField()
    images = serializers.ListField(child=serializers.DictField(), required=False)
    product = serializers.CharField()
    country = serializers.CharField()
    followers = serializers.DictField()
    external_urls = serializers.DictField()
    href = serializers.CharField()
    type = serializers.CharField()
    uri = serializers.CharField()


class SpotifyTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class DiscoveryGenresResponseSerializer(serializers.Serializer):
    genres = serializers.ListField(
        child=serializers.CharField(), help_text="List of genres to discover"
    )


class DiscoveryGenerateRequestSerializer(serializers.Serializer):
    genre = serializers.CharField(required=True, help_text="Genre to discover")
    count = serializers.IntegerField(
        required=False, default=10, min_value=1, max_value=50
    )


class DiscoveredSongSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()
    uri = serializers.CharField()
    explicit = serializers.BooleanField()


class DiscoveryGenerateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    genre = serializers.CharField()
    songs = DiscoveredSongSerializer(many=True)
    errors = serializers.ListField(child=serializers.DictField())
