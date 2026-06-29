from fastapi import APIRouter, HTTPException, Query

from app.dependencies import lastfm_service, graph_service, recommender_service
from app.models.schemas import Artist, Recommendation, RecommendationResponse
from app.services.lastfm_service import _LASTFM_ERRORS

router = APIRouter()


@router.get("/recommend/{artist_name}", response_model=RecommendationResponse)
async def recommend(artist_name: str, limit: int = Query(10, ge=1)):
    """Endpoint principal: recomenda artistas similares via RWR sobre o grafo."""
    artist_data = lastfm_service.search_artist(artist_name)
    if not artist_data:
        raise HTTPException(status_code=404, detail="Artista não encontrado")

    # artist.search não traz tags; getInfo é necessário para montar o grafo.
    try:
        artist_data = lastfm_service.get_artist(artist_data["id"])
    except _LASTFM_ERRORS:
        pass

    artist_id = artist_data["id"]
    graph_service.add_artist_genre_edges(
        artist_id, artist_data["name"], artist_data.get("genres", [])
    )

    # Artistas similares alimentam o grafo. Se a chamada falhar (rate limit,
    # rede), degradamos sem quebrar (o grafo fica só com a semente).
    try:
        related = lastfm_service.get_related_artists(artist_id)
    except _LASTFM_ERRORS:
        related = []
    for related_artist in related[:10]:
        graph_service.add_artist_genre_edges(
            related_artist["id"],
            related_artist["name"],
            related_artist.get("genres", []),
        )

    recommendations = recommender_service.get_recommendations(artist_id, top_n=limit)

    items = []
    for rec_artist_id, score in recommendations:
        try:
            artist = Artist.from_api(lastfm_service.get_artist(rec_artist_id))
        except _LASTFM_ERRORS:
            node = graph_service.graph.nodes[rec_artist_id] if rec_artist_id in graph_service.graph else {}
            artist = Artist(id=rec_artist_id, name=node.get("name", rec_artist_id))
        items.append(Recommendation(artist=artist, score=score))

    return RecommendationResponse(
        seed_artist=Artist.from_api(artist_data),
        recommendations=items,
    )
