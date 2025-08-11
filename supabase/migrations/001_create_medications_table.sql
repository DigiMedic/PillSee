-- Create medications table for vector embeddings
CREATE TABLE medications (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    active_ingredient TEXT,
    strength TEXT,
    form TEXT,
    manufacturer TEXT,
    registration_number TEXT,
    indication TEXT,
    contraindication TEXT,
    side_effects TEXT,
    interactions TEXT,
    dosage TEXT,
    prescription_required BOOLEAN DEFAULT FALSE,
    content TEXT NOT NULL, -- Combined text for embedding
    embedding VECTOR(512), -- OpenAI text-embedding-3-small dimension
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX medications_embedding_idx ON medications 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Create text search index
CREATE INDEX medications_name_idx ON medications (name);
CREATE INDEX medications_active_ingredient_idx ON medications (active_ingredient);
CREATE INDEX medications_content_gin_idx ON medications USING gin(to_tsvector('simple', content));

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_medications(
    query_embedding VECTOR(512),
    match_threshold FLOAT DEFAULT 0.6,
    match_count INT DEFAULT 5
)
RETURNS TABLE(
    id BIGINT,
    name TEXT,
    active_ingredient TEXT,
    strength TEXT,
    form TEXT,
    manufacturer TEXT,
    indication TEXT,
    contraindication TEXT,
    side_effects TEXT,
    interactions TEXT,
    dosage TEXT,
    prescription_required BOOLEAN,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        medications.id,
        medications.name,
        medications.active_ingredient,
        medications.strength,
        medications.form,
        medications.manufacturer,
        medications.indication,
        medications.contraindication,
        medications.side_effects,
        medications.interactions,
        medications.dosage,
        medications.prescription_required,
        medications.content,
        medications.metadata,
        1 - (medications.embedding <=> query_embedding) AS similarity
    FROM medications
    WHERE 1 - (medications.embedding <=> query_embedding) > match_threshold
    ORDER BY medications.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Create RLS policies for security
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;

-- Allow anonymous read access (for public app)
CREATE POLICY "Allow anonymous read access" ON medications
FOR SELECT USING (true);

-- Pro lokální vývoj - bez autorizace
-- CREATE POLICY "Only service role can modify" ON medications
-- FOR ALL USING (auth.role() = 'service_role');

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_medications_updated_at
    BEFORE UPDATE ON medications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();