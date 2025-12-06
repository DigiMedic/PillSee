"""
Parent Document Retriever
Search with small chunks, return large parent documents for context
"""

from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

class ParentDocumentRetriever:
    """
    Small chunks for embedding → Large chunks for context
    
    Strategy:
    - Index: Small 400-char chunks (better embedding precision)
    - Retrieve: Large 2000-char parents (better context for LLM)
    
    Example:
    SPC Document (5000 chars) →
    Split into 5 small chunks (400 chars each) for indexing
    When matched → Return full parent (2000 chars) for context
    
    Benefits:
    - Precise matching (small chunks)
    - Rich context (large parents)
    - No truncated information
    """
    
    def __init__(
        self,
        vector_store,
        child_chunk_size: int = 400,
        parent_chunk_size: int = 2000,
        chunk_overlap: int = 100
    ):
        """
        Initialize parent document retriever
        
        Args:
            vector_store: Supabase vector store
            child_chunk_size: Size of chunks for indexing (small)
            parent_chunk_size: Size of chunks for retrieval (large)
            chunk_overlap: Overlap between chunks
        """
        self.vector_store = vector_store
        self.child_chunk_size = child_chunk_size
        self.parent_chunk_size = parent_chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Splitters
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=chunk_overlap * 2,  # More overlap for parents
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Store parent document mapping
        self.parent_doc_store = {}  # child_id -> parent_doc
        
        logger.info(
            f"ParentDocumentRetriever initialized "
            f"(child: {child_chunk_size}, parent: {parent_chunk_size})"
        )
    
    def add_documents(
        self,
        documents: List[Document],
        ids: List[str] = None
    ) -> List[str]:
        """
        Split documents into child/parent chunks and index
        
        Args:
            documents: Original documents to split
            ids: Optional IDs for documents
            
        Returns:
            List of child chunk IDs
        """
        try:
            all_child_docs = []
            doc_ids = []
            
            for i, doc in enumerate(documents):
                doc_id = ids[i] if ids else f"doc_{i}"
                
                # Split into parent chunks
                parent_chunks = self.parent_splitter.split_documents([doc])
                
                # For each parent, create child chunks
                for p_idx, parent_chunk in enumerate(parent_chunks):
                    parent_id = f"{doc_id}_parent_{p_idx}"
                    
                    # Store parent for later retrieval
                    self.parent_doc_store[parent_id] = parent_chunk
                    
                    # Create child chunks
                    child_chunks = self.child_splitter.split_documents([parent_chunk])
                    
                    # Add parent reference to child metadata
                    for c_idx, child_chunk in enumerate(child_chunks):
                        child_id = f"{parent_id}_child_{c_idx}"
                        child_chunk.metadata["parent_id"] = parent_id
                        child_chunk.metadata["doc_id"] = doc_id
                        
                        all_child_docs.append(child_chunk)
                        doc_ids.append(child_id)
            
            logger.info(
                f"Split {len(documents)} docs into "
                f"{len(self.parent_doc_store)} parents and "
                f"{len(all_child_docs)} children"
            )
            
            # Index child chunks in vector store
            self.vector_store.add_documents(all_child_docs)
            
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return []
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Search with child chunks, return parent documents
        
        Args:
            query: Search query
            k: Number of parent documents to return
            
        Returns:
            List of parent documents
        """
        try:
            logger.info(f"Parent-doc retrieval for: '{query[:50]}...'")
            
            # Search child chunks
            child_results = self.vector_store.similarity_search(
                query,
                k=k * 3  # Get more children to ensure diverse parents
            )
            
            # Extract unique parent IDs
            parent_ids = []
            seen_parents = set()
            
            for child_doc in child_results:
                parent_id = child_doc.metadata.get("parent_id")
                if parent_id and parent_id not in seen_parents:
                    seen_parents.add(parent_id)
                    parent_ids.append(parent_id)
                    
                    if len(parent_ids) >= k:
                        break
            
            # Retrieve parent documents
            parent_docs = []
            for parent_id in parent_ids:
                if parent_id in self.parent_doc_store:
                    parent_docs.append(self.parent_doc_store[parent_id])
            
            logger.info(f"Retrieved {len(parent_docs)} parent documents")
            return parent_docs
            
        except Exception as e:
            logger.error(f"Parent-doc retrieval error: {e}")
            # Fallback to standard retrieval
            return self.vector_store.similarity_search(query, k=k)
    
    def retrieve_with_scores(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        Retrieve parent docs with aggregated child scores
        
        Args:
            query: Search query
            k: Number of parents to return
            
        Returns:
            List of (parent_doc, score) tuples
        """
        try:
            # Get child results with scores
            child_results = self.vector_store.similarity_search_with_score(
                query,
                k=k * 3
            )
            
            # Aggregate scores by parent
            parent_scores = {}  # parent_id -> (parent_doc, max_score)
            
            for child_doc, score in child_results:
                parent_id = child_doc.metadata.get("parent_id")
                
                if parent_id and parent_id in self.parent_doc_store:
                    parent_doc = self.parent_doc_store[parent_id]
                    
                    # Use max score among children
                    if parent_id not in parent_scores:
                        parent_scores[parent_id] = (parent_doc, float(score))
                    else:
                        existing_score = parent_scores[parent_id][1]
                        parent_scores[parent_id] = (
                            parent_doc,
                            max(existing_score, float(score))
                        )
            
            # Sort by score
            results = list(parent_scores.values())
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Parent-doc with scores error: {e}")
            return self.vector_store.similarity_search_with_score(query, k=k)
    
    def get_parent_doc(self, parent_id: str) -> Document | None:
        """Get parent document by ID"""
        return self.parent_doc_store.get(parent_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        return {
            "type": "parent_document",
            "child_chunk_size": self.child_chunk_size,
            "parent_chunk_size": self.parent_chunk_size,
            "num_parents": len(self.parent_doc_store),
            "chunk_overlap": self.chunk_overlap
        }


# Example Usage
"""
# Setup
retriever = ParentDocumentRetriever(
    vector_store,
    child_chunk_size=400,   # Small for precise matching
    parent_chunk_size=2000  # Large for context
)

# Index documents
spc_documents = load_spc_documents()
retriever.add_documents(spc_documents)

# Retrieve
query = "nežádoucí účinky paracetamolu"
results = retriever.retrieve(query, k=3)

# Results contain full parent context! ✨
# Instead of truncated 400-char chunks,
# you get complete 2000-char sections with full information
"""
