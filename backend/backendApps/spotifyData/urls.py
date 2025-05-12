from django.urls import path
from .views import (
    CurrentUserProfileView,
    TopTracksView,
    CurrentlyPlayingView,
)

urlpatterns = [
    path("profile/", CurrentUserProfileView.as_view(), name="spotify-profile"),
    path("top-tracks/", TopTracksView.as_view(), name="spotify-top-tracks"),
    path("currently-playing/", CurrentlyPlayingView.as_view(), name="spotify-currently-playing"),
]
