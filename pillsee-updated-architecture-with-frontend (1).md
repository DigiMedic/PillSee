# Architektura PillSee

PillSee je komplexní aplikace založená na mikroslužbách, která využívá moderní technologie pro poskytování informací o léčivech. Níže je popis klíčových komponent a jejich vzájemných interakcí, včetně nově přidané frontend části.

## Hlavní komponenty

### 1. Next.js Frontend
- Poskytuje uživatelské rozhraní pro interakci s aplikací
- Implementuje reaktivní komponenty pro chat a zobrazení informací o lécích
- Komunikuje s backendem pomocí API volání

### 2. FastAPI Backend (main.py)
- Slouží jako vstupní bod backend aplikace
- Definuje API endpointy pro interakci s frontend aplikací
- Koordinuje tok dat mezi různými službami

### 3. LangChain Service (langchain_app.py)
- Implementuje LLM (Language Model) pomocí OpenAI GPT
- Využívá LangChain framework pro vytvoření inteligentního agenta
- Zpracovává uživatelské dotazy a generuje kontextové odpovědi
- Integruje různé nástroje, včetně DrugDatabaseTool

### 4. Drug Database Client (drug_database.py)
- Poskytuje rozhraní pro komunikaci s SÚKL API
- Implementuje metody pro vyhledávání léků a získávání detailních informací
- Využívá asynchronní HTTP požadavky pro efektivní komunikaci

### 5. SÚKL API (externí služba)
- Poskytuje aktuální data o léčivých přípravcích
- Slouží jako primární zdroj informací o lécích

## Tok dat

1. Uživatel zadá dotaz prostřednictvím Next.js frontend aplikace (Chat.js komponenta).
2. Frontend odešle dotaz na FastAPI backend pomocí API volání.
3. Backend předá dotaz LangChain Service.
4. LangChain agent analyzuje dotaz a rozhodne o dalším postupu:
   a. Pokud je potřeba informace o léku, využije DrugDatabaseTool.
   b. DrugDatabaseTool komunikuje s Drug Database Client.
   c. Drug Database Client posílá požadavek na SÚKL API.
   d. SÚKL API vrací požadovaná data.
   e. Data jsou zpracována a vrácena zpět LangChain agentovi.
5. LangChain agent generuje odpověď na základě získaných dat a kontextu konverzace.
6. Odpověď je vrácena přes FastAPI backend zpět do frontend aplikace.
7. Frontend (Chat.js) aktualizuje UI a zobrazí odpověď uživateli.
8. V případě potřeby jsou detailní informace o léku zobrazeny pomocí DrugInfo.js komponenty.

## Klíčové aspekty architektury

### Oddělení frontendu a backendu
- Next.js frontend je oddělený od FastAPI backendu, což umožňuje nezávislý vývoj a nasazení
- Komunikace mezi frontendem a backendem probíhá přes RESTful API

### Reaktivní UI
- Využití React hooks pro správu stavu a efektivní aktualizace UI
- Asynchronní zpracování požadavků pro plynulou uživatelskou zkušenost

### Asynchronní zpracování na backendu
- Využití asynchronních funkcí v Python pro efektivní zpracování požadavků
- Umožňuje souběžné zpracování více uživatelských dotazů

### Modularita
- Každá komponenta má jasně definovanou zodpovědnost
- Umožňuje snadnou údržbu a rozšiřitelnost systému

### Škálovatelnost
- Možnost horizontálního škálování jednotlivých komponent
- Využití kontejnerizace (Docker) pro snadné nasazení a škálování

### Zabezpečení
- Implementace API klíčů pro autentizaci
- Využití HTTPS pro šifrovanou komunikaci

### Flexibilita AI
- LangChain framework umožňuje snadnou integraci různých LLM modelů
- Možnost přidávání nových nástrojů a rozšiřování schopností AI agenta

## Budoucí rozšíření

1. Implementace PWA (Progressive Web App) pro lepší mobilní zkušenost
2. Přidání offline podpory pro základní funkce aplikace
3. Implementace