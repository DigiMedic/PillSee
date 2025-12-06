# 🚀 PillSee LangChain Architecture Upgrade Plan

## 📊 Analýza Současného Stavu

### ✅ Co už funguje
- FastAPI backend s rate limiting a CORS
- LangGraph basic workflow (route → extract → search → validate → disclaimers)
- Basic RAG s RetrievalQA chain
- Supabase PostgreSQL + pgvector integration
- GPT-4 Vision pro image processing
- Czech medical prompts a safety disclaimers
- TextProcessor s OpenAI GPT-4o-mini
- VectorStore s similarity search

### ⚠️ Současná omezení
1. **Sequential workflow** - není true multi-agent orchestration
2. **Basic RAG** - pouze similarity search, chybí Hybrid/HyDE/MMR
3. **No memory** - každý dotaz je izolovaný, žádná konverzační historie
4. **Simple tools** - functions místo LangChain Tools s args_schema
5. **Limited monitoring** - chybí callbacks, metrics, cost tracking
6. **No conversation** - není true chatbot, jen Q&A

## 🎯 Upgrade na Pokročilou Architekturu

### Fáze 1: Enhanced RAG Pipeline (Priority 1)

**Cíl**: Nahradit basic similarity search pokročilými RAG technikami

**Implementace**:
```
pillsee-backend/app/rag/
├── __init__.py
├── hybrid_retriever.py       # BM25 + Semantic (Ensemble)
├── hyde_retriever.py          # Hypothetical Document Embeddings
├── parent_document.py         # Parent Document Retriever
├── contextual_compression.py  # LLM-based compression
└── multi_query.py             # Multi-query retrieval
```

**Změny**:
- `TextProcessor` bude používat HybridRetriever místo basic similarity
- `VectorStore` rozšířen o MMR (Maximum Marginal Relevance)
- Přidání metadata filtrů (ATC kód, forma, předpisovost)

**Přínosy**:
- ✨ Lepší recall i precision
- ✨ Diverse výsledky (ne jen top-5 nejpodobnějších)
- ✨ Keyword + semantic matching
- ✨ Lepší handling složitých dotazů

---

### Fáze 2: Multi-Agent System (Priority 1)

**Cíl**: Nahradit sequential workflow hierarchickou multi-agent architekturou

**Architektura**:
```
                    [Supervisor Agent]
                            |
        ┌───────────────────┼───────────────────┐
        v                   v                   v
    [Triage]          [RAG Expert]        [Safety Monitor]
        |                   |                   |
        └─────> [Interaction Checker]          |
        └─────> [Dosage Advisor] ──────────────┘
```

**Agents**:
1. **Supervisor Agent** - Orchestrace, routing, final answer
2. **Triage Agent** - Klasifikace query (medication_info, interaction, dosage, price)
3. **RAG Expert** - Advanced RAG pro SPC/PIL dokumenty
4. **Interaction Checker** - Kontrola lékových interakcí (ATC-based)
5. **Dosage Advisor** - Dávkování a timing
6. **Safety Monitor** - Kontraindikace, varování, disclaimery

**Implementace**:
```
pillsee-backend/app/agents/
├── __init__.py
├── supervisor.py              # Hlavní koordinátor
├── triage_agent.py            # Klasifikace dotazů
├── rag_expert.py              # Advanced RAG specialist
├── interaction_checker.py     # Lékové interakce
├── dosage_advisor.py          # Dávkování
└── safety_monitor.py          # Bezpečnostní kontroly
```

**Přínosy**:
- ✨ Specializace agentů na konkrétní úkoly
- ✨ Paralelní zpracování (kde možné)
- ✨ Lepší error handling (agent může failover)
- ✨ Transparentní reasoning chain

---

### Fáze 3: Tool-Based Architecture (Priority 2)

**Cíl**: Nahradit funkce LangChain Tools s Pydantic validací

**Tools**:
```python
@tool
def search_drug_database(drug_name: str, search_type: str = "exact") -> str:
    """Vyhledání léku v databázi SÚKL"""
    
@tool
def check_drug_interactions(drug1: str, drug2: str) -> str:
    """Kontrola interakcí mezi dvěma léky"""
    
@tool  
def get_drug_price(drug_name: str) -> str:
    """Zjištění ceny a úhrady léku"""
    
@tool
def search_by_atc(atc_code: str) -> str:
    """Vyhledání léků podle ATC kódu"""
    
@tool
def get_drug_alternatives(drug_name: str) -> str:
    """Alternativní léky se stejnou účinnou látkou"""
```

**Implementace**:
```
pillsee-backend/app/tools/
├── __init__.py
├── drug_search.py
├── interactions.py
├── pricing.py
├── atc_tools.py
└── alternatives.py
```

**Přínosy**:
- ✨ Type-safe tool calls
- ✨ Automatic validation
- ✨ Better error messages
- ✨ Composability

---

