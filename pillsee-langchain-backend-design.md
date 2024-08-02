# Návrh backend architektury PillSee s LangChain

## 1. Struktura backendu

```
backend/
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   ├── drug_info.py
│   │   └── image_analysis.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   └── pydantic_models.py
│   ├── services/
│   │   ├── langchain_service.py
│   │   ├── pocketbase_service.py
│   │   └── sukl_service.py
│   ├── utils/
│   │   └── helpers.py
│   └── main.py
├── tests/
│   ├── test_api.py
│   ├── test_langchain.py
│   └── test_services.py
└── requirements.txt
```

## 2. Hlavní komponenty

### 2.1 LangChain Service (`langchain_service.py`)

Toto je jádro našeho backendu, které bude řídit tok zpracování dotazů.

```python
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.llms import OpenAI
from langchain.prompts import StringPromptTemplate
from langchain.memory import ConversationBufferMemory
from .pocketbase_service import PocketBaseService
from .sukl_service import SUKLService

class LangChainService:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7)
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.pocketbase = PocketBaseService()
        self.sukl = SUKLService()
        
        self.tools = [
            Tool(
                name="PocketBase",
                func=self.pocketbase.query,
                description="Useful for querying and storing conversation history and drug information"
            ),
            Tool(
                name="SUKL Database",
                func=self.sukl.query,
                description="Useful for querying information about drugs from the SUKL database"
            )
        ]
        
        self.agent = self.create_agent()
        
    def create_agent(self):
        prompt = CustomPromptTemplate(
            template="You are a helpful assistant that provides information about drugs. {chat_history}\nHuman: {human_input}\nAI: Let's approach this step-by-step:",
            input_variables=["chat_history", "human_input"]
        )
        
        agent = LLMSingleActionAgent(
            llm_chain=LLMChain(llm=self.llm, prompt=prompt),
            output_parser=CustomOutputParser(),
            stop=["\nHuman:"],
            allowed_tools=[tool.name for tool in self.tools]
        )
        
        return AgentExecutor.from_agent_and_tools(
            agent=agent, tools=self.tools, verbose=True, memory=self.memory
        )
    
    async def process_query(self, query: str):
        return await self.agent.arun(query)
```

### 2.2 PocketBase Service (`pocketbase_service.py`)

Tato služba bude zajišťovat interakci s PocketBase pro ukládání a načítání dat.

```python
from pocketbase import PocketBase

class PocketBaseService:
    def __init__(self):
        self.pb = PocketBase('http://127.0.0.1:8090')
    
    async def query(self, query: str):
        # Implement logic to query PocketBase
        pass
    
    async def store_conversation(self, conversation: dict):
        # Implement logic to store conversation in PocketBase
        pass
```

### 2.3 SUKL Service (`sukl_service.py`)

Tato služba bude zajišťovat komunikaci s SÚKL API.

```python
import httpx

class SUKLService:
    def __init__(self):
        self.base_url = "http://api.sukl.cz"
    
    async def query(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/search", params={"query": query})
            return response.json()
```

## 3. Tok dat

1. Uživatel zadá dotaz přes frontend.
2. Dotaz je odeslán na backend endpoint `/api/chat`.
3. `chat.py` předá dotaz `LangChainService`.
4. `LangChainService` zpracuje dotaz pomocí LLM a nástrojů:
   - Pokud je potřeba historie konverzace, použije `PocketBaseService`.
   - Pro informace o lécích použije `SUKLService`.
5. LangChain agent rozhodne o nejlepší akci na základě dotazu a dostupných nástrojů.
6. Výsledek je zpracován a formátován.
7. Odpověď je odeslána zpět na frontend.
8. Konverzace je uložena do PocketBase pro budoucí reference.

## 4. API Endpoints

### 4.1 Chat Endpoint (`chat.py`)

```python
from fastapi import APIRouter, Depends
from ..services.langchain_service import LangChainService

router = APIRouter()

@router.post("/chat")
async def chat(message: str, lang_service: LangChainService = Depends()):
    response = await lang_service.process_query(message)
    return {"response": response}
```

### 4.2 Drug Info Endpoint (`drug_info.py`)

```python
from fastapi import APIRouter, Depends
from ..services.sukl_service import SUKLService

router = APIRouter()

@router.get("/drug/{drug_id}")
async def get_drug_info(drug_id: str, sukl_service: SUKLService = Depends()):
    drug_info = await sukl_service.query(drug_id)
    return drug_info
```

## 5. Bezpečnost a výkon

- Implementujte rate limiting pro prevenci zneužití API.
- Použijte caching pro často vyhledávané informace o lécích.
- Zajistěte, že všechna citlivá data jsou šifrována v klidu i při přenosu.
- Implementujte logování pro snadné debugování a monitorování.

## 6. Testování

- Vytvořte unit testy pro každou službu a endpoint.
- Implementujte integrační testy pro ověření správné interakce mezi komponentami.
- Proveďte zátěžové testy pro ověření výkonu při vysokém zatížení.

## 7. Rozšiřitelnost

Tento návrh umožňuje snadné přidávání nových nástrojů do LangChain agenta. V budoucnu můžete přidat:

- Nástroj pro analýzu obrázků léků
- Integraci s dalšími zdravotnickými databázemi
- Personalizované doporučení na základě historie uživatele

