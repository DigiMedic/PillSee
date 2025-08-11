'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Camera, Send, Loader2, AlertCircle, Pill } from 'lucide-react'
import CameraCapture from '@/components/CameraCapture'
import MessageList from '@/components/MessageList'
import InstallPrompt from '@/components/InstallPrompt'
import { AnonymousSessionManager } from '@/utils/session'
import { apiCall } from '@/utils/api'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  image?: string
  timestamp: Date
  metadata?: {
    confidence?: string
    sources?: string[]
    medication_info?: any
  }
}

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sessionManager = useRef(new AnonymousSessionManager())

  // Načtení existující session při mount
  useEffect(() => {
    const existingSession = sessionManager.current.getSession()
    if (existingSession?.messages) {
      setMessages(existingSession.messages)
    }
  }, [])

  // Uložení session při změně messages
  useEffect(() => {
    if (messages.length > 0) {
      sessionManager.current.saveSession(messages)
    }
  }, [messages])

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
  }

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setError(null)

    // Přidání user message
    addMessage({ type: 'user', content: userMessage })
    setIsLoading(true)

    try {
      const response = await apiCall('/api/query/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      })

      if (response.error) {
        addMessage({ 
          type: 'assistant', 
          content: `❌ **Chyba:** ${response.error}\n\nProsím zkuste to znovu nebo přeformulujte dotaz.` 
        })
      } else {
        // Strukturování odpovědi
        let content = ''
        const data = response.data

        if (data.answer) {
          // Text response from RAG
          content = data.answer
        } else if (data.medication_info) {
          // Structured medication info
          content = formatMedicationInfo(data.medication_info)
        }

        addMessage({ 
          type: 'assistant', 
          content: content,
          metadata: {
            confidence: data.confidence,
            sources: data.sources,
            medication_info: data.medication_info
          }
        })
      }

      // Přidání disclaimeru pokud existuje
      if (response.disclaimer) {
        addMessage({
          type: 'assistant',
          content: `📋 **Právní upozornění:**\n${response.disclaimer}`
        })
      }

    } catch (error: any) {
      console.error('Text query error:', error)
      setError('Nastala chyba při komunikaci se serverem')
      addMessage({ 
        type: 'assistant', 
        content: '❌ **Chyba spojení:** Nastala chyba při komunikaci se serverem. Zkontrolujte internetové připojení a zkuste to znovu.' 
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleImageCapture = async (imageData: string) => {
    setShowCamera(false)
    setError(null)
    
    // Přidání user message s obrázkem
    addMessage({ 
      type: 'user', 
      content: '📷 Vyfotil jsem obal léku', 
      image: imageData 
    })
    setIsLoading(true)

    try {
      // Odstranění data URL prefixu pro backend
      const base64Image = imageData.includes(',') ? 
        imageData.split(',')[1] : imageData

      const response = await apiCall('/api/query/image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_data: base64Image })
      })

      if (response.error) {
        addMessage({ 
          type: 'assistant', 
          content: `❌ **Nepodařilo se rozpoznat lék:** ${response.error}\n\n💡 **Tipy pro lepší rozpoznání:**\n- Ujistěte se, že je obal léku dobře osvětlen\n- Zkuste fotit přímo shora\n- Odstraňte stíny a odlesky` 
        })
      } else {
        // Formatování informací o léku
        const medicationInfo = formatMedicationInfo(response.data)
        addMessage({ 
          type: 'assistant', 
          content: medicationInfo,
          metadata: {
            confidence: response.data.confidence_score ? 
              (response.data.confidence_score > 0.8 ? 'high' : 
               response.data.confidence_score > 0.6 ? 'medium' : 'low') : 'low',
            medication_info: response.data
          }
        })
      }

      // Disclaimer pro image queries
      if (response.disclaimer) {
        addMessage({
          type: 'assistant',
          content: `📋 **Právní upozornění:**\n${response.disclaimer}`
        })
      }

    } catch (error: any) {
      console.error('Image query error:', error)
      setError('Nastala chyba při zpracování obrázku')
      addMessage({ 
        type: 'assistant', 
        content: '❌ **Chyba zpracování:** Nepodařilo se zpracovat obrázek. Zkontrolujte internetové připojení a zkuste to znovu s jiným obrázkem.' 
      })
    } finally {
      setIsLoading(false)
    }
  }

  const formatMedicationInfo = (data: any): string => {
    if (!data) return 'Nepodařilo se získat informace o léku.'

    let info = ''
    
    // Název a základní info
    if (data.name && data.name !== 'není viditelné') {
      info += `💊 **${data.name}**\n\n`
    }
    
    // Účinná látka
    if (data.active_ingredient && data.active_ingredient !== 'není viditelné') {
      info += `🧪 **Účinná látka:** ${data.active_ingredient}\n`
    }
    
    // Síla a forma
    if (data.strength && data.strength !== 'není viditelné') {
      info += `⚡ **Síla:** ${data.strength}\n`
    }
    if (data.form && data.form !== 'není viditelné') {
      info += `📋 **Léková forma:** ${data.form}\n`
    }
    
    // Výrobce
    if (data.manufacturer && data.manufacturer !== 'není viditelné') {
      info += `🏭 **Výrobce:** ${data.manufacturer}\n`
    }
    
    // Indikace a užití
    if (data.indication) {
      info += `\n🎯 **Indikace:** ${data.indication}\n`
    }
    if (data.dosage) {
      info += `💉 **Dávkování:** ${data.dosage}\n`
    }
    
    // Bezpečnostní informace
    if (data.contraindication) {
      info += `\n⚠️ **Kontraindikace:** ${data.contraindication}\n`
    }
    if (data.side_effects) {
      info += `🔴 **Nežádoucí účinky:** ${data.side_effects}\n`
    }
    if (data.interactions) {
      info += `⚡ **Interakce:** ${data.interactions}\n`
    }
    
    // Praktické informace
    if (data.prescription_required) {
      info += `\n📝 **Předpisovost:** ${data.prescription_required}\n`
    }
    if (data.price) {
      info += `💰 **Orientační cena:** ${data.price}\n`
    }
    
    // Confidence score a varování
    if (data.confidence_score !== undefined) {
      const confidence = Math.round(data.confidence_score * 100)
      info += `\n🎯 **Spolehlivost rozpoznání:** ${confidence}%\n`
    }
    
    if (data.warning) {
      info += `\n⚠️ **Upozornění:** ${data.warning}\n`
    }
    
    return info || 'Nepodařilo se extrahovat informace z obrázku.'
  }

  const clearChat = () => {
    setMessages([])
    sessionManager.current.clearSession()
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        
        {/* Header */}
        <header className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <Pill className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900">
              PillSee
            </h1>
          </div>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Anonymní AI asistent pro informace o českých lécích
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Rozpoznejte léky z obrázků nebo se zeptejte v češtině
          </p>
        </header>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <p className="text-red-700">{error}</p>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ✕
            </Button>
          </div>
        )}

        {/* Chat Interface */}
        <Card className="mb-6 p-6 bg-white/80 backdrop-blur-sm shadow-xl border-0">
          <MessageList messages={messages} isLoading={isLoading} />
          
          {messages.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Pill className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-semibold mb-2">Vítejte v PillSee!</h3>
              <p className="mb-4">Zeptejte se na lék nebo vyfotit jeho obal</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <Camera className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                  <p className="text-sm text-blue-800">Vyfotit obal léku</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <Send className="w-6 h-6 text-green-600 mx-auto mb-2" />
                  <p className="text-sm text-green-800">Zeptat se na lék</p>
                </div>
              </div>
            </div>
          )}
        </Card>

        {/* Input Controls */}
        <div className="space-y-4">
          
          {/* Text Input */}
          <form onSubmit={handleTextSubmit} className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Zeptejte se na lék (např. 'Co je to Paralen 500mg?')"
              className="flex-1 h-12 text-base bg-white/80 backdrop-blur-sm border-gray-200 focus:border-blue-400 focus:ring-blue-400"
              disabled={isLoading}
              maxLength={500}
            />
            <Button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="h-12 px-6 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </form>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button 
              onClick={() => setShowCamera(true)}
              variant="outline"
              disabled={isLoading}
              className="flex-1 h-12 bg-white/80 backdrop-blur-sm border-blue-200 text-blue-700 hover:bg-blue-50"
            >
              <Camera className="w-5 h-5 mr-2" />
              Vyfotit obal léku
            </Button>
            
            {messages.length > 0 && (
              <Button 
                onClick={clearChat}
                variant="outline"
                className="sm:w-auto h-12 bg-white/80 backdrop-blur-sm border-gray-200 text-gray-700 hover:bg-gray-50"
              >
                Vymazat chat
              </Button>
            )}
          </div>
        </div>

        {/* Camera Modal */}
        {showCamera && (
          <CameraCapture 
            onCapture={handleImageCapture}
            onClose={() => setShowCamera(false)}
          />
        )}

        {/* PWA Install Prompt */}
        <InstallPrompt />
      </div>
    </div>
  )
}