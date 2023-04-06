from .models import SpotifyData
from django.utils import timezone
from datetime import timedelta
from requests import post

CLIENT_ID = "4be9b45f83eb4c57bdf6cf341033711d"
CLIENT_SECRET = "de20e5ada839492eacc35ae7a18b02fb"

def get_user_tokens(session_id):
    user_tokens = SpotifyData.objects.filter(user=session_id)
    print(user_tokens)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None


def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyData(user=session_id, access_token=access_token,refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()
        
        