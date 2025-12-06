# PillSee - Project Brief

## Executive Summary

**PillSee** je AI-powered chatovací platforma pro poskytování přesných informací o léčivých přípravcích registrovaných v České republice. Projekt kombinuje pokročilé RAG (Retrieval-Augmented Generation) techniky s oficiální databází SÚKL (Státní ústav pro kontrolu léčiv) pro vytvoření inteligentního, anonymního a GDPR-compliant asistenta.

**Status**: ✅ Phase 1 Complete | 📋 Sprint 1 BMAD Designed
**Budget**: €24,000 (6-month development)
**Target Launch**: Q2 2024

## Vision

Demokratizovat přístup k lékařským informacím v ČR pomocí AI, při dodržení nejvyšších standardů ochrany soukromí (GDPR) a zdravotnických regulací (MDR Class I).

## Problem Statement

### Current Challenges

1. **Nedostupné informace**: Pacienti nemají snadný přístup k oficiálním informacím o lécích (SPC, PIL)
2. **Komplikovaná terminologie**: Odborné texty jsou pro laiky obtížně srozumitelné
3. **Roztříštěné zdroje**: Informace rozptýleny mezi SÚKL, lékárny, e-shopy
4. **Nedůvěryhodné zdroje**: Mnoho neověřených informací online
5. **Jazyková bariéra**: Česká specifika léčiv nejsou v zahraničních AI pokryta

### Market Opportunity

- **Target Market**: 10.5M obyvatel ČR
- **Digital Health Market CZ**: €120M (2024)
- **Growth Rate**: 15% CAGR
- **Competition**: Žádný český AI lékový asistent s SÚKL integrací

## Solution

### Core Features (Phase 1) ✅

1. **AI Chatbot**
   - Konverzační rozhraní v češtině
   - Rychlé odpovědi (< 5s)
   - Context-aware dialogy

2. **SÚKL Integration**
   - Real-time data z oficiální databáze
   - SPC/PIL dokumenty s embeddings
   - Daily synchronizace

3. **RAG Architecture**
   - Vector search (pgvector, 1536D)
   - Semantic + keyword hybrid retrieval
   - Contextual compression

4. **GDPR Compliance**
   - Anonymní použití (žádná registrace)
   - PII anonymization
   - 90-day data retention
   - IP hashing

### Advanced Features (Sprint 1-3) 📋

**Sprint 1: BMAD Multi-Agent**
- 6-agent LangGraph orchestration
- Advanced RAG strategies (6 variants)
- Safety monitoring (MDR compliance)
- Drug-drug interaction checker

**Sprint 2: RAG Enhancement**
- Fine-tuned embeddings (Czech medical)
- Query expansion
- A/B testing framework
- Performance optimization

**Sprint 3: Frontend & UX**
- Next.js 14 Progressive Web App
- Image recognition (GPT-4 Vision)
- Voice input
- Multi-language (CS, SK, EN)

## Stakeholders

### Primary Stakeholders

| Role | Name | Responsibility |
|------|------|----------------|
| **Product Owner** | Petr Sovadina | Vision, roadmap, PRD |
| **Tech Lead** | [TBD] | Architecture, BMAD implementation |
| **Backend Dev** | [TBD] | FastAPI, LangChain, LangGraph |
| **Frontend Dev** | [TBD] | Next.js, UI/UX |
| **Data Engineer** | [TBD] | SÚKL ETL, vector embeddings |
| **DevOps** | [TBD] | Cloud Run, Supabase, CI/CD |

### Secondary Stakeholders

- **Compliance Officer**: GDPR/MDR oversight
- **Medical Advisor**: Content validation
- **QA Engineer**: Testing, quality assurance
- **UX Designer**: User research, design system

### External Stakeholders

- **SÚKL**: Data provider, regulatory compliance
- **Users**: Czech patients, pharmacists
- **Healthcare Providers**: Potential B2B customers
- **Investors**: Seed funding (if applicable)

## Business Model

### Revenue Streams

1. **Affiliate Links** (Phase 1)
   - E-commerce ceny + affiliate
   - Revenue share: 5-10%
   - Est. €500/month @ 10K MAU

