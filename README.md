# trader-slave-v2

**Roadmap:** https://pittalavito.github.io/trader-slave-v2/

Trader Slave esegue in automatico strategie di trading su criptovalute: la strategia decide quando entrare, l'app applica sempre le stesse regole di rischio, esegue gli ordini e tiene i conti dei portafogli. È pensata per più utenti, ognuno con più portafogli.

## Struttura

| Cartella | Cosa contiene |
| --- | --- |
| `backend/` | API in Python (FastAPI) e motore dei bot |
| `frontend/` | Interfaccia web in React (Vite + TypeScript) |
| `deploy/` | Caddy: serve il frontend, fa da proxy verso l'API e gestisce HTTPS |
| `docs/` | [Architettura del backend](docs/architettura-backend.md) e guide, come [mettere l'app su un server](docs/server.md) |
| `site/` | La [roadmap di sviluppo](https://pittalavito.github.io/trader-slave-v2/), pubblicata su GitHub Pages |

Il motore è diviso in sei livelli (`backend/app/engine/layers.py`): 
- dati di mercato,
- segnale,
- rischio,
- dimensionamento,
- esecuzione
- portafoglio.

Ogni strategia implementa solo il livello del segnale; gli altri sono comuni a tutte.
In produzione girano quattro servizi Docker: `db` (PostgreSQL), `api`, `worker` (il motore, sempre acceso) e `web` (Caddy con il frontend).

## Sviluppo in locale

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload
```

Frontend, in un altro terminale (le chiamate a `/api` vanno al backend locale):

```bash
cd frontend
npm install
npm run dev
```

Tutto insieme con Docker, come sul server:

```bash
cp .env.example .env
docker compose up --build
```

L'app risponde su http://localhost.

## Deploy

Vedi [docs/server.md](docs/server.md). Una volta configurato il server, ogni push su `main` lo aggiorna in automatico.
