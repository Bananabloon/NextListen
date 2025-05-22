from django.urls import path
from .views import SpotifyOAuthRedirectView, SpotifyCallbackView, ProtectedView
from .GET_views import get_top_artists

urlpatterns = [
    path("spotify/login/", SpotifyOAuthRedirectView.as_view(), name="spotify-login"),
    path("spotify/callback/", SpotifyCallbackView.as_view(), name="spotify-callback"),
    path("spotify/ProtectedView/", ProtectedView.as_view(), name="spotify-me-view"),
    path('spotify/get-top-artists/', get_top_artists, name='get-top-artists'),
]
