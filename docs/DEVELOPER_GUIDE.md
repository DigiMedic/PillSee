# PillSee - Developer Guide

## Přehled

Tato příručka je určena pro vývojáře pracující na PillSee projektu. Obsahuje detailní informace o architektuře, nastavení vývojového prostředí, coding standards a deployment.

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Database Management](#database-management)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

## Quick Setup

### Prerequisites

**Backend:**
- Python 3.11+
- PostgreSQL 15+ (nebo Supabase account)
- OpenAI API key

**Frontend:**
- Node.js 18+ (LTS)
- npm nebo pnpm

**Tools:**
- Git
- Docker & Docker Compose (volitelné)
- VS Code (doporučené IDE)

### 1. Clone Repository

```bash
git clone https://github.com/pillsee/pillsee.git
cd pillsee
```

### 2. Backend Setup

```bash
cd pillsee-backend

# Vytvoření virtual environment
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# nebo
venv\Scripts\activate     # Windows

# Instalace dependencies
pip install -r requirements.txt

# Vytvoření .env souboru
cp .env.example .env
# Vyplňte: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY

# Spuštění dev serveru
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend běží na: **http://localhost:8000**
API dokumentace: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd pillsee-frontend

# Instalace dependencies
npm install

# Vytvoření .env.local
cp .env.example .env.local
# Vyplňte: NEXT_PUBLIC_API_URL=http://localhost:8000

# Spuštění dev serveru
npm run dev
```

Frontend běží na: **http://localhost:3000**

### 4. Database Setup (Supabase)

```bash
# Připojení k Supabase
psql "postgresql://postgres:[password]@[host]:5432/postgres"

# Spuštění migrací v pořadí
\i migrations/001_core_drug_tables.sql
\i migrations/002_spc_pil_vectors.sql
\i migrations/003_pricing_data.sql
\i migrations/004_drug_interactions.sql
\i migrations/005_rag_vector_search.sql
\i migrations/006_langchain_tables.sql
```

## Project Structure

```
PillSee/
├── pillsee-backend/           # FastAPI backend
│   ├── app/
│   │   ├── agents/            # LangGraph agents (Sprint 1 BMAD)
│   │   ├── api/               # API endpoints & monitoring
│   │   ├── database/          # Database clients & connections
│   │   ├── memory/            # GDPR-compliant memory
│   │   ├── rag/               # RAG retrieval strategies
│   │   ├── tools/             # LangChain tools
│   │   ├── workflows/         # LangGraph workflows
│   │   ├── ai/                # AI processors (vision, text)
│   │   ├── data/              # Data processing (SÚKL)
│   │   ├── config.py          # Configuration
│   │   ├── models.py          # Pydantic models
│   │   └── main.py            # FastAPI app
│   ├── migrations/            # Database migrations (SQL)
│   ├── tests/                 # Unit & integration tests
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Docker image
│   └── docker-compose.yml     # Local development
│
├── pillsee-frontend/          # Next.js 14 frontend
│   ├── app/                   # App Router pages
│   ├── components/            # React components
│   ├── lib/                   # Utilities
│   ├── public/                # Static assets
│   └── package.json
│
├── docs/                      # Project documentation
│   ├── api/                   # API specification
│   ├── architecture/          # Architecture docs
│   ├── phase1/                # Phase 1 implementation
│   ├── prd.md                 # Product requirements
│   └── architecture.md        # Full system design
│
├── CLAUDE.md                  # Instructions for Claude Code
├── CONSOLIDATION_REPORT.md    # Repository status
└── README.md                  # Project overview
```

## Development Workflow

### Git Workflow

```bash
# Vytvoření feature branch
git checkout -b feature/agent-implementation

# Pravidelné commity
git add .
git commit -m "feat: implement triage agent classification"

# Push a pull request
git push origin feature/agent-implementation
```

**Commit Message Format:**
- `feat:` - Nová funkcionalita
- `fix:` - Oprava bugu
- `docs:` - Dokumentace
- `test:` - Testy
- `refactor:` - Refaktoring
- `chore:` - Maintenance

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development integration
- `feature/*` - Nové funkce
- `fix/*` - Bug fixes
- `hotfix/*` - Urgentní opravy production

## Backend Development

### Folder Structure Deep Dive

#### `app/agents/` - LangGraph Agents (Sprint 1)

```python
# app/agents/supervisor_agent.py
from langgraph.graph import StateGraph
from typing import TypedDict

class SupervisorState(TypedDict):
    task: str
    assigned_agent: str
    result: dict

def create_supervisor_agent():
    """Main orchestration agent"""
    workflow = StateGraph(SupervisorState)
    # Define workflow...
    return workflow.compile()
```

**Agents to implement:**
1. `supervisor_agent.py` - Koordinace
2. `triage_agent.py` - Klasifikace dotazů
3. `rag_expert_agent.py` - RAG strategie
4. `safety_monitor_agent.py` - MDR validace
5. `interaction_checker_agent.py` - Drug-drug interactions
6. `dosage_advisor_agent.py` - Informační dávkování

#### `app/rag/` - RAG Strategies

```python
# app/rag/hybrid_retriever.py
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

def create_hybrid_retriever(vector_store, documents):
    """Kombinuje semantic + keyword search"""

    # Semantic search
    semantic_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    # Keyword search (BM25)
    keyword_retriever = BM25Retriever.from_documents(documents)
    keyword_retriever.k = 5

    # Ensemble
    ensemble = EnsembleRetriever(
        retrievers=[semantic_retriever, keyword_retriever],
        weights=[0.5, 0.5]
    )

    return ensemble
```

**Strategies to implement:**
- `hybrid_retriever.py` - Semantic + BM25
- `hyde_retriever.py` - Hypothetical Document Embeddings
- `multi_query.py` - Query expansion
- `parent_document.py` - Hierarchical retrieval
- `contextual_compression.py` - Context compression
- `rag_manager.py` - Ensemble všech strategií

#### `app/workflows/` - LangGraph Workflows

```python
# app/workflows/medication_workflow.py
from langgraph.graph import StateGraph, END
from typing import TypedDict

class MedicationState(TypedDict):
    query: str
    query_type: str  # "text" or "image"
    image_data: Optional[str]
    medication_info: Optional[dict]
    # ... další fields

def create_medication_workflow():
    workflow = StateGraph(MedicationState)

    # Nodes
    workflow.add_node("process_query", process_query_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("generate_answer", generate_answer_node)

    # Edges
    workflow.set_entry_point("process_query")
    workflow.add_edge("process_query", "retrieve_context")
    workflow.add_edge("retrieve_context", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()
```

### Configuration Management

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_text_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4-vision-preview"

    # Supabase
    supabase_url: str
    supabase_anon_key: str

    # Další nastavení...

    class Config:
        env_file = ".env"

settings = Settings()
```

### API Endpoints

```python
# app/main.py
@app.post("/api/query/text", response_model=APIResponse)
@limiter.limit("10/minute")
async def text_query(request: Request, query: TextQuery):
    """Textový dotaz na lék"""
    # Implementace...
```

**Endpointy:**
- `POST /api/query/text` - Textové dotazy (10/min)
- `POST /api/query/image` - Obrázky léků (5/min)
- `GET /health` - Health check

### Testing Backend

```bash
# Spuštění všech testů
pytest

# Konkrétní test file
pytest tests/test_api.py -v

# Konkrétní test
pytest tests/test_api.py::test_text_query -v

# S coverage
pytest --cov=app --cov-report=html
```

**Test Structure:**

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_text_query():
    response = client.post(
        "/api/query/text",
        json={"query": "Co je Paralen?"}
    )
    assert response.status_code == 200
    assert "data" in response.json()
```

## Frontend Development

### Component Structure

```tsx
// components/ChatInterface.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  const handleSubmit = async () => {
    const response = await fetch('http://localhost:8000/api/query/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: input })
    })

    const data = await response.json()
    // Handle response...
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Messages display */}
      <div className="flex-1 overflow-y-auto">
        {messages.map((msg, i) => (
          <MessageBubble key={i} {...msg} />
        ))}
      </div>

      {/* Input area */}
      <div className="p-4 border-t">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Zeptejte se na lék..."
        />
        <Button onClick={handleSubmit}>Odeslat</Button>
      </div>
    </div>
  )
}
```

### API Integration

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function queryText(query: string) {
  const response = await fetch(`${API_URL}/api/query/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  })

  if (!response.ok) {
    throw new Error('Query failed')
  }

  return response.json()
}

export async function queryImage(imageData: string) {
  const response = await fetch(`${API_URL}/api/query/image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_data: imageData })
  })

  if (!response.ok) {
    throw new Error('Image query failed')
  }

  return response.json()
}
```

### Testing Frontend

```bash
# Unit tests (Jest)
npm run test

