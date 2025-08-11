'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Download, X, Smartphone, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{outcome: 'accepted' | 'dismissed'}>
}

export default function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [showPrompt, setShowPrompt] = useState(false)
  const [isInstalled, setIsInstalled] = useState(false)

  useEffect(() => {
    // Kontrola zda už není nainstalováno
    const checkIfInstalled = () => {
      return window.matchMedia('(display-mode: standalone)').matches ||
             'standalone' in window.navigator ||
             document.referrer.includes('android-app://') ||
             window.navigator.userAgent.includes('wv') // WebView
    }

    if (checkIfInstalled()) {
      setIsInstalled(true)
      return
    }

    // Listener pro beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      const event = e as BeforeInstallPromptEvent
      
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault()
      
      // Save the event so it can be triggered later
      setDeferredPrompt(event)
      
      // Kontrola zda uživatel už prompt neviděl
      const hasSeenPrompt = localStorage.getItem('pillsee_install_prompt_seen')
      const dismissedRecently = localStorage.getItem('pillsee_install_dismissed')
      
      if (!hasSeenPrompt && !dismissedRecently) {
        // Pokazat prompt po krátké chvíli (aby uživatel měl čas aplikaci vyzkoušet)
        setTimeout(() => setShowPrompt(true), 10000) // 10 sekund
      }
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    // Cleanup
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    }
  }, [])

  const handleInstallClick = async () => {
    if (!deferredPrompt) return

    // Show the install prompt
    await deferredPrompt.prompt()

    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice

    if (outcome === 'accepted') {
      console.log('PWA was installed')
      localStorage.setItem('pillsee_installed', 'true')
    } else {
      console.log('PWA installation was dismissed')
      localStorage.setItem('pillsee_install_dismissed', Date.now().toString())
    }

    // Clear the deferred prompt
    setDeferredPrompt(null)
    setShowPrompt(false)
    localStorage.setItem('pillsee_install_prompt_seen', 'true')
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    localStorage.setItem('pillsee_install_prompt_seen', 'true')
    localStorage.setItem('pillsee_install_dismissed', Date.now().toString())
  }

  // Neukázat pokud je už nainstalováno nebo není k dispozici
  if (isInstalled || !deferredPrompt || !showPrompt) {
    return null
  }

  return (
    <div className="fixed top-4 left-4 right-4 z-40 max-w-sm mx-auto">
      <Card className={cn(
        "p-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-2xl border-0",
        "animate-slide-up"
      )}>
        
        <div className="flex items-start gap-3">
          
          {/* Icon */}
          <div className="p-2 bg-white/20 rounded-lg flex-shrink-0">
            <Download className="w-5 h-5" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg mb-1">
              Instalovat PillSee
            </h3>
            <p className="text-blue-100 text-sm mb-3 leading-relaxed">
              Přidejte si PillSee na domovskou obrazovku pro rychlý přístup k informacím o lécích
            </p>

            {/* Benefits */}
            <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
              <div className="flex items-center gap-2">
                <Smartphone className="w-4 h-4 text-blue-200" />
                <span className="text-blue-100">Jako aplikace</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-blue-200" />
                <span className="text-blue-100">Rychlý přístup</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button
                onClick={handleInstallClick}
                size="sm"
                className="bg-white text-blue-700 hover:bg-blue-50 flex-1"
              >
                <Download className="w-4 h-4 mr-2" />
                Instalovat
              </Button>
              
              <Button
                onClick={handleDismiss}
                size="sm"
                variant="ghost"
                className="text-white hover:bg-white/20 p-2"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Tip pro iOS */}
        <div className="mt-3 pt-3 border-t border-white/20">
          <p className="text-xs text-blue-200">
            <strong>iOS tip:</strong> V Safari stiskněte tlačítko "Sdílet" a vyberte "Přidat na domovskou obrazovku"
          </p>
        </div>
      </Card>
    </div>
  )
}