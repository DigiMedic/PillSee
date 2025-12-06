# PillSee - Product Requirements Document (PRD)

**Version**: 1.0
**Last Updated**: 2024-01-15
**Owner**: Petr Sovadina
**Status**: Sprint 1 BMAD in progress

## Table of Contents

1. [Overview](#overview)
2. [User Stories](#user-stories)
3. [Functional Requirements](#functional-requirements)
4. [Non-Functional Requirements](#non-functional-requirements)
5. [API Specifications](#api-specifications)
6. [User Interface](#user-interface)
7. [Data Model](#data-model)
8. [Success Criteria](#success-criteria)

## Overview

### Product Vision

PillSee je AI-powered asistent poskytující přesné a aktuální informace o léčivých přípravcích registrovaných v ČR, s důrazem na ochranu soukromí a compliance s GDPR/MDR.

### Target Users

1. **Primary**: Pacienti (18-65 let, tech-savvy)
2. **Secondary**: Lékárníci, zdravotní sestry
3. **Tertiary**: Lékaři (informační lookup)

### Core Value Proposition

- ✅ **Anonymní**: Žádná registrace
- ✅ **Přesné**: Data z SÚKL
- ✅ **Rychlé**: Odpověď < 3s
- ✅ **Srozumitelné**: Laická terminologie
- ✅ **Bezpečné**: GDPR + MDR compliant

## User Stories

### Epic 1: Základní vyhledávání (Phase 1) ✅

#### US-001: Textový dotaz na lék
**As a** patient
**I want to** ask about a medication in natural language
**So that** I can quickly get information without searching official docs

**Acceptance Criteria**:
- [ ] User can type Czech text query (max 500 chars)
- [ ] System responds within 5 seconds
- [ ] Response includes: name, active ingredient, usage, warnings
- [ ] Medical disclaimer is always shown
- [ ] Sources are cited (SPC/PIL references)

**Technical Notes**:
- Endpoint: `POST /api/query/text`
- Rate limit: 10/minute per IP
- RAG pipeline: Hybrid search + GPT-4o-mini

**Priority**: P0 (Must Have)
**Status**: ✅ Implemented

---

#### US-002: Rozpoznání léku z obrázku
**As a** patient with a medication package
**I want to** take a photo and get instant identification
**So that** I don't have to type the name or search manually

**Acceptance Criteria**:
- [ ] User can upload/drag-drop image (max 10MB)
- [ ] Supported formats: JPEG, PNG, WebP
- [ ] System extracts: name, strength, manufacturer, reg. number
- [ ] Confidence score shown (High/Medium/Low)
- [ ] Warning if confidence < 60%
- [ ] Validation against SÚKL database

**Technical Notes**:
- Endpoint: `POST /api/query/image`
- Rate limit: 5/minute per IP
- Vision: GPT-4 Vision
- Validation: Fuzzy match against drug_info table

**Priority**: P0 (Must Have)
**Status**: ✅ Implemented

---

#### US-003: Zobrazení cenových informací
**As a** patient looking to buy medication
**I want to** see price comparison from e-shops
**So that** I can find the best deal

**Acceptance Criteria**:
- [ ] Prices from min 3 e-shops shown
- [ ] Sorted by price (lowest first)
- [ ] Affiliate links clearly marked
- [ ] Last update timestamp visible
- [ ] Out-of-stock indication

**Technical Notes**:
- Table: `drug_pricing`
- Affiliate tracking: UTM parameters
- Update frequency: Daily scraping

**Priority**: P1 (Should Have)
**Status**: 📋 Designed

---

### Epic 2: Multi-Agent RAG (Sprint 1) 📋

#### US-004: Automatická klasifikace dotazů
**As a** system
**I want to** classify user queries into categories
**So that** I can route to the appropriate agent

**Acceptance Criteria**:
- [ ] Categories: general_info, drug_specific, interaction, dosage, side_effects
- [ ] Classification accuracy > 85%
- [ ] Confidence score returned
- [ ] Fallback to general_info if uncertain

**Technical Notes**:
- Agent: Triage Agent
- Model: GPT-4o-mini
- Metrics: Classification accuracy, confidence distribution

**Priority**: P0 (Must Have - Sprint 1)
**Status**: 📋 Designed

---

#### US-005: Pokročilé RAG strategie
**As a** system
**I want to** use multiple retrieval strategies
**So that** I can provide the most relevant context

**Acceptance Criteria**:
- [ ] 6 strategies implemented: Hybrid, HyDE, Multi-Query, Parent Doc, Compression, Ensemble
- [ ] Strategy selection based on query type
- [ ] A/B testing infrastructure
- [ ] RAGAS metrics tracked

**Technical Notes**:
- Agent: RAG Expert Agent
- Strategies: `app/rag/*.py`
- Metrics: Faithfulness, answer relevancy, context recall/precision

**Priority**: P0 (Must Have - Sprint 1)
**Status**: 📋 Designed

---

#### US-006: Kontrola lékových interakcí
**As a** patient taking multiple medications
**I want to** check for drug-drug interactions
**So that** I can avoid dangerous combinations

**Acceptance Criteria**:
- [ ] Input: 2+ medication names
- [ ] Output: Severity (None/Mild/Moderate/Severe), Description
- [ ] Source: drug_interactions table
- [ ] Warning if severe interaction
- [ ] Recommendation to consult doctor

**Technical Notes**:
- Agent: Interaction Checker Agent
- Table: `drug_interactions`
- Source: SÚKL + WHO ATC

**Priority**: P1 (Should Have - Sprint 1)
**Status**: 📋 Designed

---

#### US-007: Informační dávkování
**As a** patient
**I want to** get dosage information
**So that** I understand how to use the medication

**Acceptance Criteria**:
- [ ] Dosage for adults shown
- [ ] Pediatric dosage (if applicable)
- [ ] Max daily dose highlighted
- [ ] Administration route specified
- [ ] **Disclaimer**: "This is informational only, always follow doctor's prescription"

**Technical Notes**:
- Agent: Dosage Advisor Agent
- Source: SPC documents, dosage field
- **Important**: No prescriptive recommendations (MDR compliance)

**Priority**: P1 (Should Have - Sprint 1)
**Status**: 📋 Designed

---

#### US-008: Bezpečnostní monitoring
**As a** system
**I want to** validate all responses for safety
**So that** I comply with MDR Class I regulations

**Acceptance Criteria**:
- [ ] Every response has medical disclaimer
- [ ] Contraindications highlighted
- [ ] No diagnostic claims
- [ ] Safety warnings for high-risk drugs
- [ ] Audit log of all queries

**Technical Notes**:
- Agent: Safety Monitor Agent
- Compliance: MDR Class I
- Audit: `audit_logs` table

**Priority**: P0 (Must Have - Sprint 1)
**Status**: 📋 Designed

---

### Epic 3: GDPR & Privacy (Phase 1) ✅

#### US-009: Anonymní použití
**As a** privacy-conscious user
**I want to** use the service without registration
**So that** my personal data is not collected

**Acceptance Criteria**:
- [ ] No login required
- [ ] No cookies (except essential)
- [ ] IP addresses hashed (SHA-256)
- [ ] Session IDs random UUIDs
- [ ] Data retention: 90 days max

**Technical Notes**:
- Memory: `app/memory/gdpr_memory.py`
- Hashing: SHA-256 with salt
- Cleanup: Automated cron job

**Priority**: P0 (Must Have)
**Status**: ✅ Implemented

---

#### US-010: PII Anonymizace
**As a** system
**I want to** anonymize all personal data before storage
**So that** I comply with GDPR

**Acceptance Criteria**:
- [ ] Email addresses masked (e***@example.com)
- [ ] Phone numbers masked (***-***-1234)
- [ ] ID numbers (rodná čísla) completely removed
- [ ] Names replaced with placeholders
- [ ] Addresses stripped

**Technical Notes**:
- Regex patterns for PII detection
- Anonymization before DB write
- Irreversible (one-way)

**Priority**: P0 (Must Have)
**Status**: ✅ Implemented

---

#### US-011: Right to Erasure
**As a** user
**I want to** delete my conversation history
**So that** I can exercise GDPR rights

**Acceptance Criteria**:
- [ ] "Delete my data" button in UI
- [ ] Deletes all records for session_id
- [ ] Confirmation required
- [ ] Irreversible warning shown
- [ ] Audit log entry created

**Technical Notes**:
- Endpoint: `DELETE /api/session/{session_id}`
- Cascade delete: conversation_history, query_analytics
- Retain: audit_logs (compliance)

**Priority**: P0 (Must Have)
**Status**: 📋 Planned for Sprint 3

---

### Epic 4: Frontend Experience (Sprint 3) 📅

#### US-012: Real-time streaming odpovědí
**As a** user
**I want to** see the response as it's being generated
**So that** I don't wait for full completion

**Acceptance Criteria**:
- [ ] Tokens stream word-by-word
- [ ] Typing indicator while loading
- [ ] Smooth animation
- [ ] Cancel button to stop generation
- [ ] Full response shown when complete

**Technical Notes**:
- Vercel AI SDK `useChat()` hook
- SSE (Server-Sent Events)
- FastAPI `StreamingResponse`

**Priority**: P1 (Should Have - Sprint 3)
**Status**: 📅 Planned

---

#### US-013: Hlasové zadávání
**As a** user on mobile
**I want to** speak my query instead of typing
**So that** it's faster and more convenient

**Acceptance Criteria**:
- [ ] Microphone button visible
- [ ] Browser permission requested
- [ ] Speech-to-text (Czech language)
- [ ] Text shown before sending
- [ ] Edit capability

**Technical Notes**:
- Web Speech API
- Fallback: OpenAI Whisper API
- Language: `cs-CZ`

**Priority**: P2 (Nice to Have - Sprint 3)
**Status**: 📅 Planned

---

#### US-014: Multi-language podpora
**As a** Slovak or English-speaking user
**I want to** use the service in my language
**So that** I can understand the responses

**Acceptance Criteria**:
- [ ] Languages: Czech (default), Slovak, English
- [ ] Language selector in header
- [ ] All UI translated
- [ ] Responses in selected language
- [ ] SÚKL data remains Czech (original)

**Technical Notes**:
- i18n: next-intl
- Translation files: JSON
- LLM instruction: "Respond in {language}"

**Priority**: P2 (Nice to Have - Future)
**Status**: 📅 Planned

---

#### US-015: Konverzační historie
**As a** user
**I want to** see my previous questions in the session
**So that** I can refer back to earlier information

**Acceptance Criteria**:
- [ ] Session-based history (sessionStorage)
- [ ] Max 50 messages per session
- [ ] Scroll to load more
- [ ] Clear history button
- [ ] Export as PDF/text

**Technical Notes**:
- Storage: sessionStorage (not localStorage - GDPR)
- Cleared on browser close
- Export: jsPDF library

**Priority**: P1 (Should Have - Sprint 3)
**Status**: 📅 Planned

---

## Functional Requirements

### FR-001: Text Query Processing
**Description**: System must process Czech text queries about medications

**Inputs**:
- `query`: String (1-500 characters)

**Outputs**:
- `answer`: Structured response
- `sources`: List of SPC/PIL references
- `confidence`: High/Medium/Low
- `disclaimer`: Medical disclaimer

**Constraints**:
- Rate limit: 10 queries/minute per IP
- Response time: < 5 seconds (p95)
- Accuracy: > 90% (RAGAS faithfulness)

---

### FR-002: Image Recognition
**Description**: System must identify medications from package photos

**Inputs**:
- `image_data`: Base64 encoded image
- Formats: JPEG, PNG, WebP
- Max size: 10 MB

**Outputs**:
- `name`: Medication name
- `strength`: Dosage
- `manufacturer`: Company name
- `registration_number`: SÚKL code
- `confidence_score`: 0.0-1.0
- `validated`: Boolean (SÚKL match)

**Constraints**:
- Rate limit: 5 queries/minute per IP
- Response time: < 10 seconds (p95)
- Confidence threshold: 0.6 (warn if below)

---

### FR-003: Vector Search
**Description**: System must retrieve relevant SPC/PIL chunks

**Inputs**:
- `query_embedding`: 1536D vector
- `top_k`: Number of results (default: 5)

**Outputs**:
- List of document chunks with similarity scores

**Constraints**:
- Search time: < 500ms
- Index type: IVFFlat (pgvector)
- Distance metric: Cosine

---

### FR-004: GDPR Anonymization
**Description**: System must anonymize PII before storage

**Inputs**:
- Raw text with potential PII

**Outputs**:
- Anonymized text

**Rules**:
- Email: `email@example.com` → `e***@example.com`
- Phone: `+420 123 456 789` → `+420 *** *** 789`
- ID numbers: Completely removed
- Names: Replaced with `[JMÉNO]`

**Constraints**:
- Must be irreversible
- Applied before DB write
- Audit logged

---

## Non-Functional Requirements

### NFR-001: Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | < 3s (p95) | Cloud monitoring |
| Vector Search Latency | < 500ms | pgvector stats |
| Page Load Time | < 2s | Lighthouse |
| Time to Interactive | < 3s | Core Web Vitals |

### NFR-002: Scalability

| Metric | Target | Strategy |
|--------|--------|----------|
| Concurrent Users | 1,000 | Horizontal scaling (Cloud Run) |
| Queries per Second | 100 | Connection pooling, caching |
| Database Size | 50 GB | Supabase auto-scaling |
| Vector Index Size | 10M embeddings | Partitioning |

### NFR-003: Availability

| Metric | Target | Strategy |
|--------|--------|----------|
| Uptime | 99.5% | Multi-region, health checks |
| Recovery Time (RTO) | < 1 hour | Automated failover |
| Recovery Point (RPO) | < 15 minutes | Continuous backups |

### NFR-004: Security

| Requirement | Implementation |
|-------------|----------------|
| Data Encryption at Rest | AES-256 (Supabase) |
| Data Encryption in Transit | TLS 1.3 |
| Authentication | None (anonymous) |
| Authorization | IP-based rate limiting |
| Input Validation | Pydantic schemas |
| SQL Injection Prevention | Parameterized queries |

### NFR-005: Compliance

| Regulation | Requirement | Status |
|------------|-------------|--------|
| GDPR | Data minimization, right to erasure | ✅ Compliant |
| MDR Class I | No diagnostic claims, disclaimers | ✅ Compliant |
| Czech Law | SÚKL data usage | ✅ Public data |

---

## API Specifications

### Endpoint: `POST /api/query/text`

**Request**:
```json
{
  "query": "Co je Paralen a k čemu se používá?"
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "answer": "Paralen je analgetikum-antipyretikum...",
    "sources": ["SPC Paralen 500mg", "PIL Paralen"],
    "confidence": "high"
  },
  "disclaimer": "UPOZORNĚNÍ: Tyto informace slouží pouze...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Error (429 Too Many Requests)**:
```json
{
  "status": "error",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "error_message": "Překročili jste limit dotazů...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Endpoint: `POST /api/query/image`

**Request**:
```json
{
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "name": "Paralen 500mg",
    "active_ingredient": "Paracetamolum",
    "strength": "500mg",
    "form": "Potahované tablety",
    "manufacturer": "Zentiva k.s.",
    "registration_number": "16/123/45-C",
    "confidence_score": 0.95,
    "validated": true,
    "sukl_matches": [
      {"name": "Paralen 500mg tablety", "sukl_code": "0016123"}
    ]
  },
  "disclaimer": "UPOZORNĚNÍ...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Endpoint: `GET /health`

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "PillSee API",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "dependencies": {
    "openai": "connected",
    "database": "connected",
    "sukl_data": "synced"
  }
}
```

---

## User Interface

### UI Requirements

1. **Mobile-First Design**
   - Responsive: 320px - 1920px
   - Touch-optimized buttons (min 44x44px)
   - Fast mobile load (< 2s)

2. **Accessibility**
   - WCAG 2.1 Level AA
   - Keyboard navigation
   - Screen reader support
   - High contrast mode

3. **Design System**
   - Component library: shadcn/ui
   - CSS framework: Tailwind CSS
   - Typography: Inter font
   - Colors: Blue primary (#2563eb)

### Key Screens

1. **Home/Chat Interface**
   - Input: Textarea (auto-expand)
   - Send button (always visible)
   - Camera icon (image upload)
   - Mic icon (voice input)

2. **Response Display**
   - Markdown rendering
   - Syntax highlighting (code blocks)
   - Collapsible sources
   - Copy button

3. **Settings (Optional)**
   - Language selector
   - Clear history
   - Delete my data
   - Feedback form

---

## Data Model

### Core Tables

**drug_info** (SÚKL master data)
```sql
CREATE TABLE drug_info (
    id UUID PRIMARY KEY,
    sukl_code VARCHAR(20) UNIQUE,
    name VARCHAR(255),
    active_ingredient VARCHAR(255),
    strength VARCHAR(100),
    form VARCHAR(100),
    manufacturer VARCHAR(255),
    registration_number VARCHAR(50),
    atc_code VARCHAR(10),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**spc_documents** (SPC chunks + embeddings)
```sql
CREATE TABLE spc_documents (
    id UUID PRIMARY KEY,
    drug_id UUID REFERENCES drug_info(id),
    content TEXT,
    embedding VECTOR(1536),
    section VARCHAR(100),
    created_at TIMESTAMP
);
```

**user_sessions** (GDPR tracking)
```sql
CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY,
    ip_hash VARCHAR(64),  -- SHA-256
    created_at TIMESTAMP,
    last_activity TIMESTAMP,
    query_count INT DEFAULT 0,
    expires_at TIMESTAMP  -- created_at + 90 days
);
```

**query_analytics** (Anonymized metrics)
```sql
CREATE TABLE query_analytics (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES user_sessions(session_id),
    query_type VARCHAR(20),  -- text/image
    confidence_score FLOAT,
    response_time_ms INT,
    created_at TIMESTAMP
);
```

---

## Success Criteria

### Launch Criteria (Sprint 3)

- [ ] All P0 user stories implemented
- [ ] API response time < 3s (p95)
- [ ] Test coverage > 80%
- [ ] Zero critical bugs
- [ ] GDPR audit passed
- [ ] MDR compliance validated
- [ ] Load testing: 100 RPS sustained

### 3-Month Success (Post-Launch)

- [ ] 5,000 MAU
- [ ] 85% query success rate
- [ ] NPS score > 40
- [ ] < 1% error rate
- [ ] 99.5% uptime

### 6-Month Success

- [ ] 20,000 MAU
- [ ] 92% query success rate
- [ ] NPS score > 60
- [ ] 2% premium conversion
- [ ] Break-even revenue

---

**Document Status**: Living Document
**Next Review**: End of Sprint 1
**Approval**: [Product Owner Signature]
