from fastapi import APIRouter

from app.dependencies import graph_service

router = APIRouter()


@router.get("/graph/{artist_id}")
async def get_graph(artist_id: str):
    """Exporta nós e arestas do componente do artista (para visualização).

    Retorna ``{"nodes": [...], "edges": [...]}``. Se o artista ainda não estiver
    no grafo (nenhuma recomendação foi gerada para ele), retorna listas vazias.
    """
    return graph_service.get_graph_data(artist_id)
