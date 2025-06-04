from django.urls import path
from .views import (
    SpotifyOAuthRedirectView,
    SpotifyCallbackView,
    RefreshAccessToken,
    DeleteTokens,
    DeleteAccountView, 
    DeleteUserDataView
)


urlpatterns = [
    path("spotify/login/", SpotifyOAuthRedirectView.as_view(), name="spotify-login"),
    path("spotify/callback/", SpotifyCallbackView.as_view(), name="spotify-callback"),
    path("spotify/refresh-token/", RefreshAccessToken.as_view(), name="refresh-token"),
    path("spotify/delete-tokens/", DeleteTokens.as_view(), name="delete-tokens"),
    path("spotify/delete-account/", DeleteAccountView.as_view(), name="delete_account"),
    path("spotify/delete-user-data/", DeleteUserDataView.as_view(), name="delete_user_data"),
]
