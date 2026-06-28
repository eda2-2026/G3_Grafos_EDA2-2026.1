"""Testes end-to-end da API (TestClient + Spotify mockado via fixtures)."""
import pytest


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_root_online(client):
    assert client.get("/").json()["status"] == "online"


def test_search_retorna_resultados(client):
    r = client.get("/api/search", params={"q": "radiohead"})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 4
    assert {"id", "name", "genres", "popularity", "image_url"} <= set(results[0])
    assert results[0]["image_url"] == "http://img/seed.jpg"


@pytest.mark.parametrize("limit", [0, 999])
def test_search_limit_fora_de_faixa_422(client, limit):
    assert client.get("/api/search", params={"q": "x", "limit": limit}).status_code == 422


def test_recommend_ranqueia_e_exclui_desconexo(client):
    r = client.get("/api/recommend/Radiohead")
    assert r.status_code == 200
    js = r.json()
    assert js["seed_artist"]["name"] == "Radiohead"
    ids = [rec["artist"]["id"] for rec in js["recommendations"]]
    assert "a1" in ids and "a2" in ids
    assert ids.index("a1") < ids.index("a2")   # 2 gêneros em comum > 1
    assert "a3" not in ids                      # 'pop': componente separado


def test_recommend_sobrevive_a_falha_no_enriquecimento(flaky_client):
    # sp.artist('a2') falha; a recomendação não pode ser descartada nem virar 500.
    js = flaky_client.get("/api/recommend/Radiohead").json()
    recs = {rec["artist"]["id"]: rec["artist"] for rec in js["recommendations"]}
    assert "a2" in recs
    assert recs["a2"]["name"] == "Muse"   # fallback: nome vindo do grafo


def test_recommend_degrada_em_erro_de_rede(netfail_client):
    assert netfail_client.get("/api/recommend/Radiohead").status_code == 200


def test_graph_compartilha_estado_com_recommend(client):
    client.get("/api/recommend/Radiohead")   # alimenta o grafo (singleton)
    gd = client.get("/api/graph/seed1").json()
    ids = [n["id"] for n in gd["nodes"]]
    assert "seed1" in ids and "a1" in ids
    assert any(i.startswith("genre::") for i in ids)
    assert "a3" not in ids
    assert gd["edges"]


def test_graph_artista_ausente_vazio(client):
    assert client.get("/api/graph/inexistente").json() == {"nodes": [], "edges": []}


def test_credenciais_ausentes_levanta_erro(monkeypatch):
    from app.config import Config
    from app.services.spotify_service import SpotifyService, SpotifyCredentialsError

    monkeypatch.setattr(Config, "SPOTIFY_CLIENT_ID", None)
    monkeypatch.setattr(Config, "SPOTIFY_CLIENT_SECRET", None)
    with pytest.raises(SpotifyCredentialsError):
        _ = SpotifyService().sp
