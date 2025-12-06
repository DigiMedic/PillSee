"""
Hybrid Retriever - Kombinace BM25 a Semantic Search
Optimální pro české lékové dotazy - keyword + meaning
"""

from typing import List, Dict, Any
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
import logging

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Hybrid retrieval combining BM25 (keyword) and semantic search
    
    Benefits:
    - BM25: Exact name/ingredient matches (PARALEN, paracetamol)
    - Semantic: Meaning-based (bolest hlavy → léky proti bolesti)
    - Ensemble: Best of both worlds
    """
    
    def __init__(
        self,
        vector_store,
        documents: List[Document] = None,
        bm25_weight: float = 0.4,
        semantic_weight: float = 0.6
    ):
        """
        Initialize hybrid retriever
        
        Args:
            vector_store: Supabase vector store instance
            documents: List of Document objects for BM25 (if pre-loaded)
            bm25_weight: Weight for BM25 retriever (default 0.4)
            semantic_weight: Weight for semantic retriever (default 0.6)
        """
        self.vector_store = vector_store
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.documents = documents or []
        
        # Initialize retrievers
        self._setup_retrievers()
        
        logger.info(
            f"HybridRetriever initialized (BM25: {bm25_weight}, Semantic: {semantic_weight})"
        )
    
    def _setup_retrievers(self):
        """Setup BM25 and semantic retrievers"""
        
        # Semantic retriever from vector store
        self.semantic_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}  # Get more candidates
        )
        
        # BM25 retriever - needs documents
        if self.documents:
            self.bm25_retriever = BM25Retriever.from_documents(
                self.documents,
                k=10
            )
        else:
            logger.warning("No documents provided for BM25, will load from vector store")
            self.bm25_retriever = None
    
    def load_documents_from_vector_store(self, limit: int = 1000):
        """
        Load documents from vector store for BM25 indexing
        
        Args:
            limit: Max number of documents to load
        """
        try:
            logger.info(f"Loading {limit} documents for BM25 indexing...")
            
            # Query all documents from Supabase
            result = self.vector_store.client.table(
                self.vector_store.table_name
            ).select("content, metadata").limit(limit).execute()
            
            # Convert to LangChain Documents
            self.documents = [
                Document(
                    page_content=row["content"],
                    metadata=row.get("metadata", {})
                )
                for row in result.data
            ]
            
            # Re-initialize BM25 retriever
            if self.documents:
                self.bm25_retriever = BM25Retriever.from_documents(
                    self.documents,
                    k=10
                )
                logger.info(f"BM25 indexed {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Error loading documents for BM25: {e}")
            self.bm25_retriever = None
    
    def get_ensemble_retriever(self, k: int = 5) -> EnsembleRetriever:
        """
        Create ensemble retriever with weighted combination
        
        Args:
            k: Number of final results to return
            
        Returns:
            EnsembleRetriever combining BM25 and semantic
        """
        if not self.bm25_retriever:
            logger.warning("BM25 not available, loading documents...")
            self.load_documents_from_vector_store()
        
        # If still no BM25, fall back to semantic only
        if not self.bm25_retriever:
            logger.warning("BM25 unavailable, using semantic only")
            return self.semantic_retriever
        
        # Create ensemble
        ensemble = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.semantic_retriever],
            weights=[self.bm25_weight, self.semantic_weight]
        )
        
        return ensemble
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve documents using hybrid approach
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of relevant documents
        """
        try:
            logger.info(f"Hybrid retrieval for: '{query[:50]}...'")
            
            ensemble = self.get_ensemble_retriever(k=k)
            results = ensemble.get_relevant_documents(query)
            
            logger.info(f"Retrieved {len(results)} hybrid results")
            return results[:k]
            
        except Exception as e:
            logger.error(f"Hybrid retrieval error: {e}")
            # Fallback to semantic only
            return self.semantic_retriever.get_relevant_documents(query)[:k]
    
    def retrieve_with_scores(
        self, 
        query: str, 
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        Retrieve with relevance scores
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of (document, score) tuples
        """
        try:
            # Get semantic scores
            semantic_results = self.vector_store.similarity_search_with_score(
                query, k=k*2
            )
            
            # Get BM25 results
            if self.bm25_retriever:
                bm25_results = self.bm25_retriever.get_relevant_documents(query)
            else:
                bm25_results = []
            
            # Combine scores
            combined = self._combine_results(semantic_results, bm25_results)
            
            return combined[:k]
            
        except Exception as e:
            logger.error(f"Error in retrieve_with_scores: {e}")
            return [(doc, 0.5) for doc in self.retrieve(query, k)]
    
    def _combine_results(
        self,
        semantic_results: List[tuple[Document, float]],
        bm25_results: List[Document]
    ) -> List[tuple[Document, float]]:
        """
        Combine and re-rank results from both retrievers
        
        Args:
            semantic_results: (document, score) from semantic search
            bm25_results: documents from BM25
            
        Returns:
            Combined ranked results
        """
        # Create score map
        scores = {}
        
        # Add semantic scores
        for doc, score in semantic_results:
            doc_id = doc.page_content[:100]  # Use content prefix as ID
            scores[doc_id] = {
                "doc": doc,
                "semantic": float(score) * self.semantic_weight,
                "bm25": 0.0
            }
        
        # Add BM25 scores (rank-based)
        for i, doc in enumerate(bm25_results):
            doc_id = doc.page_content[:100]
            bm25_score = (len(bm25_results) - i) / len(bm25_results)
            
            if doc_id in scores:
                scores[doc_id]["bm25"] = bm25_score * self.bm25_weight
            else:
                scores[doc_id] = {
                    "doc": doc,
                    "semantic": 0.0,
                    "bm25": bm25_score * self.bm25_weight
                }
        
        # Calculate combined scores
        combined = [
            (data["doc"], data["semantic"] + data["bm25"])
            for data in scores.values()
        ]
        
        # Sort by combined score
        combined.sort(key=lambda x: x[1], reverse=True)
        
        return combined
    
    def get_retriever_info(self) -> Dict[str, Any]:
        """Get retriever configuration info"""
        return {
            "type": "hybrid",
            "bm25_weight": self.bm25_weight,
            "semantic_weight": self.semantic_weight,
            "bm25_available": self.bm25_retriever is not None,
            "documents_indexed": len(self.documents)
        }
