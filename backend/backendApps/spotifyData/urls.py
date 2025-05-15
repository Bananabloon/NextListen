from django.urls import path
from .views import (
    CurrentUserProfileView,
    TopTracksView,
    TopArtistsView,
    CurrentlyPlayingView,
    GeneratePreferencesFromTopTracksView,
    AudioFeaturesView,
    AddTrackToQueueView,
    SpotifySearchView,
)

urlpatterns = [
    path('profile/', CurrentUserProfileView.as_view()),
    path('top-tracks/', TopTracksView.as_view()),
    path('top-artists/', TopArtistsView.as_view()),
    path('currently-playing/', CurrentlyPlayingView.as_view()),
    path('generate-preferences/', GeneratePreferencesFromTopTracksView.as_view()),
    path('audio-features/<str:track_id>/', AudioFeaturesView.as_view()),
    path('search/', SpotifySearchView.as_view()),
    path("queue/add/", AddTrackToQueueView.as_view(), name="add-track-to-queue"),
]