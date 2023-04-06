from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
import requests
import json
import aiohttp
from bs4 import BeautifulSoup
from .models import SpotifyData

from .util import update_or_create_user_tokens, get_user_tokens

from requests import Request, post

SPOTIFY_AUTH_ENDPOINT = "https://accounts.spotify.com/authorize"
CLIENT_ID = "4be9b45f83eb4c57bdf6cf341033711d"
REDIRECT_URI = "http://127.0.0.1:8000/spot/"
SCOPES = ["playlist-read-private user-read-private user-read-email user-library-read playlist-modify-public playlist-modify-private"]
SCOPES_URL_PARAM = "%20".join(SCOPES)
RESPONSE_TYPE = "code"

# Create your views here.

res = []

class Auth(APIView):
    def get(self, request):
        url = Request(
            'GET',
            SPOTIFY_AUTH_ENDPOINT,
            params= 
            {
                'scope': SCOPES_URL_PARAM,
                'response_type': RESPONSE_TYPE,
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID
            }
        ).prepare().url
        
        return Response({'url': url}, status=200)
        
        
def spotify_callback(request):
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    response = post("https://accounts.spotify.com/api/token"
        ,
        data=
        {
            "code": code, 
            "redirect_uri": REDIRECT_URI, 
            "grant_type": "authorization_code", 
        }, headers={
            "Authorization": "Basic NGJlOWI0NWY4M2ViNGM1N2JkZjZjZjM0MTAzMzcxMWQ6ZGUyMGU1YWRhODM5NDkyZWFjYzM1YWU3YTE4YjAyZmI=",
            "Content-Type": "application/x-www-form-urlencoded"
        }   
        
        ).json()
    
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')
    
    if not request.session.exists(request.session.session_key):
        request.session.create()
    
    update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)
    
    return redirect('http://localhost:5173/date')


class Playlist(APIView):
    def get(self, request):
        access_token = SpotifyData.objects.all().values('access_token')[0].get('access_token')
        print(access_token)
        USER_ID_ENDPOINT = "https://api.spotify.com/v1/me"
        
        spotify_userID = requests.get(USER_ID_ENDPOINT, headers={
            "Authorization": "Bearer " + access_token
        }
        ).json().get('id')
            
            
        spotify_create_playlist = f'https://api.spotify.com/v1/users/{spotify_userID}/playlists'

        print("Billboard Top 100")
        date = request.GET.get('date')

        data_create_playlist = json.dumps({
        "name": date,
        "description": "Billboard Top 100 on " + date,
        "public": False
        })

        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json',
            "Accept": "application/json"
        }

        response_create_playlist = requests.post(spotify_create_playlist, data=data_create_playlist, headers=headers)
        print(response_create_playlist.text)
        spotify_playlist_id = response_create_playlist.json().get('id')

        spotify_endpoint = f'https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks'
        billboard_url = f"https://www.billboard.com/charts/hot-100/{date}"
        spotify_search_endpoint = "https://api.spotify.com/v1/search"

        response_billboard = requests.get(billboard_url)

        soup = BeautifulSoup(response_billboard.text, "html.parser")
        fetch_list=soup.select(".a-no-trucate")

        data_list = [record.getText().strip() for record in fetch_list ]

        song_list = [data_list[i] for i in range(0,len(data_list), 2)]
        artist_list = [data_list[i] for i in range(1,len(data_list), 2)]


        for i in range(20):
            track_params = {
                'q': song_list[i] + " " + artist_list[i],
                'type': 'track,artist'
            }

            
            search_response = requests.get(spotify_search_endpoint, params=track_params, headers=headers)
            search_response_json = search_response.json().get('tracks').get('items')[0].get('uri')
            print(search_response_json)

            spotify_params = {
                "uris": f"{search_response_json}",
                "position": 0
            }

            response = requests.post(spotify_endpoint, headers=headers, params=spotify_params)
            print(response.text)

        return JsonResponse({'success': True}, status=200)


        