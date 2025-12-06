# PillSee

![PillSee Logo](https://i.ibb.co/z4SpKPp/Pill-See-cover.png)

PillSee je inovativní AI-powered chatovací platforma zaměřená na poskytování přesných a relevantních informací o léčivých přípravcích pro české uživatele. Projekt je součástí iniciativy DigiMedic pro digitalizaci zdravotnictví.

## 🎯 Status Projektu

✅ **Repository Consolidation: COMPLETE** (2025-12-06)  
✅ **Phase 1 Implementation: READY**  
📋 **Sprint 1 BMAD: Designed, awaiting implementation**

## 📁 Struktura Projektu

```
PillSee/
├── 📂 docs/                    # BMAD Architecture Documentation
│   ├── project-brief.md        # Vision, stakeholders, budget €24K
│   ├── prd.md                  # 15 user stories, API specs
│   ├── architecture.md         # 6-agent system specification
│   ├── security-strategy.md    # GDPR/MDR compliance
│   └── phase1/                 # Phase 1 documentation
│
├── 📂 pillsee-backend/         # Complete LangChain Backend
│   ├── app/                    # Application code (~2,881 LOC)
│   │   ├── agents/            # LangChain agents
│   │   ├── memory/            # GDPR-compliant memory
│   │   ├── tools/             # 6 LangChain tools
│   │   ├── retrievers/        # Supabase vectorstore
│   │   └── ...
│   ├── migrations/            # Database migrations (6 files)
│   ├── main.py                # FastAPI server
│   └── README_BACKEND.md      # Backend documentation
│
├── 📄 CONSOLIDATION_REPORT.md  # Complete consolidation report
└── 📄 README.md                # This file
```

## 🚀 Hlavní Funkce

- **AI Chatbot**: Inteligentní konverzační rozhraní pro dotazy o lécích
- **Integrace SÚKL**: Přímé napojení na databázi Státního ústavu pro kontrolu léčiv
- **RAG Architecture**: Retrieval-Augmented Generation pro přesné odpovědi
- **GDPR Compliance**: Anonymizace PII, 90-denní data retention
- **Lékové Interakce**: Kontrola drug-drug interactions
- **Cenové Srovnání**: Affiliate links na e-shopy

## 🛠️ Technologický Stack

### Backend (Phase 1 ✅)
- **Framework**: FastAPI + LangChain
- **LLM**: OpenAI GPT-4o-mini
- **Database**: PostgreSQL 17 + pgvector (Supabase)
- **Embeddings**: text-embedding-3-small (1536D)
- **Memory**: GDPR-compliant conversation history
- **Docker**: Complete containerization

### Backend (Sprint 1 BMAD 📋)
- **Orchestration**: LangGraph multi-agent system
- **Agents**: 6-agent architecture (Supervisor, Triage, RAG Expert, Safety Monitor, Interaction Checker, Dosage Advisor)
- **RAG Strategies**: 6 strategies (hybrid, HyDE, multi-query, parent-doc, compression, ensemble)

### Frontend (Sprint 3 📅)
- **Framework**: Next.js 14
- **UI Library**: shadcn/ui + Tailwind CSS
- **AI SDK**: Vercel AI SDK
- **Type Safety**: TypeScript

### Infrastructure
- **Hosting Backend**: Cloud Run
- **Hosting Frontend**: Vercel
- **Database**: Supabase (managed PostgreSQL)
- **CDN**: Cloudflare
- **Monitoring**: Sentry + Langsmith

## 📊 Database Schema

6 kompletních migrací v `pillsee-backend/migrations/`:

1. **Core Drug Tables** - drug_info s SÚKL daty
2. **SPC/PIL Vectors** - Dokumenty s 1536D embeddings
3. **Pricing Data** - E-commerce ceny + affiliate odkazy
4. **Drug Interactions** - Interakce + WHO ATC klasifikace
5. **RAG Vector Search** - pgvector IVFFlat indexy + GDPR sessions
6. **LangChain Tables** - Phase 1 specifické tabulky

## 🚀 Rychlý Start

### 1. Clone Repository

```bash
cd /Users/petrsovadina/Desktop/Develope/PillSee
```

### 2. Backend Setup

```bash
cd pillsee-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables

```bash
cp .env.example .env
# Edituj .env:
# - OPENAI_API_KEY=...
# - SUPABASE_URL=...
# - SUPABASE_KEY=...
```

### 4. Database Migrations

```bash
# Spusť migrace v pořadí 001-006
psql "postgresql://..." -f migrations/001_core_drug_tables.sql
# ... (viz pillsee-backend/README_BACKEND.md)
```

### 5. Run Backend

```bash
# Development
uvicorn main:app --reload

# Docker
docker-compose up
```

## 📚 Dokumentace

### Pro Development
- **Backend README**: `pillsee-backend/README_BACKEND.md`
- **Consolidation Report**: `CONSOLIDATION_REPORT.md`
- **Architecture Spec**: `docs/architecture.md`
- **Security Strategy**: `docs/security-strategy.md`

### Phase 1 Guides
- **Phase 1 Summary**: `docs/phase1/PillSee_PHASE1_SUMMARY.md`
- **Deployment Guide**: `docs/phase1/PillSee_DEPLOYMENT_GUIDE.md`
- **Implementation Checklist**: `docs/phase1/PillSee_IMPLEMENTATION_CHECKLIST.md`
- **Quick Reference**: `docs/phase1/PillSee_QUICK_REFERENCE.md`

### BMAD Architecture
- **Project Brief**: `docs/project-brief.md` - Vision, timeline, budget
- **PRD**: `docs/prd.md` - 15 user stories, API specifications
- **Architecture**: `docs/architecture.md` - Complete 6-agent system
- **Security**: `docs/security-strategy.md` - GDPR/MDR compliance

## 🎯 Development Roadmap

### ✅ Phase 1: Single-Agent Foundation (COMPLETE)
- LangChain backend s RAG
- 6 LangChain tools
- GDPR-compliant memory
- Supabase integration
- Docker setup
- Database migrations

### 📋 Sprint 1: BMAD Multi-Agent (DESIGNED)
- 6-agent LangGraph orchestration
- Triage Agent - query classification
- RAG Expert - 6 RAG strategies
- Safety Monitor - MDR validation
- Interaction Checker - drug-drug interactions
- Dosage Advisor - informational dosage

### 📅 Sprint 2: RAG Enhancement
- Implement 6 RAG strategies
- GDPR/MDR utilities
- PII anonymization
- Comprehensive testing

### 📅 Sprint 3: Frontend Integration
- Next.js 14 frontend
- Vercel AI SDK streaming
- shadcn/ui components
- Real-time chat interface

## 🔒 Compliance

### GDPR
- ✅ PII anonymization (email, phone, ID numbers)
- ✅ 90-day data retention
- ✅ Right to erasure
- ✅ Hashed IP addresses
- ✅ Audit logging

### MDR Class I (Medical Device)
- ✅ No diagnostic claims
- ✅ Informational only disclaimers
- ✅ Safety warnings
- ✅ Compliance audit trails

## 🤝 Contributing

Pro přispěvání do projektu:
1. Přečti `docs/architecture.md` pro pochopení systému
2. Zkontroluj `CONSOLIDATION_REPORT.md` pro aktuální stav
3. Následuj coding standards v `pillsee-backend/`

## 📞 Support

Pro otázky viz:
- Backend docs: `pillsee-backend/README_BACKEND.md`
- Architecture: `docs/architecture.md`
- Consolidation report: `CONSOLIDATION_REPORT.md`

---

**Project Status**: ✅ Phase 1 Complete, Ready for Sprint 1  
**Last Updated**: 2025-12-06  
**Version**: 1.0.0-phase1  
**License**: Proprietary
