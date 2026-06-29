"""Testes unitários do núcleo: grafo bipartido (GraphService) + RWR (Recommender)."""
import pytest

from app.models.schemas import Artist
from app.services.graph_service import GraphService
from app.services.recommender_service import RecommenderService


def _seed_graph():
    g = GraphService()
    g.add_artist_genre_edges("SEED", "Seed", ["rock", "indie"])
    g.add_artist_genre_edges("A", "Artist A", ["rock", "indie"])   # 2 em comum
    g.add_artist_genre_edges("B", "Artist B", ["rock", "jazz"])    # 1 em comum
    g.add_artist_genre_edges("C", "Artist C", ["sertanejo"])       # desconexo
    return g


def test_ranqueia_por_generos_compartilhados():
    out = RecommenderService(_seed_graph()).get_recommendations("SEED")
    ids = [a for a, _ in out]
    assert "SEED" not in ids                       # exclui a semente
    assert all(not i.startswith("genre::") for i in ids)  # só artistas
    assert ids.index("A") < ids.index("B")         # 2 gêneros > 1 gênero
    assert "C" not in ids                          # componente separado


def test_scores_em_ordem_decrescente():
    out = RecommenderService(_seed_graph()).get_recommendations("SEED")
    assert all(out[i][1] >= out[i + 1][1] for i in range(len(out) - 1))


def test_top_n_limita_e_mantem_o_melhor():
    out = RecommenderService(_seed_graph()).get_recommendations("SEED", top_n=1)
    assert len(out) == 1 and out[0][0] == "A"


def test_semente_ausente_retorna_vazio():
    assert RecommenderService(GraphService()).get_recommendations("X") == []


def test_semente_isolada_retorna_vazio():
    g = GraphService()
    g.add_artist_genre_edges("L", "Lone", [])
    assert RecommenderService(g).get_recommendations("L") == []


def test_idempotente_nao_duplica():
    g = GraphService()
    g.add_artist_genre_edges("Z", "Ze", ["rock"])
    n, e = g.graph.number_of_nodes(), g.graph.number_of_edges()
    g.add_artist_genre_edges("Z", "Ze", ["rock"])
    assert (g.graph.number_of_nodes(), g.graph.number_of_edges()) == (n, e)


def test_normaliza_genero():
    g = GraphService()
    g.add_artist_genre_edges("P", "P", [" Rock "])
    g.add_artist_genre_edges("Q", "Q", ["rock"])
    assert g.graph.has_edge("P", "genre::rock") and g.graph.has_edge("Q", "genre::rock")


def test_ignora_generos_sujos():
    g = GraphService()
    g.add_artist_genre_edges("D", "D", ["rock", None, "", 123, "  "])
    assert g.graph.degree("D") == 1


def test_get_graph_data_restringe_ao_componente():
    gd = _seed_graph().get_graph_data("SEED")
    ids = [n["id"] for n in gd["nodes"]]
    assert "SEED" in ids and "A" in ids and "C" not in ids
    assert gd["edges"]


def test_get_graph_data_artista_ausente():
    assert GraphService().get_graph_data("nope") == {"nodes": [], "edges": []}


def test_from_api_tolera_genres_null():
    # A API pode devolver genres=null; não pode quebrar (ValidationError).
    assert Artist.from_api({"id": "x", "name": "n", "genres": None}).genres == []
