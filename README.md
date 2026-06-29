# G3_Grafos_EDA2-2026.1

## Grupo 3
|Matrícula | Aluno |
| -- | -- |
| 22/1022720  | Rayene Ferreira Almeida |
| 20/2017361  | Enzo Fernandes Borges   |

## Sobre 
O sistema é um recomendador musical que sugere artistas similares a partir de um artista de interesse, utilizando a API gratuita do [Last.fm](https://www.last.fm/api) e modelando a relação entre artistas e gêneros (tags) como um grafo bipartido. Através do algoritmo de Random Walk with Restart (uma variação do PageRank), o sistema caminha aleatoriamente pela rede de conexões musicais para identificar quais artistas são mais relevantes ao ponto de partida, revelando similaridades indiretas e sutis que métodos simples de filtragem por gênero não capturam. 

## Como rodar

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Configure backend/.env com LASTFM_API_KEY (veja backend/.env.example)

cd backend
PYTHONPATH=. python run.py
```

API disponível em http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Interface em http://localhost:5173 (proxy para a API em `/api`)

### Testes

```bash
cd backend
PYTHONPATH=. pytest -v
```

## Screenshots

## Video
