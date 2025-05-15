from django.urls import path
from .views import RegisterView, MeView, PreferenceVectorView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('preference-vector/', PreferenceVectorView.as_view(), name='preference-vector'),
]
