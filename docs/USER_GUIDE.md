# PillSee - Uživatelská příručka

## Úvod

PillSee je anonymní AI asistent pro informace o léčivých přípravcích registrovaných v České republice. Poskytuje rychlé a přesné odpovědi na dotazy o lécích na základě oficiálních dat ze SÚKL (Státní ústav pro kontrolu léčiv).

### Klíčové vlastnosti

✅ **Anonymní** - Žádná registrace ani osobní údaje
✅ **Rychlé** - Odpověď během několika sekund
✅ **Přesné** - Data přímo z oficiálních SPC a PIL dokumentů
✅ **Bezpečné** - GDPR compliant, MDR Class I certified
✅ **Multi-modal** - Textové dotazy i rozpoznávání obrázků

## Rychlý start

### 1. Zadání textového dotazu

Jednoduše napište svůj dotaz do textového pole a stiskněte Enter nebo tlačítko "Odeslat".

**Příklady dotazů:**

```
Co je Paralen?
Jakou má Ibalgin účinnou látku?
Jak se dávkuje Aspirin?
Jaké má Brufen vedlejší účinky?
Můžu brát Paralen s Ibalginem?
Kdo nesmí brát Warfarin?
```

### 2. Rozpoznání léku z obrázku

1. Klikněte na ikonu 📷 nebo přetáhněte obrázek do pole
2. Vyfotografujte nebo vyberte foto obalu léku
3. Počkejte na rozpoznání (5-10 sekund)
4. Prohlédněte si rozpoznané informace

**Tipy pro nejlepší výsledky:**
- ✅ Dobré osvětlení
- ✅ Ostrá fotka
- ✅ Celý obal viditelný
- ✅ Přímý úhel záběru
- ❌ Rozmazaná fotka
- ❌ Špatné světlo
- ❌ Částečně zakrytý obal

## Podporované typy dotazů

### Obecné informace o léku

**Dotaz:** "Co je Paralen?"

**Odpověď obsahuje:**
- Účinná látka
- Léková forma
- Terapeutické použití
- Základní informace

### Dávkování

**Dotaz:** "Jak se dávkuje Ibalgin 400mg?"

**Odpověď obsahuje:**
- Doporučené dávkování pro dospělé
- Dávkování pro děti (pokud relevantní)
- Maximální denní dávka
- Způsob podání

⚠️ **UPOZORNĚNÍ**: Vždy se řiďte doporučením lékaře nebo lékárníka!

### Nežádoucí účinky

**Dotaz:** "Jaké má Brufen vedlejší účinky?"

**Odpověď obsahuje:**
- Časté nežádoucí účinky
- Méně časté účinky
- Závažné účinky (pokud existují)
- Kdy kontaktovat lékaře

### Interakce s jinými léky

**Dotaz:** "Můžu brát Paralen s Ibalginem?"

**Odpověď obsahuje:**
- Zda je kombinace bezpečná
- Možné interakce
- Doporučení
- Varování

### Kontraindikace

**Dotaz:** "Kdo nesmí brát Warfarin?"

**Odpověď obsahuje:**
- Absolutní kontraindikace
- Relativní kontraindikace
- Zvláštní populace (těhotenství, kojení)
- Varování

### Identifikace léku z obrázku

**Použití:**
1. Nahrajte foto obalu
2. Systém rozpozná:
   - Název léku
   - Sílu/dávku
   - Výrobce
   - Registrační číslo (pokud viditelné)

**Spolehlivost:**
- **Vysoká (> 80%)**: Zelená, můžete se spolehnout
- **Střední (60-80%)**: Oranžová, ověřte si
- **Nízká (< 60%)**: Červená, zkuste lepší foto

## Pochopení odpovědí

### Struktura odpovědi

Každá odpověď obsahuje:

1. **Hlavní odpověď** - Strukturovaná informace
2. **Zdroje** - Odkaz na SPC/PIL dokumenty
3. **Spolehlivost** - High/Medium/Low
4. **Disclaimer** - Zdravotní upozornění

### Spolehlivost odpovědi

- **High (Vysoká)**: Informace přímo z SPC/PIL
- **Medium (Střední)**: Informace z více zdrojů, potřeba ověření
- **Low (Nízká)**: Nedostatek dat, doporučujeme konzultaci s lékařem

