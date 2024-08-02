# Struktura repozitáře PillSee

```
pillsee/
├── frontend/
│   ├── pages/
│   │   ├── api/
│   │   │   └── proxy.js
│   │   ├── _app.js
│   │   └── index.js
│   ├── components/
│   │   ├── ChatInterface.js
│   │   ├── DrugInfo.js
│   │   ├── ImageUpload.js
│   │   └── Layout.js
│   ├── styles/
│   │   ├── globals.css
│   │   └── Home.module.css
│   ├── lib/
│   │   └── api.js
│   ├── public/
│   │   ├── images/
│   │   └── icons/
│   ├── next.config.js
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── drug_info.py
│   │   │   └── image_analysis.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── pydantic_models.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── pocketbase_service.py
│   │   │   └── sukl_service.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_services.py
│   ├── requirements.txt
│   └── Dockerfile
├── ai/
│   ├── langchain_agent.py
│   ├── pocketbase_tool.py
│   └── sukl_tool.py
├── pocketbase/
│   ├── pb_migrations/
│   └── pb_data/
├── docs/
│   ├── api.md
│   ├── development.md
│   └── deployment.md
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── .github/
│   └── workflows/
│       ├── frontend_ci.yml
│       └── backend_ci.yml
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

## Popis klíčových adresářů a souborů:

1. `frontend/`: Obsahuje Next.js aplikaci
   - `pages/`: Routy a API endpointy
   - `components/`: Opakovaně použitelné React komponenty
   - `styles/`: CSS a stylovací soubory
   - `lib/`: Pomocné funkce a utility
   - `public/`: Statické soubory

2. `backend/`: Obsahuje FastAPI server
   - `app/`: Hlavní aplikační logika
   - `api/`: API endpointy
   - `core/`: Základní konfigurace a bezpečnostní nastavení
   - `models/`: Pydantic modely pro validaci dat
   - `services/`: Služby pro AI, PocketBase a SÚKL API
   - `tests/`: Unit a integrační testy

3. `ai/`: Obsahuje AI komponenty
   - `langchain_agent.py`: Implementace LangChain agenta
   - `pocketbase_tool.py`: Nástroj pro interakci s PocketBase
   - `sukl_tool.py`: Nástroj pro interakci se SÚKL API

4. `pocketbase/`: Obsahuje data a migrace pro PocketBase

5. `docs/`: Projektová dokumentace

6. `scripts/`: Pomocné skripty pro setup a deployment

7. `.github/workflows/`: CI/CD konfigurace pro GitHub Actions

8. `docker-compose.yml`: Konfigurace pro Docker Compose pro snadné spuštění celé aplikace

9. `README.md`: Hlavní dokumentace projektu

10. `LICENSE`: Licenční soubor projektu

