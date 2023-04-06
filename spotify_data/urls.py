from django.urls import path
from .views import Auth, spotify_callback, Playlist

urlpatterns = [
    path('', Auth.as_view()),
    path('spot/', spotify_callback),
    path('playlist/' , Playlist.as_view())
]