### Medical Disclaimer

Všechny odpovědi obsahují povinné upozornění:

> ⚠️ **UPOZORNĚNÍ**: Tyto informace slouží pouze pro informativní účely a nenahrazují odbornou lékařskou radu, diagnózu nebo léčbu. Vždy se poraďte s kvalifikovaným zdravotnickým odborníkem před užitím jakéhokoliv léku.

## Limity a omezení

### Rate Limiting

Pro ochranu služby jsou nastaveny následující limity:

- **Textové dotazy**: 10 za minutu per IP adresa
- **Obrázky**: 5 za minutu per IP adresa

Při překročení limitu se zobrazí:
```
Překročili jste limit dotazů. Zkuste to prosím za chvíli.
```

### Maximální délka dotazu

- **Text**: Max 500 znaků
- **Obrázek**: Max 10 MB

### Podporované formáty obrázků

- ✅ JPEG (.jpg, .jpeg)
- ✅ PNG (.png)
- ✅ WebP (.webp)
- ❌ GIF, TIFF, BMP

## Často kladené otázky (FAQ)

### Obecné

**Q: Musím se registrovat?**
A: Ne, PillSee je zcela anonymní služba. Žádná registrace není potřeba.

**Q: Ukládáte moje dotazy?**
A: Dotazy jsou anonymizovány a uchovávány maximálně 90 dní pro zlepšení služby (GDPR compliant).

**Q: Jsou informace aktuální?**
A: Ano, databáze SÚKL je synchronizována denně.

**Q: Můžu PillSee používat místo lékaře?**
A: Ne! PillSee je pouze informační nástroj. Vždy se poraďte s lékařem nebo lékárníkem.

### Textové dotazy

**Q: V jakém jazyce můžu psát dotazy?**
A: Pouze v češtině. Podpora slovenštiny a angličtiny je plánována.

**Q: Jak dlouho trvá odpověď?**
A: Typicky 2-5 sekund pro textové dotazy.

**Q: Co když nenajdu lék?**
A: Zkuste jiný název (obchodní vs. generický), nebo kontaktujte podporu.

### Obrázky léků

**Q: Jaké fotky fungují nejlépe?**
A: Ostré fotky celého obalu s dobrým osvětlením.

**Q: Můžu fotit tabletu samotnou?**
A: Ne, systém rozpoznává pouze obaly léků (krabičky, blistry s textem).

**Q: Proč je spolehlivost nízká?**
A: Nejčastěji kvůli špatnému osvětlení nebo rozmazanosti. Zkuste novou fotku.

### Bezpečnost a soukromí

**Q: Ukládáte fotky léků?**
A: Ne, fotky jsou zpracovány v reálném čase a ihned smazány.

**Q: Vidíte mou IP adresu?**
A: IP adresy jsou hashovány (SHA-256) pro rate limiting, nelze zpětně dohledat.

**Q: Jste v souladu s GDPR?**
A: Ano, plně. Data minimalization, anonymizace, 90-day retention.

## Tipy a triky

### Pro nejlepší výsledky

1. **Buďte konkrétní**
   - ✅ "Jak se dávkuje Ibalgin 400mg?"
   - ❌ "Kolik?"

2. **Používejte celý název**
   - ✅ "Paralen 500mg tablety"
   - ⚠️ "Paralen" (funguje, ale méně přesné)

3. **Ptejte se postupně**
   - Nejdříve obecné info, pak detaily
   - Systém si pamatuje kontext relace

4. **Ověřte si informace**
   - Zkontrolujte zdroje v odpovědi
   - Při pochybnostech konzultujte lékaře

### Zkratky a termíny

- **SPC** - Souhrn údajů o přípravku (pro lékaře)
- **PIL** - Příbalová informace (pro pacienty)
- **SÚKL** - Státní ústav pro kontrolu léčiv
- **ATC kód** - WHO klasifikace léků
- **INN** - International Nonproprietary Name (účinná látka)
- **Rx** - Pouze na lékařský předpis
- **OTC** - Over-the-counter (volně prodejné)

## Podpora a kontakt

### Nahlášení problému

