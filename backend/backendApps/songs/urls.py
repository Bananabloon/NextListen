from django.urls import path
from .views import SongAnalysisView  

urlpatterns = [
    path('', SongAnalysisView.as_view(), name="song-list"),
]
