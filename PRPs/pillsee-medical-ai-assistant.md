# PRP: PillSee - Anonymní český lékový AI asistent

## Přehled projektu

**PillSee** je anonymní AI chatbot asistent pro informace o lécích v České republice. Jedná se o mobilně orientovanou progresivní webovou aplikaci (PWA), která umožňuje:

1. **Textové dotazy k lékům** – Pokládejte otázky o českých lécích v přirozeném jazyce  
2. **Identifikace léku z obrázku** – Nahrajte fotografie obalu léku pro okamžité rozpoznání  
3. **Komplexní informace o léčivech** – Účinné látky, dávkování, nežádoucí účinky, interakce, cena a dostupnost  

**Hlavní požadavky:**
- **Anonymní používání** – Žádná registrace ani autentizace
- **Mobile-first design** – Optimalizace pro smartphony s použitím kamery  
- **Podpora českého jazyka** – Veškerá komunikace v češtině s odbornou terminologií
- **Integrace OpenAI GPT-4 Vision** – Vision modely místo tradičního OCR
- **Integrace dat SÚKL** – Napojení na oficiální databázi léčiv
- **Soulad s bezpečností** – Varování a zákonné disclaimery
- **Rychlé odpovědi** – <3 sekundy pro optimální UX
- **Offline schopnosti** – PWA se service workerem

## Technická architektura

- **Backend**: FastAPI + LangGraph pro orchestrace workflow
- **Frontend**: Next.js 14 + PWA + Shadcn/UI
- **AI modely**: OpenAI GPT-4 Vision (obrázky), GPT-4o-mini (text)
- **Vektorová databáze**: Supabase s pgvector pro RAG
- **Nasazení**: Vercel Edge Network pro globální výkon
- **Datový zdroj**: SÚKL (Státní ústav pro kontrolu léčiv) open data

## Kritická dokumentace a zdroje

