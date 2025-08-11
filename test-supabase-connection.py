#!/usr/bin/env python3
"""
Test Supabase připojení pro PillSee projekt s SÚKL daty
"""

import os
from supabase import create_client, Client
from langchain.vectorstores import SupabaseVectorStore
from langchain.embeddings import OpenAIEmbeddings

def test_supabase_connection():
    """Test základního připojení k Supabase"""
    
    # Environment proměnné
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ CHYBA: Nastavte SUPABASE_URL a SUPABASE_ANON_KEY environment proměnné")
        return False
    
    print(f"🔍 Testuji připojení k: {supabase_url}")
    
    try:
        # Vytvoření klienta
        client = create_client(supabase_url, supabase_key)
        print("✅ Supabase klient vytvořen úspěšně")
        
        # Test připojení
        result = client.table("medications").select("id").limit(1).execute()
        print("✅ Připojení k databázi funguje")
        print(f"📊 Počet léků v databázi: {len(result.data) if result.data else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ CHYBA při připojení: {e}")
        return False

def test_vector_store():
    """Test pgvector functionality"""
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ CHYBA: Nastavte OPENAI_API_KEY environment proměnnou")
        return False
    
    try:
        # Vytvoření embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=512
        )
        print("✅ OpenAI embeddings inicializovány")
        
        # Test embeddings
        test_text = "test embedding"
        embedding = embeddings.embed_query(test_text)
        print(f"✅ Test embedding: {len(embedding)} dimenzí")
        
        return True
        
    except Exception as e:
        print(f"❌ CHYBA při testování vector store: {e}")
        return False

def test_full_integration():
    """Test plné integrace Supabase + pgvector"""
    
    try:
        from pillsee_backend.app.database.vector_store import MedicationVectorStore
        
        # Inicializace vector store
        vector_store = MedicationVectorStore()
        print("✅ MedicationVectorStore inicializován")
        
        # Health check
        health = vector_store.health_check()
        print(f"🏥 Health check: {health}")
        
        # Stats
        stats = vector_store.get_database_stats()
        print(f"📈 Databázové statistiky: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ CHYBA při plné integraci: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PillSee - Test Supabase připojení")
    print("=" * 50)
    
    # Test 1: Základní připojení
    print("\n1️⃣ Test základního připojení...")
    connection_ok = test_supabase_connection()
    
    # Test 2: Vector store
    print("\n2️⃣ Test vector store...")
    vector_ok = test_vector_store()
    
    # Test 3: Plná integrace
    print("\n3️⃣ Test plné integrace...")
    integration_ok = test_full_integration()
    
    # Výsledek
    print("\n" + "=" * 50)
    if connection_ok and vector_ok and integration_ok:
        print("🎉 Všechny testy prošly! Supabase je připravený k použití.")
    else:
        print("⚠️  Některé testy selhaly. Zkontrolujte konfiguraci.")
    
    print("\n💡 Další kroky:")
    print("1. Spusťte SQL setup v Supabase SQL Editoru")
    print("2. Naimportujte SÚKL data")
    print("3. Otestujte aplikaci")