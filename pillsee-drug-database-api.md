# API pro přístup k databázi léčiv

## Základní informace

- **Base URL**: `https://api.pillsee.cz/v1`
- **Formát odpovědí**: JSON
- **Autentizace**: API Key (přidejte do hlavičky `X-API-Key`)

## Endpointy

### 1. Vyhledávání léků

#### GET /drugs/search

Vyhledá léky podle zadaných kritérií.

**Parametry dotazu:**
- `query` (string, povinné): Hledaný výraz (název léku, účinná látka, atd.)
- `limit` (int, volitelné, výchozí: 20): Počet výsledků na stránku
- `offset` (int, volitelné, výchozí: 0): Offset pro paginaci
- `sort` (string, volitelné, výchozí: "name"): Pole pro řazení (možnosti: "name", "active_ingredient")
- `order` (string, volitelné, výchozí: "asc"): Směr řazení (možnosti: "asc", "desc")

**Příklad požadavku:**
```
GET /drugs/search?query=paracetamol&limit=10&offset=0
```

**Příklad odpovědi:**
```json
{
  "total": 45,
  "limit": 10,
  "offset": 0,
  "results": [
    {
      "id": "0000123",
      "name": "Paracetamol 500mg",
      "active_ingredient": "paracetamol",
      "dosage_form": "tablety",
      "strength": "500mg"
    },
    // ... další výsledky
  ]
}
```

### 2. Detail léku

#### GET /drugs/{id}

Získá detailní informace o konkrétním léku.

**Parametry cesty:**
- `id` (string, povinné): ID léku v databázi SÚKL

**Příklad požadavku:**
```
GET /drugs/0000123
```

**Příklad odpovědi:**
```json
{
  "id": "0000123",
  "name": "Paracetamol 500mg",
  "active_ingredient": "paracetamol",
  "dosage_form": "tablety",
  "strength": "500mg",
  "manufacturer": "ACME Pharma",
  "description": "Lék na bolest a horečku",
  "indications": "Léčba mírné až střední bolesti a horečky",
  "contraindications": "Přecitlivělost na paracetamol nebo jakoukoli pomocnou látku přípravku",
  "side_effects": [
    "Vzácně alergické reakce",
    "Při dlouhodobém užívání možné poškození jater"
  ],
  "dosage": "1-2 tablety každých 4-6 hodin, maximálně 8 tablet denně",
  "storage": "Uchovávejte při teplotě do 25°C",
  "pil_url": "https://pribalovy-letak.cz/paracetamol-500mg",
  "spc_url": "https://sukl.cz/spc/paracetamol-500mg"
}
```

### 3. Aktualizace cache

#### POST /drugs/update-cache

Spustí proces aktualizace lokální cache databáze léků. Tento endpoint je určen pro interní použití a vyžaduje speciální oprávnění.

**Tělo požadavku:**
```json
{
  "force": false
}
```

**Parametry:**
- `force` (boolean, volitelné, výchozí: false): Pokud true, vynutí plnou aktualizaci bez ohledu na čas poslední aktualizace

**Příklad odpovědi:**
```json
{
  "status": "success",
  "message": "Cache update process started",
  "job_id": "update-12345"
}
```

## Chybové odpovědi

V případě chyby vrátí API odpověď s příslušným HTTP stavovým kódem a detaily chyby v těle odpovědi.

Příklad chybové odpovědi:
```json
{
  "error": {
    "code": "not_found",
    "message": "Requested drug not found"
  }
}
```

## Omezení a rate limiting

- Limit 1000 požadavků za hodinu na API klíč
- Maximální velikost požadavku: 1MB
- Timeout požadavku: 30 sekund

## Zabezpečení

- Veškerá komunikace probíhá přes HTTPS
- API klíče jsou pravidelně rotovány
- Implementováno logování a monitoring pro detekci neobvyklé aktivity