### Fáze 4: GDPR-Compliant Conversation Memory (Priority 2)

**Cíl**: Přidat konverzační paměť s GDPR compliance

**Komponenty**:
1. **ConversationMemory** - Window + Summary Memory
2. **PII Anonymizer** - Odstranění osobních údajů
3. **Session Manager** - Správa session v Supabase
4. **Cleanup Service** - Automatické mazání starých konverzací

**Implementace**:
```
pillsee-backend/app/memory/
├── __init__.py
├── gdpr_memory.py            # GDPR-compliant memory
├── anonymizer.py             # PII detection & anonymization
├── session_manager.py        # Session lifecycle
└── cleanup.py                # Data retention policy
```

**Database Schema**:
```sql
CREATE TABLE conversation_history (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    user_message TEXT,
    assistant_message TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE analytics (
    id UUID PRIMARY KEY,
    query_type VARCHAR(50),
    confidence_score FLOAT,
    processing_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Přínosy**:
- ✨ Context-aware odpovědi
- ✨ Follow-up questions
- ✨ GDPR compliance (right to erasure)
- ✨ Analytics bez PII

---

### Fáze 5: Advanced Monitoring & Callbacks (Priority 3)

**Cíl**: Komplexní monitoring produkční aplikace

**Metriky**:
- Token usage per request
- Cost per query
- Latency per component
- Tool call frequency
- Error rates
- RAG quality metrics

**Implementace**:
```
pillsee-backend/app/monitoring/
├── __init__.py
├── callbacks.py              # Custom callback handlers
├── metrics.py                # Prometheus metrics
└── logger.py                 # Structured logging
```

**Callbacks**:
```python
class PillSeeCallbackHandler(BaseCallbackHandler):
    """Custom callback pro tracking"""
    
    def on_llm_start(self, ...):
        # Log LLM request
        
    def on_tool_start(self, ...):
        # Track tool usage
        
    def on_chain_end(self, ...):
        # Calculate total latency
```

**Přínosy**:
- ✨ Real-time monitoring
- ✨ Cost tracking
- ✨ Performance optimization
- ✨ Error alerting

---

## 📅 Implementační Plán

### Sprint 1 (Týden 1-2): Enhanced RAG
- [ ] Implementovat HybridRetriever (BM25 + Semantic)
- [ ] Přidat MMR do VectorStore
- [ ] Implementovat Multi-Query Retrieval
- [ ] Tests a benchmarking

### Sprint 2 (Týden 3-4): Multi-Agent Core
- [ ] Supervisor Agent
- [ ] Triage Agent  
- [ ] RAG Expert Agent
- [ ] Integration tests

### Sprint 3 (Týden 5-6): Specialized Agents
- [ ] Interaction Checker
- [ ] Dosage Advisor
- [ ] Safety Monitor
- [ ] End-to-end tests

### Sprint 4 (Týden 7-8): Memory & Tools
- [ ] GDPR-compliant memory
- [ ] Tool-based architecture
- [ ] Session management
- [ ] Database migrations

### Sprint 5 (Týden 9-10): Monitoring & Production
- [ ] Custom callbacks
- [ ] Metrics dashboard
- [ ] Error tracking
- [ ] Performance optimization

---

## 🔧 Technický Stack

### Stávající (zachovat)
- FastAPI 0.104+
- Supabase (PostgreSQL 17 + pgvector)
- OpenAI GPT-4o-mini + text-embedding-3-small
- LangGraph (current workflow)

### Nové závislosti
```txt
# Enhanced RAG
langchain-community==0.1.0
rank-bm25==0.2.2

# Multi-Agent
langgraph==0.0.30
langchain-openai==0.0.5

# Memory
redis==5.0.1  # Pro session cache

# Monitoring
prometheus-client==0.19.0
opentelemetry-api==1.22.0
```

---

## 📊 Očekávané Výsledky

### Metriky Úspěchu
1. **Kvalita odpovědí**
   - Precision@5: > 0.85
   - Recall@5: > 0.90
   - NDCG@10: > 0.85

2. **Performance**
   - Avg response time: < 3s
   - P95 response time: < 5s
   - Token efficiency: 30% reduction

3. **User Experience**
   - Conversation fluency: Natural follow-ups
   - Context retention: 5+ turns
   - Safety compliance: 100%

---

## 🚀 Quick Start Guide

### Příprava
```bash
cd pillsee-backend
pip install -r requirements-langchain.txt
```

### Environment Variables
```bash
# Přidat do .env
REDIS_URL=redis://localhost:6379
ENABLE_MULTI_AGENT=true
ENABLE_CONVERSATION_MEMORY=true
```

### Database Migrations
```bash
# Spustit nové migrace
python -m alembic upgrade head
```

---

## 📝 Notes

- Všechny změny jsou **backward compatible**
- Feature flags pro postupný rollout
- Každá fáze je testovatelná samostatně
- Existing API zůstává funkční
