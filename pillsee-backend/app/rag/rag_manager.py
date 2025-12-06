"""
RAG Manager - Orchestration of all retrieval strategies
Intelligent routing and combination of retrieval methods
"""

from typing import List, Dict, Any, Optional, Literal
from langchain.schema import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import logging

from .hybrid_retriever import HybridRetriever
from .hyde_retriever import HyDERetriever
from .multi_query import MultiQueryRetriever
from .parent_document import ParentDocumentRetriever
from .contextual_compression import ContextualCompressionRetriever
from .enhanced_vector_store import EnhancedVectorStore

logger = logging.getLogger(__name__)

RetrievalStrategy = Literal[
    "semantic",      # Standard similarity search
    "hybrid",        # BM25 + Semantic
    "hyde",          # Hypothetical document embeddings
    "multi_query",   # Multiple query variations
    "parent_doc",    # Small chunks → large context
    "mmr",           # Maximal marginal relevance
    "compressed",    # LLM-compressed results
    "auto"           # Intelligent routing
]

class RAGManager:
    """
    Central manager for all RAG retrieval strategies
    
    Features:
    - Multiple retrieval strategies
    - Intelligent strategy selection
    - Strategy combination
    - Performance tracking
    - Easy configuration
    """
    
    def __init__(
        self,
        vector_store: EnhancedVectorStore,
        openai_api_key: str,
        default_strategy: RetrievalStrategy = "auto"
    ):
        """
        Initialize RAG Manager
        
        Args:
            vector_store: Enhanced vector store instance
            openai_api_key: OpenAI API key
            default_strategy: Default retrieval strategy
        """
        self.vector_store = vector_store
        self.openai_api_key = openai_api_key
        self.default_strategy = default_strategy
        
        # LLM for advanced retrievers
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=openai_api_key
        )
        
        # Initialize all retrievers
        self._initialize_retrievers()
        
        # Track usage
        self.usage_stats = {
            strategy: {"calls": 0, "docs_retrieved": 0}
            for strategy in RetrievalStrategy.__args__
        }
        
        logger.info(f"RAGManager initialized (default: {default_strategy})")
    
    def _initialize_retrievers(self):
        """Initialize all retrieval strategies"""
        
        logger.info("Initializing retrievers...")
        
        # Hybrid Retriever
        self.hybrid_retriever = HybridRetriever(
            vector_store=self.vector_store.vector_store,
            bm25_weight=0.4,
            semantic_weight=0.6
        )
        
        # HyDE Retriever
        self.hyde_retriever = HyDERetriever(
            vector_store=self.vector_store.vector_store,
            llm=self.llm
        )
        
        # Multi-Query Retriever
        self.multi_query_retriever = MultiQueryRetriever(
            vector_store=self.vector_store.vector_store,
            llm=self.llm,
            num_queries=3
        )
        
        # Parent Document Retriever
        self.parent_doc_retriever = ParentDocumentRetriever(
            vector_store=self.vector_store.vector_store,
            child_chunk_size=400,
            parent_chunk_size=2000
        )
        
        # Contextual Compression (wraps hybrid)
        base_retriever = self.hybrid_retriever.get_ensemble_retriever()
        self.compression_retriever = ContextualCompressionRetriever(
            base_retriever=base_retriever,
            llm=self.llm,
            top_k=5
        )
        
        logger.info("All retrievers initialized ✓")
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        strategy: Optional[RetrievalStrategy] = None,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Document]:
        """
        Main retrieval method with strategy selection
        
        Args:
            query: Search query
            k: Number of results
            strategy: Retrieval strategy (uses default if None)
            filters: Metadata filters
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            List of retrieved documents
        """
        strategy = strategy or self.default_strategy
        
        logger.info(f"Retrieving with strategy '{strategy}' for: '{query[:50]}...'")
        
        try:
            # Route to appropriate strategy
            if strategy == "auto":
                results = self._auto_select_strategy(query, k, filters)
            elif strategy == "semantic":
                results = self._semantic_retrieve(query, k, filters)
            elif strategy == "hybrid":
                results = self._hybrid_retrieve(query, k)
            elif strategy == "hyde":
                results = self._hyde_retrieve(query, k)
            elif strategy == "multi_query":
                results = self._multi_query_retrieve(query, k)
            elif strategy == "parent_doc":
                results = self._parent_doc_retrieve(query, k)
            elif strategy == "mmr":
                results = self._mmr_retrieve(query, k, filters, **kwargs)
            elif strategy == "compressed":
                results = self._compressed_retrieve(query, k)
            else:
                logger.warning(f"Unknown strategy '{strategy}', using semantic")
                results = self._semantic_retrieve(query, k, filters)
            
            # Track usage
            self.usage_stats[strategy]["calls"] += 1
            self.usage_stats[strategy]["docs_retrieved"] += len(results)
            
            logger.info(f"Retrieved {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Retrieval error with strategy '{strategy}': {e}")
            # Fallback to semantic
            return self._semantic_retrieve(query, k, filters)
    
    def _auto_select_strategy(
        self,
        query: str,
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Intelligent strategy selection based on query characteristics
        
        Rules:
        - Short exact name queries → Hybrid (BM25 + Semantic)
        - "How" or "What" questions → HyDE
        - Vague queries → Multi-Query
        - Need diversity → MMR
        - Default → Hybrid
        """
        query_lower = query.lower()
        
        # Rule 1: Exact drug names → Hybrid
        if len(query.split()) <= 3 and not any(
            word in query_lower for word in ["jak", "co", "proč", "kdy"]
        ):
            logger.info("Auto-select: HYBRID (short/exact query)")
            return self._hybrid_retrieve(query, k)
        
        # Rule 2: "How" or "What" questions → HyDE
        if any(word in query_lower for word in ["jak", "co je", "jaké jsou"]):
            logger.info("Auto-select: HyDE (question query)")
            return self._hyde_retrieve(query, k)
        
        # Rule 3: Vague/broad queries → Multi-Query
        if len(query.split()) >= 5:
            logger.info("Auto-select: MULTI-QUERY (complex query)")
            return self._multi_query_retrieve(query, k)
        
        # Rule 4: With filters → Semantic + Filters
        if filters:
            logger.info("Auto-select: SEMANTIC (with filters)")
            return self._semantic_retrieve(query, k, filters)
        
        # Default: Hybrid
        logger.info("Auto-select: HYBRID (default)")
        return self._hybrid_retrieve(query, k)
    
    def _semantic_retrieve(
        self,
        query: str,
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Standard semantic similarity search"""
        return self.vector_store.similarity_search(query, k=k, filter=filters)
    
    def _hybrid_retrieve(self, query: str, k: int) -> List[Document]:
        """Hybrid BM25 + Semantic retrieval"""
        return self.hybrid_retriever.retrieve(query, k=k)
    
    def _hyde_retrieve(self, query: str, k: int) -> List[Document]:
        """HyDE retrieval"""
        return self.hyde_retriever.retrieve(query, k=k)
    
    def _multi_query_retrieve(self, query: str, k: int) -> List[Document]:
        """Multi-query retrieval"""
        return self.multi_query_retriever.retrieve(query, k=k)
    
    def _parent_doc_retrieve(self, query: str, k: int) -> List[Document]:
        """Parent document retrieval"""
        return self.parent_doc_retriever.retrieve(query, k=k)
    
    def _mmr_retrieve(
        self,
        query: str,
        k: int,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Document]:
        """MMR retrieval for diversity"""
        lambda_mult = kwargs.get("lambda_mult", 0.5)
        fetch_k = kwargs.get("fetch_k", k * 4)
        
        return self.vector_store.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            filter=filters
        )
    
    def _compressed_retrieve(self, query: str, k: int) -> List[Document]:
        """Contextual compression retrieval"""
        return self.compression_retriever.retrieve(query, k=k)
    
    def retrieve_with_strategy_comparison(
        self,
        query: str,
        k: int = 5,
        strategies: List[RetrievalStrategy] = None
    ) -> Dict[str, List[Document]]:
        """
        Compare multiple strategies side-by-side
        
        Args:
            query: Search query
            k: Number of results per strategy
            strategies: List of strategies to compare
            
        Returns:
            Dict mapping strategy names to results
        """
        if strategies is None:
            strategies = ["semantic", "hybrid", "hyde", "multi_query"]
        
        logger.info(f"Comparing {len(strategies)} strategies")
        
        results = {}
        for strategy in strategies:
            try:
                results[strategy] = self.retrieve(query, k=k, strategy=strategy)
            except Exception as e:
                logger.error(f"Error with strategy '{strategy}': {e}")
                results[strategy] = []
        
        return results
    
    def get_best_strategy_for_query(self, query: str) -> RetrievalStrategy:
        """
        Suggest best strategy for a given query
        
        Args:
            query: Query to analyze
            
        Returns:
            Recommended strategy
        """
        query_lower = query.lower()
        
        # Exact drug names
        if len(query.split()) <= 2:
            return "hybrid"
        
        # Questions
        if any(word in query_lower for word in ["jak", "co", "proč", "kdy", "kde"]):
            return "hyde"
        
        # Complex queries
        if len(query.split()) >= 6:
            return "multi_query"
        
        # Need diversity
        if "různé" in query_lower or "alternativy" in query_lower:
            return "mmr"
        
        return "hybrid"
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get retrieval usage statistics"""
        return {
            "usage_by_strategy": self.usage_stats,
            "total_calls": sum(s["calls"] for s in self.usage_stats.values()),
            "total_docs_retrieved": sum(
                s["docs_retrieved"] for s in self.usage_stats.values()
            ),
            "default_strategy": self.default_strategy
        }
    
    def get_retriever_info(self) -> Dict[str, Any]:
        """Get information about all retrievers"""
        return {
            "available_strategies": list(RetrievalStrategy.__args__),
            "default_strategy": self.default_strategy,
            "retrievers": {
                "hybrid": self.hybrid_retriever.get_retriever_info(),
                "multi_query": self.multi_query_retriever.get_retriever_info(),
                "parent_doc": self.parent_doc_retriever.get_stats(),
                "compression": self.compression_retriever.get_compression_stats(),
                "vector_store": self.vector_store.get_stats()
            }
        }


# Example Usage
"""
# Initialize
rag_manager = RAGManager(
    vector_store=enhanced_vector_store,
    openai_api_key=api_key,
    default_strategy="auto"
)

# Simple retrieval with auto strategy selection
docs = rag_manager.retrieve("paralen na bolest", k=5)

# Explicit strategy
docs = rag_manager.retrieve(
    "jaké jsou nežádoucí účinky paracetamolu",
    k=5,
    strategy="hyde"
)

# With filters
docs = rag_manager.retrieve(
    "analgetikum",
    k=5,
    strategy="hybrid",
    filters={"dosage_form": "tableta"}
)

# MMR for diversity
docs = rag_manager.retrieve(
    "léky na bolest",
    k=5,
    strategy="mmr",
    lambda_mult=0.3  # More diversity
)

# Compare strategies
comparison = rag_manager.retrieve_with_strategy_comparison(
    "paralen",
    k=3,
    strategies=["semantic", "hybrid", "hyde"]
)

# Get recommendations
best_strategy = rag_manager.get_best_strategy_for_query(
    "jak správně užívat paralen"
)
print(f"Recommended: {best_strategy}")  # → "hyde"

# Usage stats
stats = rag_manager.get_usage_stats()
print(f"Total retrievals: {stats['total_calls']}")
"""
