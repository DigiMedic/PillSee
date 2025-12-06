# PillSee - Architektura systému

## Přehled

PillSee je AI-powered chatovací platforma pro poskytování informací o léčivých přípravcích registrovaných v České republice. Systém kombinuje moderní RAG (Retrieval-Augmented Generation) techniky s oficiální databází SÚKL.

## Systémová architektura

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Next.js 14 UI<br/>React + shadcn/ui]
        Mobile[Mobile Web<br/>PWA Ready]
    end

    subgraph "API Gateway"
        APIGW[FastAPI Gateway<br/>Rate Limiting + CORS]
        RateLimit[SlowAPI Limiter<br/>10 text/min, 5 image/min]
    end

    subgraph "Application Layer"
        LangGraph[LangGraph Workflow<br/>Medication Pipeline]

        subgraph "Agents - Sprint 1 BMAD"
            Supervisor[Supervisor Agent<br/>Orchestration]
            Triage[Triage Agent<br/>Query Classification]
            RAGExpert[RAG Expert Agent<br/>6 Strategies]
            Safety[Safety Monitor<br/>MDR Validation]
            Interaction[Interaction Checker<br/>Drug-Drug]
            Dosage[Dosage Advisor<br/>Informational]
        end

        subgraph "RAG Components"
            Hybrid[Hybrid Retriever<br/>Semantic + BM25]
            HyDE[HyDE Retriever<br/>Hypothetical Docs]
            MultiQuery[Multi-Query<br/>Query Expansion]
            ParentDoc[Parent Document<br/>Hierarchical]
            Compression[Contextual<br/>Compression]
            Manager[RAG Manager<br/>Ensemble]
        end

        subgraph "AI Processors"
            VisionProc[Vision Processor<br/>GPT-4 Vision]
            TextProc[Text Processor<br/>GPT-4o-mini]
            Embedder[Embedder<br/>text-embedding-3-small]
        end
    end

    subgraph "Data Layer"
        VectorStore[Supabase pgvector<br/>1536D embeddings]

        subgraph "PostgreSQL Tables"
            DrugInfo[(drug_info<br/>SÚKL master)]
            SPCDocs[(spc_documents<br/>+ embeddings)]
            PILDocs[(pil_documents<br/>+ embeddings)]
            Pricing[(drug_pricing<br/>e-shop data)]
            Interactions[(drug_interactions)]
            ATC[(atc_classification<br/>WHO codes)]
            Sessions[(user_sessions<br/>GDPR 90-day)]
            Analytics[(query_analytics<br/>anonymized)]
            Audit[(audit_logs<br/>compliance)]
        end
    end

    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT-4 + Embeddings]
        SUKL[SÚKL Open Data<br/>Daily Updates]
    end

    UI --> APIGW
    Mobile --> APIGW

    APIGW --> RateLimit
    RateLimit --> LangGraph

    LangGraph --> Supervisor
    Supervisor --> Triage
    Supervisor --> Safety

    Triage --> RAGExpert
    RAGExpert --> Hybrid
    RAGExpert --> HyDE
    RAGExpert --> MultiQuery
    RAGExpert --> ParentDoc
    RAGExpert --> Compression

    Hybrid --> Manager
    HyDE --> Manager
    MultiQuery --> Manager
    ParentDoc --> Manager
    Compression --> Manager

    Manager --> VectorStore

    Triage --> Interaction
    Triage --> Dosage

    VisionProc --> OpenAI
    TextProc --> OpenAI
    Embedder --> OpenAI

    VectorStore --> SPCDocs
    VectorStore --> PILDocs
    VectorStore --> DrugInfo

    DrugInfo --> Pricing
    DrugInfo --> Interactions
    DrugInfo --> ATC

    LangGraph --> Sessions
    LangGraph --> Analytics
    LangGraph --> Audit

    SUKL -.->|Daily sync| DrugInfo

    style Supervisor fill:#e1f5ff
    style RAGExpert fill:#fff4e1
    style Safety fill:#ffe1e1
    style VectorStore fill:#e8f5e9
    style OpenAI fill:#f3e5f5
```

## Component Architecture

### Frontend (Next.js 14)

```mermaid
graph LR
    subgraph "Next.js App Router"
        Pages[app/<br/>Route Handlers]
        Components[components/<br/>React Components]
        Lib[lib/<br/>Utilities]
    end

    subgraph "UI Components"
        Chat[Chat Interface<br/>shadcn/ui]
        ImageUpload[Image Upload<br/>Drag & Drop]
        ResultDisplay[Result Display<br/>Markdown]
    end

    subgraph "State Management"
        SessionStore[Session Storage<br/>Anonymous]
        QueryCache[Query Cache<br/>Local]
    end

    Pages --> Components
    Components --> Chat
    Components --> ImageUpload
    Components --> ResultDisplay

    Chat --> SessionStore
    ResultDisplay --> QueryCache
