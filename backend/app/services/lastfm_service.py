import re
from typing import Dict, List, Optional

import httpx

from app.config import Config

_MBID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
_IMAGE_SIZES = ("extralarge", "large", "medium", "small")


class LastFmCredentialsError(RuntimeError):
    """Levantada quando a API key do Last.fm não está configurada."""


class LastFmApiError(Exception):
    """Erro retornado pela API do Last.fm (rate limit, artista inválido, etc.)."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class LastFmService:
    _BASE_URL = "https://ws.audioscrobbler.com/2.0/"

    def __init__(self) -> None:
        # Cliente lazy: o app sobe sem .env e só falha ao chamar a API.
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            if not Config.LASTFM_API_KEY:
                raise LastFmCredentialsError(
                    "API key do Last.fm ausente: defina LASTFM_API_KEY "
                    "(gratuita em https://www.last.fm/api/account/create)."
                )
            self._client = httpx.Client(timeout=10.0)
        return self._client

    def _call(self, method: str, **params) -> dict:
        response = self.client.get(
            self._BASE_URL,
            params={
                "method": method,
                "api_key": Config.LASTFM_API_KEY,
                "format": "json",
                **params,
            },
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise LastFmApiError(int(data["error"]), data.get("message", "erro desconhecido"))
        return data

    @staticmethod
    def _looks_like_mbid(artist_id: str) -> bool:
        return bool(_MBID_RE.match(artist_id))

    @staticmethod
    def _extract_images(data: dict) -> List[dict]:
        images = data.get("image") or []
        if isinstance(images, dict):
            images = [images]
        for size in _IMAGE_SIZES:
            for image in images:
                if image.get("size") == size and image.get("#text"):
                    return [{"url": image["#text"]}]
        return []

    @staticmethod
    def _extract_tags(data: dict) -> List[str]:
        tags = (data.get("tags") or {}).get("tag") or []
        if isinstance(tags, dict):
            tags = [tags]
        return [tag["name"] for tag in tags if tag.get("name")]

    def _normalize_artist(self, data: dict) -> dict:
        name = data["name"]
        artist_id = (data.get("mbid") or "").strip() or name
        listeners = data.get("listeners") or (data.get("stats") or {}).get("listeners")
        popularity = int(listeners) if listeners else None
        return {
            "id": artist_id,
            "name": name,
            "genres": self._extract_tags(data),
            "popularity": popularity,
            "images": self._extract_images(data),
        }

    def _artist_params(self, artist_id: str) -> dict:
        if self._looks_like_mbid(artist_id):
            return {"mbid": artist_id}
        return {"artist": artist_id}

    def search_artist(self, name: str) -> Optional[Dict]:
        """Busca um artista pelo nome e retorna o primeiro resultado (ou None)."""
        artists = self.search_artists(name, limit=1)
        return artists[0] if artists else None

    def search_artists(self, name: str, limit: int = 10) -> List[Dict]:
        """Busca artistas pelo nome e retorna a lista de resultados."""
        data = self._call("artist.search", artist=name, limit=limit)
        artists = data.get("results", {}).get("artistmatches", {}).get("artist", [])
        if isinstance(artists, dict):
            artists = [artists]
        return [self._normalize_artist(artist) for artist in artists[:limit]]

    def get_artist(self, artist_id: str) -> Dict:
        """Retorna metadados completos de um artista (tags, imagem, ouvintes)."""
        data = self._call("artist.getInfo", **self._artist_params(artist_id))
        return self._normalize_artist(data["artist"])

    def get_related_artists(self, artist_id: str, limit: int = 10) -> List[Dict]:
        """Retorna artistas similares, enriquecidos com tags quando possível."""
        data = self._call("artist.getSimilar", limit=limit, **self._artist_params(artist_id))
        artists = data.get("similarartists", {}).get("artist", [])
        if isinstance(artists, dict):
            artists = [artists]

        related: List[Dict] = []
        for artist in artists[:limit]:
            normalized = self._normalize_artist(artist)
            if not normalized["genres"]:
                try:
                    full = self.get_artist(normalized["id"])
                    normalized["genres"] = full.get("genres", [])
                    if not normalized["images"]:
                        normalized["images"] = full.get("images", [])
                except (LastFmApiError, httpx.RequestError):
                    pass
            related.append(normalized)
        return related


# Alias para tratamento de erros de rede/API nas rotas.
_LASTFM_ERRORS = (LastFmApiError, httpx.RequestError)
