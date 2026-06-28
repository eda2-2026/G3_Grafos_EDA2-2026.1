from pydantic import BaseModel
from typing import List, Optional


class Artist(BaseModel):
    id: str
    name: str
    genres: List[str] = []
    popularity: Optional[int] = None
    image_url: Optional[str] = None

    @classmethod
    def from_spotify(cls, data: dict) -> "Artist":
        """Constrói um Artist a partir do dict cru retornado pela API do Spotify."""
        images = data.get("images") or []
        return cls(
            id=data["id"],
            name=data["name"],
            genres=data.get("genres") or [],
            popularity=data.get("popularity"),
            image_url=images[0].get("url") if images else None,
        )


class Recommendation(BaseModel):
    artist: Artist
    score: float  # Pontuação do RWR


class RecommendationResponse(BaseModel):
    seed_artist: Artist
    recommendations: List[Recommendation]
