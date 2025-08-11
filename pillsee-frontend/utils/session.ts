/**
 * Anonymní správa relací pro PillSee
 * Používá pouze sessionStorage pro dočasné ukládání
 */

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  image?: string
  timestamp: Date
  metadata?: any
}

interface SessionData {
  sessionId: string
  messages: Message[]
  createdAt: Date
  lastActivity: Date
  queryCount: number
}

export class AnonymousSessionManager {
  private readonly SESSION_KEY = 'pillsee_session'
  private readonly SESSION_TIMEOUT = 30 * 60 * 1000 // 30 minut

  constructor() {
    // Automatické čištění expired sessions
    this.cleanupExpiredSession()
  }

  getSession(): SessionData | null {
    try {
      if (typeof window === 'undefined') return null
      
      const sessionData = sessionStorage.getItem(this.SESSION_KEY)
      if (!sessionData) return null

      const session = JSON.parse(sessionData) as SessionData
      
      // Konverze string dates zpět na Date objekty
      session.createdAt = new Date(session.createdAt)
      session.lastActivity = new Date(session.lastActivity)
      session.messages = session.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
      
      // Kontrola expirace
      if (Date.now() - session.lastActivity.getTime() > this.SESSION_TIMEOUT) {
        this.clearSession()
        return null
      }

      return session

    } catch (error) {
      console.warn('Chyba při načítání session:', error)
      this.clearSession()
      return null
    }
  }

  saveSession(messages: Message[]): void {
    try {
      if (typeof window === 'undefined') return

      const existingSession = this.getSession()
      
      const session: SessionData = {
        sessionId: existingSession?.sessionId || this.generateSessionId(),
        messages,
        createdAt: existingSession?.createdAt || new Date(),
        lastActivity: new Date(),
        queryCount: messages.filter(m => m.type === 'user').length
      }

      sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(session))
      
    } catch (error) {
      console.warn('Chyba při ukládání session:', error)
    }
  }

  clearSession(): void {
    try {
      if (typeof window === 'undefined') return
      sessionStorage.removeItem(this.SESSION_KEY)
    } catch (error) {
      console.warn('Chyba při mazání session:', error)
    }
  }

  getSessionStats(): {
    hasActiveSession: boolean
    messageCount: number
    queryCount: number
    sessionAge: number | null
  } {
    const session = this.getSession()
    
    if (!session) {
      return {
        hasActiveSession: false,
        messageCount: 0,
        queryCount: 0,
        sessionAge: null
      }
    }

    return {
      hasActiveSession: true,
      messageCount: session.messages.length,
      queryCount: session.queryCount,
      sessionAge: Date.now() - session.createdAt.getTime()
    }
  }

  private generateSessionId(): string {
    // Anonymní session ID bez osobních údajů
    const timestamp = Date.now()
    const random = Math.random().toString(36).substr(2, 9)
    return `session_${timestamp}_${random}`
  }

  private cleanupExpiredSession(): void {
    const session = this.getSession()
    if (!session) {
      // Session se již vyčistila v getSession()
      return
    }
  }

  // Utility pro export/import session (pro debugging)
  exportSession(): string | null {
    const session = this.getSession()
    if (!session) return null
    
    // Anonymizované informace pro export
    return JSON.stringify({
      messageCount: session.messages.length,
      queryCount: session.queryCount,
      sessionAge: Date.now() - session.createdAt.getTime(),
      lastActivity: session.lastActivity
    })
  }
}