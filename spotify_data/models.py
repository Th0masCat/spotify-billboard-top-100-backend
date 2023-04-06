from django.db import models


# Create your models here.

class SpotifyData(models.Model):
    user = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=100)
