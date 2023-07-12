import logging
import spotipy
import spotipy.util as util
import os
import requests
from io import BytesIO
from PIL import Image

import configparser

config = configparser.ConfigParser()
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config/authConfig.cfg')

config.read(filename) # using config file instead of environment variables
client_id = config['DEFAULT']['client_id']
client_secret = config['DEFAULT']['client_secret']
redirect_uri = config['DEFAULT']['redirect_uri']

def getSongInfo(username, token_path):
  scope = 'user-read-currently-playing'
  token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, cache_path=token_path)
  if token:
      sp = spotipy.Spotify(auth=token)
      result = sp.current_user_playing_track()
    
      if result is None:
         print("No song playing")
      else:  
        song = result["item"]["name"]
        imageURL = result["item"]["album"]["images"][0]["url"]
        print(song)
        return [song, imageURL]
  else:
      print("Can't get token for", username)
      return None