2. **Premium Features** (Phase 2)
   - Advanced analytics
   - Personalized recommendations
   - Multi-user accounts
   - Pricing: €4.99/month

3. **B2B Licensing** (Phase 3)
   - Healthcare providers
   - Pharmacy chains
   - Custom white-label
   - Pricing: €500-2000/month/org

4. **API Access** (Phase 4)
   - Developer API
   - Volume pricing
   - SLA guarantees

### Cost Structure

**Development (6 months)**: €24,000
- Backend development: €8,000
- Frontend development: €6,000
- Data engineering: €4,000
- DevOps & Infrastructure: €3,000
- Design & UX: €2,000
- Compliance & Legal: €1,000

**Operational (monthly)**:
- **Infrastructure**: €150/month
  - Cloud Run: €50
  - Supabase: €50
  - Vercel: €20
  - CDN: €30
- **AI APIs**: €300/month
  - OpenAI: €250 @ 50K queries
  - Others: €50
- **Monitoring**: €50/month
  - Sentry, Langsmith

**Total Monthly OpEx**: ~€500

### Break-even Analysis

- **MAU Target**: 20,000 users
- **Conversion Rate**: 2% premium
- **Avg Revenue per User**: €2.50
- **Monthly Revenue**: €1,000
- **Break-even**: ~6 months post-launch

## Timeline & Milestones

### Phase 1: Foundation (COMPLETE) ✅
**Duration**: 8 weeks
**Budget**: €8,000
**Status**: Delivered 2024-01-15

**Deliverables**:
- ✅ FastAPI backend with LangChain
- ✅ 6 LangChain tools
- ✅ GDPR-compliant memory
- ✅ Supabase vector store
- ✅ Database migrations (6 files)
- ✅ Docker setup
- ✅ Basic RAG workflow

### Sprint 1: BMAD Multi-Agent (CURRENT) 📋
**Duration**: 5 weeks
**Budget**: €6,000
**Status**: Designed, awaiting implementation

**Week 1-2: BUILD**
- [ ] Implement 6 agents (Supervisor, Triage, RAG Expert, Safety, Interaction, Dosage)
- [ ] 6 RAG strategies (Hybrid, HyDE, Multi-Query, Parent Doc, Compression, Ensemble)
- [ ] LangGraph orchestration

**Week 3: MEASURE**
- [ ] Metrics framework (RAGAS, latency, cost)
- [ ] Structured logging
- [ ] Performance tracking

**Week 4: ANALYZE**
- [ ] A/B testing results
- [ ] Bottleneck identification
- [ ] Cost optimization

**Week 5: DEPLOY**
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] Documentation

### Sprint 2: RAG Enhancement (PLANNED) 📅
**Duration**: 4 weeks
**Budget**: €4,000

**Deliverables**:
- Fine-tuned embeddings (Czech medical corpus)
- Query expansion (Czech synonyms)
- Feedback loop integration
- Performance optimization

### Sprint 3: Frontend Integration (PLANNED) 📅
**Duration**: 6 weeks
**Budget**: €6,000

**Deliverables**:
- Next.js 14 Progressive Web App
- shadcn/ui component library
- Real-time streaming chat
- Image recognition (GPT-4 Vision)
- Responsive design (mobile-first)

## Success Metrics

### Technical KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Response Time** | < 3s | 95th percentile |
| **Accuracy** | > 90% | RAGAS faithfulness |
| **Availability** | 99.5% | Uptime monitoring |
| **Error Rate** | < 1% | Failed queries |
| **Cache Hit Rate** | > 40% | Redis analytics |

### Business KPIs

| Metric | Target (3 months) | Target (6 months) |
|--------|-------------------|-------------------|
| **MAU** | 5,000 | 20,000 |
| **DAU/MAU Ratio** | 20% | 25% |
| **Avg Session Time** | 3 min | 5 min |
| **Query Success Rate** | 85% | 92% |
| **Premium Conversion** | 1% | 2% |
| **NPS Score** | 40 | 60 |

### Compliance KPIs

