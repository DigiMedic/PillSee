# PillSee - project brief

PillSee je konverzační platforma zaměřená na české uživatele, která využívá rámec Langchain pro poskytování přesných a relevantních informací o léčivých přípravcích. Aplikace umožňuje uživatelům získávat informace o léčivech pomocí textu nebo fotografií obalů a integruje nezávislou databázi léčiv dostupných v České republice. Hlavním cílem je shrnout klíčové informace z příbalových letáků a zdůraznit potenciální nežádoucí účinky. Monetizační strategie zahrnuje affiliate marketing, kde aplikace nabízí odkazy na eshopy pro objednání léčivých přípravků, čímž generuje příjmy pro další vývoj.

---

💡 **Cílem**: Vyvinout konverzační platformu zaměřenou na české uživatele, která využívá rámec Langchain pro poskytování přesných a relevantních informací o léčivých přípravcích. Aplikace bude sloužit jako rozhraní pro dotazy na léčiva, umožní uživatelům získávat informace o přípravcích pomocí textu nebo fotografií obalů a bude integrovat nezávislou databázi léčiv dostupných v České republice. Hlavním úkolem agenta bude shrnutí klíčových informací z příbalových letáků, včetně zdůraznění potenciálních nežádoucích účinků.

---

## Flow

1. **Uživatelský Dotaz**:  
   Uživatel zahájí konverzaci zasláním dotazu nebo fotografie léčivého přípravku. Tento dotaz může být zadán formou textu nebo jako obrázek skrze uživatelské rozhraní aplikace.

2. **Zpracování Dotazu**:  
   Aplikace přijme uživatelský dotaz a provede předběžnou analýzu k určení, zda je dotaz ve formě textu nebo obrázku. Pro fotografie se použije modul pro optické rozpoznání znaků (OCR) nebo obrazové rozpoznávací technologie k identifikaci produktu.

3. **Vyhledávání v Databázi**:  
   Po identifikaci léčivého přípravku se vyhledají relevantní informace v nezávislé databázi léčiv. Tento krok zahrnuje přístup k databázi pomocí API nebo jiného rozhraní pro získání informací o přípravku, včetně sumarizace důležitých údajů z příbalového letáku.

4. **Nezávislé a Relevantní Informace**:  
   Systém zpracuje informace, aby zabezpečil, že poskytnuté údaje o léčivém přípravku jsou nezávislé na ceně a jsou relevantní pro uživatele. Informace budou zahrnovat účinky, dávkování, nežádoucí účinky a jakékoli rizikové informace.

5. **Poskytnutí Odpovědi Uživateli**:  
   Aplikace pak vrací shrnutí informací uživateli, včetně zvýrazněných upozornění, pokud jsou k dispozici, a to vše v přívětivém formátu konverzačního chatu.

## Poskytování informací o léčivém přípravku

Po přijetí a zpracování uživatelského dotazu aplikace provede vyhledávání v databázi léčiv. Databáze obsahuje podrobné informace o různých léčivých přípravcích dostupných v České republice. Na základě uživatelova dotazu aplikace identifikuje relevantní léčivý přípravek a získá z databáze následující informace:

1. **Účinky léčivého přípravku**:  
   Co lék dělá, jak působí na tělo a jak pomáhá léčit nebo řešit zdravotní problémy.

2. **Dávkování**:  
   Doporučené množství a frekvence užití léčivého přípravku.

3. **Potenciální nežádoucí účinky**:  
   Možné vedlejší účinky, které může lék způsobit.

4. **Rizikové informace**:  
   Jakákoliv varování nebo opatření spojená s užíváním léku.

Tyto informace jsou pak převedeny do srozumitelné a přehledné formy, která je předložena uživateli. Cílem je poskytnout uživateli přesné a relevantní informace, které mu pomohou lépe porozumět léčivému přípravku a jeho užití.

💡 **Důležité oznámení administrátora**:  
Prosím, berte na vědomí, že náš AI modul je zde, aby poskytl přesné a užitečné informace. Avšak, jeho schopnosti jsou omezené a neměl by nahradit profesionální lékařskou radu.

- **Prompty**:
    
    ```plaintext
    Vyhledej informace o léku {lék} a poskytni údaje o jeho účincích, dávkování, nežádoucích účincích a {rizika}. Upozorni uživatele, aby vždy konzultoval jakékoliv otázky týkající se užití léků se svým lékařem nebo lékárníkem. Neprováděj žádné vlastní interpretace informací o léku, pouze poskytni přesné údaje ze zdroje.
    ```

## Monetizační strategie: Affiliate marketing

**Cíl:** Získat finance pro další vývoj projektu bez zatížení uživatele.

### Implementace:

1. **Detekce záměru uživatele**:
   - Když uživatel zahájí konverzaci o léčivém přípravku, aplikace analyzuje sentiment konverzace.
   - Pokud aplikace identifikuje zájem uživatele o léčivý přípravek, například dotazy na jeho účinky, dávkování nebo dostupnost.

2. **Nabídka pomoci s objednáním**:
   - Aplikace ve vhodný okamžik během konverzace položí uživateli otázku, zda si přeje vyhledat dostupné prodejce a pomoci s objednáním léčivého přípravku.
   - Pokud uživatel souhlasí, aplikace zašle požadavek na AI agenta s touto funkcí.

3. **Získání relevantních odkazů**:
   - AI agent provede vyhledávání a vrátí odpověď s relevantními odkazy na nákup léčivého přípravku.
   - Tyto odkazy budou obsahovat affiliate odkazy, které zabezpečí, že za každou transakci uskutečněnou přes tyto odkazy obdržíme provizi.

4. **Odpověď uživateli**:
   - Aplikace vrátí uživateli odkazy na eshopy, kde může léčivý přípravek objednat.
   - Tyto odkazy budou předloženy přívětivým způsobem jako součást konverzace.

### Výhody:

- **Finanční podpora pro další vývoj**: Zajištění prostředků na další rozvoj projektu bez přímých nákladů pro uživatele.
- **Relevance a užitečnost**: Poskytnutí užitečných informací a přímé možnosti objednání léčivého přípravku uživateli v rámci jedné aplikace.
- **Zvýšení hodnoty pro uživatele**: Uživatelé ocení integrovanou funkci, která jim ušetří čas a poskytne pohodlné řešení.

## Databaze léčiv

- [Databáze léčivých přípravků DLP | Otevřená data](https://opendata.sukl.cz/?q=katalog/databaze-lecivych-pripravku-dlp)
- [Přehled léčiv](https://prehledy.sukl.cz/prehled_leciv.html#/?typ=0&filtr=%22%22&pocet=10&stranka=1&sort=%5B%22nazev%22%5D&smer=%22asc%22&leciveLatky=%5B%5B%5D%5D&leciveLatkyOperace=%22OR%22&leciveLatkyOperaceZavorek=%22ANY%22&atc=%22%22&cestaPodani=%22%22&drzitelRegistrace=%5B%5D&stavRegistrace=%22%22&zpusobVydeje=%5B%5D&uhrada=%5B%5D&dovoz=%22%22&jeDodavka=false&stavZruseni=%22N%22&ochrannyPrvek=%22X%22&dostupnost=%5B%5D&omezenaDostupnost=false&lecivaLatkaSelected=%5B%5B%5D%5D&lecivaLatkaValue=%5B%22%22%5D&lecivaLatkaCiselnik=%5B%5B%5D%5D&typVydeje=%223%22)
