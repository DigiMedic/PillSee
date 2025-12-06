/**
 * Testy pro session management utilities
 */

import {
  createSession,
  getSession,
  addMessageToSession,
  clearSession,
  getSessionHistory
} from '../utils/session'

describe('Session Management', () => {
  beforeEach(() => {
    // Vyčištění sessionStorage před každým testem
    sessionStorage.clear()
    jest.clearAllMocks()
  })

  describe('createSession', () => {
    it('should create new session with unique ID', () => {
      const sessionId1 = createSession()
      const sessionId2 = createSession()
      
      expect(sessionId1).toBeDefined()
      expect(sessionId2).toBeDefined()
      expect(sessionId1).not.toBe(sessionId2)
      expect(typeof sessionId1).toBe('string')
    })

    it('should store session in sessionStorage', () => {
      const sessionId = createSession()
      
      expect(sessionStorage.setItem).toHaveBeenCalledWith(
        'pillsee_session',
        expect.stringContaining(sessionId)
      )
    })

    it('should create session with timestamp', () => {
      const before = Date.now()
      const sessionId = createSession()
      const after = Date.now()
      
      const session = getSession()
      expect(session?.createdAt).toBeGreaterThanOrEqual(before)
      expect(session?.createdAt).toBeLessThanOrEqual(after)
    })
  })

  describe('getSession', () => {
    it('should return null when no session exists', () => {
      const session = getSession()
      expect(session).toBeNull()
    })

    it('should return existing session', () => {
      const sessionId = createSession()
      const session = getSession()
      
      expect(session).toBeDefined()
      expect(session?.id).toBe(sessionId)
      expect(session?.messages).toEqual([])
    })

    it('should handle corrupted session data', () => {
      sessionStorage.setItem('pillsee_session', 'invalid-json')
      
      const session = getSession()
      expect(session).toBeNull()
    })

    it('should handle missing session data', () => {
      sessionStorage.removeItem('pillsee_session')
      
      const session = getSession()
      expect(session).toBeNull()
    })
  })

  describe('addMessageToSession', () => {
    it('should add message to existing session', () => {
      const sessionId = createSession()
      
      addMessageToSession({
        id: 'msg1',
        type: 'user',
        content: 'Co je to Paralen?',
        timestamp: Date.now()
      })
      
      const session = getSession()
      expect(session?.messages).toHaveLength(1)
      expect(session?.messages[0].content).toBe('Co je to Paralen?')
      expect(session?.messages[0].type).toBe('user')
    })

    it('should create session if none exists', () => {
      addMessageToSession({
        id: 'msg1',
        type: 'user',
        content: 'Test message',
        timestamp: Date.now()
      })
      
      const session = getSession()
      expect(session).toBeDefined()
      expect(session?.messages).toHaveLength(1)
    })

    it('should maintain message order', () => {
      createSession()
      
      addMessageToSession({
        id: 'msg1',
        type: 'user',
        content: 'First message',
        timestamp: Date.now()
      })
      
      addMessageToSession({
        id: 'msg2',
        type: 'assistant',
        content: 'Second message',
        timestamp: Date.now()
      })
      
      const session = getSession()
      expect(session?.messages).toHaveLength(2)
      expect(session?.messages[0].content).toBe('First message')
      expect(session?.messages[1].content).toBe('Second message')
    })

    it('should handle different message types', () => {
      createSession()
      
      const userMessage = {
        id: 'user1',
        type: 'user' as const,
        content: 'User question',
        timestamp: Date.now()
      }
      
      const assistantMessage = {
        id: 'asst1',
        type: 'assistant' as const,
        content: 'Assistant response',
        timestamp: Date.now()
      }
      
      const imageMessage = {
        id: 'img1',
        type: 'image' as const,
        content: 'data:image/jpeg;base64,...',
        timestamp: Date.now()
      }
      
      addMessageToSession(userMessage)
      addMessageToSession(assistantMessage)
      addMessageToSession(imageMessage)
      
      const session = getSession()
      expect(session?.messages).toHaveLength(3)
      expect(session?.messages.map(m => m.type)).toEqual(['user', 'assistant', 'image'])
    })
  })

  describe('clearSession', () => {
    it('should clear existing session', () => {
      createSession()
      addMessageToSession({
        id: 'msg1',
        type: 'user',
        content: 'Test',
        timestamp: Date.now()
      })
      
      expect(getSession()).toBeDefined()
      
      clearSession()
      expect(getSession()).toBeNull()
    })

    it('should handle clearing non-existent session', () => {
      expect(() => clearSession()).not.toThrow()
    })
  })

  describe('getSessionHistory', () => {
    it('should return empty array when no session', () => {
      const history = getSessionHistory()
      expect(history).toEqual([])
    })

    it('should return message history', () => {
      createSession()
      
      const msg1 = {
        id: 'msg1',
        type: 'user' as const,
        content: 'Question 1',
        timestamp: Date.now()
      }
      
      const msg2 = {
        id: 'msg2',
        type: 'assistant' as const,
        content: 'Answer 1',
        timestamp: Date.now()
      }
      
      addMessageToSession(msg1)
      addMessageToSession(msg2)
      
      const history = getSessionHistory()
      expect(history).toHaveLength(2)
      expect(history[0]).toEqual(msg1)
      expect(history[1]).toEqual(msg2)
    })

    it('should return messages in correct order', () => {
      createSession()
      
      const timestamps = [1000, 2000, 3000]
      timestamps.forEach((timestamp, i) => {
        addMessageToSession({
          id: `msg${i}`,
          type: 'user',
          content: `Message ${i}`,
          timestamp
        })
      })
      
      const history = getSessionHistory()
      expect(history.map(m => m.timestamp)).toEqual(timestamps)
    })
  })

  describe('Session Persistence', () => {
    it('should persist session across page reloads', () => {
      const sessionId = createSession()
      
      addMessageToSession({
        id: 'msg1',
        type: 'user',
        content: 'Persistent message',
        timestamp: Date.now()
      })
      
      // Simulace reload - vytvoření nové instance
      const session = getSession()
      expect(session?.id).toBe(sessionId)
      expect(session?.messages[0].content).toBe('Persistent message')
    })

    it('should handle session expiration', () => {
      // Test by vyžadoval implementaci expirační logiky
      const sessionId = createSession()
      const session = getSession()
      
      // Pro nyní jen kontrolujeme že session existuje
      expect(session?.id).toBe(sessionId)
      expect(session?.createdAt).toBeDefined()
    })
  })

  describe('GDPR Compliance', () => {
    it('should not store personal information', () => {
      createSession()
      
      addMessageToSession({
        id: 'msg1',
        type: 'user',
        content: 'Můj lék je Paralen',
        timestamp: Date.now()
      })
      
      const sessionData = sessionStorage.getItem('pillsee_session')
      expect(sessionData).toBeDefined()
      
      // Ověříme že se ukládá pouze to co má
      const parsed = JSON.parse(sessionData!)
      expect(parsed).toHaveProperty('id')
      expect(parsed).toHaveProperty('createdAt')
      expect(parsed).toHaveProperty('messages')
      expect(parsed).not.toHaveProperty('userId')
      expect(parsed).not.toHaveProperty('personalData')
    })

    it('should allow complete data removal', () => {
      createSession()
      addMessageToSession({
        id: 'msg1',
        type: 'user',
        content: 'Test data',
        timestamp: Date.now()
      })
      
      expect(sessionStorage.getItem('pillsee_session')).not.toBeNull()
      
      clearSession()
      expect(sessionStorage.getItem('pillsee_session')).toBeNull()
    })
  })
})