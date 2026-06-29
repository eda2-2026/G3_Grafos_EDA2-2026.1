from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import recommend, search, graph
from app.services.lastfm_service import LastFmCredentialsError

app = FastAPI(title="Recomendador Musical - API", version="1.0.0")

# Configuração CORS para permitir requisições do frontend
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


# Registra as rotas
app.include_router(recommend.router, prefix="/api", tags=["Recomendações"])
app.include_router(search.router, prefix="/api", tags=["Busca"])
app.include_router(graph.router, prefix="/api", tags=["Grafo"])


@app.get("/")
async def root():
    return {"message": "Recomendador Musical API", "status": "online"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
