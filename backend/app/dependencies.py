"""Instâncias compartilhadas dos serviços (singletons da aplicação).

Centralizar aqui garante que TODAS as rotas operem sobre o MESMO grafo: a rota
``/recommend`` alimenta o grafo e a rota ``/graph`` o expõe — ambas precisam do
mesmo ``GraphService``. Construir os serviços é seguro no import porque o cliente
do Last.fm é inicializado de forma preguiçosa (lazy).
"""

from app.services.lastfm_service import LastFmService
from app.services.graph_service import GraphService
from app.services.recommender_service import RecommenderService

lastfm_service = LastFmService()
graph_service = GraphService()
recommender_service = RecommenderService(graph_service)
