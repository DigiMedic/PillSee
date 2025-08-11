## FUNKCE:

Vytvořte PillSee – anonymního AI chatového asistenta pro informace o lécích v České republice. Aplikace má být mobilně orientovaná progresivní webová aplikace (PWA), která umožní uživatelům:

![PillSee – anonymní AI asistent pro léky (cover)](examples/project-cover.png)

*Ilustrační titulní obrázek aplikace PillSee: mobilně orientované PWA rozhraní s anonymním chatem, nahráním fotografie obalu léku a přehledným zobrazením ověřených informací (účinná látka, dávkování, interakce, bezpečnostní upozornění).*

1. **Textové dotazy na léky** – Pokládejte otázky ohledně českých léčiv v přirozeném jazyce
2. **Identifikace léků pomocí obrázků** – Nahrajte fotografie obalů léků pro okamžité rozpoznání a získání informací
3. **Získejte komplexní informace o lécích** včetně:
   - Účinných látek a terapeutických indikací
   - Dávkování a způsobu podání
   - Nežádoucích účinků a kontraindikací
   - Interakcí s jinými léky a upozornění
   - Informací o ceně a dostupnosti

**Klíčové požadavky:**
- **Anonymní používání** – Není vyžadována registrace ani autentizace uživatele
- **Mobilně orientovaný design** – Optimalizováno pro chytré telefony s integrací kamery
- **Podpora češtiny** – Veškerá komunikace v češtině, odborná lékařská terminologie
- **Integrace vision modelu** – Použijte OpenAI GPT-4 Vision místo tradičního OCR
- **Integrace dat SÚKL** – Napojení na oficiální českou databázi léčiv
- **Bezpečnost** – Zahrnout vhodná upozornění a bezpečnostní varování
- **Rychlé odpovědi** – Odezva do 3 sekund pro optimální UX
- **Offline funkce** – PWA se service workerem pro offline použití

**Technická architektura:**
- **Backend**: FastAPI + LangGraph pro orchestraci workflow
- **Frontend**: Next.js 14 + PWA funkce
- **AI modely**: OpenAI GPT-4 Vision pro zpracování obrázků, GPT-4o-mini pro text
- **Vektorová databáze**: Supabase s pgvector pro RAG implementaci
- **Nasazení**: Vercel Edge Network pro globální výkon
- **Zdroj dat**: SÚKL (Státní ústav pro kontrolu léčiv) otevřená data

## PŘÍKLADY:

Následující příklady by měly být vytvořeny ve složce `examples/` jako vodítko pro implementaci:

### `/examples/fastapi_langgraph/`
- **`app.py`** – FastAPI aplikace s integrací workflow LangGraph
- **`agent.py`** – Správa stavů LangGraph a definice uzlů
- **`models.py`** – Pydantic modely pro validaci požadavků/odpovědí
- Ukazuje: Nastavení anonymního endpointu, konfigurace CORS, zpracování chyb

### `/examples/vision_processing/`
- **`vision_client.py`** – Implementace OpenAI GPT-4 Vision pro rozpoznání léků
- **`image_handler.py`** – Předzpracování obrázků a base64 kódování
- **`medication_parser.py`** – Parsování strukturovaného výstupu z vision modelu
- Ukazuje: Rozpoznání českého textu na lécích, skórování jistoty, záložní řešení

### `/examples/rag_sukl/`
- **`document_processor.py`** – Pipeline pro zpracování CSV a PDF SÚKL
- **`vector_store.py`** – Integrace Supabase pgvector
- **`retrieval_chain.py`** – Řetězec pro vyhledávání a generování s LangChain
- Ukazuje: Dělení českého textu, embeddingy lékařské terminologie, kontextové vyhledávání

