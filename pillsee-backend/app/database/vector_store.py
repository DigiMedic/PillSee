"""
PostgreSQL Vector Store - RAG implementace pro česká léková data
Využívá pgvector extension pro similarity search s Supabase klientem
"""

from supabase import create_client, Client
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain.schema import Document
import os
import logging
from typing import List, Dict, Any, Optional

from ..models import MedicationInfo

logger = logging.getLogger(__name__)

class MedicationVectorStore:
    """Vector store pro léková data s českým obsahem"""
    
    def __init__(self):
        """Inicializace PostgreSQL vector store přes Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL a SUPABASE_ANON_KEY environment variables musí být nastavené"
            )
        
        # Inicializace PostgreSQL klienta přes Supabase (anon pro čtení)
        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            
            # Service klient pro zápis (pokud je k dispozici)
            if self.service_key:
                self.service_client: Client = create_client(self.supabase_url, self.service_key)
                logger.info("PostgreSQL database klient inicializován s service key")
            else:
                self.service_client = self.client
                logger.warning("SUPABASE_SERVICE_KEY není nastavená, používám anon key pro vše")
            
            logger.info("PostgreSQL database klient inicializován úspěšně")
        except Exception as e:
            logger.error(f"Chyba při inicializaci database klienta: {e}")
            raise
        
        # OpenAI embeddings pro český text
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Menší model, rychlejší a levnější
            dimensions=512  # Optimální pro medical use case
        )
        
        # Názvy tabulek
        self.table_name = "medications"
        self.query_name = "match_medications"
        
    def setup_vector_store(self) -> SupabaseVectorStore:
        """
        Inicializace pgvector store pro léková data
        
        Returns:
            SupabaseVectorStore: Wrapper pro PostgreSQL pgvector
        """
        try:
            vector_store = SupabaseVectorStore(
                client=self.client,
                embedding=self.embeddings,
                table_name=self.table_name,
                query_name=self.query_name
            )
            logger.info(f"Vector store nastaven pro tabulku: {self.table_name}")
            return vector_store
            
        except Exception as e:
            logger.error(f"Chyba při nastavení vector store: {e}")
            raise
    
    def create_database_schema(self):
        """
        Vytvoří databázové schéma pro vector store (SQL commands)
        
        Note: Tyto SQL příkazy je potřeba spustit v PostgreSQL databázi s pgvector extension
        """
        schema_sql = """
        -- Povolení pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Tabulka pro léková data
        CREATE TABLE IF NOT EXISTS medications (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            content TEXT NOT NULL,
            metadata JSONB,
            embedding VECTOR(512),
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Index pro rychlejší similarity search
        CREATE INDEX IF NOT EXISTS medications_embedding_idx 
        ON medications USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        
        -- Index na metadata pro rychlejší filtrování
        CREATE INDEX IF NOT EXISTS medications_metadata_idx 
        ON medications USING GIN (metadata);
        
        -- Funkce pro similarity search
        CREATE OR REPLACE FUNCTION match_medications(
            query_embedding VECTOR(512),
            match_count INT DEFAULT 5,
            filter JSONB DEFAULT '{}'
        )
        RETURNS TABLE(
            id UUID,
            content TEXT,
            metadata JSONB,
            similarity FLOAT
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RETURN QUERY
            SELECT
                medications.id,
                medications.content,
                medications.metadata,
                1 - (medications.embedding <=> query_embedding) AS similarity
            FROM medications
            WHERE 
                CASE 
                    WHEN filter = '{}' THEN TRUE
                    ELSE medications.metadata @> filter
                END
            ORDER BY medications.embedding <=> query_embedding
            LIMIT match_count;
        END;
        $$;
        
        -- RLS (Row Level Security) pro anonymní přístup
        ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
        
        -- Policy pro anonymní čtení
        CREATE POLICY "Allow anonymous read access" 
        ON medications FOR SELECT
        TO anon
        USING (TRUE);
        
        -- Policy pro service role write access
        CREATE POLICY "Allow service role full access" 
        ON medications FOR ALL
        TO service_role
        USING (TRUE);
        """
        
        logger.info("SQL schéma pro vector store:")
        print(schema_sql)
        return schema_sql
    
    def ingest_sukl_data(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Ingest dat SÚKL do vector databáze
        
        Args:
            documents: Seznam dokumentů s content a metadata
            
        Returns:
            bool: True pokud úspěšné
        """
        if not documents:
            logger.warning("Žádné dokumenty k ingestu")
            return False
            
        logger.info(f"Začínám ingest {len(documents)} dokumentů")
        
        try:
            # Pokusíme se o přímé vložení, aby se vyhnuli problémům s LangChain SupabaseVectorStore
            return self._direct_bulk_insert(documents)
            
        except Exception as e:
            logger.error(f"Chyba při ingestu dat: {e}")
            return False
    
    def _direct_bulk_insert(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Přímé vložení dokumentů do databáze pomocí Supabase klienta
        """
        try:
            # Batch zpracování embeddings
            texts = [doc["content"] for doc in documents]
            embeddings = self.embeddings.embed_documents(texts)
            
            # Příprava záznamů pro vložení
            records = []
            for i, doc in enumerate(documents):
                record = {
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "embedding": embeddings[i]  # Supabase automaticky převede na vector
                }
                records.append(record)
            
            # Bulk insert do Supabase s service key
            result = self.service_client.table(self.table_name).insert(records).execute()
            
            if result.data:
                logger.info(f"Úspěšně vloženo {len(result.data)} záznamů")
                return True
            else:
                logger.error("Vložení se nepodařilo - žádná data vrácena")
                return False
                
        except Exception as e:
            logger.error(f"Chyba při přímém vložení: {e}")
            return False
    
    def search_medications(
        self, 
        query: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Vyhledání léků podle textového dotazu
        
        Args:
            query: Textový dotaz
            limit: Počet výsledků
            similarity_threshold: Minimální similarity score
            filters: Metadata filtry
            
        Returns:
            List[Dict]: Seznam nalezených léků s similarity scores
        """
        if not query.strip():
            logger.warning("Prázdný search query")
            return []
        
        try:
            logger.info(f"Hledám: '{query}' (limit: {limit})")
            
            # Použití přímé metody místo LangChain wrapper
            return self._direct_similarity_search(query, limit, similarity_threshold, filters)
            
        except Exception as e:
            logger.error(f"Chyba při vyhledávání: {e}")
            return []
    
    def _direct_similarity_search(
        self, 
        query: str, 
        limit: int, 
        similarity_threshold: float,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Přímé vyhledávání pomocí Supabase match_medications funkce
        """
        try:
            # Vytvoření embeddingu pro query
            query_embedding = self.embeddings.embed_query(query)
            
            # Volání match_medications funkce
            rpc_result = self.client.rpc(
                self.query_name,
                {
                    "query_embedding": query_embedding,
                    "match_count": limit,
                    "filter": filters or {}
                }
            ).execute()
            
            if not rpc_result.data:
                logger.info("Žádné výsledky nalezeny")
                return []
            
            # Zpracování výsledků
            results = []
            for row in rpc_result.data:
                similarity = row.get("similarity", 0.0)
                
                # Filtrování podle threshold
                if similarity >= similarity_threshold:
                    result = {
                        "id": row.get("id"),
                        "content": row.get("content", ""),
                        "metadata": row.get("metadata", {}),
                        "similarity": similarity
                    }
                    results.append(result)
            
            logger.info(f"Nalezeno {len(results)} výsledků nad threshold {similarity_threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Chyba při přímém vyhledávání: {e}")
            return []
    
    def search_by_name(self, medication_name: str) -> List[Dict[str, Any]]:
        """
        Vyhledání konkrétního léku podle názvu
        
        Args:
            medication_name: Název léku
            
        Returns:
            List[Dict]: Nalezené léky
        """
        return self.search_medications(
            query=f"název {medication_name}",
            limit=10,
            similarity_threshold=0.6
        )
    
    def search_by_active_ingredient(self, active_ingredient: str) -> List[Dict[str, Any]]:
        """
        Vyhledání léků podle účinné látky
        
        Args:
            active_ingredient: Účinná látka
            
        Returns:
            List[Dict]: Léky se stejnou účinnou látkou
        """
        return self.search_medications(
            query=f"účinná látka {active_ingredient}",
            limit=15,
            similarity_threshold=0.7
        )
    
    def validate_medication_info(self, vision_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validace informací rozpoznaných z obrázku proti databázi
        
        Args:
            vision_result: Výsledek z GPT-4 Vision
            
        Returns:
            Dict: Obohacené informace s validací
        """
        if not vision_result.get("name") or vision_result["name"] == "není viditelné":
            logger.info("Chybí název pro validaci")
            return vision_result
        
        logger.info(f"Validuji rozpoznaný lék: {vision_result['name']}")
        
        # Vyhledání v databázi
        search_query = vision_result["name"]
        if vision_result.get("active_ingredient", "") != "není viditelné":
            search_query += f" {vision_result['active_ingredient']}"
            
        matches = self.search_medications(
            query=search_query,
            limit=3,
            similarity_threshold=0.6
        )
        
        if matches:
            logger.info(f"Nalezeno {len(matches)} shod v SÚKL databázi")
            vision_result["sukl_matches"] = [match["metadata"] for match in matches]
            vision_result["validated"] = True
            
            # Použití nejlepší shody pro obohacení
            best_match = matches[0]
            best_metadata = best_match["metadata"]
            
            # Obohacení informací z databáze
            for key, value in best_metadata.items():
                if key not in vision_result or vision_result[key] == "není viditelné":
                    vision_result[key] = value
                    
        else:
            logger.warning(f"Lék nebyl nalezen v databázi: {vision_result['name']}")
            vision_result["validated"] = False
            vision_result["warning"] = "Lék nebyl nalezen v databázi SÚKL. Ověřte správnost informací."
            
        return vision_result
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Statistiky databáze
        
        Returns:
            Dict: Základní statistiky
        """
        try:
            # Query pro počet dokumentů
            result = self.client.table(self.table_name).select("id", count="exact").execute()
            
            return {
                "total_medications": result.count,
                "status": "connected",
                "table_name": self.table_name
            }
            
        except Exception as e:
            logger.error(f"Chyba při získání statistik: {e}")
            return {
                "total_medications": 0,
                "status": "error",
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, str]:
        """
        Health check pro vector store
        
        Returns:
            Dict: Status připojení
        """
        try:
            # Jednoduchý test připojení
            self.client.table(self.table_name).select("id").limit(1).execute()
            return {"status": "healthy", "connection": "ok"}
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}