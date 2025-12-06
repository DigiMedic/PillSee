# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PillSee je AI-powered chatovací platforma pro poskytování informací o léčivých přípravcích v České republice. Projekt využívá LangChain/LangGraph pro multi-agent orchestraci s napojením na databázi SÚKL (Státní ústav pro kontrolu léčiv).

**Současný stav**: ✅ Phase 1 Complete (single-agent RAG), 📋 Sprint 1 BMAD Designed (6-agent system)

## Development Commands

### Backend Development

```bash
cd pillsee-backend

# Aktivace virtuálního prostředí
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Instalace dependencies
pip install -r requirements.txt

# Spuštění dev serveru
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Spuštění testů
pytest
pytest tests/test_api.py -v
pytest -k "test_name" -v  # Konkrétní test

# Type checking (pokud je mypy nainstalován)
mypy app/

# Linting
ruff check app/
```

### Frontend Development

```bash
cd pillsee-frontend

# Instalace dependencies
npm install

# Dev server
npm run dev          # http://localhost:3000

# Production build
npm run build
npm run start

# Linting & Type check
npm run lint
npm run type-check

# Testing
npm run test
npm run test:watch
```

### Docker

```bash
cd pillsee-backend

# Build a spuštění
docker-compose up --build

# Spuštění na pozadí
docker-compose up -d

# Zobrazení logů
docker-compose logs -f

# Zastavení
docker-compose down
```

### Database Migrations

Migrace jsou v `pillsee-backend/migrations/` a **musí být spuštěny v pořadí**:

```bash
# Připojení k Supabase databázi
psql "postgresql://postgres:[password]@[host]:5432/postgres"

# Spuštění migrací v pořadí
\i migrations/001_core_drug_tables.sql
\i migrations/002_spc_pil_vectors.sql
\i migrations/003_pricing_data.sql
\i migrations/004_drug_interactions.sql
\i migrations/005_rag_vector_search.sql
\i migrations/006_langchain_tables.sql
```

## Architecture Overview

### Backend (FastAPI + LangChain)

**Phase 1 (✅ Implementováno):**
- Single-agent RAG system v `app/workflows/medication_workflow.py`
- 6 LangChain tools v `app/tools/`
- GDPR-compliant memory v `app/memory/gdpr_memory.py`
- Supabase vector store integration v `app/database/vector_store.py`
- FastAPI endpoints v `app/main.py`

**Sprint 1 BMAD (📋 Designed, čeká na implementaci):**
- **LangGraph Orchestration**: Multi-agent system s 6 agenty
- **Agents** (plánováno v `app/agents/`):
  - `supervisor_agent.py` - Řídí koordinaci všech agentů
  - `triage_agent.py` - Klasifikace dotazů (general/drug_specific/interaction/dosage/side_effects)
  - `rag_expert_agent.py` - 6 RAG strategií (hybrid, HyDE, multi-query, parent-doc, compression, ensemble)
  - `safety_monitor_agent.py` - MDR validace, safety warnings
  - `interaction_checker_agent.py` - Drug-drug interactions
  - `dosage_advisor_agent.py` - Informační dávkování (ne prescriptive)

**RAG Strategies** (v `app/rag/`):
- `hybrid_retriever.py` - Kombinace semantic + keyword search
- `hyde_retriever.py` - Hypothetical Document Embeddings
- `multi_query.py` - Multi-query expansion
- `parent_document.py` - Parent document retrieval
- `contextual_compression.py` - Contextual compression
- `rag_manager.py` - Ensemble všech strategií

### Frontend (Next.js 14)

```
pillsee-frontend/
├── app/                    # Next.js 14 App Router
├── components/             # React komponenty (shadcn/ui)
├── lib/                    # Utilities
└── public/                 # Statické assets
```

### Database Schema (PostgreSQL + pgvector)

**9 hlavních tabulek**:
1. `drug_info` - SÚKL data (kód SÚKL, název, forma, dávka)
2. `spc_documents` / `pil_documents` - SPC/PIL texty + 1536D embeddings
3. `drug_pricing` - Ceny z e-shopů + affiliate odkazy
4. `drug_interactions` - Drug-drug interactions
5. `atc_classification` - WHO ATC codes
6. `user_sessions` - GDPR session tracking (90-day retention)
7. `query_analytics` - Anonymizovaná analytika
8. `conversation_history` - Konverzační historie (PII anonymizovaná)
9. `audit_logs` - Compliance audit trail

**Indexy**:
- `IVFFlat` indexy na vektorových sloupcích (cosine distance)
- B-tree na `sukl_code`, `atc_code`, `session_id`

## Environment Variables

```bash
# Backend (.env v pillsee-backend/)
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...  # Volitelné
ALLOWED_ORIGINS=http://localhost:3000,https://pillsee.vercel.app
ENVIRONMENT=development
LOG_LEVEL=INFO

# Frontend (.env.local v pillsee-frontend/)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=PillSee
```

## Code Organization Principles

### Backend Code Layout