| Metric | Target | Status |
|--------|--------|--------|
| **GDPR Compliance** | 100% | ✅ Certified |
| **Data Retention** | ≤ 90 days | ✅ Automated |
| **PII Anonymization** | 100% | ✅ Implemented |
| **Audit Trail** | 100% | ✅ Complete |
| **MDR Class I** | Compliant | ✅ Validated |

## Risk Analysis

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **OpenAI API outage** | High | Low | Fallback to cached responses |
| **Supabase downtime** | High | Low | Read replicas, monitoring |
| **SÚKL data quality** | Medium | Medium | Daily validation, alerts |
| **Rate limiting hit** | Medium | Medium | Caching, queue system |
| **Embedding drift** | Low | Medium | Version control, A/B testing |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Low adoption** | High | Medium | Marketing, SEO, partnerships |
| **Regulatory changes** | High | Low | Legal monitoring, flexibility |
| **Competition** | Medium | Medium | First-mover advantage, quality |
| **SÚKL API changes** | Medium | Low | Abstract data layer, monitoring |

### Compliance Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **GDPR violation** | Critical | Low | Automated compliance checks |
| **MDR non-compliance** | Critical | Low | Medical advisor oversight |
| **Data breach** | Critical | Very Low | Encryption, penetration testing |
| **Liability claims** | High | Low | Clear disclaimers, insurance |

## Competitive Analysis

### Direct Competitors

| Competitor | Strengths | Weaknesses | Our Advantage |
|------------|-----------|------------|---------------|
| **Google Search** | Universal, fast | Generic, no Czech focus | Specialized, SÚKL direct |
| **SÚKL Website** | Official, accurate | Poor UX, not conversational | AI-powered, user-friendly |
| **Pharmacy Sites** | Local, trusted | Fragmented, commercial bias | Neutral, comprehensive |

### Indirect Competitors

- **ChatGPT/Claude**: General AI but no SÚKL data, hallucinations
- **WebMD Czech**: Limited local data
- **Doctor consultations**: Expensive, not 24/7

### Competitive Moat

1. **Data Exclusivity**: Direct SÚKL integration
2. **Czech Specialization**: Language, regulations, culture
3. **GDPR/MDR Compliance**: First-mover in compliant AI health
4. **RAG Quality**: Advanced multi-strategy retrieval
5. **Open Source**: Community trust, transparency

## Go-to-Market Strategy

### Phase 1: Soft Launch (Month 1-2)
- **Target**: 1,000 early adopters
- **Channels**: Product Hunt, Czech tech forums
- **Content**: Blog posts, demo videos
- **Budget**: €500

### Phase 2: Public Beta (Month 3-4)
- **Target**: 10,000 MAU
- **Channels**: SEO, social media, PR
- **Partnerships**: Pharmacy chains, health bloggers
- **Budget**: €2,000

### Phase 3: Scale (Month 5-6)
- **Target**: 50,000 MAU
- **Channels**: Paid ads (Google, Facebook)
- **B2B**: Healthcare provider pilots
- **Budget**: €5,000

## Appendices

### Tech Stack Summary

**Backend**: FastAPI, LangChain, LangGraph, Python 3.11
**Frontend**: Next.js 14, React, TypeScript, shadcn/ui
**Database**: PostgreSQL 15 + pgvector (Supabase)
**AI**: OpenAI GPT-4o-mini, text-embedding-3-small
**Infrastructure**: Google Cloud Run, Vercel, Cloudflare
**Monitoring**: Sentry, Langsmith, Plausible Analytics

### Key Documents

- **PRD**: `docs/prd.md` - Detailed product requirements
- **Architecture**: `docs/architecture.md` - Technical specification
- **Security**: `docs/security-strategy.md` - GDPR/MDR compliance
- **BMAD Guide**: `docs/BMAD_DEVELOPMENT_GUIDE.md` - Development methodology

### Contact

**Project Owner**: Petr Sovadina
**Email**: petr@pillsee.cz
**GitHub**: https://github.com/pillsee/pillsee
**Website**: https://pillsee.cz (TBD)

---

**Version**: 1.0
**Last Updated**: 2024-01-15
**Status**: Active Development
