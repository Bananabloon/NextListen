from django.urls import path
from .views import SpotifyOAuthRedirectView, SpotifyCallbackView, SpotifyLoginView

urlpatterns = [
    path("spotify/login/", SpotifyOAuthRedirectView.as_view(), name="spotify-login"),
    path("spotify/callback/", SpotifyCallbackView.as_view(), name="spotify-callback"),
    path("spotify/token-login/", SpotifyLoginView.as_view(), name="spotify-token-login"),
]