- **app/agents/** - LangGraph/LangChain agents (BMAD multi-agent)
- **app/memory/** - GDPR-compliant conversation memory
- **app/tools/** - LangChain tools (SÚKL lookup, pricing, interactions, etc.)
- **app/rag/** - RAG retrieval strategies
- **app/workflows/** - LangGraph workflows (current: single-agent)
- **app/database/** - Supabase/pgvector integration
- **app/api/** - FastAPI endpoints (v `app/main.py`)
- **app/config.py** - Centralized configuration (pydantic-settings)
- **app/models.py** - Pydantic models pro API

### Critical Design Patterns

**1. GDPR Compliance**:
- Všechny PII data (email, telefon, rodná čísla) musí být anonymizována před uložením
- Implementace v `app/memory/gdpr_memory.py`
- 90-day data retention policy
- IP adresy hashované (SHA-256)

**2. MDR Class I Medical Device**:
- Žádné diagnostické/prescriptive claims
- Vždy zahrnout medical disclaimer (v `app/config.py`)
- Safety warnings pro kontraindikace
- Audit trail pro compliance

**3. RAG Architecture**:
- Embeddings: OpenAI `text-embedding-3-small` (1536D)
- Vector store: Supabase pgvector s IVFFlat indexy
- Retrieval: Hybrid search (semantic + keyword BM25)
- Reranking: Contextual compression

**4. Rate Limiting**:
- Implementováno pomocí `slowapi`
- Text queries: 10/minute per IP
- Image queries: 5/minute per IP
- Konfigurace v `app/main.py`

## Testing Strategy

```bash
# Backend unit tests
pytest tests/test_api.py          # API endpoints
pytest tests/test_sukl_processor.py  # SÚKL data processing
pytest tests/test_rag_components.py  # RAG strategies

# Frontend tests
npm run test                      # Jest unit tests
npm run test:watch               # Watch mode
```

## Deployment

**Backend**: Google Cloud Run (containerized FastAPI)
**Frontend**: Vercel (Next.js)
**Database**: Supabase (managed PostgreSQL + pgvector)

Deployment guide: `docs/phase1/PillSee_DEPLOYMENT_GUIDE.md`

## Documentation Structure

```
docs/
├── project-brief.md              # Vision, stakeholders, €24K budget
├── prd.md                        # 15 user stories, API specs
├── architecture.md               # Complete 6-agent BMAD system
├── security-strategy.md          # GDPR/MDR compliance strategy
├── phase1/                       # Phase 1 implementation docs
│   ├── PillSee_PHASE1_SUMMARY.md
│   ├── PillSee_DEPLOYMENT_GUIDE.md
│   ├── PillSee_IMPLEMENTATION_CHECKLIST.md
│   └── PillSee_QUICK_REFERENCE.md
└── BMAD_*.md                     # BMAD architecture analysis

pillsee-backend/
└── README_BACKEND.md             # Backend developer guide

CONSOLIDATION_REPORT.md           # Repository consolidation status
```

## Implementation Priorities

**Sprint 1 (Current Priority)**: BMAD Multi-Agent Implementation
1. Implementovat LangGraph orchestration v `app/agents/`
2. Vytvořit 6 specialized agents
3. Integrovat 6 RAG strategies z `app/rag/`
4. GDPR/MDR utilities
5. Comprehensive testing

**Sprint 2**: RAG Enhancement
- Fine-tune retrieval strategies
- Optimize embeddings
- A/B testing different approaches

**Sprint 3**: Frontend Integration
- Next.js 14 UI
- Vercel AI SDK streaming
- Real-time chat interface

## Common Issues

### ModuleNotFoundError při importu
- Ujistěte se, že máte aktivované venv: `source venv/bin/activate`
- Zkontrolujte instalované balíčky: `pip list`
- Reinstalujte dependencies: `pip install -r requirements.txt`

### Supabase Connection Issues
- Ověřte správnost `SUPABASE_URL` a `SUPABASE_ANON_KEY` v `.env`
- Zkontrolujte network connectivity
- Supabase project musí mít povolenou pgvector extension

### Rate Limiting v Development
- Rate limity jsou aplikovány per IP address
- Pro dev účely můžete upravit limity v `app/config.py`

### Database Migrations Failed
- Migrace **musí být spuštěny v pořadí** (001 → 006)
- pgvector extension musí být nainstalovaná: `CREATE EXTENSION IF NOT EXISTS vector;`
- Zkontrolujte database credentials

## Key Files to Understand First

1. **Backend Entry**: `pillsee-backend/app/main.py` - FastAPI app setup
2. **Configuration**: `pillsee-backend/app/config.py` - Všechna nastavení
3. **Current Workflow**: `app/workflows/medication_workflow.py` - Phase 1 RAG
4. **Architecture Spec**: `docs/architecture.md` - BMAD multi-agent design
5. **Database Schema**: `pillsee-backend/migrations/` - All tables

## Contributing Guidelines

1. Před implementací si přečíst `docs/architecture.md` pro pochopení celkové architektury
2. Používat type hints ve všech Python funkcích
3. Dodržovat GDPR/MDR compliance requirements
4. Přidat testy pro novou funkcionalitu
5. Update dokumentaci v `docs/` při změnách v architektuře
