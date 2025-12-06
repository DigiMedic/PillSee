'use client'

import { useEffect, useRef } from 'react'
import { User, Bot, Loader2, Camera, AlertCircle, CheckCircle, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

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

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll na nejnovější zprávu
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const formatMessageContent = (content: string) => {
    // Převod Markdown-style formátování na HTML
    return content
      .split('\n')
      .map(line => {
        // Bold text **text**
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        
        // Emojis pro lepší vizuální rozlišení
        line = line.replace(/^(💊|🧪|⚡|📋|🏭|🎯|💉|⚠️|🔴|📝|💰)/g, '<span class="inline-block w-6">$1</span>')
        
        return line
      })
      .join('<br />')
  }

  const getConfidenceColor = (confidence?: string) => {
    switch (confidence) {
      case 'high':
        return 'text-green-600'
      case 'medium':
        return 'text-yellow-600'
      case 'low':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getConfidenceIcon = (confidence?: string) => {
    switch (confidence) {
      case 'high':
        return <CheckCircle className="w-4 h-4" />
      case 'medium':
        return <Info className="w-4 h-4" />
      case 'low':
        return <AlertCircle className="w-4 h-4" />
      default:
        return null
    }
  }

  return (
    <div 
      ref={containerRef}
      className="flex flex-col space-y-4 max-h-[60vh] overflow-y-auto scrollbar-hide p-2"
    >
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex gap-3 animate-slide-up",
            message.type === 'user' ? 'flex-row-reverse' : 'flex-row'
          )}
        >
          {/* Avatar */}
          <div className={cn(
            "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
            message.type === 'user' 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-100 text-gray-700'
          )}>
            {message.type === 'user' ? (
              <User className="w-5 h-5" />
            ) : (
              <Bot className="w-5 h-5" />
            )}
          </div>

          {/* Message bubble */}
          <div className={cn(
            "flex flex-col max-w-[80%] min-w-[100px]",
            message.type === 'user' ? 'items-end' : 'items-start'
          )}>
            
            {/* Message content */}
            <div className={cn(
              "rounded-2xl px-4 py-3 shadow-sm",
              message.type === 'user'
                ? "bg-blue-600 text-white rounded-br-lg"
                : "bg-white border border-gray-200 text-gray-900 rounded-bl-lg"
            )}>
              
              {/* Image pokud existuje */}
              {message.image && (
                <div className="mb-3">
                  <div className="flex items-center gap-2 mb-2">
                    <Camera className="w-4 h-4" />
                    <span className="text-sm opacity-80">Obrázek léku</span>
                  </div>
                  <img
                    src={message.image}
                    alt="Obrázek léku"
                    className="max-w-[200px] max-h-[200px] object-contain rounded-lg border"
                  />
                </div>
              )}
              
              {/* Text content */}
              <div 
                className="czech-text text-sm leading-relaxed"
                dangerouslySetInnerHTML={{ 
                  __html: formatMessageContent(message.content) 
                }}
              />
            </div>

            {/* Metadata */}
            {message.metadata && message.type === 'assistant' && (
              <div className="flex flex-wrap gap-2 mt-2 text-xs text-gray-500">
                
                {/* Confidence badge */}
                {message.metadata.confidence && (
                  <div className={cn(
                    "flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100",
                    getConfidenceColor(message.metadata.confidence)
                  )}>
                    {getConfidenceIcon(message.metadata.confidence)}
                    <span className="capitalize">
                      {message.metadata.confidence === 'high' ? 'Vysoká spolehlivost' :
                       message.metadata.confidence === 'medium' ? 'Střední spolehlivost' :
                       message.metadata.confidence === 'low' ? 'Nízká spolehlivost' :
                       message.metadata.confidence}
                    </span>
                  </div>
                )}

                {/* Sources */}
                {message.metadata.sources && message.metadata.sources.length > 0 && (
                  <div className="text-xs text-gray-400">
                    Zdroj: {message.metadata.sources.join(', ')}
                  </div>
                )}
              </div>
            )}

            {/* Timestamp */}
            <div className="text-xs text-gray-400 mt-1 px-1">
              {message.timestamp.toLocaleTimeString('cs-CZ', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
        </div>
      ))}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex gap-3">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
            <Bot className="w-5 h-5 text-gray-700" />
          </div>
          <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-lg px-4 py-3 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Zpracovávám...</span>
            </div>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  )
}