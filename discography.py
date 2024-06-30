# Shows the list of all songs sung by the artist or the band
import argparse
import logging
from spotipy_token import authenticate
from pprint import pprint
import pandas as pd

logger = logging.getLogger('examples.artist_discography')
logging.basicConfig(level='INFO')


def get_args():
    parser = argparse.ArgumentParser(description='Shows albums and tracks for '
                                     'given artist')
    parser.add_argument('-a', '--artist', required=True,
                        help='Name of Artist')
    return parser.parse_args()


def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None


def show_album_tracks(album):
    tracks = []
    results = sp.album_tracks(album['id'])
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    track_df = pd.DataFrame()
    for i, track in enumerate(tracks):
        logger.info('%s. %s', i + 1, track['name'])
        track_details = sp.track(track['uri'])
        track_audio_features = sp.audio_features(track['uri'])
        track_data = {}
        track_data['uri'] = track['uri']
        track_data['name'] = track['name']
        track_data['album_name'] = track_details['album']['name']
        track_data['release_date'] = track_details['album']['release_date']
        track_data['popularity'] = track_details['popularity']
        track_data['duration_ms'] = track_details['duration_ms']
        for k, v in track_audio_features[0].items():
            if k in ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']:
                track_data[k] = v
        df = pd.DataFrame.from_dict(track_data, orient='index').transpose()
        track_df = pd.concat([track_df, df], axis=0)

    return track_df

def show_artist_albums(artist):
    discography_df = pd.DataFrame()
    albums = []
    results = sp.artist_albums(artist['id'], album_type='album')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    logger.info('Total albums: %s', len(albums))
    unique = set()  # skip duplicate albums
    for album in albums:
        name = album['name'].lower()
        if name not in unique:
            logger.info('ALBUM: %s', name)
            unique.add(name)
            album_df = show_album_tracks(album)
            discography_df = pd.concat([discography_df, album_df], axis=0)
    
    return discography_df


def show_artist(artist):
    logger.info('====%s====', artist['name'])
    logger.info('Popularity: %s', artist['popularity'])
    if len(artist['genres']) > 0:
        logger.info('Genres: %s', ','.join(artist['genres']))


sp = authenticate()
artist = get_artist('ODESZA')
show_artist(artist)
discography_df = show_artist_albums(artist)
discography_df.to_csv('discography.csv', index=False)