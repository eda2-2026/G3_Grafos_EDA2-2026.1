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

## Deploy no Render (

Frontend e backend sobem juntos em um único serviço Docker.

### Pré-requisitos

1. Repositório no [GitHub](https://github.com) com o código deste projeto
2. Conta no [Render](https://render.com)
3. API key do Last.fm

### Passo a passo

1. No Render, clique em **New +** → **Blueprint**
2. Conecte o repositório GitHub — o Render detecta o `render.yaml`
3. Na criação do serviço, informe a variável **`LASTFM_API_KEY`**
4. Aguarde o build (5–10 min na primeira vez)
5. Acesse a URL gerada, ex.: `https://recomendador-musical.onrender.com`

### URLs em produção

| URL | Função |
|-----|--------|
| `/` | Interface React |
| `/api/search` | Busca de artistas |
| `/api/recommend/{nome}` | Recomendações |
| `/health` | Health check do Render |

### Observações

- O plano **free** coloca o app em sleep após ~15 min sem acesso; a primeira requisição pode demorar ~30–60s
- O grafo fica em memória e é reiniciado a cada deploy
- Em dev local, continue usando backend (`:8000`) + frontend (`:5173`) separados

### Testar o Docker localmente (opcional)

```bash
docker build -t recomendador .
docker run -p 8000:8000 -e LASTFM_API_KEY=sua_chave -e PORT=8000 recomendador
```

Abra http://localhost:8000

## Screenshots

## Video
