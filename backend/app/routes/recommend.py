from fastapi import APIRouter, HTTPException
from app.services.spotify_service import SpotifyService
from app.services.graph_service import GraphService
from app.services.recommender_service import RecommenderService
from app.models.schemas import RecommendationResponse, Artist

router = APIRouter()
spotify_service = SpotifyService()
graph_service = GraphService()
recommender_service = RecommenderService(graph_service)

@router.get("/recommend/{artist_name}")
async def recommend(artist_name: str, limit: int = 10):
    """Endpoint principal para recomendações."""
    # Busca o artista
    artist_data = spotify_service.search_artist(artist_name)
    if not artist_data:
        raise HTTPException(status_code=404, detail="Artista não encontrado")
    
    # Constrói o grafo (em produção, carregaria de cache)
    artist_id = artist_data['id']
    genres = artist_data['genres']
    graph_service.add_artist_genre_edges(artist_id, artist_data['name'], genres)
    
    # Busca artistas relacionados e adiciona ao grafo
    related = spotify_service.get_related_artists(artist_id)
    for related_artist in related[:10]:  # Limita para não sobrecarregar
        related_genres = related_artist.get('genres', [])
        graph_service.add_artist_genre_edges(
            related_artist['id'],
            related_artist['name'],
            related_genres
        )
    
    # Gera recomendações
    recommendations = recommender_service.get_recommendations(artist_id, top_n=limit)
    
    # Constrói resposta
    seed_artist = Artist(
        id=artist_id,
        name=artist_data['name'],
        genres=genres,
        popularity=artist_data.get('popularity')
    )
    
    result = []
    for rec_artist_id, score in recommendations:
        # Busca dados do artista recomendado (em produção, teria em cache)
        rec_data = spotify_service.sp.artist(rec_artist_id)
        result.append({
            'artist': Artist(
                id=rec_artist_id,
                name=rec_data['name'],
                genres=rec_data.get('genres', []),
                popularity=rec_data.get('popularity')
            ),
            'score': score
        })
    
    return {
        'seed_artist': seed_artist.dict(),
        'recommendations': result
    }