from bs4 import BeautifulSoup
import requests
import os
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import pprint

# date = input("What year would you like to be taken to? YYYY-MM-DD ")
date= "2009-09-23"
year = date.split("-")[0]

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
response.raise_for_status()
billboard_webpage = response.text

soup = BeautifulSoup(billboard_webpage, "html.parser")


def get_text_span(class_name):
    return [tag.getText() for tag in soup.find_all(name="span", class_=class_name)]


top100_rank = get_text_span("chart-element__rank__number")
top100_titles = get_text_span("chart-element__information__song text--truncate color--primary")
top100_artists = get_text_span("chart-element__information__artist text--truncate color--secondary")

# Spotify

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri="http://example.com", scope=scope))

user_id = sp.current_user()["id"]


track_uris = []
for track in top100_titles:
    result = sp.search(q=f"track:{track} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        track_uris.append(uri)
    except IndexError:
        print(f"{track} doesn't exist in Spotify. Skipped.")

print(track_uris)

# pprint

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(sp)

# create playlist

name_playlist = f"Top 100 of {date}"

playlist = sp.user_playlist_create(user=user_id, name=name_playlist, public=False)
playlist_id = playlist["id"]

# add tracks to created playlist

sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=track_uris)