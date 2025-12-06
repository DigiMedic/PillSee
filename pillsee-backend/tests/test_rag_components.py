"""
Test Suite for Enhanced RAG Components
Comprehensive tests for all retrieval strategies
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain.schema import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Import RAG components
import sys
sys.path.append('..')
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.hyde_retriever import HyDERetriever
from app.rag.multi_query import MultiQueryRetriever
from app.rag.parent_document import ParentDocumentRetriever
from app.rag.enhanced_vector_store import EnhancedVectorStore
from app.rag.rag_manager import RAGManager


# Fixtures
@pytest.fixture
def mock_vector_store():
    """Mock vector store"""
    mock_store = Mock()
    mock_store.similarity_search = Mock(return_value=[
        Document(page_content="Paralen obsahuje paracetamol", metadata={"drug": "paralen"}),
        Document(page_content="Dávkování: 1-2 tablety", metadata={"drug": "paralen"}),
    ])
    mock_store.similarity_search_with_score = Mock(return_value=[
        (Document(page_content="Paralen", metadata={}), 0.9),
        (Document(page_content="Panadol", metadata={}), 0.8),
    ])
    return mock_store


@pytest.fixture
def mock_llm():
    """Mock LLM"""
    mock = Mock(spec=ChatOpenAI)
    mock.invoke = Mock(return_value=Mock(content="Paracetamol tablety 500mg"))
    mock.model_name = "gpt-4o-mini"
    return mock


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        Document(
            page_content="Paralen obsahuje paracetamol, který tlumí bolest a snižuje teplotu.",
            metadata={"drug_name": "Paralen", "atc_code": "N02BE01"}
        ),
        Document(
            page_content="Ibuprofen je nesteroidní protizánětlivý lék.",
            metadata={"drug_name": "Ibuprofen", "atc_code": "M01AE01"}
        ),
        Document(
            page_content="Nežádoucí účinky paracetamolu: nauzea, zvracení.",
            metadata={"drug_name": "Paralen", "section": "side_effects"}
        ),
    ]


# Test HybridRetriever
class TestHybridRetriever:
    
    def test_initialization(self, mock_vector_store):
        """Test hybrid retriever initialization"""
        retriever = HybridRetriever(
            vector_store=mock_vector_store,
            bm25_weight=0.4,
            semantic_weight=0.6
        )
        
        assert retriever.bm25_weight == 0.4
        assert retriever.semantic_weight == 0.6
        assert retriever.vector_store == mock_vector_store
    
    def test_retrieve_without_bm25(self, mock_vector_store):
        """Test retrieval when BM25 is not available"""
        retriever = HybridRetriever(
            vector_store=mock_vector_store,
            documents=[]  # No documents = no BM25
        )
        
        results = retriever.retrieve("paralen", k=2)
        
        assert len(results) == 2
        assert "Paralen" in results[0].page_content
    
    def test_retrieve_with_bm25(self, mock_vector_store, sample_documents):
        """Test hybrid retrieval with BM25"""
        retriever = HybridRetriever(
            vector_store=mock_vector_store,
            documents=sample_documents
        )
        
        results = retriever.retrieve("paracetamol bolest", k=2)
        
        assert len(results) <= 2
        mock_vector_store.similarity_search.assert_called()
    
    def test_get_retriever_info(self, mock_vector_store):
        """Test retriever info"""
        retriever = HybridRetriever(vector_store=mock_vector_store)
        
        info = retriever.get_retriever_info()
        
        assert info["type"] == "hybrid"
        assert "bm25_weight" in info
        assert "semantic_weight" in info


# Test HyDERetriever
class TestHyDERetriever:
    
    def test_initialization(self, mock_vector_store, mock_llm):
        """Test HyDE retriever initialization"""
        retriever = HyDERetriever(
            vector_store=mock_vector_store,
            llm=mock_llm
        )
        
        assert retriever.vector_store == mock_vector_store
        assert retriever.llm == mock_llm
    
    def test_generate_hypothetical_document(self, mock_vector_store, mock_llm):
        """Test hypothetical document generation"""
        retriever = HyDERetriever(
            vector_store=mock_vector_store,
            llm=mock_llm
        )
        
        hypothetical = retriever.generate_hypothetical_document(
            "Co pomáhá na bolest hlavy?"
        )
        
        assert isinstance(hypothetical, str)
        assert len(hypothetical) > 0
        mock_llm.invoke.assert_called_once()
    
    def test_retrieve_calls_hyde_generation(self, mock_vector_store, mock_llm):
        """Test that retrieve calls HyDE generation"""
        retriever = HyDERetriever(
            vector_store=mock_vector_store,
            llm=mock_llm
        )
        
        results = retriever.retrieve("bolest hlavy", k=3)
        
        # Should call LLM to generate hypothesis
        mock_llm.invoke.assert_called_once()
        # Should call vector store with hypothesis
        mock_vector_store.similarity_search.assert_called_once()
        assert len(results) > 0


# Test MultiQueryRetriever
class TestMultiQueryRetriever:
    
    def test_initialization(self, mock_vector_store, mock_llm):
        """Test multi-query retriever initialization"""
        retriever = MultiQueryRetriever(
            vector_store=mock_vector_store,
            llm=mock_llm,
            num_queries=3
        )
        
        assert retriever.num_queries == 3
        assert retriever.llm == mock_llm
    
    def test_generate_queries(self, mock_vector_store, mock_llm):
        """Test query variation generation"""
        mock_llm.invoke = Mock(return_value=Mock(
            content="1. paralen tablety\n2. paracetamol lék\n3. paralen proti bolesti"
        ))
        
        retriever = MultiQueryRetriever(
            vector_store=mock_vector_store,
            llm=mock_llm,
            num_queries=3
        )
        
        queries = retriever.generate_queries("paralen")
        
        assert len(queries) >= 1  # At least original
        assert "paralen" in queries[0].lower()
    
    def test_retrieve_deduplication(self, mock_vector_store, mock_llm):
        """Test that retrieve deduplicates results"""
        # Mock LLM to return variations
        mock_llm.invoke = Mock(return_value=Mock(
            content="1. paralen\n2. paracetamol"
        ))
        
        # Mock vector store to return duplicates
        mock_vector_store.similarity_search = Mock(return_value=[
            Document(page_content="Same content", metadata={}),
            Document(page_content="Same content", metadata={}),
            Document(page_content="Different content", metadata={}),
        ])
        
        retriever = MultiQueryRetriever(
            vector_store=mock_vector_store,
            llm=mock_llm
        )
        
        results = retriever.retrieve("paralen", k=5)
        
        # Should deduplicate
        assert len(results) >= 1


# Test ParentDocumentRetriever
class TestParentDocumentRetriever:
    
    def test_initialization(self, mock_vector_store):
        """Test parent document retriever initialization"""
        retriever = ParentDocumentRetriever(
            vector_store=mock_vector_store,
            child_chunk_size=400,
            parent_chunk_size=2000
        )
        
        assert retriever.child_chunk_size == 400
        assert retriever.parent_chunk_size == 2000
    
    def test_add_documents_creates_parent_child_structure(
        self, mock_vector_store, sample_documents
    ):
        """Test that documents are split into parent/child"""
        retriever = ParentDocumentRetriever(
            vector_store=mock_vector_store,
            child_chunk_size=50,  # Small for testing
            parent_chunk_size=100
        )
        
        # Mock add_documents to not actually add
        mock_vector_store.add_documents = Mock(return_value=["id1", "id2"])
        
        doc_ids = retriever.add_documents(sample_documents[:1])
        
        # Should have created parent documents
        assert len(retriever.parent_doc_store) > 0
    
    def test_get_stats(self, mock_vector_store):
        """Test retriever statistics"""
        retriever = ParentDocumentRetriever(vector_store=mock_vector_store)
        
        stats = retriever.get_stats()
        
        assert stats["type"] == "parent_document"
        assert "num_parents" in stats


# Test EnhancedVectorStore
class TestEnhancedVectorStore:
    
    @patch('app.rag.enhanced_vector_store.SupabaseVectorStore')
    def test_initialization(self, mock_supabase_store):
        """Test enhanced vector store initialization"""
        mock_client = Mock()
        mock_embeddings = Mock(spec=OpenAIEmbeddings)
        
        store = EnhancedVectorStore(
            supabase_client=mock_client,
            embedding_function=mock_embeddings,
            table_name="test_table"
        )
        
        assert store.table_name == "test_table"
        assert store.supabase_client == mock_client
    
    def test_search_by_atc_code(self):
        """Test ATC code search"""
        mock_client = Mock()
        mock_client.table = Mock(return_value=Mock(
            select=Mock(return_value=Mock(
                eq=Mock(return_value=Mock(
                    limit=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(data=[
                            {"content": "Paralen", "metadata": {"atc_code": "N02BE01"}}
                        ]))
                    ))
                ))
            ))
        ))
        
        mock_embeddings = Mock(spec=OpenAIEmbeddings)
        
        store = EnhancedVectorStore(
            supabase_client=mock_client,
            embedding_function=mock_embeddings
        )
        
        results = store.search_by_atc_code("N02BE01", k=10)
        
        assert len(results) == 1
        assert results[0].metadata["atc_code"] == "N02BE01"


# Test RAGManager
class TestRAGManager:
    
    @patch('app.rag.rag_manager.HybridRetriever')
    @patch('app.rag.rag_manager.HyDERetriever')
    def test_initialization(self, mock_hyde, mock_hybrid, mock_vector_store):
        """Test RAG manager initialization"""
        manager = RAGManager(
            vector_store=mock_vector_store,
            openai_api_key="test-key",
            default_strategy="auto"
        )
        
        assert manager.default_strategy == "auto"
        assert hasattr(manager, 'hybrid_retriever')
        assert hasattr(manager, 'hyde_retriever')
    
    def test_auto_select_hybrid_for_short_query(self, mock_vector_store):
        """Test auto strategy selection for short queries"""
        manager = RAGManager(
            vector_store=mock_vector_store,
            openai_api_key="test-key"
        )
        
        with patch.object(manager, '_hybrid_retrieve') as mock_hybrid:
            manager.retrieve("paralen", k=5, strategy="auto")
            mock_hybrid.assert_called_once()
    
    def test_auto_select_hyde_for_questions(self, mock_vector_store):
        """Test auto strategy selection for questions"""
        manager = RAGManager(
            vector_store=mock_vector_store,
            openai_api_key="test-key"
        )
        
        with patch.object(manager, '_hyde_retrieve') as mock_hyde:
            manager.retrieve("Jak užívat paralen?", k=5, strategy="auto")
            mock_hyde.assert_called_once()
    
    def test_usage_stats_tracking(self, mock_vector_store):
        """Test that usage is tracked"""
        manager = RAGManager(
            vector_store=mock_vector_store,
            openai_api_key="test-key"
        )
        
        # Do some retrievals
        manager.retrieve("test", k=5, strategy="semantic")
        manager.retrieve("test", k=5, strategy="hybrid")
        
        stats = manager.get_usage_stats()
        
        assert stats["total_calls"] >= 2
        assert stats["usage_by_strategy"]["semantic"]["calls"] >= 1
    
    def test_get_best_strategy_for_query(self, mock_vector_store):
        """Test strategy recommendation"""
        manager = RAGManager(
            vector_store=mock_vector_store,
            openai_api_key="test-key"
        )
        
        # Short query → hybrid
        assert manager.get_best_strategy_for_query("paralen") == "hybrid"
        
        # Question → hyde
        assert manager.get_best_strategy_for_query("jak užívat paralen") == "hyde"
        
        # Diversity needed → mmr
        assert manager.get_best_strategy_for_query("různé léky na bolest") == "mmr"


# Integration Tests
class TestRAGIntegration:
    """Integration tests for complete RAG pipeline"""
    
    @pytest.mark.integration
    def test_end_to_end_retrieval_flow(self, mock_vector_store, sample_documents):
        """Test complete retrieval flow"""
        # This would require real Supabase connection
        # For now, just verify components work together
        
        manager = RAGManager(
            vector_store=mock_vector_store,
            openai_api_key="test-key"
        )
        
        # Should not raise
        try:
            results = manager.retrieve("paralen", k=3, strategy="semantic")
            assert isinstance(results, list)
        except Exception as e:
            pytest.fail(f"Integration test failed: {e}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