# Watch mode
npm run test:watch

# E2E tests (Playwright)
npm run test:e2e
```

## Database Management

### Running Migrations

Migrace **musí být spuštěny v pořadí**:

```bash
psql "postgresql://postgres:[password]@[host]:5432/postgres"

\i migrations/001_core_drug_tables.sql
\i migrations/002_spc_pil_vectors.sql
\i migrations/003_pricing_data.sql
\i migrations/004_drug_interactions.sql
\i migrations/005_rag_vector_search.sql
\i migrations/006_langchain_tables.sql
```

### Creating New Migration

```sql
-- migrations/007_new_feature.sql
-- Migration: Add new feature
-- Date: 2024-01-15
-- Author: Your Name

BEGIN;

-- Your changes here
CREATE TABLE IF NOT EXISTS new_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT NOW()
);

COMMIT;
```

### Database Schema

**9 hlavních tabulek:**

1. `drug_info` - SÚKL master data
2. `spc_documents` - SPC dokumenty + embeddings
3. `pil_documents` - PIL dokumenty + embeddings
4. `drug_pricing` - Cenové informace
5. `drug_interactions` - Interakce léků
6. `atc_classification` - ATC kódy
7. `user_sessions` - Session tracking (GDPR)
8. `query_analytics` - Anonymizovaná analytika
9. `audit_logs` - Compliance audit trail

### Vector Search Query Example

```sql
-- Sémantické vyhledávání v SPC dokumentech
SELECT
    sd.id,
    sd.drug_id,
    sd.content,
    sd.section,
    1 - (sd.embedding <=> $1::vector) AS similarity
