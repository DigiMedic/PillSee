# PillSee Backend - Phase 1 Implementation

Kompletní LangChain backend pro PillSee s RAG architekturou a GDPR compliance.

## 📁 Struktura

```
pillsee-backend/
├── app/                      # Hlavní aplikační kód
│   ├── agents/              # LangChain agenti
│   ├── memory/              # GDPR-compliant memory
│   ├── tools/               # LangChain tools (6 nástrojů)
│   ├── retrievers/          # Supabase vectorstore
│   ├── config/              # Konfigurace
│   ├── utils/               # Utilities (callbacks, monitoring)
│   └── rag/                 # (připraveno pro BMAD expansion)
├── migrations/              # Databázové migrace (6 souborů)
├── examples/                # Příklady použití
├── tests/                   # Testy
├── main.py                  # FastAPI server
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image
└── docker-compose.yml      # Local development stack
```

## 🚀 Rychlý Start

### 1. Instalace Dependencies

```bash
cd pillsee-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Nastavení Environment Variables

```bash
cp .env.example .env
# Edituj .env a doplň:
# - OPENAI_API_KEY
# - SUPABASE_URL
# - SUPABASE_KEY
```

### 3. Spuštění Databázových Migrací

```bash
# Připoj se k Supabase databázi
psql "postgresql://..." -f migrations/001_core_drug_tables.sql
psql "postgresql://..." -f migrations/002_spc_pil_vectors.sql
psql "postgresql://..." -f migrations/003_pricing_data.sql
psql "postgresql://..." -f migrations/004_drug_interactions.sql
# Migration 005 spusť AŽ PO nahrání SPC/PIL dat
psql "postgresql://..." -f migrations/006_langchain_tables.sql
```

### 4. Spuštění Serveru

```bash
# Development
uvicorn main:app --reload --port 8000

# Production (Docker)
docker-compose up --build
```

## 🛠️ Dostupné Nástroje (Tools)

Agent má k dispozici 6 LangChain nástrojů:

1. **search_drug** - Vyhledání léku v databázi
2. **get_drug_details** - Detailní informace o léku
3. **check_interactions** - Kontrola lékových interakcí
4. **get_price_comparison** - Srovnání cen z e-shopů
5. **search_sukl** - Vyhledání v SÚKL databázi
6. **get_affiliate_links** - Získání affiliate odkazů

## 📊 Database Schema

Kompletní schéma v `migrations/`:

- **drug_info** - Základní informace o lécích (SÚKL)
- **spc_documents** - SPC dokumenty + vector embeddings (1536D)
- **pil_documents** - PIL dokumenty + vector embeddings (1536D)
- **pricing_data** - Ceny z e-shopů + affiliate odkazy
- **drug_interactions** - Lékové interakce + WHO ATC klasifikace
- **sessions** - GDPR-compliant user sessions
- **conversations** - Anonymizovaná historie konverzací

## 🔒 GDPR Compliance

### PII Anonymizace

Memory systém automaticky anonymizuje:
- Email adresy → `[EMAIL]`
- Telefonní čísla → `[PHONE]`
- Rodná čísla → `[ID_NUMBER]`

### Data Retention

- **Conversations**: 90 dní, pak automatické smazání
- **Sessions**: Expirace po 30 minutách neaktivity
- **Analytics**: Anonymizovaná data bez PII (retained forever)

### Právo na výmaz

```python
# GDPR erasure request
from app.memory.gdpr_memory import GDPRConversationMemory

memory = GDPRConversationMemory(session_id="...")
memory.delete_conversation()  # Smaže všechna data
```

## 🧪 Testování

```bash
# Unit testy
pytest tests/unit/

# Integration testy
pytest tests/integration/

# Všechny testy
pytest
```

## 📝 Příklady Použití

```python
from app.agents.pillsee_agent import create_agent

# Vytvoř agenta
agent = create_agent(session_id="user-123")

# Dotaz
response = agent.query("Jaké vedlejší účinky má Paralen?")

print(response["response"])
print(response["sources"])  # RAG zdroje
print(response["conversation_summary"])
```

Více příkladů v `examples/usage_examples.py`

## 🔗 API Endpointy (FastAPI)

```
POST   /api/v1/chat           - Poslat zprávu chatbotu
GET    /api/v1/history        - Získat historii konverzace
DELETE /api/v1/session        - Smazat session (GDPR)
GET    /api/v1/health         - Health check
```

API dokumentace: http://localhost:8000/docs

## 🐳 Docker

```bash
# Build
docker build -t pillsee-backend .

# Run
docker run -p 8000:8000 --env-file .env pillsee-backend

# Docker Compose (PostgreSQL + Redis + Backend)
docker-compose up
```

## 📚 Další Dokumentace

- **Phase 1 Overview**: `../docs/phase1/PillSee_PHASE1_SUMMARY.md`
- **Deployment Guide**: `../docs/phase1/PillSee_DEPLOYMENT_GUIDE.md`
- **BMAD Architecture**: `../docs/architecture.md` (pro Sprint 1 expansion)
- **Security Strategy**: `../docs/security-strategy.md`

## 🚀 Sprint 1: BMAD Expansion

Phase 1 je **single-agent** systém. Sprint 1 rozšíří na **6-agent** multi-agent architekturu:

1. **Supervisor** - Orchestrátor (refactor existing agent)
2. **Triage Agent** - Klasifikace dotazů
3. **RAG Expert** - 6 RAG strategií
4. **Safety Monitor** - MDR validace
5. **Interaction Checker** - Lékové interakce
6. **Dosage Advisor** - Informační dávkování

Viz `../docs/architecture.md` lines 430-680 pro detaily.

## 📞 Support

Pro otázky nebo problémy viz hlavní `CONSOLIDATION_REPORT.md` v repository root.

---

**Last Updated**: 2025-12-06  
**Version**: Phase 1 - Single Agent RAG System  
**Status**: ✅ Production Ready
