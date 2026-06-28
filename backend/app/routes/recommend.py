from fastapi import APIRouter, HTTPException, Query
from requests.exceptions import RequestException
from spotipy import SpotifyException

from app.dependencies import spotify_service, graph_service, recommender_service
from app.models.schemas import Artist, Recommendation, RecommendationResponse

router = APIRouter()

# Erros de rede/HTTP que justificam degradar (em vez de quebrar) chamadas
# opcionais ao Spotify: SpotifyException cobre erros HTTP da API; RequestException
# cobre falhas de transporte (timeout, conexão) que NÃO viram SpotifyException.
_SPOTIFY_ERRORS = (SpotifyException, RequestException)


@router.get("/recommend/{artist_name}", response_model=RecommendationResponse)
async def recommend(artist_name: str, limit: int = Query(10, ge=1)):
    """Endpoint principal: recomenda artistas similares via RWR sobre o grafo."""
    # Busca o artista-semente.
    artist_data = spotify_service.search_artist(artist_name)
    if not artist_data:
        raise HTTPException(status_code=404, detail="Artista não encontrado")

    artist_id = artist_data["id"]
    graph_service.add_artist_genre_edges(
        artist_id, artist_data["name"], artist_data.get("genres", [])
    )

    # Artistas relacionados alimentam o grafo. O endpoint related-artists do
    # Spotify foi descontinuado (nov/2024) para apps novos; se ele falhar (erro
    # HTTP ou de rede), degradamos sem quebrar (o grafo fica só com a semente).
    try:
        related = spotify_service.get_related_artists(artist_id)
    except _SPOTIFY_ERRORS:
        related = []
    for related_artist in related[:10]:  # Limita para não sobrecarregar.
        graph_service.add_artist_genre_edges(
            related_artist["id"],
            related_artist["name"],
            related_artist.get("genres", []),
        )

    # Gera recomendações com Random Walk with Restart.
    recommendations = recommender_service.get_recommendations(artist_id, top_n=limit)

    # Enriquece cada recomendação. O enriquecimento é best-effort: se a chamada
    # por artista falhar (rate limit, id obsoleto, rede), usamos o nome já
    # presente no grafo em vez de abortar a resposta inteira com 500.
    items = []
    for rec_artist_id, score in recommendations:
        try:
            artist = Artist.from_spotify(spotify_service.sp.artist(rec_artist_id))
        except _SPOTIFY_ERRORS:
            node = graph_service.graph.nodes[rec_artist_id] if rec_artist_id in graph_service.graph else {}
            artist = Artist(id=rec_artist_id, name=node.get("name", rec_artist_id))
        items.append(Recommendation(artist=artist, score=score))

    return RecommendationResponse(
        seed_artist=Artist.from_spotify(artist_data),
        recommendations=items,
    )
