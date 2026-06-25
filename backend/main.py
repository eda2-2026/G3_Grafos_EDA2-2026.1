from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import recommend, search, graph

app = FastAPI(title="Recomendador Musical - API", version="1.0.0")

# Configuração CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Portas do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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