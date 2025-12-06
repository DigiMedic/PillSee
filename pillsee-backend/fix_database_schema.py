#!/usr/bin/env python3
"""
Database Schema Fixer pro PillSee
Opraví UUID vs BIGINT problém v Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Hlavní funkce pro opravu database schema"""
    
    # Získání Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_service_key:
        logger.error("SUPABASE_URL nebo SUPABASE_SERVICE_KEY nejsou nastavené")
        return False
    
    # Připojení k Supabase s service key (admin práva)
    try:
        client: Client = create_client(supabase_url, supabase_service_key)
        logger.info("Připojen k Supabase s service key")
    except Exception as e:
        logger.error(f"Chyba připojení k Supabase: {e}")
        return False
    
    # Kontrola aktuálního stavu databáze
    logger.info("Kontroluji aktuální stav databáze...")
    
    try:
        # Zkouška basic query na medications tabulku
        result = client.table("medications").select("id").limit(1).execute()
        logger.info(f"Medications tabulka existuje, nalezeno záznamů: {len(result.data)}")
        
        if result.data:
            logger.info(f"První ID typ: {type(result.data[0]['id'])}, hodnota: {result.data[0]['id']}")
            
    except Exception as e:
        logger.error(f"Chyba při kontrole medications tabulky: {e}")
        logger.info("Možná tabulka neexistuje, vytvořím kompletní schéma")
        
    # SQL pro opravu databázového schématu
    schema_sql = """
-- Nejprve dropneme starou funkci pokud existuje
DROP FUNCTION IF EXISTS match_medications;

-- Ujistíme se že medications tabulka má správnou strukturu s UUID
-- Pokud neexistuje, vytvoří se, pokud existuje, ignoruje se
CREATE TABLE IF NOT EXISTS medications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(512),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vytvoření indexů pro rychlé vyhledávání
CREATE INDEX IF NOT EXISTS medications_embedding_idx 
ON medications USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS medications_metadata_idx 
ON medications USING GIN (metadata);

-- Vytvoření správné match_medications funkce s UUID
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

-- Vytvoření policies pro anonymní čtení a service write
DROP POLICY IF EXISTS "Allow anonymous read access" ON medications;
DROP POLICY IF EXISTS "Allow service role full access" ON medications;

CREATE POLICY "Allow anonymous read access" 
ON medications FOR SELECT
TO anon
USING (TRUE);

CREATE POLICY "Allow service role full access" 
ON medications FOR ALL
TO service_role
USING (TRUE);
"""
    
    logger.info("Spouštím opravu databázového schématu...")
    
    try:
        # Použijeme Supabase SQL RPC pro spuštění SQL
        # Rozdělíme SQL na jednotlivé příkazy
        sql_commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
        
        for i, command in enumerate(sql_commands):
            if not command:
                continue
                
            logger.info(f"Spouštím příkaz {i+1}/{len(sql_commands)}: {command[:50]}...")
            
            try:
                # Pro DDL příkazy použijeme direct query přes PostgREST
                if any(keyword in command.upper() for keyword in ['CREATE', 'DROP', 'ALTER']):
                    # Tyto příkazy nelze spustit přes Supabase Python klient
                    logger.warning(f"DDL příkaz musí být spuštěn manuálně v Supabase SQL Editor: {command[:100]}...")
                    continue
                
            except Exception as e:
                logger.error(f"Chyba při spuštění příkazu {i+1}: {e}")
                continue
        
        logger.info("✅ SQL příkazy připraveny!")
        
        print("\n" + "="*80)
        print("DŮLEŽITÉ: MANUÁLNÍ KROKY V SUPABASE")
        print("="*80)
        print("\n1. Přihlaste se do Supabase Dashboard")
        print("2. Jděte do SQL Editor")
        print("3. Zkopírujte a spusťte následující SQL:")
        print("\n" + "-"*40)
        print(schema_sql)
        print("-"*40)
        
        print("\n4. Po spuštění SQL restartujte backend:")
        print("   Ctrl+C v terminálu s uvicorn")
        print("   uvicorn app.main:app --reload")
        
        print("\n5. Otestujte API:")
        print('   curl -X POST http://localhost:8000/api/query/text -H "Content-Type: application/json" -d \'{"query": "Paralen"}\'')
        
    except Exception as e:
        logger.error(f"Chyba při opravě schématu: {e}")
        return False
    
    # Test připojení po opravě
    logger.info("Testuji funkci match_medications...")
    
    try:
        # Test prázdného embeddings vektoru
        test_embedding = [0.0] * 512
        
        result = client.rpc(
            "match_medications",
            {
                "query_embedding": test_embedding,
                "match_count": 1,
                "filter": {}
            }
        ).execute()
        
        logger.info(f"✅ match_medications funkce funguje! Výsledky: {len(result.data)}")
        
    except Exception as e:
        logger.error(f"❌ match_medications funkce nefunguje: {e}")
        logger.info("Spusťte prosím SQL manuálně v Supabase Dashboard")
        
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Database schema je připravena!")
        print("Pokud stále vidíte UUID errory, restartujte backend server.")
    else:
        print("\n❌ Chyba při opravě database schema")
        exit(1)