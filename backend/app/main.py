from pathlib import Path
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes import recommend, search, graph
from app.services.lastfm_service import LastFmCredentialsError

app = FastAPI(title="Recomendador Musical - API", version="1.0.0")

STATIC_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
SERVE_STATIC = os.getenv("SERVE_STATIC", "").lower() in ("1", "true", "yes")

# CORS só necessário em dev (front e back em portas diferentes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(LastFmCredentialsError)
async def _lastfm_credentials_handler(request: Request, exc: LastFmCredentialsError):
    """Traduz API key ausente do Last.fm em um 503 claro (em vez de 500)."""
    return JSONResponse(status_code=503, content={"detail": str(exc)})


app.include_router(recommend.router, prefix="/api", tags=["Recomendações"])
app.include_router(search.router, prefix="/api", tags=["Busca"])
app.include_router(graph.router, prefix="/api", tags=["Grafo"])


def _static_enabled() -> bool:
    return SERVE_STATIC and (STATIC_DIR / "index.html").is_file()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    if _static_enabled():
        return FileResponse(STATIC_DIR / "index.html")
    return {"message": "Recomendador Musical API", "status": "online"}


if _static_enabled():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path == "health" or full_path.startswith("api"):
            raise HTTPException(status_code=404)
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
