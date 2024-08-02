# Podrobný návod pro vývoj a nasazení PillSee

## Fáze 1: Příprava prostředí

1. Instalace potřebného software:
   ```bash
   # Instalace Node.js a npm
   curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
   sudo apt-get install -y nodejs

   # Instalace Python 3.8+
   sudo apt-get install python3.8 python3-pip

   # Instalace Docker a Docker Compose
   sudo apt-get install docker.io docker-compose

   # Instalace Git
   sudo apt-get install git
   ```

2. Nastavení Git a klonování repozitáře:
   ```bash
   git config --global user.name "Vaše Jméno"
   git config --global user.email "vas.email@example.com"
   git clone https://github.com/DigiMedic/PillSee.git
   cd PillSee
   ```

3. Vytvoření virtuálního prostředí pro Python:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Instalace závislostí:
   ```bash
   # Backend závislosti
   pip install -r backend/requirements.txt

   # Frontend závislosti
   cd frontend
   npm install
   cd ..
   ```

5. Nastavení proměnných prostředí:
   ```bash
   cp .env.example .env
   # Otevřete .env soubor a nastavte všechny potřebné proměnné
   ```

## Fáze 2: Implementace backendu

6. Implementace FastAPI aplikace:
   ```bash
   cd backend/app
   touch main.py
   ```
   Otevřete `main.py` a implementujte základní strukturu FastAPI aplikace.

7. Implementace API endpointů:
   ```bash
   mkdir api
   touch api/chat.py api/drug_info.py api/image_analysis.py
   ```
   Implementujte jednotlivé API endpointy v příslušných souborech.

8. Implementace služeb:
   ```bash
   mkdir services
   touch services/ai_service.py services/pocketbase_service.py services/sukl_service.py
   ```
   Implementujte služby pro AI, PocketBase a SÚKL API.

9. Implementace modelů:
   ```bash
   mkdir models
   touch models/pydantic_models.py
   ```
   Definujte Pydantic modely pro validaci dat.

10. Implementace konfigurace a zabezpečení:
    ```bash
    mkdir core
    touch core/config.py core/security.py
    ```
    Implementujte konfiguraci aplikace a bezpečnostní nastavení.

11. Spuštění a testování backendu:
    ```bash
    uvicorn main:app --reload
    ```

## Fáze 3: Implementace AI komponenty

12. Implementace LangChain agenta:
    ```bash
    cd ../../ai
    touch langchain_agent.py
    ```
    Implementujte LangChain agenta v `langchain_agent.py`.

13. Implementace PocketBase a SÚKL nástrojů:
    ```bash
    touch pocketbase_tool.py sukl_tool.py
    ```
    Implementujte nástroje pro interakci s PocketBase a SÚKL API.

14. Integrace AI komponenty s backendem:
    Upravte `backend/app/services/ai_service.py` pro využití LangChain agenta.

## Fáze 4: Implementace frontendu

15. Nastavení Next.js projektu:
    ```bash
    cd ../frontend
    npx create-next-app .
    ```

16. Implementace komponent:
    ```bash
    mkdir components
    touch components/ChatInterface.js components/DrugInfo.js components/ImageUpload.js components/Layout.js
    ```
    Implementujte jednotlivé React komponenty.

17. Implementace stránek:
    ```bash
    cd pages
    touch index.js
    mkdir api
    touch api/proxy.js
    ```
    Implementujte hlavní stránku a API proxy pro komunikaci s backendem.

18. Stylování aplikace:
    ```bash
    cd ../styles
    touch globals.css Home.module.css
    ```
    Implementujte styly pro aplikaci.

19. Konfigurace Next.js:
    Upravte `next.config.js` podle potřeb projektu.

20. Spuštění a testování frontendu:
    ```bash
    npm run dev
    ```

## Fáze 5: Integrace PocketBase

21. Stažení a nastavení PocketBase:
    ```bash
    cd ../../pocketbase
    wget https://github.com/pocketbase/pocketbase/releases/download/v0.x.x/pocketbase_0.x.x_linux_amd64.zip
    unzip pocketbase_0.x.x_linux_amd64.zip
    ./pocketbase serve
    ```

22. Konfigurace PocketBase:
    Otevřete admin rozhraní PocketBase (obvykle na `http://127.0.0.1:8090/_/`) a vytvořte potřebné kolekce.

23. Integrace PocketBase s backendem:
    Upravte `backend/app/services/pocketbase_service.py` pro komunikaci s PocketBase.

## Fáze 6: Testování

24. Implementace unit testů:
    ```bash
    cd ../backend/tests
    touch test_api.py test_services.py
    ```
    Implementujte unit testy pro API a služby.

25. Spuštění testů:
    ```bash
    pytest
    ```

26. Implementace integračních testů:
    Přidejte integrační testy do `tests` adresáře a spusťte je.

27. Manuální testování:
    Proveďte manuální testování celé aplikace, včetně všech hlavních funkcí.

## Fáze 7: Dokumentace

28. Vytvoření dokumentace:
    ```bash
    cd ../../docs
    touch api.md development.md deployment.md
    ```
    Napište dokumentaci pro API, vývoj a nasazení.

29. Aktualizace README:
    Aktualizujte `README.md` v kořenovém adresáři projektu s nejnovějšími informacemi.

## Fáze 8: Příprava pro nasazení

30. Vytvoření Dockerfile pro backend:
    ```bash
    cd ../backend
    touch Dockerfile
    ```
    Implementujte Dockerfile pro backend.

31. Vytvoření docker-compose.yml:
    ```bash
    cd ..
    touch docker-compose.yml
    ```
    Implementujte docker-compose.yml pro orchestraci všech služeb.

32. Implementace CI/CD:
    ```bash
    mkdir -p .github/workflows
    touch .github/workflows/frontend_ci.yml .github/workflows/backend_ci.yml
    ```
    Implementujte CI/CD workflows pro GitHub Actions.

## Fáze 9: Nasazení

33. Příprava produkčního prostředí:
    Nastavte produkční server (např. na AWS, DigitalOcean nebo jiné cloudové platformě).

34. Nasazení backendu:
    ```bash
    docker-compose up -d backend
    ```

35. Nasazení frontendu:
    ```bash
    cd frontend
    npm run build
    npm run start
    ```

36. Nasazení PocketBase:
    ```bash
    docker-compose up -d pocketbase
    ```

37. Konfigurace HTTPS:
    Nastavte HTTPS pomocí Let's Encrypt nebo jiného poskytovatele SSL certifikátů.

38. Nastavení monitoringu:
    Implementujte monitoring pomocí nástrojů jako Prometheus a Grafana.

## Fáze 10: Post-nasazení

39. Monitorování výkonu:
    Sledujte výkon aplikace a řešte případné problémy.

40. Sběr zpětné vazby:
    Implementujte systém pro sběr zpětné vazby od uživatelů.

41. Plánování dalších vylepšení:
    Na základě zpětné vazby a monitoringu naplánujte další vylepšení aplikace.

42. Pravidelné aktualizace:
    Pravidelně aktualizujte závislosti a provádějte údržbu kódu.

