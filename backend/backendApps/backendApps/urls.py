from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from . import views

urlpatterns = [
    # Strona główna
    path("", views.homepage),
    # Widok informacyjny
    path("api/about/", views.about),
    # Admin panel
    path("api/admin/", admin.site.urls),
    # Endpointy aplikacji
    path("api/auth/", include("authentication.urls")),
    path("api/users/", include("users.urls")),
    path("api/spotify/", include("spotifyData.urls")),
    path("api/songs/", include("songs.urls")),
    # Dokumentacja OpenAPI (drf-spectacular)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
