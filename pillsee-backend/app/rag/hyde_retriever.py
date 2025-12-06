"""
HyDE (Hypothetical Document Embeddings) Retriever
Generates hypothetical answer, uses its embedding for better search
"""

from typing import List
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class HyDERetriever:
    """
    HyDE: Generate hypothetical answer, embed it, search with that embedding
    
    Example:
    Query: "Co pomáhá na bolest hlavy?"
    HyDE generates: "Paralen nebo Ibuprofen obsahující paracetamol/ibuprofen..."
    Embeds that ↑ and searches → Better matches than embedding the question!
    
    Benefits:
    - Bridges semantic gap between questions and answers
    - Better for "how" and "what" questions
    - Especially good for Czech medical terminology
    """
    
    def __init__(
        self,
        vector_store,
        llm: ChatOpenAI = None,
        openai_api_key: str = None
    ):
        """
        Initialize HyDE retriever
        
        Args:
            vector_store: Supabase vector store
            llm: LLM for generating hypothetical documents
            openai_api_key: OpenAI API key
        """
        self.vector_store = vector_store
        
        # Initialize LLM for hypothesis generation
        if llm:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,  # Low temp for consistent medical info
                max_tokens=200,   # Short hypothetical answer
                openai_api_key=openai_api_key
            )
        
        # Prompt for generating hypothetical document
        self.hyde_prompt = self._create_hyde_prompt()
        
        logger.info("HyDERetriever initialized")
    
    def _create_hyde_prompt(self) -> PromptTemplate:
        """
        Create prompt template for generating hypothetical documents
        """
        template = """Jsi odborný farmaceutický asistent. 
Vygeneruj krátkou, fakticky přesnou odpověď na tento dotaz o léku.
Odpověz tak, jako by to bylo z příbalového letáku.

DOTAZ: {query}

HYPOTETICKÁ ODPOVĚĎ (2-3 věty):"""
        
        return PromptTemplate(
            template=template,
            input_variables=["query"]
        )
    
    def generate_hypothetical_document(self, query: str) -> str:
        """
        Generate hypothetical answer to the query
        
        Args:
            query: User's question
            
        Returns:
            Hypothetical answer
        """
        try:
            logger.info(f"Generating HyDE for: '{query[:50]}...'")
            
            # Generate hypothetical doc
            prompt = self.hyde_prompt.format(query=query)
            response = self.llm.invoke(prompt)
            
            # Extract text from response
            if hasattr(response, 'content'):
                hypothetical = response.content
            else:
                hypothetical = str(response)
            
            logger.info(f"HyDE generated: '{hypothetical[:50]}...'")
            return hypothetical
            
        except Exception as e:
            logger.error(f"Error generating HyDE: {e}")
            # Fallback to original query
            return query
    
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve using HyDE approach
        
        Args:
            query: User query
            k: Number of results
            
        Returns:
            List of relevant documents
        """
        try:
            # Step 1: Generate hypothetical document
            hypothetical = self.generate_hypothetical_document(query)
            
            # Step 2: Search using hypothetical document's embedding
            results = self.vector_store.similarity_search(
                hypothetical,
                k=k
            )
            
            logger.info(f"HyDE retrieved {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"HyDE retrieval error: {e}")
            # Fallback to direct query
            return self.vector_store.similarity_search(query, k=k)
    
    def retrieve_with_scores(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        Retrieve with similarity scores
        
        Args:
            query: User query
            k: Number of results
            
        Returns:
            List of (document, score) tuples
        """
        try:
            hypothetical = self.generate_hypothetical_document(query)
            
            results = self.vector_store.similarity_search_with_score(
                hypothetical,
                k=k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"HyDE with scores error: {e}")
            return self.vector_store.similarity_search_with_score(query, k=k)
    
    def get_retriever_chain(self):
        """
        Get LangChain-compatible retriever
        
        Returns:
            Retriever object for use in chains
        """
        from langchain.retrievers import BaseRetriever
        from langchain.schema import BaseRetriever as BR
        
        class HyDERetrieverWrapper(BaseRetriever):
            hyde_retriever: 'HyDERetriever'
            
            def _get_relevant_documents(self, query: str) -> List[Document]:
                return self.hyde_retriever.retrieve(query)
            
            async def _aget_relevant_documents(self, query: str) -> List[Document]:
                return self.hyde_retriever.retrieve(query)
        
        return HyDERetrieverWrapper(hyde_retriever=self)


# Example usage comparison
"""
# Standard retrieval:
Query: "Co pomáhá na bolest hlavy?"
Embeds: "co pomáhá na bolest hlavy"
Searches: [low similarity to actual drug descriptions]

# HyDE retrieval:
Query: "Co pomáhá na bolest hlavy?"
Generates: "Paracetamol v tabletách po 500mg, jako Paralen nebo Panadol, tlumí bolest..."
Embeds: "paracetamol tablety 500mg paralen panadol tlumí bolest"
Searches: [HIGH similarity to actual drug descriptions!]
Result: Much better matches! ✨
"""