Pokud narazíte na:
- Nesprávné informace
- Technické problémy
- Chybějící léky

Kontaktujte nás na: **support@pillsee.cz**

### Zpětná vazba

Pomáhá nám zlepšovat službu:
- 👍 Byla odpověď užitečná?
- 👎 Co chybělo?
- 💡 Návrhy na zlepšení

### Sledujte nás

- **Web**: https://pillsee.cz
- **GitHub**: https://github.com/pillsee/pillsee
- **Status Page**: https://status.pillsee.cz

## Slovníček pojmů

| Termín | Význam |
|--------|--------|
| **Účinná látka** | Chemická látka zodpovědná za léčebný účinek |
| **Léková forma** | Způsob podání (tableta, sirup, injekce...) |
| **Síla** | Množství účinné látky (mg, ml, % atd.) |
| **Indikace** | Stavy/choroby, kdy se lék používá |
| **Kontraindikace** | Stavy, kdy lék NESMÍ být použit |
| **Nežádoucí účinky** | Vedlejší účinky léku |
| **Interakce** | Ovlivnění účinku kombinací s jiným lékem |
| **Dávkování** | Kolik a jak často lék užívat |
| **Předpisovost** | Zda je nutný lékařský předpis |
| **Registrační číslo** | Unikátní kód přípravku v ČR |

## Příklady použití

### Scénář 1: Potřebuji informace o léku

```
Uživatel: "Co je Paralen a k čemu se používá?"

PillSee: "Paralen je analgetikum-antipyretikum (lék proti bolesti
         a horečce) obsahující účinnou látku paracetamol.

         Používá se k léčbě:
         - Mírné až středně silné bolesti
         - Horečky při chřipce a nachlazení

         Léková forma: Potahované tablety
         Síla: 500mg paracetamolu
         Výrobce: Zentiva k.s.

         Zdroje: SPC Paralen 500mg, PIL Paralen
         Spolehlivost: High

         ⚠️ UPOZORNĚNÍ: Tyto informace slouží pouze pro
         informativní účely..."
```

### Scénář 2: Kontrola interakce

```
Uživatel: "Můžu brát Paralen (paracetamol) společně s Ibalginem
          (ibuprofen)?"

PillSee: "Ano, Paralen (paracetamol) a Ibalgin (ibuprofen) lze
         obvykle kombinovat.

         Klíčové body:
         - Různé mechanismy účinku - doplňují se
         - Dodržujte max. denní dávky obou léků
         - Ibuprofen berte s jídlem (ochrana žaludku)

         ⚠️ Varování:
         - Nekombinujte s jinými léky obsahujícími paracetamol/ibuprofen
         - Při dlouhodobém užívání konzultujte lékaře

         Zdroje: SPC Paralen, SPC Ibalgin 400mg
         Spolehlivost: High"
```

### Scénář 3: Rozpoznání léku z fotky

```
1. Uživatel nahraje foto obalu s nápisem "PARALEN 500mg"
2. Systém rozpozná:

   Název: Paralen 500mg
   Účinná látka: Paracetamolum
   Síla: 500mg
   Forma: Potahované tablety
   Výrobce: Zentiva k.s.
   Reg. číslo: 16/123/45-C

   Spolehlivost: 95% ✅
   Validováno proti SÚKL: Ano

3. Uživatel může kliknout na "Zobrazit více informací"
```

## Bezpečnostní upozornění

### ⚠️ Kdy NEPOU

ŽÍVAT PillSee

PillSee **NENAHRAZUJE**:
- Konzultaci s lékařem
- Lékařský předpis
- Diagnózu onemocnění
- Naléhavou lékařskou pomoc

### 🚨 Kdy okamžitě kontaktovat lékaře

- Závažné nežádoucí účinky
- Alergická reakce na lék
- Předávkování
- Těhotenství/kojení bez konzultace
- Chronické onemocnění

### ☎️ Linky důvěry

- **Všeobecná lékařská pohotovost**: 155
- **Toxikologické centrum**: +420 224 919 293
- **Lékařská pohotovost**: 155

---

**Verze**: 1.0.0
**Poslední aktualizace**: 2024-01-15
**Platforma**: https://pillsee.cz
