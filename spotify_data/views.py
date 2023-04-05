from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect, JsonResponse
import requests
import json
from bs4 import BeautifulSoup

SPOTIFY_AUTH_ENDPOINT = "https://accounts.spotify.com/authorize"
CLIENT_ID = "4be9b45f83eb4c57bdf6cf341033711d"
REDIRECT_URI = "http://127.0.0.1:8000/spot/"
SCOPES = ["playlist-read-private user-read-private user-read-email user-library-read playlist-modify-public playlist-modify-private"]
SCOPES_URL_PARAM = "%20".join(SCOPES)
RESPONSE_TYPE = "code"

# Create your views here.

res = []

class SpotifyAuth(APIView):
    def get(self, request):
        return HttpResponseRedirect(f"{SPOTIFY_AUTH_ENDPOINT}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPES_URL_PARAM}&response_type={RESPONSE_TYPE}")

class Data(APIView):
    def get(self, request):
        res.append(request.GET)
        code = res[len(res)-1]['code']
        
        print(code)
        req = requests.post("https://accounts.spotify.com/api/token", 
        data={ 
            
            "code": code, 
            "redirect_uri": REDIRECT_URI, 
            "grant_type": "authorization_code", 
        }, headers={
            "Authorization": "Basic NGJlOWI0NWY4M2ViNGM1N2JkZjZjZjM0MTAzMzcxMWQ6ZGUyMGU1YWRhODM5NDkyZWFjYzM1YWU3YTE4YjAyZmI=",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        
        print(req.text)
    
        USER_ID_ENDPOINT = "https://api.spotify.com/v1/me"
        
        
        spotify_userID = requests.get(USER_ID_ENDPOINT, headers={
            "Authorization": "Bearer " + req.json()['access_token']
        }
        ).json().get('id')
            
            
        spotify_create_playlist = f'https://api.spotify.com/v1/users/{spotify_userID}/playlists'

        print("Billboard Top 100")
        date = "2010-10-02"

        data_create_playlist = json.dumps({
        "name": date,
        "description": "Billboard Top 100 on " + date,
        "public": False
        })

        headers = {
            'Authorization': 'Bearer ' + req.json()['access_token'],
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


        for i in range(len(song_list)):
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
            
        
        print(len(res))
        return JsonResponse(req.json())
    

        