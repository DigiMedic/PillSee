"""
Contextual Compression Retriever
Use LLM to re-rank and compress retrieved documents
"""

from typing import List
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class ContextualCompressionRetriever:
    """
    Post-process retrieved docs: re-rank + extract relevant parts
    
    Process:
    1. Retrieve top-k documents (e.g., 10)
    2. LLM re-ranks by relevance to query
    3. Extract only relevant sentences
    4. Return compressed, highly relevant content
    
    Benefits:
    - Removes irrelevant content from retrieved docs
    - Focuses LLM attention on relevant parts
    - Reduces token usage
    - Improves answer quality
    """
    
    def __init__(
        self,
        base_retriever,
        llm: ChatOpenAI = None,
        openai_api_key: str = None,
        top_k: int = 3
    ):
        """
        Initialize contextual compression retriever
        
        Args:
            base_retriever: Underlying retriever (hybrid, semantic, etc.)
            llm: LLM for compression
            openai_api_key: OpenAI API key
            top_k: Number of compressed docs to return
        """
        self.base_retriever = base_retriever
        self.top_k = top_k
        
        # LLM for compression
        if llm:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,  # Deterministic extraction
                max_tokens=300,
                openai_api_key=openai_api_key
            )
        
        # Create compressor
        self.compressor = self._create_compressor()
        
        # Create compression retriever
        self.compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.compressor,
            base_retriever=self.base_retriever
        )
        
        logger.info("ContextualCompressionRetriever initialized")
    
    def _create_compressor(self) -> LLMChainExtractor:
        """Create LLM-based document compressor"""
        
        # Czech medical prompt for extraction
        prompt_template = """S ohledem na následující dotaz, extrahuj pouze relevantní informace z dokumentu.
Pokud dokument neobsahuje relevantní informace, vrať prázdný string.

DOTAZ: {question}

DOKUMENT: {context}

RELEVANTNÍ INFORMACE (pouze to, co se přímo týká dotazu):"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["question", "context"]
        )
        
        compressor = LLMChainExtractor.from_llm(
            llm=self.llm,
            prompt=prompt
        )
        
        return compressor
    
    def retrieve(self, query: str, k: int = None) -> List[Document]:
        """
        Retrieve and compress documents
        
        Args:
            query: Search query
            k: Number of compressed docs (uses top_k if None)
            
        Returns:
            List of compressed, relevant documents
        """
        try:
            k = k or self.top_k
            
            logger.info(f"Contextual compression retrieval for: '{query[:50]}...'")
            
            # Get compressed docs
            compressed_docs = self.compression_retriever.get_relevant_documents(
                query
            )
            
            logger.info(f"Compressed {len(compressed_docs)} documents")
            return compressed_docs[:k]
            
        except Exception as e:
            logger.error(f"Compression retrieval error: {e}")
            # Fallback to base retriever without compression
            return self.base_retriever.get_relevant_documents(query)[:k]
    
    def retrieve_verbose(
        self,
        query: str,
        k: int = None
    ) -> dict:
        """
        Retrieve with before/after comparison
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            Dict with original and compressed docs
        """
        try:
            k = k or self.top_k
            
            # Get original docs
            original_docs = self.base_retriever.get_relevant_documents(query)
            
            # Get compressed docs
            compressed_docs = self.compression_retriever.get_relevant_documents(
                query
            )
            
            # Calculate compression ratio
            original_chars = sum(len(doc.page_content) for doc in original_docs[:k])
            compressed_chars = sum(len(doc.page_content) for doc in compressed_docs[:k])
            
            compression_ratio = (
                1 - (compressed_chars / original_chars)
            ) if original_chars > 0 else 0
            
            logger.info(
                f"Compression: {original_chars} → {compressed_chars} chars "
                f"({compression_ratio:.1%} reduction)"
            )
            
            return {
                "query": query,
                "original_docs": original_docs[:k],
                "compressed_docs": compressed_docs[:k],
                "original_chars": original_chars,
                "compressed_chars": compressed_chars,
                "compression_ratio": compression_ratio
            }
            
        except Exception as e:
            logger.error(f"Verbose retrieval error: {e}")
            return {
                "query": query,
                "error": str(e),
                "compressed_docs": []
            }
    
    def get_compression_stats(self) -> dict:
        """Get compression statistics"""
        return {
            "type": "contextual_compression",
            "base_retriever": type(self.base_retriever).__name__,
            "compressor": "LLMChainExtractor",
            "llm_model": self.llm.model_name if hasattr(self.llm, 'model_name') else "unknown",
            "top_k": self.top_k
        }


# Example Usage and Comparison
"""
# Setup
base_retriever = hybrid_retriever.get_ensemble_retriever()
compression_retriever = ContextualCompressionRetriever(
    base_retriever=base_retriever,
    top_k=3
)

# Query
query = "dávkování paracetamolu pro dospělé"

# WITHOUT compression:
docs = base_retriever.get_relevant_documents(query)
# Returns: Full 2000-char chunks with lots of irrelevant info
# "Paralen 500mg obsahuje paracetamol... [500 words about everything]"

# WITH compression:
compressed = compression_retriever.retrieve(query)
# Returns: Only relevant sentences
# "Dávkování pro dospělé: 1-2 tablety po 500mg každých 4-6 hodin, 
#  maximálně 8 tablet za 24 hodin."

# Result: 
# - Token savings: ~70%
# - Better LLM focus
# - Faster response ✨
"""
