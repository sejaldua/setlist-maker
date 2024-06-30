import spotipy 
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import yaml

def authenticate():
    # sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    stream = open('config.yaml')
    user_config = yaml.load(stream, Loader=yaml.FullLoader)
    token = util.prompt_for_user_token(
            user_config['username'], 
            scope='playlist-read-private',
            client_id=user_config['client_id'],
            client_secret=user_config['client_secret'],
            redirect_uri=user_config['redirect_uri'])
    if token:
        sp = spotipy.Spotify(auth=token)
        # print(sp.artist('0fA0VVWsXO9YnASrzqfmYu'))
    else:
        print("Can't get token for", username)
        sp = None
    
    return sp
    