```

### Backend (FastAPI + LangChain)

```mermaid
graph TB
    subgraph "FastAPI Application"
        Main[main.py<br/>App Entry]
        Routes[API Routes<br/>/api/query/*]
        Models[Pydantic Models<br/>Request/Response]
        Config[config.py<br/>Settings]
    end

    subgraph "LangGraph Workflow"
        Workflow[medication_workflow.py<br/>State Machine]
        State[MedicationState<br/>TypedDict]
        Nodes[Workflow Nodes<br/>process_query, etc.]
    end

    subgraph "Memory & Storage"
        GDPRMemory[gdpr_memory.py<br/>Anonymization]
        VectorDB[vector_store.py<br/>Supabase Client]
    end

    Main --> Routes
    Routes --> Models
    Routes --> Workflow

    Workflow --> State
    Workflow --> Nodes

    Nodes --> GDPRMemory
    Nodes --> VectorDB

    Config -.->|Settings| Main
    Config -.->|Settings| VectorDB
```

## Data Flow - Textový dotaz

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js Frontend
    participant API as FastAPI Gateway
    participant WF as LangGraph Workflow
    participant RAG as RAG Expert
    participant VS as Vector Store
    participant LLM as OpenAI GPT-4
    participant DB as PostgreSQL

    U->>FE: Zadá dotaz "Co je Paralen?"
    FE->>API: POST /api/query/text

    Note over API: Rate Limit Check<br/>10/minute

    API->>WF: invoke(MedicationState)

    WF->>WF: Triage Agent<br/>Klasifikace: general_info

    WF->>RAG: Retrieve context

    RAG->>VS: Semantic search<br/>"Paralen účinky indikace"
    VS->>DB: SELECT * FROM spc_documents<br/>ORDER BY embedding <=> query_embedding
    DB-->>VS: Top 5 SPC chunks

    RAG->>VS: Keyword search (BM25)
    VS->>DB: Full-text search "Paralen"
    DB-->>VS: Matching documents

    RAG->>RAG: Ensemble ranking<br/>Combine results
    RAG-->>WF: Relevant context

    WF->>LLM: Generate answer<br/>+ context + prompt
    LLM-->>WF: Structured response

    WF->>WF: Safety Monitor<br/>Add disclaimer

    WF->>DB: Log query (anonymized)
    WF-->>API: Final state

    API-->>FE: APIResponse JSON
    FE-->>U: Zobrazí odpověď
```

## Data Flow - Obrázek léku

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js Frontend
    participant API as FastAPI Gateway
    participant WF as LangGraph Workflow
    participant Vision as Vision Processor
    participant GPT4V as GPT-4 Vision
    participant DB as PostgreSQL
    participant SUKL as SÚKL Database

    U->>FE: Nahraje foto obalu
    FE->>FE: Convert to base64
    FE->>API: POST /api/query/image

    Note over API: Rate Limit Check<br/>5/minute

    API->>WF: invoke(MedicationState)<br/>query_type: "image"

    WF->>Vision: extract_text(base64_image)
    Vision->>GPT4V: Analyze image<br/>"Extract drug name, strength..."

    GPT4V-->>Vision: Structured extraction:<br/>{name: "Paralen 500mg",...}

    Vision->>Vision: Confidence scoring<br/>0.95 (high)

    Vision-->>WF: VisionResult

    WF->>DB: Validate against SÚKL
    DB->>SUKL: SELECT * WHERE name LIKE '%Paralen%'<br/>AND strength = '500mg'
    SUKL-->>DB: Match found
    DB-->>WF: validated: true

    WF->>WF: Safety Monitor<br/>Add disclaimer

    WF->>DB: Log image query
    WF-->>API: Final state

    API-->>FE: APIResponse JSON
    FE-->>U: Zobrazí rozpoznané info
```

## Database Schema

### ER Diagram

```mermaid
erDiagram
    drug_info ||--o{ spc_documents : "has"
    drug_info ||--o{ pil_documents : "has"
    drug_info ||--o{ drug_pricing : "has"
    drug_info ||--o{ drug_interactions : "participates"
    drug_info }o--|| atc_classification : "classified by"

    user_sessions ||--o{ query_analytics : "generates"
    user_sessions ||--o{ conversation_history : "contains"
    user_sessions ||--o{ audit_logs : "tracked in"

    drug_info {
        uuid id PK
        string sukl_code UK
        string name
        string active_ingredient
        string strength
        string form
        string manufacturer
        string registration_number
        timestamp created_at
        timestamp updated_at
    }

    spc_documents {
        uuid id PK
        uuid drug_id FK
        text content
        vector embedding "1536D"
        string section
        timestamp created_at
    }

    pil_documents {
        uuid id PK
        uuid drug_id FK
        text content
        vector embedding "1536D"
        string section
        timestamp created_at
    }

    drug_pricing {
        uuid id PK
        uuid drug_id FK
        decimal price
        string pharmacy_name
        string affiliate_url
        timestamp scraped_at
    }

    drug_interactions {
        uuid id PK
        uuid drug_a_id FK
        uuid drug_b_id FK
        string severity
        text description
    }

    atc_classification {
        string atc_code PK
        string level1_name
        string level2_name
        string level3_name
        text description
    }

    user_sessions {
        uuid session_id PK
        string ip_hash
        timestamp created_at
        timestamp last_activity
        int query_count
    }

    query_analytics {
        uuid id PK
        uuid session_id FK
        string query_type
        float confidence_score
        int response_time_ms
        timestamp created_at
    }

    conversation_history {
        uuid id PK
        uuid session_id FK
        text query_anonymized
        text response
        timestamp created_at
    }

    audit_logs {
        uuid id PK
        uuid session_id FK
        string action
        text details
        timestamp created_at
    }
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "CDN & Edge"
        Vercel[Vercel Edge Network<br/>Next.js Frontend]
        CDN[Cloudflare CDN<br/>Static Assets]
    end

    subgraph "Application Tier"
        CloudRun[Google Cloud Run<br/>FastAPI Container]
        LB[Load Balancer<br/>Auto-scaling]
    end

    subgraph "Data Tier"
        Supabase[Supabase<br/>PostgreSQL + pgvector]
        Redis[Redis Cache<br/>Rate Limiting]
    end

    subgraph "External APIs"
        OpenAIAPI[OpenAI API<br/>GPT-4 + Embeddings]
        SUKLAPI[SÚKL Open Data<br/>Daily Sync]
    end

    subgraph "Monitoring & Logging"
        GCPLogs[GCP Logging]
        Sentry[Sentry<br/>Error Tracking]
        Analytics[Plausible Analytics<br/>Privacy-first]
    end

    Internet[Internet Users] --> Vercel
    Internet --> CDN

    Vercel --> LB
    LB --> CloudRun

    CloudRun --> Supabase
    CloudRun --> Redis
    CloudRun --> OpenAIAPI

    CloudRun -.->|Daily sync| SUKLAPI

    CloudRun --> GCPLogs
    CloudRun --> Sentry
    Vercel --> Analytics

    style CloudRun fill:#4285f4
    style Supabase fill:#3ecf8e
    style OpenAIAPI fill:#412991
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React Context + Session Storage
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI 0.109+
- **AI Orchestration**: LangChain + LangGraph
- **Language**: Python 3.11
- **Rate Limiting**: SlowAPI
- **Deployment**: Google Cloud Run (Docker)

### Database & Storage
- **Primary DB**: PostgreSQL 15 (Supabase)
- **Vector Store**: pgvector extension (IVFFlat indexes)
- **Cache**: Redis (rate limiting)
- **File Storage**: Supabase Storage (future)

### AI & ML
- **LLM**: OpenAI GPT-4o-mini (text queries)
- **Vision**: OpenAI GPT-4 Vision (image recognition)
- **Embeddings**: text-embedding-3-small (1536 dimensions)
- **RAG Framework**: LangChain

### DevOps & Monitoring
- **CI/CD**: GitHub Actions
- **Containerization**: Docker + docker-compose
- **Logging**: Google Cloud Logging
- **Error Tracking**: Sentry
- **Analytics**: Plausible (GDPR compliant)

## Security & Compliance

### GDPR Compliance
- Anonymní použití (žádná registrace)
- IP adresy hashované (SHA-256)
- 90-day data retention
- Žádné cookies/tracking
- Data minimalization

### MDR Class I (Medical Device Regulation)
- Pouze informační účely (ne diagnostika)
- Medical disclaimer u všech odpovědí
- Safety warnings pro kontraindikace
- Audit trail pro compliance
- Post-market surveillance ready

### Security Measures
- Rate limiting (IP-based)
- CORS whitelist
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- XSS prevention (sanitization)
- No authentication = No credential leaks

## Scalability

### Horizontal Scaling
- **Frontend**: Edge functions (Vercel)
- **Backend**: Cloud Run auto-scaling (0-100 instances)
- **Database**: Supabase connection pooling

### Performance Optimization
- **Vector Search**: IVFFlat indexes (sub-linear search)
- **Caching**: Redis for rate limits
- **CDN**: Static assets cached globally
- **Lazy Loading**: React code splitting

### Cost Optimization
- **Serverless**: Pay-per-request (Cloud Run)
- **Vector Store**: Indexed queries only
- **OpenAI**: GPT-4o-mini for most queries (cheaper than GPT-4)
- **Batch Processing**: SÚKL updates once daily

## Future Enhancements (Phase 2+)

### Sprint 2 - RAG Enhancement
- A/B testing different RAG strategies
- Fine-tuned embeddings on Czech medical texts
- Query expansion with Czech synonyms
- Feedback loop for retrieval quality

### Sprint 3 - Feature Expansion
- User feedback system (thumbs up/down)
- Multi-language support (Slovak, English)
- Voice input (Web Speech API)
- Pharmacy locator integration

### Sprint 4 - Advanced Features
- Drug-food interactions
- Pregnancy/breastfeeding warnings
- Pediatric dosing calculator
- Side effect reporting integration

## Odkazy

- **PRD**: `/docs/prd.md`
- **Architecture Deep Dive**: `/docs/architecture.md`
- **BMAD Analysis**: `/docs/BMAD_*.md`
- **API Spec**: `/docs/api/openapi.yaml`
- **Deployment Guide**: `/docs/phase1/PillSee_DEPLOYMENT_GUIDE.md`
