from django.urls import path
from .views import SongAnalysisView, SimilarSongsView, GenerateQueueView, GenerateFromTopView, GenerateFromArtistsView

urlpatterns = [
    path('', SongAnalysisView.as_view(), name="song-list"),
    path('similar/', SimilarSongsView.as_view(), name="recomendations"),
    path('generate-from-song/', GenerateQueueView.as_view(), name="generate-queue"),
    path('generate-from-top/', GenerateFromTopView.as_view()),
    path('generate-from-artist/', GenerateFromArtistsView.as_view()),
    
]
