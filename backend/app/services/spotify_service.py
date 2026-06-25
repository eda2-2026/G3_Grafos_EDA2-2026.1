import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from app.config import Config
from typing import List, Dict

class SpotifyService:
    def __init__(self):
        auth_manager = SpotifyClientCredentials(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
    
    def search_artist(self, name: str) -> Dict:
        """Busca um artista pelo nome."""
        results = self.sp.search(q=f'artist:{name}', type='artist', limit=5)
        if results['artists']['items']:
            return results['artists']['items'][0]
        return None
    
    def get_artist_genres(self, artist_id: str) -> List[str]:
        """Retorna os gêneros de um artista."""
        artist = self.sp.artist(artist_id)
        return artist['genres']
    
    def get_related_artists(self, artist_id: str) -> List[Dict]:
        """Retorna artistas relacionados."""
        results = self.sp.artist_related_artists(artist_id)
        return results['artists']