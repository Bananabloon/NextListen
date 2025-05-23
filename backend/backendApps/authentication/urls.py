from django.urls import path
from .views import SpotifyOAuthRedirectView, SpotifyCallbackView


urlpatterns = [
    path("spotify/login/", SpotifyOAuthRedirectView.as_view(), name="spotify-login"),
    path("spotify/callback/", SpotifyCallbackView.as_view(), name="spotify-callback"),
]
