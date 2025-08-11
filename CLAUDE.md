# PillSee - Claude Kontextový soubor

## Přehled projektu
PillSee je český medicínský AI asistent, který poskytuje anonymní a přesné informace o lécích. Systém kombinuje oficiální data SÚKL (Státní ústav pro kontrolu léčiv) s AI rozpoznáváním obrazu a zpracováním přirozeného jazyka.

## Architektura
- **Backend**: FastAPI se Supabase PostgreSQL + pgvector
- **Frontend**: Next.js 14 PWA s integrací kamery
- **AI Stack**: OpenAI GPT-4 Vision + GPT-4o-mini s RAG
- **Datový zdroj**: Oficiální otevřená data SÚKL
- **Orchestrace**: LangGraph workflow management

## Klíčové technologie
- Supabase: Cloud PostgreSQL s rozšířením pgvector
- OpenAI API: GPT-4 Vision, GPT-4o-mini, text-embedding-3-small
- FastAPI: Rate limiting, CORS, asynchronní endpointy
- Next.js 14: PWA s offline podporou, kamera API
- LangChain: Zpracování dokumentů a embeddingy
- GDPR compliance: Anonymní relace, žádné sledování uživatelů

## Struktura projektu
```
PillSee/
├── README.md                    # Hlavní dokumentace
├── TERMINOLOGY.md               # Technický architektonický průvodce
├── CLAUDE.md                    # Tento kontextový soubor
├── quick-setup.sh               # Skript pro rychlé nastavení
├── test-supabase-connection.py  # Test připojení k databázi
├── supabase-setup.sql           # Databázové schéma
├── pillsee-backend/             # FastAPI backend
│   ├── README.md                # Dokumentace backendu
│   ├── app/                     # Aplikační kód
│   ├── sukl_data_downloader.py  # Stažení dat SÚKL
│   ├── import_sukl_data.py      # Zpracovací pipeline
│   └── requirements.txt         # Python závislosti
└── pillsee-frontend/            # Next.js PWA frontend
    ├── README.md                # Dokumentace frontendu
    ├── app/                     # Next.js 14 App Router
    ├── components/              # React komponenty
    └── package.json             # Node.js závislosti
```

## Nastavení prostředí
Požadované proměnné prostředí:
- `OPENAI_API_KEY`: Přístup k OpenAI API
- `SUPABASE_URL`: URL projektu Supabase
- `SUPABASE_ANON_KEY`: Anonymní klíč Supabase
- `SUPABASE_SERVICE_KEY`: Service role klíč Supabase
- `NEXT_PUBLIC_API_BASE_URL`: Frontend API endpoint

## Pipeline zpracování dat
1. **Stažení dat SÚKL**: Automatizované získání z oficiálních API
2. **Zpracování dat**: Parsování CSV s podporou českého kódování
3. **Vektorové embeddingy**: OpenAI text-embedding-3-small (512 dimenzí)
4. **Uložení do DB**: Supabase s pgvector podobnostním vyhledáváním
5. **RAG integrace**: LangChain retrieval pro přesné odpovědi

## Klíčové funkce
- Anonymní používání bez registrace
- GPT-4 Vision pro rozpoznání léků z obrázku
- Reálné textové dotazy s RAG nad databází SÚKL
- PWA s offline funkcionalitou
- Ochrana soukromí v souladu s GDPR
- Optimalizace pro český jazyk

## Vývojové příkazy
```bash
# Rychlé nastavení
./quick-setup.sh

# Backend
cd pillsee-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd pillsee-frontend
npm install
npm run dev

# Import dat
cd pillsee-backend
python import_sukl_data.py

# Testování
python test-supabase-connection.py
```

## Důležité soubory
- `pillsee-backend/app/main.py`: Vstupní bod FastAPI aplikace
- `pillsee-backend/app/database/vector_store.py`: Logika vektorového vyhledávání
- `pillsee-backend/app/services/llm_service.py`: Orchestrace AI
- `pillsee-frontend/app/page.tsx`: Hlavní aplikační rozhraní
- `pillsee-frontend/components/CameraCapture.tsx`: Zachytávání obrazu
- `supabase-setup.sql`: Databázové schéma a funkce

## Časté problémy a řešení
1. **Chyby importů modulů**: Zkontrolujte aktivaci virtuálního prostředí
2. **Problémy s připojením k Supabase**: Ověřte proměnné prostředí
3. **Kódování dat SÚKL**: Použijte chardet pro správné české kódování
4. **Nesoulad dimenzí vektoru**: Ujistěte se o 512 dimenzích embeddingu
5. **Instalace PWA**: Testujte v Chrome/Safari pro správné chování

## Zdravotní upozornění
PillSee poskytuje pouze informační obsah a nenahrazuje odbornou lékařskou radu. Všechny odpovědi obsahují patřičná upozornění vyzývající k konzultaci se zdravotnickým pracovníkem.

## Nedávné aktualizace
- Kompletní migrace na cloudovou infrastrukturu Supabase
- Reálná integrace dat SÚKL s automatizovaným stahováním
- Komplexní přepracování dokumentace
- Vylepšené zpracování českého textu se správným kódováním
- Vylepšené zpracování chyb a logování napříč systémem
- Přidány automatizované skripty pro vývojové prostředí

## Další oblasti vývoje
- Zlepšení přesnosti rozpoznávání obrazu
- Rozšířená integrace datových zdrojů SÚKL
- Optimalizace výkonu pro velké datasety
- Pokročilé možnosti filtrování vyhledávání
- Optimalizace nasazení pro mobilní aplikace

## Kritické implementační požadavky

### Medicínská a právní compliance
- **POVINNÁ lékařská upozornění**: Každá odpověď MUSÍ obsahovat upozornění
- **Žádné diagnózy**: Nikdy neposkytujte diagnózy ani doporučení léčby
- **Pouze ověřená data**: Používejte výhradně data SÚKL

### Ochrana soukromí & GDPR
- **Naprostá anonymita**: Žádné sledování nebo uchovávání dat
- **Pouze SessionStorage**: Nikdy localStorage pro anonymní aplikace
- **GDPR compliance**: Explicitní souhlas s cookies

### Specifika českého jazyka
- **Lékařská terminologie**: Správná česká farmaceutická terminologie
- **Diakritika**: Správné zpracování českých znaků (ě, š, č, ř, ž, ý, á, í, é, ů, ú)
- **Kódování dat SÚKL**: CSV soubory používají win-1250 encoding