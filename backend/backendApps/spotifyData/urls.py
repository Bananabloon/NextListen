from django.urls import path
from .views import (
    CurrentUserProfileView,
    TopTracksView,
    CurrentlyPlayingView,
    GeneratePreferencesFromTopTracksView,
    AudioFeaturesView
)

urlpatterns = [
    path("profile/", CurrentUserProfileView.as_view(), name="spotify-profile"),
    path("top-tracks/", TopTracksView.as_view(), name="spotify-top-tracks"),
    path("currently-playing/", CurrentlyPlayingView.as_view(), name="spotify-currently-playing"),
    path("audio-features/<str:track_id>/", AudioFeaturesView.as_view(), name="audio-features"),
    path("generate-preferences/", GeneratePreferencesFromTopTracksView.as_view())
]
