from django.urls import path
from .views import PreferenceVectorView

urlpatterns = [
    path('preference-vector/', PreferenceVectorView.as_view(), name='preference-vector'),
]
