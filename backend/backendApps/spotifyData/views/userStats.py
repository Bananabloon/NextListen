from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from datetime import timedelta
from django.utils import timezone
from collections import Counter
from .views_helpers import SpotifyBaseView
from users.models import UserFeedback
from .serializers import UserStatsResponseSerializer


class UserStatsView(SpotifyBaseView):
    @extend_schema(
        summary="User statistics",
        description=(
            "Returns statistics about the user's activity in the music recommendation system. "
            "Includes the total number of feedbacks, liked and disliked tracks, curveball information, "
            "top genres, artists, and media types, as well as the most listened genres from the last 30 days."
        ),
        responses=UserStatsResponseSerializer,
    )
    def get(self, request):
        user = request.user
        feedbacks = UserFeedback.objects.filter(user=user).select_related("media")

        total_feedbacks = feedbacks.count()
        liked_count = feedbacks.filter(is_liked=True).count()
        disliked_count = total_feedbacks - liked_count

        curveballs = feedbacks.filter(source="curveball")
        curveballs_total = curveballs.count()
        curveballs_liked = curveballs.filter(is_liked=True).count()

        top_genres = self.get_top_counts(feedbacks, "genre", 5)
        top_artists = self.get_top_counts(feedbacks, "artist_name", 5)
        most_common_media_type = self.get_most_common_value(feedbacks, "media_type")

        month_ago = timezone.now() - timedelta(days=30)
        recent_feedbacks = feedbacks.filter(feedback_at__gte=month_ago)
        recent_top_genres = self.get_top_counts(recent_feedbacks, "genre", 3)

        data = {
            "total_feedbacks": total_feedbacks,
            "liked": liked_count,
            "disliked": disliked_count,
            "curveball_enjoyment": user.curveball_enjoyment,
            "curveballs_total": curveballs_total,
            "curveballs_liked": curveballs_liked,
            "top_genres": top_genres,
            "top_artists": top_artists,
            "most_common_media_type": most_common_media_type,
            "recent_top_genres": recent_top_genres,
        }

        return Response(data)

    def get_top_counts(self, queryset, field_name, limit):
        values = queryset.values_list(f"media__{field_name}", flat=True)

        flattened = []
        for value in values:
            if isinstance(value, list):
                flattened.extend(value)
            elif value is not None:
                flattened.append(value)
        return Counter(flattened).most_common(limit)
    
    def get_most_common_value(self, queryset, field_name):
        values = queryset.values_list(f"media__{field_name}", flat=True)
        return Counter(values).most_common(1)[0][0] if values else None

