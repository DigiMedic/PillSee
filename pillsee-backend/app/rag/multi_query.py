"""
Multi-Query Retriever
Generates multiple query variations for better recall
"""

from typing import List, Set
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class MultiQueryRetriever:
    """
    Generate multiple query variations and combine results
    
    Example:
    Original: "paralen na bolest"
    Generates: 
    - "paralen proti bolesti"
    - "paracetamol tablety"
    - "lék na bolest hlavy paralen"
    
    Benefits:
    - Captures different phrasings
    - Better recall (finds more relevant docs)
    - Reduces sensitivity to exact wording
    """
    
    def __init__(
        self,
        vector_store,
        llm: ChatOpenAI = None,
        num_queries: int = 3,
        openai_api_key: str = None
    ):
        """
        Initialize multi-query retriever
        
        Args:
            vector_store: Supabase vector store
            llm: LLM for generating query variations
            num_queries: Number of variations to generate
            openai_api_key: OpenAI API key
        """
        self.vector_store = vector_store
        self.num_queries = num_queries
        
        if llm:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.5,  # Slightly higher for variation
                max_tokens=150,
                openai_api_key=openai_api_key
            )
        
        self.query_generation_prompt = self._create_prompt()
        
        logger.info(f"MultiQueryRetriever initialized (variations: {num_queries})")
    
    def _create_prompt(self) -> PromptTemplate:
        """Create prompt for generating query variations"""
        
        template = """Jsi expert na české lékové databáze. 
Vygeneruj {num_queries} různé varianty dotazu pro vyhledání léčiv.
Každá varianta by měla používat trochu jiná slova, ale hledat stejnou informaci.

PŮVODNÍ DOTAZ: {query}

VARIANTY (každá na novém řádku):
1."""
        
        return PromptTemplate(
            template=template,
            input_variables=["query", "num_queries"]
        )
    
    def generate_queries(self, query: str) -> List[str]:
        """
        Generate multiple query variations
        
        Args:
            query: Original query
            
        Returns:
            List of query variations (including original)
        """
        try:
            logger.info(f"Generating {self.num_queries} variations for: '{query}'")
            
            prompt = self.query_generation_prompt.format(
                query=query,
                num_queries=self.num_queries
            )
            
            response = self.llm.invoke(prompt)
            
            # Extract queries from response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Parse variations
            variations = self._parse_variations(response_text)
            
            # Always include original query
            all_queries = [query] + variations
            
            # Remove duplicates while preserving order
            seen = set()
            unique_queries = []
            for q in all_queries:
                q_lower = q.lower().strip()
                if q_lower and q_lower not in seen:
                    seen.add(q_lower)
                    unique_queries.append(q)
            
            logger.info(f"Generated {len(unique_queries)} unique queries")
            return unique_queries
            
        except Exception as e:
            logger.error(f"Error generating query variations: {e}")
            return [query]  # Fallback to original
    
    def _parse_variations(self, response_text: str) -> List[str]:
        """Parse query variations from LLM response"""
        
        variations = []
        lines = response_text.strip().split('\n')
        
        for line in lines:
            # Remove numbering and clean
            cleaned = line.strip()
            
            # Remove common prefixes
            for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•']:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
            
            if cleaned and len(cleaned) > 5:  # Minimum length check
                variations.append(cleaned)
        
        return variations[:self.num_queries]
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve using multiple query variations
        
        Args:
            query: Original query
            k: Number of final results
            
        Returns:
            Deduplicated list of documents
        """
        try:
            # Generate query variations
            queries = self.generate_queries(query)
            
            # Retrieve for each variation
            all_results = []
            seen_contents = set()
            
            for q in queries:
                logger.debug(f"Searching for variation: '{q}'")
                
                results = self.vector_store.similarity_search(q, k=k)
                
                # Deduplicate by content
                for doc in results:
                    content_hash = hash(doc.page_content[:200])
                    if content_hash not in seen_contents:
                        seen_contents.add(content_hash)
                        all_results.append(doc)
            
            logger.info(f"Multi-query retrieved {len(all_results)} unique documents")
            
            # Return top k most diverse results
            return all_results[:k * 2]  # Return more for diversity
            
        except Exception as e:
            logger.error(f"Multi-query retrieval error: {e}")
            return self.vector_store.similarity_search(query, k=k)
    
    def retrieve_with_scores(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        Retrieve with scores using multi-query
        
        Args:
            query: Original query
            k: Number of results
            
        Returns:
            List of (document, aggregated_score) tuples
        """
        try:
            queries = self.generate_queries(query)
            
            # Collect all results with scores
            doc_scores = {}  # content_hash -> (doc, max_score)
            
            for q in queries:
                results = self.vector_store.similarity_search_with_score(q, k=k)
                
                for doc, score in results:
                    content_hash = hash(doc.page_content[:200])
                    
                    # Keep max score for each unique document
                    if content_hash not in doc_scores:
                        doc_scores[content_hash] = (doc, float(score))
                    else:
                        existing_score = doc_scores[content_hash][1]
                        doc_scores[content_hash] = (
                            doc,
                            max(existing_score, float(score))
                        )
            
            # Sort by score
            results = list(doc_scores.values())
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Multi-query with scores error: {e}")
            return self.vector_store.similarity_search_with_score(query, k=k)
    
    def get_retriever_info(self) -> dict:
        """Get retriever configuration"""
        return {
            "type": "multi_query",
            "num_variations": self.num_queries,
            "model": self.llm.model_name if hasattr(self.llm, 'model_name') else "unknown"
        }


# Example Usage
"""
retriever = MultiQueryRetriever(vector_store, num_queries=3)

query = "lék na kašel"
results = retriever.retrieve(query, k=5)

# Behind the scenes:
# Generates:
# 1. "lék na kašel"
# 2. "přípravek proti kašli"  
# 3. "antitusikum sirup"
# 4. "léčba kašle"

# Searches with all 4 → More comprehensive results! ✨
"""
