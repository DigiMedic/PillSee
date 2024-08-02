# PillSee

![PillSee Logo](https://i.ibb.co/z4SpKPp/Pill-See-cover.png)

PillSee je inovativní AI-powered chatovací platforma zaměřená na poskytování přesných a relevantních informací o léčivých přípravcích pro české uživatele. Projekt je součástí iniciativy DigiMedic pro digitalizaci zdravotnictví.

## 🚀 Hlavní funkce

- **AI Chatbot**: Inteligentní konverzační rozhraní pro dotazy o lécích
- **Integrace SÚKL**: Přímé napojení na databázi Státního ústavu pro kontrolu léčiv
- **Zpracování obrazu**: Možnost identifikace léků pomocí fotografií
- **Personalizované odpovědi**: Využití historie konverzací pro kontextuální odpovědi
- **Realtime aktualizace**: Okamžité aktualizace chatovacího rozhraní

## 🛠️ Technologický stack

- **Frontend**: Next.js
- **Backend**: FastAPI
- **AI Framework**: LangChain
- **Databáze**: PocketBase
- **Externí API**: SÚKL API
- **Kontejnerizace**: Docker
- **CI/CD**: GitHub Actions

## 📋 Prerekvizity

- Node.js (v14 nebo vyšší)
- Python (v3.8 nebo vyšší)
- Docker a Docker Compose
- Git

## 🔧 Instalace a spuštění

1. Klonování repozitáře:
   ```bash
   git clone https://github.com/DigiMedic/PillSee.git
   cd PillSee
   ```

2. Nastavení prostředí:
   ```bash
   cp .env.example .env
   # Upravte .env soubor podle vašich potřeb
   ```

3. Spuštění pomocí Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Přístup k aplikaci:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - PocketBase Admin: `http://localhost:8090/_/`

## 📁 Struktura projektu

```
pillsee/
├── frontend/          # Next.js aplikace
├── backend/           # FastAPI server
├── ai/                # LangChain a AI komponenty
├── pocketbase/        # PocketBase konfigurace a data
├── docs/              # Projektová dokumentace
├── scripts/           # Pomocné skripty
├── .github/           # GitHub Actions konfigurace
├── docker-compose.yml # Docker Compose konfigurace
└── README.md          # Tento soubor
```

## 🧪 Testování

Spuštění testů pro backend:
```bash
cd backend
pytest
```

Spuštění testů pro frontend:
```bash
cd frontend
npm test
```

## 📄 Licence

Tento projekt je licencován pod MIT licencí. Viz soubor [LICENSE](LICENSE) pro více informací.

## 📊 Integrace s SÚKL API

PillSee využívá SÚKL API pro získávání aktuálních informací o léčivech. Hlavní endpointy:

- `/api/pharmaceuticals`: Seznam všech léčiv
- `/api/pharmaceuticals/{id}`: Detaily konkrétního léčiva
- `/api/search`: Vyhledávání léčiv

Pro více informací o API viz [oficiální dokumentaci SÚKL](https://prehledy.sukl.cz/prehled_leciv.html).

