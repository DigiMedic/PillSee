# PillSee Backend

FastAPI backend pro PillSee - anonymní český AI asistent pro informace o lécích.

## 🏗️ Architektura

- **FastAPI** - Moderní Python web framework
- **LangGraph** - AI workflow orchestrace pro text a obrázky  
- **OpenAI GPT-4** - Vision pro rozpoznání léků, GPT-4o-mini pro textové dotazy
- **Supabase** - Managed PostgreSQL s pgvector pro vector search
- **SÚKL Integration** - Oficiální databáze českých léčiv

## 🚀 Instalace a spuštění

### Prerekvizity
- Python 3.9+
- Supabase účet ([supabase.com](https://supabase.com))
- OpenAI API klíč

### Setup

```bash
# Vytvoření virtuálního prostředí
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalace závislostí
pip install -r requirements.txt
pip install chardet requests  # Pro SÚKL data processing

# Environment proměnné
cp .env.example .env
# Upravte .env s vašimi klíči
```

### Environment proměnné (.env)

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Supabase Cloud
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Rate Limiting
TEXT_QUERY_LIMIT=10/minute
IMAGE_QUERY_LIMIT=5/minute

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://pillsee.vercel.app
```

## 📊 SÚKL Data Import

### Automatický import

```bash
# Aktivace environment
source venv/bin/activate
export $(grep -v '^#' .env | xargs)

# Spuštění automatického importu
python import_sukl_data.py
```

**Co se děje:**
1. 🔍 **Discovery** - Hledá dostupné SÚKL datasety na opendata.sukl.cz
2. 📥 **Download** - Stahuje CSV/JSON data z oficiálních zdrojů
3. 🧹 **Processing** - Zpracovává česká kódování (UTF-8, Windows-1250)
4. 🤖 **Embeddings** - Generuje vector embeddings pomocí OpenAI
5. 💾 **Import** - Ukládá do Supabase PostgreSQL s pgvector

### Manuální testování

```bash
# Test stahování dat
python sukl_data_downloader.py

# Test Supabase připojení
python ../test-supabase-connection.py
```

## 🔌 API Endpointy

### Health Check
```http
GET /health
```
Vrací stav služby a připojených dependencí.

### Textový dotaz
```http
POST /api/query/text
Content-Type: application/json

{
  "query": "Co je to Paralen a jak se užívá?"
}
```

### Rozpoznání léku z obrázku
```http
POST /api/query/image
Content-Type: application/json

{
  "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

## 📁 Struktura kódu

```
pillsee-backend/
├── app/
│   ├── main.py                    # FastAPI aplikace + CORS
│   ├── config.py                  # Pydantic settings
│   ├── models.py                  # Pydantic modely
│   ├── ai/
│   │   ├── image_processor.py     # GPT-4 Vision pro obrázky
│   │   ├── text_processor.py      # RAG pro textové dotazy
│   │   └── vision_processor.py    # Rozpoznávání léků
│   ├── data/
│   │   └── sukl_processor.py      # SÚKL data processing
│   ├── database/
│   │   └── vector_store.py        # Supabase vector operations
│   └── workflows/
│       └── medication_workflow.py # LangGraph orchestrace
├── tests/                         # Pytest testy
├── import_sukl_data.py           # SÚKL data import script
├── sukl_data_downloader.py       # Pokročilý data downloader
└── requirements.txt               # Python závislosti
```

## 🧪 Testování

```bash
# Spuštění všech testů
python -m pytest tests/ -v

# Spuštění s coverage
python -m pytest tests/ --cov=app --cov-report=html

# Konkrétní test
python -m pytest tests/test_sukl_processor.py -v
```

## 🔄 LangGraph Workflow

Backend používá LangGraph pro orchestraci AI workflow:

1. **Route Detection** - Rozhoduje mezi text/image processing
2. **Preprocessing** - Validace a příprava dat  
3. **AI Processing** - GPT-4 Vision nebo RAG s SÚKL databází
4. **Validation** - Křížová kontrola výsledků
5. **Enhancement** - Obohacení o detailní informace
6. **Response** - Formatování s bezpečnostními disclaimery

## 🗄️ Databázová integrace

### Supabase PostgreSQL + pgvector
- **medications tabulka** - České léky s OpenAI embeddings
- **Vector similarity** - Cosine similarity search
- **Match funkce** - Optimalizované PostgreSQL funkce
- **RLS Security** - Anonymní přístup s row-level security

### SÚKL Data Schema
```python
MedicationInfo:
  - name: str              # Název léku
  - active_ingredient: str # Účinná látka  
  - strength: str          # Síla
  - form: str             # Léková forma
  - manufacturer: str     # Výrobce
  - indication: str       # Indikace
  - contraindication: str # Kontraindikace
  - side_effects: str     # Nežádoucí účinky
  - dosage: str          # Dávkování
  - price: str           # Cena
```

## 🔒 Bezpečnost

- **Rate Limiting** - SlowAPI middleware pro IP-based ochranu
- **CORS** - Konfigurované origins pro frontend
- **Input Validation** - Pydantic modely pro všechny endpointy  
- **Error Handling** - Structured logging bez exposure citlivých dat
- **Medical Disclaimers** - Povinné bezpečnostní upozornění

## 🐳 Docker

```bash
# Build image
docker build -t pillsee-backend .

# Spuštění s Supabase
docker run -d \
  --name pillsee-backend \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_key \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_ANON_KEY=your_anon_key \
  -e SUPABASE_SERVICE_KEY=your_service_key \
  pillsee-backend
```

## 🔧 Development

### Přidání nového AI procesu

1. Vytvořte modul v `app/ai/`
2. Implementujte processing funkci
3. Přidejte do LangGraph workflow v `app/workflows/`
4. Vytvořte testy v `tests/`

### Debugging

```bash
# Debug režim
PYTHONPATH=. python -m uvicorn app.main:app --reload --log-level debug

# API dokumentace
open http://localhost:8000/docs
```

### SÚKL Data Processing

```bash
# Test jednotlivých komponent
python -c "from app.data.sukl_processor import SUKLDataProcessor; p = SUKLDataProcessor(); print('OK')"

# Vytvoření nového datasetu
python sukl_data_downloader.py

# Reprocessing existujících dat
python -c "
from app.data.sukl_processor import SUKLDataProcessor
p = SUKLDataProcessor()
df = p.load_sukl_csv('data/sukl_data.csv')
meds = p.extract_medication_info(df)
print(f'Zpracováno {len(meds)} léků')
"
```

## 📊 Monitoring

Backend poskytuje structured JSON logy:
- Request/Response times
- Error tracking s kontextem  
- AI model usage metrics
- Database query performance
- SÚKL data processing statistiky

## 🌐 Production Deployment

### Railway / Fly.io
```bash
# Environment proměnné
OPENAI_API_KEY=your_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Post-deployment checklist
1. ✅ Health endpoint responds
2. ✅ SÚKL data imported
3. ✅ Text queries working  
4. ✅ Image processing functional
5. ✅ Rate limiting active
6. ✅ CORS properly configured

---

**💊 PillSee Backend** - Robustní AI backend pro českou lékovou databázi.