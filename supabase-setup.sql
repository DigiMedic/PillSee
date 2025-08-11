-- PillSee - Supabase databázové schéma
-- Spusťte tento SQL v Supabase SQL Editor

-- 1. Povolení pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Tabulka pro léková data
CREATE TABLE IF NOT EXISTS medications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(512),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Index pro rychlejší similarity search
CREATE INDEX IF NOT EXISTS medications_embedding_idx 
ON medications USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Index na metadata pro rychlejší filtrování
CREATE INDEX IF NOT EXISTS medications_metadata_idx 
ON medications USING GIN (metadata);

-- 5. Funkce pro similarity search
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

-- 6. RLS (Row Level Security) pro anonymní přístup
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;

-- 7. Policy pro anonymní čtení
CREATE POLICY "Allow anonymous read access" 
ON medications FOR SELECT
TO anon
USING (TRUE);

-- 8. Policy pro service role write access
CREATE POLICY "Allow service role full access" 
ON medications FOR ALL
TO service_role
USING (TRUE);

-- Hotovo! Databáze je připravená pro PillSee aplikaci