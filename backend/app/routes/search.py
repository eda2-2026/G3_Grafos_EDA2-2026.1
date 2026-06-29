from fastapi import APIRouter, Query

from app.dependencies import lastfm_service
from app.models.schemas import Artist

router = APIRouter()


@router.get("/search")
async def search(q: str, limit: int = Query(10, ge=1, le=50)):
    """Busca artistas pelo nome e retorna a lista de resultados."""
    items = lastfm_service.search_artists(q, limit=limit)
    return {"query": q, "results": [Artist.from_api(item) for item in items]}
