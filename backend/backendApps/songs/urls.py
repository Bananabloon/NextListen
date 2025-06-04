from django.urls import path
from .views.feedbackViews import SongAnalysisView, SimilarSongsView, SongFeedbackView, SingleSongFeedbackView
from .views.generationViews import GenerateQueueView, GenerateFromTopView, GenerateFromArtistsView, GenerateQueueFromPromptView
from .views.playlistViews import CreateLikedPlaylistsView, CreatePlaylistFromPromptView

urlpatterns = [
    path('analysis/', SongAnalysisView.as_view(), name="song-list"),
    path('similar/', SimilarSongsView.as_view(), name="recomendations"),
    path('generate-from-song/', GenerateQueueView.as_view(), name="generate-queue"),
    path('generate-from-top/', GenerateFromTopView.as_view()),
    path('generate-from-artist/', GenerateFromArtistsView.as_view()),
    path('create-liked-playlist/', CreateLikedPlaylistsView.as_view()),
    path('feedback/update', SongFeedbackView.as_view(), name="make-feedback"),
    path("generate-queue-from-prompt/", GenerateQueueFromPromptView.as_view(), name="queue-from-prompt"),
    path("generate-playlist-from-prompt/", CreatePlaylistFromPromptView.as_view(), name="playlist-from-prompt"),
    path("feedback/", SingleSongFeedbackView.as_view(), name="get-feedback")
]