### AI modely a API
- [OpenAI Vision API Dokumentace](https://platform.openai.com/docs/guides/vision)
- [OpenAI GPT-4o-mini Dokumentace](https://platform.openai.com/docs/models/gpt-4o-mini)
- [LangChain OpenAI Integrace](https://python.langchain.com/docs/integrations/providers/openai)
- [LangGraph Dokumentace](https://langchain-ai.github.io/langgraph/)

### Frameworky a knihovny
- [FastAPI Dokumentace](https://fastapi.tiangolo.com/)
- [Next.js 14 App Router](https://nextjs.org/docs/app)
- [next-pwa Plugin Dokumentace](https://github.com/shadowwalker/next-pwa)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/UI Komponenty](https://ui.shadcn.com/)

### Databáze a vektorové vyhledávání
- [Supabase Dokumentace](https://supabase.com/docs)
- [pgvector Extension](https://github.com/pgvector/pgvector)
- [LangChain Supabase Integrace](https://python.langchain.com/docs/integrations/vectorstores/supabase)

### Česká léková data
- [SÚKL Open Data Portal](https://opendata.sukl.cz/)
- [Databáze léčivých přípravků (DLP)](https://opendata.sukl.cz/?q=katalog/databaze-lecivych-pripravku-dlp)
- [SÚKL API Dokumentace (Apitalks)](https://api.store/czechia-api/sukl.cz)

### Soulad a legislativa
- [GDPR Guidelines](https://gdpr.eu/)
- [EU Směrnice k zdravotnickému software](https://ec.europa.eu/health/md_sector/new_regulations/guidance_en)
- [České standardy zdravotnických informací](https://www.sukl.cz/)

## Implementační plán (Blueprint)

### Fáze 1: Backend infrastruktura (FastAPI + LangGraph)

**1.1 Inicializace projektu**
```bash
# Inicializace Python projektu s FastAPI
uv init pillsee-backend
cd pillsee-backend
uv add fastapi uvicorn langchain langgraph openai supabase pydantic
uv add --dev pytest black mypy ruff
```

**1.2 Struktura FastAPI aplikace**
```python
# app/main.py - Hlavní FastAPI aplikace
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

# Rate limiting pro anonymní uživatele
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="PillSee API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS pro Next.js frontend
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000", "https://pillsee.vercel.app"],
  allow_credentials=False,  # Bez cookies (anonymní)
  allow_methods=["GET", "POST"],
  allow_headers=["*"],
)

@app.post("/api/query/text")
@limiter.limit("10/minute")
async def text_query(request: Request, query: TextQuery):
  """Zpracování textového dotazu na léky"""
  pass

@app.post("/api/query/image") 
@limiter.limit("5/minute")
async def image_query(request: Request, image_data: ImageQuery):
  """Zpracování dotazu s obrázkem (identifikace léku)"""
  pass
```

**1.3 Implementace LangGraph workflow**
```python
# app/workflows/medication_workflow.py
from langgraph import StateGraph, END
from typing import Dict, Any

class MedicationState(TypedDict):
  query: str
  query_type: str  # "text" nebo "image"
  image_data: Optional[str] = None
  extracted_text: Optional[str] = None
  medication_info: Optional[Dict] = None
  safety_warnings: List[str] = []
  disclaimer: str = ""

def extract_medication_from_image(state: MedicationState) -> MedicationState:
  """Použít GPT-4 Vision k extrakci informací z obrázku"""
  pass

def search_sukl_database(state: MedicationState) -> MedicationState:
  """Vyhledat v databázi SÚKL pomocí RAG"""
  pass

def add_safety_disclaimers(state: MedicationState) -> MedicationState:
  """Přidat povinná zdravotní upozornění v češtině"""
  state["disclaimer"] = """
  UPOZORNĚNÍ: Tyto informace slouží pouze pro informativní účely a nenahrazují 
  odbornou lékařskou radu, diagnózu nebo léčbu. Vždy se poraďte s kvalifikovaným 
  zdravotnickým odborníkem před užitím jakéhokoliv léku.
  """
  return state

# Sestavení workflow grafu
workflow = StateGraph(MedicationState)
workflow.add_node("extract_image", extract_medication_from_image)
workflow.add_node("search_database", search_sukl_database) 
workflow.add_node("add_disclaimers", add_safety_disclaimers)
workflow.add_edge("extract_image", "search_database")
workflow.add_edge("search_database", "add_disclaimers")
workflow.add_edge("add_disclaimers", END)
```

### Fáze 2: Integrace dat SÚKL & RAG

**2.1 Zpracování dat SÚKL**
```python
# app/data/sukl_processor.py
import pandas as pd
import chardet
from typing import List, Dict

class SUKLDataProcessor:
  def __init__(self):
    self.encoding = 'windows-1250'  # SÚKL používá win-1250
    
  def load_sukl_csv(self, file_path: str) -> pd.DataFrame:
    """Načíst SÚKL CSV data se správným kódováním"""
    try:
      with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        detected_encoding = result['encoding']
      df = pd.read_csv(file_path, encoding=detected_encoding or self.encoding)
      return self._clean_czech_text(df)
    except UnicodeDecodeError:
      df = pd.read_csv(file_path, encoding=self.encoding, errors='ignore')
      return self._clean_czech_text(df)
  
  def _clean_czech_text(self, df: pd.DataFrame) -> pd.DataFrame:
    """Čištění a normalizace českého textu"""
    for col in df.select_dtypes(include=['object']).columns:
      df[col] = df[col].astype(str).str.strip()
    return df
  
  def extract_medication_info(self, df: pd.DataFrame) -> List[Dict]:
    """Extrakce strukturovaných informací o lécích pro embedding"""
    medications = []
    for _, row in df.iterrows():
      med_info = {
        'name': row.get('NAZEV', ''),
        'active_ingredient': row.get('UCINNE_LATKY', ''),
        'strength': row.get('SILA', ''), 
        'form': row.get('LEKOVA_FORMA', ''),
        'manufacturer': row.get('DRZITEL_ROZHODNUTI', ''),
        'registration_number': row.get('REGISTRACNI_CISLO', ''),
        'atc_code': row.get('ATC_KOD', ''),
        'indication': row.get('INDIKACE', ''),
        'contraindication': row.get('KONTRAINDIKACE', ''),
        'side_effects': row.get('NEZADOUCI_UCINKY', ''),
        'interactions': row.get('INTERAKCE', ''),
        'dosage': row.get('DAVKOVANI', ''),
        'price': row.get('CENA', ''),
        'prescription_required': row.get('PREDPISOVOST', '')
      }
      medications.append(med_info)
    return medications
```

**2.2 Nastavení vektorového úložiště (Supabase)**
```python
# app/database/vector_store.py
from supabase import create_client, Client
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
import os

class MedicationVectorStore:
  def __init__(self):
    self.supabase_url = os.getenv("SUPABASE_URL")
    self.supabase_key = os.getenv("SUPABASE_ANON_KEY") 
    self.client: Client = create_client(self.supabase_url, self.supabase_key)
    self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
  def setup_vector_store(self) -> SupabaseVectorStore:
    """Inicializace Supabase vector store pro léková data"""
    return SupabaseVectorStore(
      client=self.client,
      embedding=self.embeddings,
      table_name="medications",
      query_name="match_medications"
    )
  
  def ingest_sukl_data(self, medications: List[Dict]):
    """Ingest dat SÚKL do vektorové databáze"""
    vector_store = self.setup_vector_store()
    documents = []
    for med in medications:
      text_content = f"""
      Název: {med['name']}
      Účinná látka: {med['active_ingredient']}
      Síla: {med['strength']}
      Léková forma: {med['form']}
      Výrobce: {med['manufacturer']}
      Indikace: {med['indication']}
      Kontraindikace: {med['contraindication']}
      Nežádoucí účinky: {med['side_effects']}
      Interakce: {med['interactions']}
      Dávkování: {med['dosage']}
      """
      documents.append({
        'content': text_content,
        'metadata': med
      })
    vector_store.add_documents(documents)
```

### Fáze 3: Integrace AI modelů

**3.1 OpenAI Vision integrace**
```python
# app/ai/vision_processor.py
from openai import OpenAI
import base64
from typing import Optional, Dict
import logging

class VisionProcessor:
  def __init__(self):
    self.client = OpenAI()
    self.model = "gpt-4-vision-preview"
    
  def process_medication_image(self, image_data: str) -> Dict:
    """Zpracování obrázku léku pomocí GPT-4 Vision"""
    try:
      if not image_data.startswith('data:image'):
        image_data = f"data:image/jpeg;base64,{image_data}"
        
      response = self.client.chat.completions.create(
        model=self.model,
        messages=[
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": """
                Analyzujte tento obrázek léku a extrahujte následující informace v češtině:
                1. Název léku (obchodní název)
                2. Účinnou látku (pokud je viditelná)
                3. Sílu/dávkování (mg, ml, atd.)
                4. Lékovou formu (tablety, sirup, atd.)
                5. Výrobce
                6. Registrační číslo (pokud je viditelné)
                
                Odpovězte ve formátu JSON s těmito klíči: name, active_ingredient, strength, form, manufacturer, registration_number, confidence_score.
                Pokud některé informace nejsou jasně viditelné, použijte "není viditelné".
                Přidejte confidence_score od 0.0 do 1.0 pro spolehlivost rozpoznání.
                """
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": image_data
                }
              }
            ]
          }
        ],
        max_tokens=500
      )
      
      content = response.choices[0].message.content
      import json
      result = json.loads(content)
      
      if result.get('confidence_score', 0) < 0.6:
        logging.warning(f"Low confidence score: {result.get('confidence_score')}")
        result['warning'] = "Nízká spolehlivost rozpoznání. Ověřte informace."
        
      return result
      
    except Exception as e:
      logging.error(f"Vision processing error: {str(e)}")
      return {
        'error': 'Chyba při zpracování obrázku',
        'details': str(e),
        'fallback_message': 'Prosím zkuste obrázek s lepším osvětlením nebo jiný úhel.'
      }
  
  def validate_against_sukl(self, vision_result: Dict, vector_store) -> Dict:
    """Validace výsledků vision proti databázi SÚKL"""
    if 'name' not in vision_result or vision_result['name'] == 'není viditelné':
      return vision_result
      
    query = f"název {vision_result['name']} účinná látka {vision_result.get('active_ingredient', '')}"
    similar_meds = vector_store.similarity_search(query, k=3)
    
    if similar_meds:
      vision_result['sukl_matches'] = [doc.metadata for doc in similar_meds]
      vision_result['validated'] = True
    else:
      vision_result['validated'] = False
      vision_result['warning'] = "Lék nebyl nalezen v databázi SÚKL. Ověřte správnost informací."
      
    return vision_result
```

**3.2 Zpracování textových dotazů s RAG**
```python
# app/ai/text_processor.py
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

class TextProcessor:
  def __init__(self, vector_store):
    self.vector_store = vector_store
    self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
  def process_text_query(self, query: str) -> Dict:
    """Zpracování textového dotazu na lék"""
    
    prompt_template = """
    Jste odborný farmaceutický asistent pro české léky. Odpovězte na otázku na základě poskytnutých informací z databáze SÚKL.

    Kontext z databáze:
    {context}

    Otázka: {question}

    Instrukce pro odpověď:
    1. Odpovězte pouze v češtině
    2. Použijte pouze informace z poskytnutého kontextu
    3. Pokud informace nejsou k dispozici, jasně to uveďte
    4. Zahrňte relevantní bezpečnostní upozornění
    5. Strukturujte odpověď přehledně (účinná látka, indikace, dávkování, atd.)
    6. Nikdy neposkytujte diagnózy nebo doporučení léčby
    
    Odpověď:
    """
    
    prompt = PromptTemplate(
      template=prompt_template,
      input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
      llm=self.llm,
      chain_type="stuff",
      retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
      chain_type_kwargs={"prompt": prompt}
    )
    
    try:
      result = qa_chain.run(query)
      
      disclaimer = """
      
      ⚠️ DŮLEŽITÉ UPOZORNĚNÍ:
      Tyto informace slouží pouze pro informativní účely a nenahrazují odbornou lékařskou radu, 
      diagnózu nebo léčbu. Před užitím jakéhokoliv léku se vždy poraďte s lékařem nebo lékárníkem.
      """
      
      return {
        'answer': result + disclaimer,
        'sources': [doc.metadata.get('name', 'Neznámý zdroj') 
               for doc in self.vector_store.similarity_search(query, k=3)],
        'confidence': 'high' if len(result) > 100 else 'medium'
      }
      
    except Exception as e:
      logging.error(f"Text processing error: {str(e)}")
      return {
        'error': 'Chyba při zpracování dotazu',
        'details': str(e),
        'fallback_message': 'Prosím zkuste přeformulovat dotaz nebo kontaktujte lékárnu.'
      }
```

### Fáze 4: Frontend Next.js PWA

**4.1 Inicializace projektu**
```bash
# Inicializace Next.js s PWA
npx create-next-app@latest pillsee-frontend --typescript --tailwind --eslint --app
cd pillsee-frontend
npm install next-pwa @types/node
npm install @shadcn/ui lucide-react class-variance-authority clsx tailwind-merge
npm install react-camera-pro react-dropzone
```

**4.2 Konfigurace PWA**
```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development'
})

module.exports = withPWA({
  reactStrictMode: true,
  swcMinify: true,
  images: {
  domains: ['localhost'],
  },
})
```

```json
// public/manifest.json
{
  "name": "PillSee - Informace o lécích",
  "short_name": "PillSee",
  "description": "Anonymní AI asistent pro informace o českých lécích",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2563eb",
  "orientation": "portrait",
  "categories": ["medical", "health"],
  "lang": "cs-CZ",
  "icons": [
  {
    "src": "/icon-192.png",
    "sizes": "192x192",
    "type": "image/png"
  },
  {
    "src": "/icon-512.png", 
    "sizes": "512x512",
    "type": "image/png"
  }
  ]
}
```

**4.3 Hlavní chat rozhraní**
```tsx
// app/page.tsx
'use client'

import { useState, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Camera, Send, Upload } from 'lucide-react'
import CameraCapture from '@/components/CameraCapture'
import MessageList from '@/components/MessageList'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  image?: string
  timestamp: Date
}

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showCamera, setShowCamera] = useState(false)

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
  const newMessage: Message = {
    ...message,
    id: Date.now().toString(),
    timestamp: new Date()
  }
  setMessages(prev => [...prev, newMessage])
  }

  const handleTextSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  if (!input.trim()) return

  addMessage({ type: 'user', content: input })
  setIsLoading(true)

  try {
    const response = await fetch('/api/query/text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: input })
    })

    const data = await response.json()
    
    if (data.error) {
    addMessage({ 
      type: 'assistant', 
      content: `Omlouvám se, nastala chyba: ${data.error}` 
    })
    } else {
    addMessage({ 
      type: 'assistant', 
      content: data.answer 
    })
    }
  } catch (error) {
    addMessage({ 
    type: 'assistant', 
    content: 'Nastala chyba při komunikaci se serverem. Zkuste to prosím znovu.' 
    })
  } finally {
    setIsLoading(false)
    setInput('')
  }
  }

  const handleImageCapture = async (imageData: string) => {
  setShowCamera(false)
  
  addMessage({ 
    type: 'user', 
    content: 'Vyfotil jsem lék', 
    image: imageData 
  })
  setIsLoading(true)

  try {
    const response = await fetch('/api/query/image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      image_data: imageData.split(',')[1]
    })
    })

    const data = await response.json()
    
    if (data.error) {
    addMessage({ 
      type: 'assistant', 
      content: `Nepodařilo se rozpoznat lék: ${data.error}` 
    })
    } else {
    const medicationInfo = formatMedicationInfo(data)
    addMessage({ 
      type: 'assistant', 
      content: medicationInfo 
    })
    }
  } catch (error) {
    addMessage({ 
    type: 'assistant', 
    content: 'Nastala chyba při zpracování obrázku. Zkuste to prosím znovu s lepším osvětlením.' 
    })
  } finally {
    setIsLoading(false)
  }
  }

  const formatMedicationInfo = (data: any) => {
  let info = `**${data.name || 'Neznámý lék'}**\n\n`
  
  if (data.active_ingredient && data.active_ingredient !== 'není viditelné') {
    info += `**Účinná látka:** ${data.active_ingredient}\n`
  }
  if (data.strength && data.strength !== 'není viditelné') {
    info += `**Síla:** ${data.strength}\n`
  }
  if (data.form && data.form !== 'není viditelné') {
    info += `**Léková forma:** ${data.form}\n`
  }
  if (data.manufacturer && data.manufacturer !== 'není viditelné') {
    info += `**Výrobce:** ${data.manufacturer}\n`
  }
  
  if (data.confidence_score) {
    const confidence = Math.round(data.confidence_score * 100)
    info += `\n**Spolehlivost rozpoznání:** ${confidence}%\n`
  }
  
  if (data.warning) {
    info += `\n⚠️ **Upozornění:** ${data.warning}\n`
  }
  
  info += `\n---\n**DŮLEŽITÉ UPOZORNĚNÍ:**\nTyto informace slouží pouze pro informativní účely a nenahrazují odbornou lékařskou radu. Před užitím se vždy poraďte s lékařem nebo lékárníkem.`
  
  return info
  }

  return (
  <div className="min-h-screen bg-gray-50">
    <div className="container mx-auto px-4 py-8 max-w-4xl">
    <div className="text-center mb-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">
      💊 PillSee
      </h1>
      <p className="text-gray-600">
      Anonymní AI asistent pro informace o českých lécích
      </p>
    </div>

    <Card className="mb-4 p-4">
      <MessageList messages={messages} isLoading={isLoading} />
    </Card>

    <div className="space-y-4">
      <form onSubmit={handleTextSubmit} className="flex gap-2">
      <Input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Zeptejte se na lék (např. 'Co je to Paralen?')"
        className="flex-1"
        disabled={isLoading}
      />
      <Button type="submit" disabled={isLoading || !input.trim()}>
        <Send className="w-4 h-4" />
      </Button>
      </form>

      <div className="flex gap-2 justify-center">
        <Button 
        onClick={() => setShowCamera(true)}
        variant="outline"
        className="flex-1 max-w-xs"
        >
        <Camera className="w-4 h-4 mr-2" />
        Vyfotit lék
        </Button>
      </div>
    </div>

    {showCamera && (
      <CameraCapture 
      onCapture={handleImageCapture}
      onClose={() => setShowCamera(false)}
      />
    )}
    </div>
  </div>
  )
}
```

**4.4 Komponenta pro kameru**
```tsx
// components/CameraCapture.tsx
'use client'

import { useRef, useCallback } from 'react'
import { Camera } from 'react-camera-pro'
import { Button } from "@/components/ui/button"
import { X, Camera as CameraIcon } from 'lucide-react'

interface CameraCaptureProps {
  onCapture: (imageData: string) => void
  onClose: () => void
}

export default function CameraCapture({ onCapture, onClose }: CameraCaptureProps) {
  const camera = useRef<any>(null)

  const takePhoto = useCallback(() => {
  if (camera.current) {
    const imageData = camera.current.takePhoto()
    onCapture(imageData)
  }
  }, [onCapture])

  return (
  <div className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center">
    <div className="relative w-full h-full max-w-lg max-h-[80vh] bg-white rounded-lg overflow-hidden">
    <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-black bg-opacity-50">
      <div className="flex justify-between items-center">
      <h3 className="text-white font-semibold">Vyfotit obal léku</h3>
      <Button 
        onClick={onClose}
        variant="ghost" 
        size="sm"
        className="text-white hover:bg-white hover:bg-opacity-20"
      >
        <X className="w-4 h-4" />
      </Button>
      </div>
    </div>

    <div className="w-full h-full">
      <Camera 
      ref={camera}
      aspectRatio={4/3}
      facingMode="environment"
      errorMessages={{
        noCameraAccessible: 'Kamera není dostupná. Zkontrolujte oprávnění.',
        permissionDenied: 'Povolte přístup ke kameře v nastavení prohlížeče.',
        switchCamera: 'Přepnout kameru',
        canvas: 'Canvas není podporován',
      }}
      />
    </div>

    <div className="absolute bottom-0 left-0 right-0 p-4 bg-black bg-opacity-50">
      <div className="flex justify-center">
      <Button 
        onClick={takePhoto}
        size="lg"
        className="bg-blue-600 hover:bg-blue-700 text-white rounded-full w-16 h-16"
      >
        <CameraIcon className="w-6 h-6" />
      </Button>
      </div>
      <p className="text-white text-sm text-center mt-2">
      Zaměřte kameru na obal léku a stiskněte tlačítko
      </p>
    </div>
    </div>
  </div>
  )
}
```

### Fáze 5: Bezpečnost & compliance

**5.1 Anonymní správa relací**
```tsx
// utils/session.ts
interface SessionData {
  sessionId: string
  messages: Message[]
  createdAt: Date
  lastActivity: Date
}

export class AnonymousSessionManager {
  private readonly SESSION_KEY = 'pillsee_session'
  private readonly SESSION_TIMEOUT = 30 * 60 * 1000 // 30 minut

  getSession(): SessionData | null {
  try {
    const sessionData = sessionStorage.getItem(this.SESSION_KEY)
    if (!sessionData) return null

    const session = JSON.parse(sessionData) as SessionData
    
    if (Date.now() - new Date(session.lastActivity).getTime() > this.SESSION_TIMEOUT) {
    this.clearSession()
    return null
    }

    return session
  } catch {
    this.clearSession()
    return null
  }
  }

  saveSession(messages: Message[]): void {
  const session: SessionData = {
    sessionId: this.generateSessionId(),
    messages,
    createdAt: new Date(),
    lastActivity: new Date()
  }

  sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(session))
  }

  clearSession(): void {
  sessionStorage.removeItem(this.SESSION_KEY)
  }

  private generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
}
```

**5.2 GDPR komponenta**
```tsx
// components/GDPRNotice.tsx
'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export default function GDPRNotice() {
  const [showNotice, setShowNotice] = useState(false)

  useEffect(() => {
  const hasConsented = localStorage.getItem('pillsee_gdpr_consent')
  if (!hasConsented) {
    setShowNotice(true)
  }
  }, [])

  const acceptConsent = () => {
  localStorage.setItem('pillsee_gdpr_consent', 'accepted')
  localStorage.setItem('pillsee_gdpr_date', new Date().toISOString())
  setShowNotice(false)
  }

  if (!showNotice) return null

  return (
  <div className="fixed bottom-4 left-4 right-4 z-50">
    <Card className="p-4 bg-white shadow-lg border border-gray-200">
    <div className="text-sm space-y-3">
      <h3 className="font-semibold">Ochrana soukromí</h3>
      <p className="text-gray-600">
      PillSee je anonymní aplikace, která neukládá žádné osobní údaje. 
      Používáme pouze sessionStorage pro dočasné ukládání konverzace během relace 
      a localStorage pro zapamatování tohoto souhlasu.
      </p>
      <p className="text-gray-600">
        <strong>Co neděláme:</strong> Nesledujeme vás, neukládáme historii, 
        nesbíráme osobní údaje ani IP adresy.
      </p>
      <div className="flex gap-2">
      <Button onClick={acceptConsent} className="flex-1">
        Rozumím a souhlasím
      </Button>
      </div>
    </div>
    </Card>
  </div>
  )
}
```

## Validační brány

### Backend validace
```bash
# Kvalita kódu a typová kontrola
cd pillsee-backend
ruff check --fix .
mypy app/
black app/

# Jednotkové testy
uv run pytest tests/ -v --cov=app

# Integrační testy
uv run pytest tests/integration/ -v

# API testy s českými scénáři
uv run pytest tests/api/ -k "test_czech_medication" -v
```

### Frontend validace
```bash
# TypeScript a lint
cd pillsee-frontend
npm run type-check
npm run lint
npm run build

# Komponentové testy
npm test

# PWA testy
npm run test:pwa

# Testy přístupnosti
npm run test:a11y
```

### End-to-End validace
```bash
# Test rozpoznání českých léků
pytest tests/e2e/test_medication_recognition.py

# Test GDPR compliance
pytest tests/e2e/test_gdpr_compliance.py

# Výkonnostní testy (mobilní 3G simulace)
pytest tests/performance/test_mobile_performance.py
```

## Seznam implementačních úkolů (řazeno)

1. **Základ backendu**
   - [ ] Nastavit FastAPI projekt a závislosti
   - [ ] Implementovat rate limiting a CORS
   - [ ] Vytvořit Pydantic modely pro request/response

2. **Integrace dat SÚKL**
   - [ ] Stáhnout a zpracovat SÚKL CSV (win-1250)
   - [ ] Nastavit Supabase + pgvector
   - [ ] Pipeline ingestu lékových dat
   - [ ] Embeddingy pro českou farmaceutickou terminologii

3. **LangGraph workflow**
   - [ ] Návrh stavového modelu dotazů
   - [ ] Implementovat uzly (obrázek, databáze, bezpečnost)
   - [ ] Logika směrování text vs obrázek

4. **Integrace AI modelů**
   - [ ] GPT-4 Vision pro rozpoznávání obalů
   - [ ] RAG pipeline s českými daty
   - [ ] Skórování spolehlivosti + validace v SÚKL
   - [ ] Error handling pro selhání AI

5. **Frontend PWA**
   - [ ] Inicializace Next.js 14 + PWA
   - [ ] Responzivní mobile-first UI (Tailwind)
   - [ ] Komponenta kamery
   - [ ] Chat rozhraní

6. **Bezpečnost & compliance**
   - [ ] Anonymní session (sessionStorage)
   - [ ] GDPR souhlas
   - [ ] Zdravotní disclaimery
   - [ ] Validace a sanitace vstupů

7. **Testování & validace**
   - [ ] Jednotkové testy
   - [ ] Test přesnosti rozpoznání léků
   - [ ] Kontrola GDPR
   - [ ] Výkon na mobilních sítích
   - [ ] E2E scénáře

8. **Nasazení & monitoring**
   - [ ] Backend na Vercel s env proměnnými
   - [ ] Frontend PWA nasazení
   - [ ] Monitoring výkonu a chyb
   - [ ] CORS + bezpečnostní hlavičky

## Kritické poznámky k implementaci

### Čeština & medicínská specifičnost
- **Kódování**: SÚKL → windows-1250
- **Diakritika**: Správné zacházení s (ě, š, č, ř, ž, ý, á, í, é, ů, ú)
- **Terminologie**: Konzistentní odborné názvy
- **Legální požadavky**: Povinné disclaimery ve všech odpovědích

### Soukromí & bezpečnost
- **Žádné sledování**: Nepoužívat persistentní identifikaci
- **Anonymní relace**: Pouze sessionStorage (ne historie)
- **GDPR**: Transparentní informování + minimální data
- **Sanitace vstupů**: Obrázky a text validovat

### Výkonové požadavky
- **Latence**: Text < 2s, obrázek < 3s
- **Mobilní optimalizace**: 3G, slabší zařízení
- **Caching**: Populární léky cache, pravidelný refresh
- **Graceful degradation**: Při výpadku externích služeb

### Časté chyby k vyhnutí
- **Nepoužívat localStorage** pro obsah konverzací
- **Neimplementovat autentizaci**
- **Neukládat historii** mimo dočasné relace
- **Nevynechávat disclaimery**
- **Nehardcodovat lékové informace**
- **Nepoužívat OCR** místo vision modelů
- **Neignorovat mobilní UX**
- **Neangličtina** v odpovědích – vždy česky

## Kontrolní seznam kvality

- [ ] Kompletní kontext (SÚKL formát, čeština, compliance)
- [ ] Spustitelné validační brány
- [ ] Ověřené vzory (FastAPI + LangGraph, PWA best practices)
- [ ] Jasná posloupnost úkolů
- [ ] Dokumentované scénáře selhání
- [ ] Zahrnuty disclaimery a GDPR
- [ ] Výkonové cíle definované a testovatelné
- [ ] Bezpečnostní aspekty integrovány

## Skóre důvěry: 9/10

Tento PRP poskytuje komplexní podklad pro implementaci PillSee s:
- Detailní technickou implementací a ukázkami kódu
- Správnou prací s českými lékovými daty a terminologií
- Souladem s GDPR a zdravotní legislativou
- Mobile-first PWA architekturou s offline podporou
- Robustním error handlingem a bezpečnostními prvky
- Důkladným testovacím a validačním rámcem

Vysoké skóre reflektuje hloubku výzkumu, konkrétní příklady, kompletní odkazy a zohlednění českých specifik pro lékový AI asistent.
