from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

urlpatterns = [
    path("", views.homepage),
    path("api/admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/users/", include("users.urls")),
    path("api/spotify/", include("spotifyData.urls")),
    path("api/songs/", include("songs.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
