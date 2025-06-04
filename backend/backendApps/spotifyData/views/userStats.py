from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import UserFeedback, Media
from collections import Counter
from django.db.models import Count, Q
from datetime import timedelta
from django.utils import timezone

class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        feedbacks = UserFeedback.objects.filter(user=user).select_related("media")

        total = feedbacks.count()
        liked = feedbacks.filter(is_liked=True).count()
        disliked = feedbacks.filter(is_liked=False).count()

        curveballs = feedbacks.filter(source="curveball")
        liked_curveballs = curveballs.filter(is_liked=True).count()

        genre_counter = Counter()
        for f in feedbacks:
            genre_counter.update(f.media.genre)

        top_genres = genre_counter.most_common(5)

        artist_counter = Counter(f.media.artist_name for f in feedbacks)
        top_artists = artist_counter.most_common(5)

        media_type_counter = Counter(f.media.media_type for f in feedbacks)
        most_common_type = media_type_counter.most_common(1)

        month_ago = timezone.now().date() - timedelta(days=30)
        recent_feedback = feedbacks.filter(feedback_at__gte=month_ago)
        recent_genres = Counter()
        for f in recent_feedback:
            recent_genres.update(f.media.genre)
        recent_top_genres = recent_genres.most_common(3)

        return Response({
            "total_feedbacks": total,
            "liked": liked,
            "disliked": disliked,
            "curveball_enjoyment": user.curveball_enjoyment,
            "curveballs_total": curveballs.count(),
            "curveballs_liked": liked_curveballs,
            "top_genres": top_genres,
            "top_artists": top_artists,
            "most_common_media_type": most_common_type[0][0] if most_common_type else None,
            "recent_top_genres": recent_top_genres,
        })

