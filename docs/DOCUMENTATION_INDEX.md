# PillSee - Kompletní dokumentační index

Vítejte v dokumentaci PillSee projektu! Tento index vám pomůže rychle najít potřebné informace.

## 📚 Dokumentační struktura

### Pro uživatele

| Dokument | Popis | Cílová skupina |
|----------|-------|----------------|
| [Uživatelská příručka](USER_GUIDE.md) | Kompletní návod k používání PillSee | Koncoví uživatelé |
| [FAQ](USER_GUIDE.md#často-kladené-otázky-faq) | Nejčastější dotazy | Všichni uživatelé |

### Pro vývojáře

| Dokument | Popis | Použití |
|----------|-------|---------|
| [Developer Guide](DEVELOPER_GUIDE.md) | Kompletní vývojářská příručka | Setup, development, testing |
| [BMAD Development Guide](BMAD_DEVELOPMENT_GUIDE.md) | BMAD metodika pro multi-agent systém | Sprint planning, metriky |
| [API Documentation](api/README.md) | OpenAPI specifikace + příklady | API integration |
| [System Architecture](architecture/system-architecture.md) | Architektura systému + diagramy | Pochopení systému |

### Pro product management

| Dokument | Popis | Použití |
|----------|-------|---------|
| [PRD](prd.md) | Product Requirements Document | User stories, funkce |
| [Architecture](architecture.md) | Kompletní 6-agent BMAD design | Technická specifikace |
| [Security Strategy](security-strategy.md) | GDPR/MDR compliance | Compliance, audit |

### Phase 1 dokumentace

| Dokument | Popis |
|----------|-------|
| [Phase 1 Summary](phase1/PillSee_PHASE1_SUMMARY.md) | Shrnutí Phase 1 implementace |
| [Deployment Guide](phase1/PillSee_DEPLOYMENT_GUIDE.md) | Production deployment guide |
| [Implementation Checklist](phase1/PillSee_IMPLEMENTATION_CHECKLIST.md) | Checklist pro implementaci |
| [Quick Reference](phase1/PillSee_QUICK_REFERENCE.md) | Rychlá reference |

## 🎯 Rychlé odkazy podle úkolu

### "Chci začít vyvíjet"
1. [Developer Guide - Quick Setup](DEVELOPER_GUIDE.md#quick-setup)
2. [Project Structure](DEVELOPER_GUIDE.md#project-structure)
3. [Development Workflow](DEVELOPER_GUIDE.md#development-workflow)

### "Potřebuji pochopit architekturu"
1. [System Architecture](architecture/system-architecture.md)
2. [Architecture Deep Dive](architecture.md)
3. [BMAD Analysis](BMAD_DEVELOPMENT_GUIDE.md)

### "Chci integrovat API"
1. [API Documentation](api/README.md)
2. [OpenAPI Spec](api/openapi.yaml)
3. [Code Examples](api/README.md#code-examples)

### "Implementuji multi-agent systém"
1. [BMAD Development Guide](BMAD_DEVELOPMENT_GUIDE.md)
2. [Agent Implementation](BMAD_DEVELOPMENT_GUIDE.md#build-phase-týden-1-2)
3. [Metrics & Analytics](BMAD_DEVELOPMENT_GUIDE.md#measure-phase-týden-3)

### "Potřebuji nasadit do produkce"
1. [Deployment Guide](phase1/PillSee_DEPLOYMENT_GUIDE.md)
2. [Environment Setup](DEVELOPER_GUIDE.md#environment-variables)
3. [CI/CD Pipeline](.github/workflows/docs-generation.yml)

### "Chci přidat novou funkci"
1. [PRD - User Stories](prd.md)
2. [Implementation Checklist](phase1/PillSee_IMPLEMENTATION_CHECKLIST.md)
3. [Testing Guide](DEVELOPER_GUIDE.md#testing)

## 📊 Dokumentace podle komponent

### Backend (FastAPI + LangChain)

```
pillsee-backend/
├── app/
│   ├── agents/          → BMAD_DEVELOPMENT_GUIDE.md
│   ├── rag/             → architecture/system-architecture.md
│   ├── workflows/       → DEVELOPER_GUIDE.md#backend-development
│   ├── database/        → DEVELOPER_GUIDE.md#database-management
│   └── main.py          → api/openapi.yaml
├── migrations/          → DEVELOPER_GUIDE.md#database-setup
└── tests/              → DEVELOPER_GUIDE.md#testing-backend
```

### Frontend (Next.js 14)

```
pillsee-frontend/
├── app/                → DEVELOPER_GUIDE.md#frontend-development
├── components/         → USER_GUIDE.md (pro UX/UI)
└── lib/               → api/README.md#code-examples
```

### Database (PostgreSQL + pgvector)

```
migrations/
├── 001_*.sql          → architecture/system-architecture.md#database-schema
├── 002_*.sql          → DEVELOPER_GUIDE.md#database-management
└── ...                → ER Diagram v system-architecture.md
```

## 🔍 Dokumentace podle tématu

### AI & RAG

- **Architektura**: [System Architecture - RAG Components](architecture/system-architecture.md#component-architecture)
- **Implementace**: [BMAD Guide - RAG Expert Agent](BMAD_DEVELOPMENT_GUIDE.md#3-rag-expert-agent)
- **Strategie**: [Architecture - RAG Strategies](architecture.md)

### LangGraph Workflows

- **Design**: [Architecture - Multi-Agent System](architecture.md)
- **Implementace**: [BMAD Guide - BUILD Phase](BMAD_DEVELOPMENT_GUIDE.md#build-phase-týden-1-2)
- **Metriky**: [BMAD Guide - MEASURE Phase](BMAD_DEVELOPMENT_GUIDE.md#measure-phase-týden-3)

### GDPR & Compliance

- **Strategie**: [Security Strategy](security-strategy.md)
- **Implementace**: [Developer Guide - Security](DEVELOPER_GUIDE.md#security-and-compliance)
- **Audit**: [Architecture - Database Schema](architecture/system-architecture.md#database-schema)

### Testing

- **Backend**: [Developer Guide - Testing Backend](DEVELOPER_GUIDE.md#testing-backend)
- **Frontend**: [Developer Guide - Testing Frontend](DEVELOPER_GUIDE.md#testing-frontend)
- **E2E**: [Implementation Checklist](phase1/PillSee_IMPLEMENTATION_CHECKLIST.md)

### Deployment

- **Backend**: [Deployment Guide](phase1/PillSee_DEPLOYMENT_GUIDE.md)
- **Frontend**: [Developer Guide - Deployment](DEVELOPER_GUIDE.md#deployment)
- **CI/CD**: [GitHub Actions](.github/workflows/docs-generation.yml)

## 📖 Dokumentační standardy

### Markdown Formatting

Všechny `.md` soubory dodržují:
- **Linting**: `.markdownlint.json` config
- **Max line length**: 120 znaků
- **Headings**: ATX style (`#` syntax)
- **Code blocks**: Vždy s language specifier

### Code Documentation

- **Python**: Docstrings (Google style) + type hints
- **TypeScript**: JSDoc comments + types
- **SQL**: Inline comments v migracích

### Diagram Standards

- **Format**: Mermaid (renderuje se na GitHubu)
- **Types**: System, Component, Sequence, ER
- **Style**: Konzistentní barvy podle typu

## 🔄 Aktualizace dokumentace

### Kdy aktualizovat

| Změna | Dokumenty k aktualizaci |
|-------|------------------------|
| Nový API endpoint | `api/openapi.yaml`, `api/README.md` |
| Nový agent | `BMAD_DEVELOPMENT_GUIDE.md`, `architecture/system-architecture.md` |
| Database schema | `DEVELOPER_GUIDE.md`, `system-architecture.md` |
| Deployment proces | `phase1/PillSee_DEPLOYMENT_GUIDE.md` |
| User-facing feature | `USER_GUIDE.md` |

### Automatická generace

**GitHub Actions** automaticky generuje:
- ✅ API dokumentaci (Redoc + Swagger)
- ✅ Code documentation (Sphinx)
- ✅ Docstring coverage report
- ✅ Markdown linting
- ✅ Link checking

Viz: `.github/workflows/docs-generation.yml`

## 🎓 Tutoriály a příklady

### Getting Started Tutorial

1. **Setup**: [Developer Guide - Quick Setup](DEVELOPER_GUIDE.md#quick-setup)
2. **První dotaz**: [User Guide - Rychlý start](USER_GUIDE.md#rychlý-start)
3. **API Integration**: [API README - Code Examples](api/README.md#code-examples)

### Advanced Tutorials

- **BMAD Implementation**: [BMAD Guide - Sprint 1](BMAD_DEVELOPMENT_GUIDE.md#sprint-1-bmad-multi-agent-implementation-current)
- **RAG Optimization**: [Architecture - RAG Strategies](architecture.md)
- **Multi-Agent Orchestration**: [System Architecture](architecture/system-architecture.md)

## 📞 Podpora

### Kde hledat pomoc

| Problém | Zdroj |
|---------|-------|
| Setup issues | [Developer Guide - Troubleshooting](DEVELOPER_GUIDE.md#troubleshooting) |
| API errors | [API README - Error Handling](api/README.md#error-handling) |
| Deployment failures | [Deployment Guide](phase1/PillSee_DEPLOYMENT_GUIDE.md) |
| BMAD metrics | [BMAD Guide](BMAD_DEVELOPMENT_GUIDE.md) |

### Kontakty

- **Email**: dev@pillsee.cz
- **GitHub Issues**: https://github.com/pillsee/pillsee/issues
- **Documentation Site**: https://docs.pillsee.cz

## 🔖 Changelog

### Version 1.0.0 (2024-01-15)

✅ **Kompletní dokumentace:**
- API Documentation (OpenAPI 3.0)
- System Architecture (Mermaid diagramy)
- User Guide (česky)
- Developer Guide
- BMAD Development Guide
- CI/CD Automation

---

**Poslední aktualizace**: 2024-01-15
**Maintainer**: PillSee Documentation Team
**Verze**: 1.0.0
