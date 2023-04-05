from django.urls import path
from .views import SpotifyAuth, Data

urlpatterns = [
    path('', SpotifyAuth.as_view()),
    path('spot/', Data.as_view())
]