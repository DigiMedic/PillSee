"""
Integration Guide: Enhanced RAG into Existing PillSee Workflow
How to integrate new RAG components with backward compatibility
"""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from supabase import create_client, Client
import os

# Import existing components
from app.database.vector_store import VectorStore as OldVectorStore
from app.ai.text_processor import TextProcessor

# Import new RAG components
from app.rag.enhanced_vector_store import EnhancedVectorStore
from app.rag.rag_manager import RAGManager


class RAGIntegration:
    """
    Integration layer between old and new RAG systems
    
    Features:
    - Backward compatible with existing code
    - Feature flags for gradual rollout
    - Performance comparison
    - Easy migration path
    """
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        openai_api_key: str,
        use_enhanced_rag: bool = False,
        default_strategy: str = "auto"
    ):
        """
        Initialize RAG integration
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            openai_api_key: OpenAI API key
            use_enhanced_rag: Enable new RAG features (feature flag)
            default_strategy: Default retrieval strategy
        """
        self.use_enhanced_rag = use_enhanced_rag
        
        # Initialize Supabase
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_api_key
        )
        
        # Initialize OLD vector store (for compatibility)
        self.old_vector_store = OldVectorStore(
            supabase_client=self.supabase,
            embedding_function=self.embeddings
        )
        
        # Initialize NEW enhanced RAG (if enabled)
        if use_enhanced_rag:
            self.enhanced_vector_store = EnhancedVectorStore(
                supabase_client=self.supabase,
                embedding_function=self.embeddings
            )
            
            self.rag_manager = RAGManager(
                vector_store=self.enhanced_vector_store,
                openai_api_key=openai_api_key,
                default_strategy=default_strategy
            )
        else:
            self.enhanced_vector_store = None
            self.rag_manager = None
    
    def search(
        self,
        query: str,
        k: int = 5,
        strategy: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ):
        """
        Unified search interface (routes to old or new system)
        
        Args:
            query: Search query
            k: Number of results
            strategy: Retrieval strategy (only for enhanced RAG)
            filters: Metadata filters
            
        Returns:
            Search results
        """
        if self.use_enhanced_rag and self.rag_manager:
            # Use new enhanced RAG
            return self.rag_manager.retrieve(
                query=query,
                k=k,
                strategy=strategy,
                filters=filters
            )
        else:
            # Use old vector store
            return self.old_vector_store.similarity_search(
                query=query,
                k=k
            )
    
    def compare_retrievals(
        self,
        query: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Compare old vs new retrieval for testing
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            Comparison results
        """
        # Old system results
        old_results = self.old_vector_store.similarity_search(query, k=k)
        
        # New system results (if available)
        if self.use_enhanced_rag and self.rag_manager:
            new_results = self.rag_manager.retrieve(query, k=k, strategy="auto")
        else:
            new_results = []
        
        return {
            "query": query,
            "old_system": {
                "results": old_results,
                "count": len(old_results)
            },
            "new_system": {
                "results": new_results,
                "count": len(new_results),
                "enabled": self.use_enhanced_rag
            }
        }


# Migration Guide
"""
=======================================================================
MIGRATION GUIDE: Old → Enhanced RAG
=======================================================================

## Phase 1: Add Enhanced RAG (Parallel Running)

### Step 1: Update requirements.txt
```txt
# Add to requirements.txt
langchain-community==0.1.0
rank-bm25==0.2.2
```

### Step 2: Update config.py
```python
# Add feature flag
USE_ENHANCED_RAG = os.getenv("USE_ENHANCED_RAG", "false").lower() == "true"
DEFAULT_RETRIEVAL_STRATEGY = os.getenv("DEFAULT_RETRIEVAL_STRATEGY", "auto")
```

### Step 3: Update workflows/medication_workflow.py
```python
# OLD CODE:
from app.database.vector_store import VectorStore
vector_store = VectorStore(supabase_client, embeddings)
results = vector_store.similarity_search(query, k=5)

# NEW CODE (backward compatible):
from app.rag.rag_integration import RAGIntegration
from app.config import USE_ENHANCED_RAG, DEFAULT_RETRIEVAL_STRATEGY

rag = RAGIntegration(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY,
    openai_api_key=OPENAI_API_KEY,
    use_enhanced_rag=USE_ENHANCED_RAG,
    default_strategy=DEFAULT_RETRIEVAL_STRATEGY
)

# Same interface works for both!
results = rag.search(query, k=5)
```

### Step 4: Update search_database node in workflow
```python
def search_database(state: WorkflowState) -> WorkflowState:
    query = state["query"]
    
    # Use integrated RAG
    results = rag.search(
        query=query,
        k=5,
        strategy="auto",  # Intelligent routing
        filters=state.get("filters")  # Optional metadata filters
    )
    
    state["search_results"] = results
    return state
```

## Phase 2: Test with Feature Flag

### Enable for specific users
```python
# In main.py
@app.post("/api/query")
async def query_endpoint(request: QueryRequest):
    # Check if user is beta tester
    use_enhanced = request.user_id in BETA_TESTERS
    
    rag = RAGIntegration(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY,
        openai_api_key=OPENAI_API_KEY,
        use_enhanced_rag=use_enhanced
    )
    
    results = rag.search(request.query, k=5)
    return {"results": results}
```

### A/B Testing
```python
import random

def get_rag_config(user_id: str):
    # 50% get enhanced RAG
    use_enhanced = hash(user_id) % 2 == 0
    
    return RAGIntegration(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY,
        openai_api_key=OPENAI_API_KEY,
        use_enhanced_rag=use_enhanced
    )
```

## Phase 3: Monitor Performance

### Compare old vs new
```python
# In testing endpoint
@app.post("/api/test/compare")
async def compare_rag(query: str):
    rag = RAGIntegration(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY,
        openai_api_key=OPENAI_API_KEY,
        use_enhanced_rag=True
    )
    
    comparison = rag.compare_retrievals(query, k=5)
    
    return {
        "old_results": len(comparison["old_system"]["results"]),
        "new_results": len(comparison["new_system"]["results"]),
        "quality_improvement": analyze_quality(comparison)
    }
```

## Phase 4: Full Migration

### Remove old code
```python
# Delete old imports
# from app.database.vector_store import VectorStore

# Use enhanced by default
rag = RAGIntegration(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY,
    openai_api_key=OPENAI_API_KEY,
    use_enhanced_rag=True,  # Always on
    default_strategy="auto"
)
```

=======================================================================
USAGE EXAMPLES
=======================================================================

## Example 1: Simple Query (Auto Strategy)
```python
results = rag.search("paralen na bolest")
# Auto-selects: Hybrid (short query)
```

## Example 2: Question Query (HyDE)
```python
results = rag.search("jaké jsou nežádoucí účinky paracetamolu")
# Auto-selects: HyDE (question)
```

## Example 3: Explicit Strategy
```python
results = rag.search(
    query="analgetikum",
    k=5,
    strategy="mmr"  # Force MMR for diversity
)
```

## Example 4: With Filters
```python
results = rag.search(
    query="lék na bolest",
    k=5,
    strategy="hybrid",
    filters={
        "dosage_form": "tableta",
        "prescription_required": False
    }
)
```

## Example 5: A/B Test Comparison
```python
comparison = rag.compare_retrievals("paralen", k=5)

print(f"Old system: {len(comparison['old_system']['results'])} results")
print(f"New system: {len(comparison['new_system']['results'])} results")
```

=======================================================================
ROLLBACK PLAN
=======================================================================

If issues arise:

1. Set environment variable:
   ```bash
   export USE_ENHANCED_RAG=false
   ```

2. Restart service:
   ```bash
   docker-compose restart backend
   ```

3. System automatically falls back to old vector store

4. No data loss - both use same Supabase tables

=======================================================================
"""


# Environment Configuration
"""
# .env file additions

# Feature flags
USE_ENHANCED_RAG=true
DEFAULT_RETRIEVAL_STRATEGY=auto

# RAG Configuration
RAG_HYBRID_BM25_WEIGHT=0.4
RAG_HYBRID_SEMANTIC_WEIGHT=0.6
RAG_MULTIQUERY_NUM_VARIATIONS=3
RAG_PARENT_DOC_CHILD_SIZE=400
RAG_PARENT_DOC_PARENT_SIZE=2000
RAG_MMR_LAMBDA=0.5

# Performance
RAG_CACHE_TTL=3600
RAG_MAX_CONCURRENT_QUERIES=10
"""
