'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Shield, Eye, Database, Clock, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function GDPRNotice() {
  const [showNotice, setShowNotice] = useState(false)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Kontrola pouze po načtení na klientu
    const hasConsented = typeof window !== 'undefined' && 
      localStorage.getItem('pillsee_gdpr_consent')
    
    if (!hasConsented) {
      setShowNotice(true)
      // Delay pro smooth animation
      setTimeout(() => setIsVisible(true), 100)
    }
  }, [])

  const acceptConsent = () => {
    try {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      localStorage.setItem('pillsee_gdpr_date', new Date().toISOString())
      localStorage.setItem('pillsee_gdpr_version', '1.0')
      
      setIsVisible(false)
      // Wait for animation then hide
      setTimeout(() => setShowNotice(false), 300)
    } catch (error) {
      console.warn('Cannot save GDPR consent:', error)
      // Pokud selže localStorage, aspoň skryjeme notice
      setIsVisible(false)
      setTimeout(() => setShowNotice(false), 300)
    }
  }

  const showDetails = () => {
    // Pro podrobnosti by se otevřel modal nebo redirect na privacy policy
    alert('Podrobnosti o ochraně soukromí:\n\n' +
          '• PillSee je zcela anonymní aplikace\n' +
          '• Nesledujeme vaši aktivitu\n' +
          '• Neukládáme osobní údaje\n' +
          '• Konverzace se ukládají pouze v sessionStorage\n' +
          '• Žádné cookies kromě tohoto souhlasu\n' +
          '• Obrázky se zpracovávají a okamžitě mažou\n' +
          '• Žádné analýzy ani tracking\n\n' +
          'Více informací na našich stránkách.')
  }

  if (!showNotice) return null

  return (
    <div className={cn(
      "fixed bottom-4 left-4 right-4 z-50 max-w-md mx-auto transition-all duration-300",
      isVisible ? "transform translate-y-0 opacity-100" : "transform translate-y-full opacity-0"
    )}>
      <Card className="p-4 bg-white shadow-2xl border-2 border-blue-100 animate-slide-up">
        
        {/* Header */}
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Shield className="w-5 h-5 text-blue-600" />
          </div>
          <h3 className="font-bold text-gray-900 text-lg">
            Ochrana soukromí
          </h3>
        </div>

        {/* Content */}
        <div className="space-y-3 text-sm text-gray-700 mb-4">
          
          <p className="font-medium text-blue-800 bg-blue-50 p-3 rounded-lg">
            🔒 PillSee je zcela anonymní aplikace
          </p>

          {/* Privacy highlights */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            
            <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg">
              <Eye className="w-4 h-4 text-green-600 flex-shrink-0" />
              <span className="text-green-800">Žádné sledování</span>
            </div>
            
            <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg">
              <Database className="w-4 h-4 text-green-600 flex-shrink-0" />
              <span className="text-green-800">Žádná data</span>
            </div>
            
            <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg">
              <Clock className="w-4 h-4 text-green-600 flex-shrink-0" />
              <span className="text-green-800">Jen session</span>
            </div>
            
            <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg">
              <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
              <span className="text-green-800">GDPR OK</span>
            </div>
          </div>

          <p className="text-gray-600 leading-relaxed">
            Používáme pouze <strong>sessionStorage</strong> pro dočasné ukládání konverzace 
            a <strong>localStorage</strong> pro zapamatování tohoto souhlasu.
          </p>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <p className="text-amber-800 text-xs">
              <strong>Co neděláme:</strong> Nesledujeme vás, neukládáme historii, 
              nesbíráme osobní údaje, IP adresy ani žádné identifikátory.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          <Button 
            onClick={acceptConsent} 
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          >
            <CheckCircle className="w-4 h-4 mr-2" />
            Rozumím a souhlasím
          </Button>
          
          <Button 
            onClick={showDetails}
            variant="ghost" 
            size="sm"
            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
          >
            Podrobnosti o ochraně soukromí
          </Button>
        </div>

        {/* Legal info */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            PillSee v1.0 • Anonymní AI asistent • České léky
          </p>
        </div>
      </Card>
    </div>
  )
}