FROM spc_documents sd
WHERE 1 - (sd.embedding <=> $1::vector) > 0.7
ORDER BY sd.embedding <=> $1::vector
LIMIT 5;
```

## Coding Standards

### Python (Backend)

**Style Guide: PEP 8 + Type Hints**

```python
from typing import Optional, List, Dict, Any

def process_medication_query(
    query: str,
    limit: int = 5,
    include_inactive: bool = False
) -> Dict[str, Any]:
    """
    Zpracování dotazu na léčivý přípravek.

    Args:
        query: Textový dotaz uživatele
        limit: Maximální počet výsledků
        include_inactive: Zahrnout neregistrované léky

    Returns:
        Dictionary s výsledky vyhledávání

    Raises:
        ValueError: Pokud je dotaz prázdný
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")

    # Implementation...
    return {"results": []}
```

**Linting & Formatting:**

```bash
# Ruff (linting)
ruff check app/

# Mypy (type checking)
mypy app/

# Black (formatting) - volitelné
black app/
```

### TypeScript (Frontend)

**Style Guide: Airbnb + Prettier**

```typescript
interface MedicationQuery {
  query: string
  type: 'text' | 'image'
}

async function submitQuery(
  data: MedicationQuery
): Promise<APIResponse> {
  // Implementation...
}
```

**Linting:**

```bash
npm run lint
npm run type-check
```

## Environment Variables

### Backend (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...  # Optional

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,https://pillsee.vercel.app

# Rate Limiting
TEXT_QUERY_LIMIT=10/minute
IMAGE_QUERY_LIMIT=5/minute
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=PillSee
```

## Deployment

### Backend (Google Cloud Run)

```bash
# Build Docker image
docker build -t pillsee-backend .

# Tag for GCR
docker tag pillsee-backend gcr.io/[PROJECT_ID]/pillsee-backend

# Push to GCR
docker push gcr.io/[PROJECT_ID]/pillsee-backend

# Deploy to Cloud Run
gcloud run deploy pillsee-backend \
  --image gcr.io/[PROJECT_ID]/pillsee-backend \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### Environment Variables Setup

**Backend (Cloud Run):**
```bash
gcloud run services update pillsee-backend \
  --update-env-vars OPENAI_API_KEY=sk-... \
  --update-env-vars SUPABASE_URL=https://...
```

**Frontend (Vercel):**
```bash
vercel env add NEXT_PUBLIC_API_URL
# Zadejte: https://pillsee-backend-xxx.run.app
```

## Troubleshooting

### Common Issues

#### ModuleNotFoundError

```bash
# Ujistěte se, že je aktivován venv
source venv/bin/activate

# Reinstalujte dependencies
pip install -r requirements.txt
```

#### Supabase Connection Failed

```bash
# Zkontrolujte environment variables
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# Test připojení
python -c "from app.database.vector_store import init_supabase; init_supabase()"
```

#### Rate Limiting v Development

```python
# app/config.py
# Zvyšte limity pro dev
text_query_limit: str = "100/minute"  # Was: 10/minute
image_query_limit: str = "50/minute"  # Was: 5/minute
```

#### CORS Errors

```python
# app/config.py
allowed_origins: str = "http://localhost:3000,http://localhost:3001"
```

### Debug Mode

```bash
# Backend s debug logováním
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Frontend s verbose output
npm run dev -- --debug
```

### Logs

```bash
# Backend logs (Cloud Run)
gcloud run logs read pillsee-backend

# Frontend logs (Vercel)
vercel logs pillsee-frontend
```

## Resources

### Documentation
- **PRD**: `/docs/prd.md`
- **Architecture**: `/docs/architecture.md`
- **API Spec**: `/docs/api/openapi.yaml`
- **Deployment Guide**: `/docs/phase1/PillSee_DEPLOYMENT_GUIDE.md`

### External Links
- **LangChain Docs**: https://python.langchain.com/docs
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **Supabase Docs**: https://supabase.com/docs

### Tools
- **OpenAPI Editor**: https://editor.swagger.io
- **Supabase Dashboard**: https://app.supabase.com
- **Vercel Dashboard**: https://vercel.com/dashboard

---

**Poslední aktualizace**: 2024-01-15
**Maintainer**: PillSee Team
**Support**: dev@pillsee.cz
