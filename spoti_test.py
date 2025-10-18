from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os

sp = Spotify(auth_manager=SpotifyOAuth(
    scope="user-read-currently-playing",
    # If you set env vars (recommended), you don't need to pass client_id/client_secret here.
    # client_id="...", client_secret="...",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

# This will open a browser the first run so you can authorize the app
now = sp.current_user_playing_track()
if now and now['item']:
    print("Track:", now['item']['name'], "by", now['item']['artists'][0]['name'])
    album_url = now['item']['album']['images'][0]['url']
    print("Album cover URL:", album_url)
