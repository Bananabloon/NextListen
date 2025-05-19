from django.urls import path
from .views import SongAnalysisView, SimilarSongsView, GenerateQueueView, GenerateFromTopView

urlpatterns = [
    path('', SongAnalysisView.as_view(), name="song-list"),
    path('similar/', SimilarSongsView.as_view(), name="recomendations"),
    path('generate-queue/', GenerateQueueView.as_view(), name="generate-queue"),
    path('generate-from-top/', GenerateFromTopView.as_view()),

]
