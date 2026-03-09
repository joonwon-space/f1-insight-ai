# F1 Insight AI

Automatically collect, summarize, and translate F1 news and interviews using LLM — delivered through a fast, organized web interface.

## Quick Start

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Start infrastructure (MongoDB, Elasticsearch)
docker compose up -d

# 3. Run backend
cd backend
pip install -e .
uvicorn app.main:app --reload

# 4. Run frontend
cd frontend
npm install
npm run dev
```

## Architecture

- **Backend**: Python 3.12+ / FastAPI
- **Frontend**: Next.js 15 / TypeScript / Tailwind CSS
- **Database**: MongoDB (raw data) + Elasticsearch (search index)
- **LLM**: Ollama (local) / Claude API (cloud)
- **Infra**: Docker Compose on Mac Mini

See [docs/project-overview.md](docs/project-overview.md) for full details.
