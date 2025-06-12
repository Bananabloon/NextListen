from django.urls import path
from .views.genres import DiscoveryGenresView
from .views.userStats import UserStatsView
from .views.solidData import GetArtistView
from .views.profile import CurrentUserProfileView, SpotifyTokenView
from .views.liked import (
    LikedTracksView,
    LikeTrackView,
    RemoveLikedTrackView,
    AreTracksLikedView,
)
from .views.tracks import (
    TopTracksView,
    TopArtistsView,
    CurrentlyPlayingView,
    SpotifySearchView,
    AddTrackToQueueView,
    TransferPlaybackView,
    StartPlaybackView,
)


urlpatterns = [
    path("are-tracks-liked/", AreTracksLikedView.as_view()),
    path("profile/", CurrentUserProfileView.as_view()),
    path("tokens/", SpotifyTokenView.as_view()),
    path("top-tracks/", TopTracksView.as_view()),
    path("top-artists/", TopArtistsView.as_view()),
    path("currently-playing/", CurrentlyPlayingView.as_view()),
    path("search/", SpotifySearchView.as_view()),
    path("queue/add/", AddTrackToQueueView.as_view(), name="add-track-to-queue"),
    path("discover/", DiscoveryGenresView.as_view()),
    path("user-stats/", UserStatsView.as_view()),
    path("playback/transfer/", TransferPlaybackView.as_view()),
    path("playback/start/", StartPlaybackView.as_view()),
    path("liked-tracks/", LikedTracksView.as_view()),
    path("liked-tracks/like/", LikeTrackView.as_view()),
    path("liked-tracks/remove/", RemoveLikedTrackView.as_view()),
    path("get-artist/", GetArtistView.as_view()),
]
