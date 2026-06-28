"""Fixtures de teste: sobem a API real (TestClient) com o Spotify mockado.

Mockar o Spotify deixa os testes determinísticos e dispensa credenciais/rede —
exercitamos a NOSSA lógica (grafo + RWR + rotas), não a API externa.
"""
import networkx as nx
import pytest
import requests
from fastapi.testclient import TestClient
from spotipy import SpotifyException

import app.dependencies as deps
from app.main import app

# Cenário fixo: SEED compartilha 2 gêneros com a1, 1 com a2, 0 com a3.
# Logo a1 deve ranquear acima de a2, e a3 (componente separado) é excluído.
SEED = {"id": "seed1", "name": "Radiohead", "genres": ["rock", "art rock"],
        "popularity": 90, "images": [{"url": "http://img/seed.jpg"}]}
RELATED = [
    {"id": "a1", "name": "Thom Yorke", "genres": ["rock", "art rock"], "popularity": 75, "images": []},
    {"id": "a2", "name": "Muse", "genres": ["rock", "alternative"], "popularity": 80, "images": [{"url": "http://img/muse.jpg"}]},
    {"id": "a3", "name": "Anitta", "genres": ["pop"], "popularity": 85, "images": []},
]
ARTISTS = {a["id"]: a for a in [SEED, *RELATED]}


class _FakeSp:
    """Stub do cliente spotipy: .artist() devolve dados falsos (ou falha)."""

    def __init__(self, fail_ids=()):
        self.fail_ids = set(fail_ids)

    def artist(self, artist_id):
        if artist_id in self.fail_ids:
            raise SpotifyException(429, -1, "rate limited")
        return ARTISTS[artist_id]


def _patch_common(monkeypatch):
    # Grafo limpo a cada teste (o singleton acumula entre requisições).
    monkeypatch.setattr(deps.graph_service, "graph", nx.Graph())
    monkeypatch.setattr(deps.spotify_service, "search_artist", lambda name: SEED)
    monkeypatch.setattr(deps.spotify_service, "search_artists", lambda q, limit=10: [SEED, *RELATED][:limit])
    monkeypatch.setattr(deps.spotify_service, "get_related_artists", lambda aid: list(RELATED))


@pytest.fixture
def client(monkeypatch):
    """API com Spotify mockado no caminho feliz."""
    _patch_common(monkeypatch)
    monkeypatch.setattr(deps.spotify_service, "_sp", _FakeSp())
    return TestClient(app)


@pytest.fixture
def flaky_client(monkeypatch):
    """sp.artist() falha para 'a2' (simula 429/404 no enriquecimento)."""
    _patch_common(monkeypatch)
    monkeypatch.setattr(deps.spotify_service, "_sp", _FakeSp(fail_ids={"a2"}))
    return TestClient(app)


@pytest.fixture
def netfail_client(monkeypatch):
    """get_related_artists levanta erro de REDE (não SpotifyException)."""
    _patch_common(monkeypatch)

    def boom(_artist_id):
        raise requests.exceptions.ConnectionError("rede caiu")

    monkeypatch.setattr(deps.spotify_service, "get_related_artists", boom)
    monkeypatch.setattr(deps.spotify_service, "_sp", _FakeSp())
    return TestClient(app)
