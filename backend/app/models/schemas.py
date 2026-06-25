from pydantic import BaseModel
from typing import List, Optional

class Artist(BaseModel):
    id: str
    name: str
    genres: List[str]
    popularity: Optional[int]
    image_url: Optional[str]

class Recommendation(BaseModel):
    artist: Artist
    score: float  # Pontuação do RWR

class RecommendationResponse(BaseModel):
    seed_artist: Artist
    recommendations: List[Recommendation]