### `/examples/nextjs_pwa/`
- **`app/page.tsx`** – Hlavní komponenta chatovacího rozhraní
- **`components/ChatInterface.tsx`** – Zpracování a zobrazování zpráv
- **`components/ImageUpload.tsx`** – Integrace kamery a zachycení obrázků
- **`next.config.js`** – Konfigurace PWA pomocí next-pwa
- **`manifest.json`** – Manifest PWA pro instalaci na mobil
- Ukazuje: Responzivní mobilní design, použití API kamery, offline podpora

### `/examples/anonymous_chat/`
- **`chat_session.ts`** – Správa relace pouze v prohlížeči
- **`message_types.ts`** – TypeScript rozhraní pro chatové zprávy
- **`privacy_handler.ts`** – Zpracování dat v souladu s ochranou soukromí
- Ukazuje: Bezstavový chat, žádné ukládání dat, GDPR compliance

### `/examples/medical_safety/`
- **`disclaimer_generator.py`** – Automatické vkládání lékařských upozornění
- **`safety_checker.py`** – Validace obsahu pro bezpečnost
- **`response_enhancer.py`** – Přidávání bezpečnostních varování do odpovědí
- Ukazuje: Ochrana před odpovědností, doporučení odborníků

## DOKUMENTACE:

### **AI modely & API:**
- [OpenAI Vision API Dokumentace](https://platform.openai.com/docs/guides/vision)
- [OpenAI GPT-4o-mini Dokumentace](https://platform.openai.com/docs/models/gpt-4o-mini)
- [LangChain OpenAI Integrace](https://python.langchain.com/docs/integrations/providers/openai)
- [LangGraph Dokumentace](https://langchain-ai.github.io/langgraph/)

### **Dokumentace frameworků:**
- [FastAPI Dokumentace](https://fastapi.tiangolo.com/)
- [Next.js 14 App Router](https://nextjs.org/docs/app)
- [next-pwa Plugin Dokumentace](https://github.com/shadowwalker/next-pwa)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/UI Komponenty](https://ui.shadcn.com/)

### **Databáze & vektorové vyhledávání:**
- [Supabase Dokumentace](https://supabase.com/docs)
- [pgvector Rozšíření](https://github.com/pgvector/pgvector)
- [LangChain Supabase Integrace](https://python.langchain.com/docs/integrations/vectorstores/supabase)

### **Česká data o lécích:**
- [SÚKL Open Data Portal](https://opendata.sukl.cz/)
- [Databáze léčivých přípravků (DLP)](https://opendata.sukl.cz/?q=katalog/databaze-lecivych-pripravku-dlp)
- [SÚKL API Dokumentace (Apitalks)](https://api.store/czechia-api/sukl.cz)

### **Nasazení & infrastruktura:**
- [Vercel Functions Dokumentace](https://vercel.com/docs/functions)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Edge Network](https://vercel.com/docs/edge-network)

### **Lékařská & právní compliance:**
- [GDPR Compliance Guidelines](https://gdpr.eu/)
- [Pokyny pro software zdravotnických prostředků](https://ec.europa.eu/health/md_sector/new_regulations/guidance_en)
- [České standardy zdravotnických informací](https://www.sukl.cz/)

## DALŠÍ DOPORUČENÍ:

### **Lékařská & právní compliance:**
- **Lékařská upozornění**: Každá odpověď MUSÍ obsahovat upozornění, že informace nenahrazují odbornou lékařskou radu
- **Doporučení odborníků**: Vždy doporučte konzultaci s lékařem při rozhodování o léčbě
- **Ochrana před odpovědností**: Nikdy neposkytujte diagnózy ani doporučení léčby
- **Přesné informace**: Používejte pouze ověřená data SÚKL, nikdy nevymýšlejte informace o lécích
- **České lékařské standardy**: Dodržujte českou terminologii a standardy

### **Ochrana soukromí & dat:**
- **GDPR compliance**: Žádné sbírání osobních údajů, explicitní souhlas s cookies
- **Anonymita**: Žádné sledování uživatelů, žádné logování konverzací
- **Pouze úložiště v prohlížeči**: Používejte sessionStorage, nikdy localStorage nebo externí úložiště
- **IP adresy**: Neuchovávejte ani neukládejte IP adresy
- **Minimální analytika**: Pouze agregované, anonymní statistiky

### **Specifika českého jazyka:**
- **Lékařská terminologie**: Používejte správnou českou farmaceutickou terminologii
- **Podpora diakritiky**: Správné zpracování českých znaků (ě, š, č, ř, ž, ý, á, í, é, ů, ú)
- **Názvy léků**: Respektujte obchodní i generické názvy v češtině
- **Jednotky dávkování**: Používejte české jednotky (mg, ml, atd.)
- **Kulturní kontext**: Zohledněte specifika českého zdravotnictví

### **Technické požadavky na výkon:**
- **Odezva**: Textové dotazy < 2 sekundy, zpracování obrázků < 3 sekundy
- **Mobilní výkon**: Optimalizace pro 3G sítě a starší zařízení
- **Zpracování obrázků**: Podpora běžných formátů z mobilních kamer (JPEG, PNG)
- **Strategie cachování**: Cache populárních léků, aktualizace dat SÚKL
- **Zpracování chyb**: Plynulé fungování při výpadku služeb

### **Vision model – úskalí:**
- **Rozpoznání českého textu**: Testujte na skutečných obalech českých léků
- **Kvalita obrázků**: Zvládněte rozmazané, otočené nebo špatně osvětlené snímky
- **Částečný text**: Zpracujte i částečně viditelné názvy léků
- **Falešná rozpoznání**: Validujte rozpoznaný text vůči databázi SÚKL
- **Skóre jistoty**: Implementujte prahové hodnoty pro rozpoznání

### **Integrace dat SÚKL:**
- **Formát dat**: SÚKL používá CSV soubory s kódováním win-1250
- **Frekvence aktualizací**: Data SÚKL se aktualizují týdně/měsíčně – implementujte synchronizaci
- **Validace dat**: Ověřujte integritu dat a zpracujte chybějící informace
- **API limity**: Při použití Apitalks API dodržujte limity
- **Záložní strategie**: Mějte záložní řešení při výpadku služeb SÚKL

### **Implementace PWA:**
- **Service Worker**: Implementujte správné cachování dat o lécích
- **Offline podpora**: Cache základních funkcí aplikace pro offline použití
- **Instalační výzva**: Upozorněte uživatele na možnost instalace PWA na domovskou obrazovku
- **Přístup ke kameře**: Správně žádejte o oprávnění, zpracujte zamítnutí
- **Push notifikace**: Zvažte připomínky k užívání léků (budoucí funkce)

### **Bezpečnostní aspekty:**
- **Validace vstupů**: Sanitizujte všechny uživatelské vstupy, zejména obrázky
- **Rate limiting**: Zabraňte zneužití rozumným omezením požadavků
- **Konfigurace CORS**: Správné nastavení CORS pro API endpointy
- **Content Security Policy**: Implementujte CSP hlavičky pro ochranu proti XSS
- **Pouze HTTPS**: Vynucujte HTTPS pro veškerou komunikaci

### **Časté chyby AI asistenta – vyvarujte se:**
- **Nepoužívejte localStorage** pro anonymní aplikace – pouze sessionStorage
- **Neimplementujte autentizaci uživatelů** – aplikace musí být zcela anonymní
- **Neukládejte historii konverzací** – každá relace je nezávislá
- **Nevynechávejte lékařská upozornění** – jsou právně povinná
- **Nezadávejte informace o lécích napevno** – vždy používejte data SÚKL
- **Nepoužívejte OCR pro rozpoznání textu** – použijte vision modely
- **Neignorujte mobilní design** – aplikace je primárně mobilní
- **Neopomíjejte česká jazyková specifika** – nejde jen o překlad z angličtiny
- **Nezanedbávejte zpracování chyb při rozpoznání obrázků** – obrázky mohou být problematické
- **Neimplementujte složité řízení stavu** – pro anonymní použití udržujte jednoduchost