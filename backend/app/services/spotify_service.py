import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from app.config import Config
from typing import List, Dict, Optional


class SpotifyCredentialsError(RuntimeError):
    """Levantada quando as credenciais do Spotify não estão configuradas."""


class SpotifyService:
    def __init__(self) -> None:
        # O cliente é criado sob demanda (lazy) para que importar este módulo
        # NÃO exija credenciais — o app sobe mesmo sem .env e só falha ao
        # efetivamente chamar a API.
        self._sp: Optional[spotipy.Spotify] = None

    @property
    def sp(self) -> spotipy.Spotify:
        """Cliente spotipy autenticado, criado na primeira utilização."""
        if self._sp is None:
            if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
                raise SpotifyCredentialsError(
                    "Credenciais do Spotify ausentes: defina SPOTIFY_CLIENT_ID e "
                    "SPOTIFY_CLIENT_SECRET (veja backend/app/config.py)."
                )
            auth_manager = SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
            )
            self._sp = spotipy.Spotify(auth_manager=auth_manager)
        return self._sp

    def search_artist(self, name: str) -> Optional[Dict]:
        """Busca um artista pelo nome e retorna o primeiro resultado (ou None)."""
        results = self.sp.search(q=f"artist:{name}", type="artist", limit=5)
        items = results["artists"]["items"]
        return items[0] if items else None

    def search_artists(self, name: str, limit: int = 10) -> List[Dict]:
        """Busca artistas pelo nome e retorna a lista de resultados."""
        results = self.sp.search(q=f"artist:{name}", type="artist", limit=limit)
        return results["artists"]["items"]

    def get_artist_genres(self, artist_id: str) -> List[str]:
        """Retorna os gêneros de um artista."""
        return self.sp.artist(artist_id)["genres"]

    def get_related_artists(self, artist_id: str) -> List[Dict]:
        """Retorna artistas relacionados."""
        return self.sp.artist_related_artists(artist_id)["artists"]
