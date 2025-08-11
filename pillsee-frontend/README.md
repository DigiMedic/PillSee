# PillSee Frontend

Next.js PWA frontend pro PillSee - anonymní český AI asistent pro informace o lécích.

## 🌟 Klíčové funkce

- 📱 **Progressive Web App** - Instalovatelná jako nativní aplikace
- 📸 **AI Camera** - Rozpoznání léků z fotografií pomocí GPT-4 Vision  
- 💬 **Smart Chat** - Textové dotazy s RAG search v SÚKL databázi
- 🔒 **Anonymní** - Bez registrace, cookies, nebo sledování
- ⚡ **Rychlé** - Optimalizované pro rychlé načítání a odezvu
- 🌐 **Offline** - Základní funkčnost i bez internetu
- 🛡️ **GDPR** - Plná transparentnost zpracování dat

## 🚀 Quick Start

### Prerekvizity
- Node.js 18+
- npm nebo yarn
- PillSee backend běžící s SÚKL daty

### Instalace

```bash
# Klonování a vstup do adresáře
cd pillsee-frontend

# Instalace závislostí
npm install

# Environment proměnné
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" > .env.local

# Spuštění dev serveru
npm run dev

# Aplikace běží na: http://localhost:3000
```

## 📁 Struktura projektu

```
pillsee-frontend/
├── app/                     # Next.js 14 App Router
│   ├── layout.tsx          # Root layout s PWA manifest
│   ├── page.tsx            # Hlavní stránka aplikace
│   └── globals.css         # Globální styly s TailwindCSS
├── components/             # React komponenty
│   ├── CameraCapture.tsx   # Kamera pro fotografování léků
│   ├── GDPRNotice.tsx     # GDPR compliance notice
│   ├── InstallPrompt.tsx   # PWA instalační prompt
│   ├── MessageList.tsx     # Historie dotazů a odpovědí
│   └── ui/                # UI komponenty (button, card, input)
├── lib/
│   └── utils.ts           # Utility funkce (cn, formátování)
├── utils/
│   ├── api.ts             # API client pro backend komunikaci
│   └── session.ts         # SessionStorage management
├── public/
│   ├── manifest.json      # PWA manifest
│   └── icons/             # PWA ikony
├── __tests__/             # Jest testy
└── next.config.js         # Next.js konfigurace s PWA
```

## 🔧 Environment Variables

```bash
# Backend API URL
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# PWA nastavení
NEXT_PUBLIC_APP_NAME=PillSee
NEXT_PUBLIC_APP_DESCRIPTION=Anonymní AI asistent pro české léky

# Analytics (volitelné)
NEXT_PUBLIC_GA_ID=your_google_analytics_id
```

## 🧪 Testování

```bash
# Spuštění všech testů
npm test

# Spuštění testů s watch režimem
npm run test:watch

# Spuštění s coverage
npm run test:coverage

# Spuštění konkrétního testu
npm test -- CameraCapture.test.tsx
```

## 📱 PWA Funkce

### Instalace aplikace
1. Otevřete aplikaci v Chrome/Safari
2. Klikněte na "Přidat na plochu" při instalačním promptu
3. Aplikace se nainstaluje jako nativní app

### Offline režim
- Service Worker cache pro statické soubory
- Fallback stránka pro offline režim
- Lokální sessionStorage pro historii

### Camera API
- Přístup k zadní kameře s vysokým rozlišením
- Flash/torch podpora pro lepší osvětlení
- Automatické změny velikosti pro optimalizaci

## 🎨 Design System

### TailwindCSS Konfigurace
- **Colors**: Custom zdravotnická barevná paleta
- **Typography**: Optimalizované pro čitelnost
- **Spacing**: Mobile-first spacing systém
- **Components**: Reusable UI komponenty

### Responsive Breakpoints
```css
sm: '640px'   // Malé tablety
md: '768px'   // Tablety
lg: '1024px'  // Desktopy
xl: '1280px'  // Velké desktopy
```

## 🔄 API Integration

### Text Query
```typescript
const response = await fetch('/api/query/text', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'Co je to Paralen?' })
})
```

### Image Query
```typescript
const formData = new FormData()
formData.append('image', file)

const response = await fetch('/api/query/image', {
  method: 'POST',
  body: formData
})
```

## 🔒 Bezpečnost a Soukromí

### Anonymní použití
- Žádné user accounts nebo registrace
- Žádné cookies kromě GDPR consent
- Veškerá data pouze v sessionStorage

### GDPR Compliance
- Transparentní GDPR notice při prvním použití
- Opt-out možnost pro analytics
- Clear data mechanismus

### Content Security Policy
- Strict CSP headers pro XSS ochranu
- Allowed sources pouze pro trusted domény
- Inline styles pouze s nonce

## 🐳 Docker

```bash
# Build image
docker build -t pillsee-frontend .

# Spuštění kontejneru
docker run -d \
  --name pillsee-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=http://backend:8000 \
  pillsee-frontend
```

## 🚀 Deployment

### Vercel (doporučeno)
```bash
# Připojte GitHub repo k Vercel
# Nastavte environment proměnné v Vercel dashboard
# Deploy se spustí automaticky při push do main
```

### Netlify
```bash
# Build command
npm run build

# Publish directory
out/

# Environment variables
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
```

## 🔧 Development

### Přidání nové komponenty
```bash
# Vytvořte komponentu v components/
touch components/NewComponent.tsx

# Přidejte test
touch __tests__/components/NewComponent.test.tsx

# Přidejte do příslušných stránek
```

### PWA Update Process
1. Upravte `public/manifest.json` pro změny PWA
2. Aktualizujte service worker v `next.config.js`
3. Testujte v dev tools > Application > Service Workers

### Debugging
```bash
# Spuštění s detailním logováním
npm run dev -- --debug

# Analýza bundle velikosti  
npm run analyze

# Lighthouse audit
npm run lighthouse
```

## 📊 Performance

- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s  
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

### Optimalizace
- Image optimization s next/image
- Code splitting na route úrovni
- Lazy loading komponent
- Preloading kritických zdrojů

## 🤝 Contributing

1. Fork the repository
2. Vytvořte feature branch (`git checkout -b feature/amazing-feature`)
3. Commit změny (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Otevřete Pull Request

## 📄 License

Tento projekt je licencován pod MIT License - viz [LICENSE](LICENSE) soubor.