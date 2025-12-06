"""
RAG Pipeline Manager
Orchestrates all RAG retrieval strategies
"""

from typing import List, Dict, Any, Literal
from langchain.schema import Document
from langchain_openai import ChatOpenAI
import logging

from .hybrid_retriever import HybridRetriever
from .hyde_retriever import HyDERetriever
from .multi_query import MultiQueryRetriever
from .parent_document import ParentDocumentRetriever
from .contextual_compression import ContextualCompressionRetriever

logger = logging.getLogger(__name__)

RAGStrategy = Literal["hybrid", "hyde", "multi_query", "parent_doc", "compressed", "ensemble"]

class RAGPipeline:
    """
    Central manager for all RAG retrieval strategies
    
    Provides unified interface for:
    - Hybrid retrieval (BM25 + Semantic)
    - HyDE (hypothetical documents)
    - Multi-query (query variations)
    - Parent documents (small chunks → large context)
    - Contextual compression (re-ranking + extraction)
    - Ensemble (combine multiple strategies)
    """
    
    def __init__(
        self,
        vector_store,
        openai_api_key: str = None,
        default_strategy: RAGStrategy = "hybrid"
    ):
        """
        Initialize RAG pipeline
        
        Args:
            vector_store: Supabase vector store
            openai_api_key: OpenAI API key
            default_strategy: Default retrieval strategy
        """
        self.vector_store = vector_store
        self.openai_api_key = openai_api_key
        self.default_strategy = default_strategy
        
        # Initialize LLM for advanced strategies
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=openai_api_key
        )
        
        # Initialize retrievers
        self.retrievers = {}
        self._initialize_retrievers()
        
        logger.info(f"RAGPipeline initialized (default: {default_strategy})")
    
    def _initialize_retrievers(self):
        """Initialize all retrieval strategies"""
        
        try:
            self.retrievers["hybrid"] = HybridRetriever(
                vector_store=self.vector_store,
                bm25_weight=0.4,
                semantic_weight=0.6
            )
            logger.info("✓ Hybrid retriever initialized")
        except Exception as e:
            logger.error(f"✗ Hybrid retriever failed: {e}")
        
        try:
            self.retrievers["hyde"] = HyDERetriever(
                vector_store=self.vector_store,
                llm=self.llm
            )
            logger.info("✓ HyDE retriever initialized")
        except Exception as e:
            logger.error(f"✗ HyDE retriever failed: {e}")
        
        try:
            self.retrievers["multi_query"] = MultiQueryRetriever(
                vector_store=self.vector_store,
                llm=self.llm,
                num_queries=3
            )
            logger.info("✓ Multi-query retriever initialized")
        except Exception as e:
            logger.error(f"✗ Multi-query retriever failed: {e}")
        
        try:
            self.retrievers["parent_doc"] = ParentDocumentRetriever(
                vector_store=self.vector_store,
                child_chunk_size=400,
                parent_chunk_size=2000
            )
            logger.info("✓ Parent-doc retriever initialized")
        except Exception as e:
            logger.error(f"✗ Parent-doc retriever failed: {e}")
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        strategy: RAGStrategy = None,
        use_compression: bool = False
    ) -> List[Document]:
        """
        Retrieve documents using specified strategy
        
        Args:
            query: Search query
            k: Number of results
            strategy: Retrieval strategy (uses default if None)
            use_compression: Apply contextual compression
            
        Returns:
            List of relevant documents
        """
        strategy = strategy or self.default_strategy
        
        logger.info(f"RAG retrieve: strategy={strategy}, k={k}, compression={use_compression}")
        
        try:
            if strategy == "ensemble":
                results = self._ensemble_retrieve(query, k)
            else:
                retriever = self.retrievers.get(strategy)
                if not retriever:
                    logger.warning(f"Strategy '{strategy}' not available, using hybrid")
                    retriever = self.retrievers.get("hybrid", self.vector_store)
                
                results = retriever.retrieve(query, k=k)
            
            if use_compression and results:
                results = self._apply_compression(query, results, k)
            
            logger.info(f"Retrieved {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return self.vector_store.similarity_search(query, k=k)
    
    def _ensemble_retrieve(self, query: str, k: int) -> List[Document]:
        """Combine multiple retrieval strategies"""
        logger.info("Using ensemble retrieval (hybrid + hyde + multi_query)")
        
        all_results = []
        seen_contents = set()
        
        for strategy in ["hybrid", "hyde", "multi_query"]:
            if strategy in self.retrievers:
                try:
                    results = self.retrievers[strategy].retrieve(query, k=k)
                    
                    for doc in results:
                        content_hash = hash(doc.page_content[:200])
                        if content_hash not in seen_contents:
                            seen_contents.add(content_hash)
                            all_results.append(doc)
                
                except Exception as e:
                    logger.error(f"Strategy {strategy} failed in ensemble: {e}")
        
        logger.info(f"Ensemble retrieved {len(all_results)} unique documents")
        return all_results[:k * 2]
    
    def _apply_compression(
        self,
        query: str,
        documents: List[Document],
        k: int
    ) -> List[Document]:
        """Apply contextual compression to results"""
        
        try:
            from langchain.retrievers.document_compressors import LLMChainExtractor
            from langchain.prompts import PromptTemplate
            
            prompt_template = """S ohledem na dotaz, extrahuj pouze relevantní informace.
Pokud dokument není relevantní, vrať prázdný string.

DOTAZ: {question}
DOKUMENT: {context}

RELEVANTNÍ INFORMACE:"""
            
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["question", "context"]
            )
            
            compressor = LLMChainExtractor.from_llm(llm=self.llm, prompt=prompt)
            compressed = compressor.compress_documents(documents, query)
            
            logger.info(f"Compressed {len(documents)} → {len(compressed)} documents")
            return compressed[:k]
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return documents[:k]
    
    def get_best_strategy_for_query(self, query: str) -> RAGStrategy:
        """Determine best retrieval strategy for query"""
        query_lower = query.lower()
        
        if any(drug in query_lower for drug in ["paralen", "ibuprofen", "aspirin"]):
            return "hybrid"
        
        if any(word in query_lower for word in ["co je", "co dělá", "jak funguje"]):
            return "hyde"
        
        if len(query.split()) < 4:
            return "multi_query"
        
        if any(word in query_lower for word in ["interakce", "kombinace", "spolu s"]):
            return "ensemble"
        
        return "hybrid"
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline configuration and status"""
        return {
            "default_strategy": self.default_strategy,
            "available_strategies": list(self.retrievers.keys()),
            "retrievers": {
                name: retriever.get_retriever_info() 
                if hasattr(retriever, 'get_retriever_info') else {"type": type(retriever).__name__}
                for name, retriever in self.retrievers.items()
            }
        }
