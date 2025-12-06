"""
Enhanced Vector Store with MMR and Advanced Filtering
Wraps Supabase vector store with additional capabilities
"""

from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
import logging

logger = logging.getLogger(__name__)

class EnhancedVectorStore:
    """
    Enhanced wrapper around Supabase vector store
    
    Features:
    - MMR (Maximal Marginal Relevance) for diversity
    - Metadata filtering (ATC code, dosage form, prescription)
    - Batch operations
    - Query optimization
    """
    
    def __init__(
        self,
        supabase_client,
        embedding_function: OpenAIEmbeddings,
        table_name: str = "drug_embeddings",
        query_name: str = "match_documents"
    ):
        """
        Initialize enhanced vector store
        
        Args:
            supabase_client: Supabase client instance
            embedding_function: OpenAI embeddings
            table_name: Name of the embeddings table
            query_name: Name of the similarity search function
        """
        self.supabase_client = supabase_client
        self.embedding_function = embedding_function
        self.table_name = table_name
        self.query_name = query_name
        
        # Create base vector store
        self.vector_store = SupabaseVectorStore(
            client=supabase_client,
            embedding=embedding_function,
            table_name=table_name,
            query_name=query_name
        )
        
        logger.info(f"EnhancedVectorStore initialized (table: {table_name})")
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Standard similarity search
        
        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter dict
            
        Returns:
            List of documents
        """
        try:
            if filter:
                return self.vector_store.similarity_search(
                    query, k=k, filter=filter
                )
            else:
                return self.vector_store.similarity_search(query, k=k)
                
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Similarity search with relevance scores
        
        Args:
            query: Search query
            k: Number of results
            filter: Metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        try:
            if filter:
                return self.vector_store.similarity_search_with_relevance_scores(
                    query, k=k, filter=filter
                )
            else:
                return self.vector_store.similarity_search_with_relevance_scores(
                    query, k=k
                )
                
        except Exception as e:
            logger.error(f"Similarity search with score error: {e}")
            return []
    
    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        MMR search for diverse results
        
        MMR balances relevance and diversity:
        - lambda_mult=1.0: Pure relevance (like similarity search)
        - lambda_mult=0.5: Balanced (default)
        - lambda_mult=0.0: Pure diversity
        
        Args:
            query: Search query
            k: Number of final results
            fetch_k: Number of candidates to fetch first
            lambda_mult: Diversity parameter (0=diverse, 1=relevant)
            filter: Metadata filter
            
        Returns:
            Diverse list of documents
        """
        try:
            logger.info(
                f"MMR search: k={k}, fetch_k={fetch_k}, λ={lambda_mult}"
            )
            
            # Fetch candidates
            if filter:
                candidates = self.vector_store.similarity_search(
                    query, k=fetch_k, filter=filter
                )
            else:
                candidates = self.vector_store.similarity_search(
                    query, k=fetch_k
                )
            
            if not candidates:
                return []
            
            # Get query embedding
            query_embedding = self.embedding_function.embed_query(query)
            
            # Get candidate embeddings
            candidate_embeddings = [
                self.embedding_function.embed_query(doc.page_content)
                for doc in candidates
            ]
            
            # MMR selection
            selected_indices = self._mmr_selection(
                query_embedding,
                candidate_embeddings,
                k=k,
                lambda_mult=lambda_mult
            )
            
            results = [candidates[i] for i in selected_indices]
            
            logger.info(f"MMR selected {len(results)} diverse documents")
            return results
            
        except Exception as e:
            logger.error(f"MMR search error: {e}")
            # Fallback to standard similarity
            return self.similarity_search(query, k=k, filter=filter)
    
    def _mmr_selection(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        k: int,
        lambda_mult: float
    ) -> List[int]:
        """
        MMR algorithm implementation
        
        Selects k documents that maximize:
        λ * relevance - (1-λ) * similarity to already selected
        """
        import numpy as np
        
        query_emb = np.array(query_embedding)
        candidate_embs = np.array(candidate_embeddings)
        
        # Compute relevance scores (cosine similarity to query)
        relevance = np.dot(candidate_embs, query_emb)
        
        selected = []
        remaining = list(range(len(candidate_embs)))
        
        # Select first document (most relevant)
        best_idx = remaining[np.argmax(relevance[remaining])]
        selected.append(best_idx)
        remaining.remove(best_idx)
        
        # Select remaining k-1 documents
        while len(selected) < k and remaining:
            selected_embs = candidate_embs[selected]
            
            # Compute similarity to already selected
            similarity_to_selected = np.dot(
                candidate_embs[remaining],
                selected_embs.T
            ).max(axis=1)
            
            # MMR score
            mmr_scores = (
                lambda_mult * relevance[remaining] -
                (1 - lambda_mult) * similarity_to_selected
            )
            
            # Select best MMR score
            best_idx = remaining[np.argmax(mmr_scores)]
            selected.append(best_idx)
            remaining.remove(best_idx)
        
        return selected
    
    def search_by_atc_code(
        self,
        atc_code: str,
        k: int = 10
    ) -> List[Document]:
        """
        Search drugs by ATC classification code
        
        Args:
            atc_code: ATC code (e.g., "N02BE01" for paracetamol)
            k: Number of results
            
        Returns:
            List of matching documents
        """
        try:
            logger.info(f"Searching by ATC code: {atc_code}")
            
            filter_dict = {"atc_code": atc_code}
            
            # Query without semantic search, pure metadata filter
            result = self.supabase_client.table(self.table_name)\
                .select("content, metadata")\
                .eq("metadata->>atc_code", atc_code)\
                .limit(k)\
                .execute()
            
            documents = [
                Document(
                    page_content=row["content"],
                    metadata=row.get("metadata", {})
                )
                for row in result.data
            ]
            
            logger.info(f"Found {len(documents)} docs with ATC {atc_code}")
            return documents
            
        except Exception as e:
            logger.error(f"ATC search error: {e}")
            return []
    
    def search_with_filters(
        self,
        query: str,
        k: int = 5,
        atc_code: Optional[str] = None,
        dosage_form: Optional[str] = None,
        prescription_required: Optional[bool] = None,
        manufacturer: Optional[str] = None
    ) -> List[Document]:
        """
        Advanced search with multiple metadata filters
        
        Args:
            query: Search query
            k: Number of results
            atc_code: Filter by ATC code
            dosage_form: Filter by form (tableta, sirup, etc.)
            prescription_required: Filter by prescription requirement
            manufacturer: Filter by manufacturer
            
        Returns:
            Filtered documents
        """
        try:
            # Build filter dict
            filter_dict = {}
            
            if atc_code:
                filter_dict["atc_code"] = atc_code
            if dosage_form:
                filter_dict["dosage_form"] = dosage_form
            if prescription_required is not None:
                filter_dict["prescription_required"] = prescription_required
            if manufacturer:
                filter_dict["manufacturer"] = manufacturer
            
            logger.info(f"Search with filters: {filter_dict}")
            
            return self.similarity_search(query, k=k, filter=filter_dict)
            
        except Exception as e:
            logger.error(f"Filtered search error: {e}")
            return self.similarity_search(query, k=k)
    
    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add documents in batches
        
        Args:
            documents: Documents to add
            batch_size: Batch size for insertion
            
        Returns:
            List of document IDs
        """
        try:
            logger.info(f"Adding {len(documents)} documents in batches of {batch_size}")
            
            all_ids = []
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                ids = self.vector_store.add_documents(batch)
                all_ids.extend(ids)
                
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} docs")
            
            logger.info(f"Total documents added: {len(all_ids)}")
            return all_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return []
    
    def delete_by_metadata(self, filter_dict: Dict[str, Any]) -> int:
        """
        Delete documents by metadata filter
        
        Args:
            filter_dict: Metadata filter
            
        Returns:
            Number of deleted documents
        """
        try:
            logger.warning(f"Deleting documents with filter: {filter_dict}")
            
            # This would need custom Supabase function
            # For now, log warning
            logger.warning("Delete by metadata not implemented yet")
            return 0
            
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            result = self.supabase_client.table(self.table_name)\
                .select("id", count="exact")\
                .execute()
            
            return {
                "table_name": self.table_name,
                "total_documents": result.count,
                "embedding_dimension": 1536,  # text-embedding-3-small
                "query_function": self.query_name
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def as_retriever(self, **kwargs):
        """Get base retriever for LangChain chains"""
        return self.vector_store.as_retriever(**kwargs)


# Example Usage
"""
# Initialize
enhanced_store = EnhancedVectorStore(
    supabase_client=supabase,
    embedding_function=embeddings
)

# Standard similarity search
docs = enhanced_store.similarity_search("paralen", k=5)

# MMR for diverse results
diverse_docs = enhanced_store.max_marginal_relevance_search(
    "bolest hlavy",
    k=5,
    fetch_k=20,
    lambda_mult=0.5  # Balance relevance and diversity
)

# Search with metadata filters
filtered_docs = enhanced_store.search_with_filters(
    query="analgetikum",
    k=5,
    atc_code="N02BE01",  # Paracetamol
    dosage_form="tableta",
    prescription_required=False
)

# Search by ATC code only
atc_docs = enhanced_store.search_by_atc_code("N02BE01", k=10)

# Get stats
stats = enhanced_store.get_stats()
print(f"Total documents: {stats['total_documents']}")
"""
