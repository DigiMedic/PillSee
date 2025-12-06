# PillSee API Documentation

## Přehled

Tato složka obsahuje kompletní API dokumentaci pro PillSee backend.

## Soubory

### `openapi.yaml`
OpenAPI 3.0 specifikace pro PillSee API. Obsahuje:
- Všechny endpointy (`/health`, `/api/query/text`, `/api/query/image`)
- Request/Response schemas
- Rate limiting dokumentaci
- Příklady použití
- Error handling

### Generování dokumentace

#### Redoc (doporučeno pro čitelnost)
```bash
npm install -g @redocly/cli
redocly build-docs openapi.yaml -o index.html
```

Výstup: Statický HTML soubor s krásnou dokumentací

#### Swagger UI (doporučeno pro interaktivní testování)
```bash
# Vytvoření HTML s Swagger UI
cat > swagger-ui.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: "openapi.yaml",
            dom_id: '#swagger-ui'
        });
    </script>
</body>
</html>
EOF
```

#### FastAPI automatická dokumentace

Při spuštění backendu:
- **Swagger UI**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Použití

### Lokální preview

1. **Pomocí Python HTTP serveru:**
```bash
python -m http.server 8080
# Otevřete: http://localhost:8080/index.html
```

2. **Pomocí npx:**
```bash
npx serve .
```

### Validace OpenAPI spec

```bash
# Pomocí Redocly
redocly lint openapi.yaml

# Pomocí Swagger Editor online
# https://editor.swagger.io
# Zkopírujte obsah openapi.yaml
```

### Generování klientských SDK

#### Python
```bash
openapi-python-client generate --url openapi.yaml
```

#### TypeScript/JavaScript
```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-axios \
  -o ./generated/typescript-client
```

#### cURL examples
```bash
# Text query
curl -X POST http://localhost:8000/api/query/text \
  -H "Content-Type: application/json" \
  -d '{"query": "Co je Paralen?"}'

# Health check
curl http://localhost:8000/health
```

## Code Examples

### Python (requests)

```python
import requests

# Text query
response = requests.post(
    "http://localhost:8000/api/query/text",
    json={"query": "Co je Paralen?"}
)
data = response.json()
print(data["data"]["answer"])

# Image query
with open("pill_photo.jpg", "rb") as f:
    import base64
    image_b64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/api/query/image",
    json={"image_data": f"data:image/jpeg;base64,{image_b64}"}
)
```

### JavaScript (fetch)

```javascript
// Text query
const response = await fetch('http://localhost:8000/api/query/text', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: 'Co je Paralen?'})
});
const data = await response.json();
console.log(data.data.answer);

// Image query
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];
const reader = new FileReader();

reader.onload = async (e) => {
    const response = await fetch('http://localhost:8000/api/query/image', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({image_data: e.target.result})
    });
    const data = await response.json();
    console.log(data);
};

reader.readAsDataURL(file);
```

### TypeScript (typed)

```typescript
interface TextQuery {
    query: string;
}

interface APIResponse {
    status: 'success' | 'error';
    data: Record<string, any>;
    error?: string;
    disclaimer: string;
    timestamp: string;
}

async function queryMedication(query: string): Promise<APIResponse> {
    const response = await fetch('http://localhost:8000/api/query/text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query} as TextQuery)
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    return response.json() as Promise<APIResponse>;
}

// Usage
const result = await queryMedication('Co je Paralen?');
console.log(result.data.answer);
```

## Rate Limits

| Endpoint | Limit | Scope |
|----------|-------|-------|
| `POST /api/query/text` | 10/minute | Per IP |
| `POST /api/query/image` | 5/minute | Per IP |
| `GET /health` | Unlimited | - |

**Při překročení:**
- HTTP Status: `429 Too Many Requests`
- Response: `{"error_code": "RATE_LIMIT_EXCEEDED", ...}`

## Error Handling

### Error Response Format

```json
{
    "status": "error",
    "error_code": "INVALID_QUERY",
    "error_message": "Dotaz nemůže být prázdný",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Codes

| Code | Meaning | HTTP Status |
|------|---------|-------------|
| `INVALID_QUERY` | Prázdný nebo neplatný dotaz | 400 |
| `INVALID_IMAGE` | Neplatný formát obrázku | 400 |
| `RATE_LIMIT_EXCEEDED` | Překročen limit dotazů | 429 |
| `INTERNAL_ERROR` | Interní chyba serveru | 500 |
| `SERVICE_UNAVAILABLE` | Služba dočasně nedostupná | 503 |

## Authentication

**PillSee API je zcela anonymní.**
- ❌ Žádná registrace
- ❌ Žádné API klíče
- ❌ Žádné tokeny
- ✅ Pouze IP-based rate limiting

## CORS

Povolené origins:
- `http://localhost:3000` (development)
- `https://pillsee.cz` (production)
- `https://pillsee.vercel.app` (production)

## Changelog

### Version 1.0.0 (2024-01-15)
- ✅ Initial API release
- ✅ Text query endpoint
- ✅ Image query endpoint
- ✅ Health check endpoint
- ✅ Rate limiting
- ✅ OpenAPI 3.0 specification

## Support

- **Email**: support@pillsee.cz
- **GitHub Issues**: https://github.com/pillsee/pillsee/issues
- **Documentation**: https://docs.pillsee.cz

---

**Poslední aktualizace**: 2024-01-15
**OpenAPI verze**: 3.0.0
**API verze**: 1.0.0
