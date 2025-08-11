'use client'

import { useRef, useCallback, useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { X, Camera as CameraIcon, RotateCcw, Zap, ZapOff } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CameraCaptureProps {
  onCapture: (imageData: string) => void
  onClose: () => void
}

export default function CameraCapture({ onCapture, onClose }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [hasFlash, setHasFlash] = useState(false)
  const [isFlashOn, setIsFlashOn] = useState(false)
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment')
  const [error, setError] = useState<string | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // Inicializace kamery
  useEffect(() => {
    startCamera()
    return () => {
      stopCamera()
    }
  }, [facingMode])

  const startCamera = async () => {
    try {
      setError(null)
      
      // Zastavit předchozí stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }

      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
          aspectRatio: { ideal: 4/3 }
        },
        audio: false
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
        setIsStreaming(true)
      }

      // Kontrola podpory blesku
      const videoTrack = stream.getVideoTracks()[0]
      const capabilities = videoTrack.getCapabilities?.()
      setHasFlash(!!(capabilities as any)?.torch)

    } catch (err: any) {
      console.error('Camera error:', err)
      
      let errorMessage = 'Nepodařilo se spustit kameru'
      
      if (err.name === 'NotAllowedError') {
        errorMessage = 'Přístup ke kameře byl zamítnut. Povolte přístup v nastavení prohlížeče.'
      } else if (err.name === 'NotFoundError') {
        errorMessage = 'Kamera nebyla nalezena. Zkontrolujte připojení kamery.'
      } else if (err.name === 'OverconstrainedError') {
        errorMessage = 'Kamera nepodporuje požadované nastavení.'
      }
      
      setError(errorMessage)
      setIsStreaming(false)
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    setIsStreaming(false)
  }

  const toggleFlash = async () => {
    try {
      if (!streamRef.current || !hasFlash) return

      const videoTrack = streamRef.current.getVideoTracks()[0]
      await videoTrack.applyConstraints({
        advanced: [{ torch: !isFlashOn }] as any
      })
      
      setIsFlashOn(!isFlashOn)
    } catch (err) {
      console.warn('Flash toggle failed:', err)
    }
  }

  const switchCamera = () => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user')
  }

  const takePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !isStreaming) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    if (!ctx) return

    // Nastavit rozměry canvas podle videa
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Nakreslit aktuální frame z videa
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Převést na base64
    const imageData = canvas.toDataURL('image/jpeg', 0.8)

    // Validace velikosti
    const sizeInMB = (imageData.length * 0.75) / (1024 * 1024) // Přibližný výpočet
    if (sizeInMB > 10) {
      setError('Obrázek je příliš velký (max 10MB). Zkuste nižší rozlišení.')
      return
    }

    onCapture(imageData)
  }, [onCapture, isStreaming])

  const handleClose = () => {
    stopCamera()
    onClose()
  }

  return (
    <div className="camera-overlay animate-fade-in">
      <div className="camera-container">
        
        {/* Header s ovládáním */}
        <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-gradient-to-b from-black/50 to-transparent">
          <div className="flex justify-between items-center">
            <h3 className="text-white font-semibold">Vyfotit obal léku</h3>
            
            <div className="flex gap-2">
              {/* Flash toggle */}
              {hasFlash && (
                <Button 
                  onClick={toggleFlash}
                  variant="ghost" 
                  size="sm"
                  className="text-white hover:bg-white/20 p-2"
                  disabled={!isStreaming}
                >
                  {isFlashOn ? 
                    <Zap className="w-5 h-5 fill-current" /> : 
                    <ZapOff className="w-5 h-5" />
                  }
                </Button>
              )}
              
              {/* Camera switch */}
              <Button 
                onClick={switchCamera}
                variant="ghost" 
                size="sm"
                className="text-white hover:bg-white/20 p-2"
                disabled={!isStreaming}
              >
                <RotateCcw className="w-5 h-5" />
              </Button>
              
              {/* Close button */}
              <Button 
                onClick={handleClose}
                variant="ghost" 
                size="sm"
                className="text-white hover:bg-white/20 p-2"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Video stream */}
        <div className="relative w-full h-full">
          {error ? (
            <div className="flex flex-col items-center justify-center h-full p-6 text-center">
              <CameraIcon className="w-16 h-16 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2 text-gray-700">
                Problém s kamerou
              </h3>
              <p className="text-gray-600 mb-4 max-w-sm">
                {error}
              </p>
              <div className="flex gap-2">
                <Button onClick={startCamera} variant="outline">
                  Zkusit znovu
                </Button>
                <Button onClick={handleClose} variant="ghost">
                  Zrušit
                </Button>
              </div>
            </div>
          ) : (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              
              {/* Camera overlay guides */}
              <div className="absolute inset-0 pointer-events-none">
                {/* Focus area indicator */}
                <div className="absolute inset-4 border-2 border-white/50 rounded-lg">
                  <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-white rounded-tl-lg" />
                  <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-white rounded-tr-lg" />
                  <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-white rounded-bl-lg" />
                  <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-white rounded-br-lg" />
                </div>
                
                {/* Instructions */}
                <div className="absolute bottom-20 left-4 right-4 text-center">
                  <p className="text-white text-sm bg-black/50 rounded-lg px-3 py-2">
                    Zaměřte kameru na obal léku a ujistěte se, že je text čitelný
                  </p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Controls */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/50 to-transparent">
          <div className="flex justify-center items-center">
            <Button 
              onClick={takePhoto}
              disabled={!isStreaming || !!error}
              size="lg"
              className={cn(
                "bg-blue-600 hover:bg-blue-700 text-white rounded-full w-20 h-20 p-0",
                "disabled:bg-gray-400 disabled:cursor-not-allowed",
                "transition-all duration-200 hover:scale-105 active:scale-95"
              )}
            >
              <CameraIcon className="w-8 h-8" />
            </Button>
          </div>
          
          <p className="text-white text-sm text-center mt-3">
            {isStreaming ? 
              "Stiskněte tlačítko pro vyfocení" : 
              "Připravuje se kamera..."
            }
          </p>
        </div>

        {/* Hidden canvas pro image capture */}
        <canvas
          ref={canvasRef}
          className="hidden"
        />
      </div>
    </div>
  )
}