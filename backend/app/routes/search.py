from fastapi import APIRouter, Query

from app.dependencies import spotify_service
from app.models.schemas import Artist

router = APIRouter()


@router.get("/search")
async def search(q: str, limit: int = Query(10, ge=1, le=50)):
    """Busca artistas pelo nome e retorna a lista de resultados."""
    items = spotify_service.search_artists(q, limit=limit)
    return {"query": q, "results": [Artist.from_spotify(item) for item in items]}
