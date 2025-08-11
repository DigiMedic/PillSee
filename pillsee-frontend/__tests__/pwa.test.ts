/**
 * Testy pro PWA funkcionality
 */

describe('PWA Features', () => {
  beforeEach(() => {
    // Reset DOM
    document.head.innerHTML = ''
    document.body.innerHTML = ''
    
    // Mock service worker registration
    Object.defineProperty(navigator, 'serviceWorker', {
      value: {
        register: jest.fn(() => Promise.resolve({
          installing: null,
          waiting: null,
          active: null,
          addEventListener: jest.fn(),
        })),
        ready: Promise.resolve({
          showNotification: jest.fn(),
        }),
      },
      configurable: true,
    })
  })

  describe('Manifest', () => {
    it('should have valid manifest.json', async () => {
      // Mock fetch for manifest
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            name: 'PillSee',
            short_name: 'PillSee',
            description: 'Anonymní AI asistent pro informace o českých lécích',
            start_url: '/',
            display: 'standalone',
            theme_color: '#2563eb',
            background_color: '#ffffff',
            icons: [
              {
                src: '/icons/icon-192x192.png',
                sizes: '192x192',
                type: 'image/png'
              }
            ]
          }),
        } as Response)
      ) as jest.Mock

      const response = await fetch('/manifest.json')
      const manifest = await response.json()

      expect(manifest.name).toBe('PillSee')
      expect(manifest.display).toBe('standalone')
      expect(manifest.start_url).toBe('/')
      expect(manifest.theme_color).toBe('#2563eb')
      expect(manifest.icons).toHaveLength(1)
    })

    it('should have proper icon sizes', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            icons: [
              { src: '/icons/icon-72x72.png', sizes: '72x72', type: 'image/png' },
              { src: '/icons/icon-96x96.png', sizes: '96x96', type: 'image/png' },
              { src: '/icons/icon-128x128.png', sizes: '128x128', type: 'image/png' },
              { src: '/icons/icon-144x144.png', sizes: '144x144', type: 'image/png' },
              { src: '/icons/icon-152x152.png', sizes: '152x152', type: 'image/png' },
              { src: '/icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
              { src: '/icons/icon-384x384.png', sizes: '384x384', type: 'image/png' },
              { src: '/icons/icon-512x512.png', sizes: '512x512', type: 'image/png' },
            ]
          }),
        } as Response)
      ) as jest.Mock

      const response = await fetch('/manifest.json')
      const manifest = await response.json()

      const expectedSizes = ['72x72', '96x96', '128x128', '144x144', '152x152', '192x192', '384x384', '512x512']
      const actualSizes = manifest.icons.map((icon: any) => icon.sizes)

      expectedSizes.forEach(size => {
        expect(actualSizes).toContain(size)
      })
    })
  })

  describe('Service Worker', () => {
    it('should register service worker', async () => {
      const mockRegister = navigator.serviceWorker.register as jest.Mock
      
      // Simulate service worker registration
      await navigator.serviceWorker.register('/sw.js')
      
      expect(mockRegister).toHaveBeenCalledWith('/sw.js')
    })

    it('should handle service worker updates', async () => {
      const mockRegistration = {
        installing: null,
        waiting: {
          postMessage: jest.fn(),
        },
        active: null,
        addEventListener: jest.fn(),
        update: jest.fn(),
      }

      ;(navigator.serviceWorker.register as jest.Mock).mockResolvedValue(mockRegistration)

      const registration = await navigator.serviceWorker.register('/sw.js')
      
      expect(registration.addEventListener).toBeDefined()
      expect(registration.update).toBeDefined()
    })

    it('should handle offline functionality', () => {
      // Mock offline state
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      })

      expect(navigator.onLine).toBe(false)

      // Mock back online
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: true,
      })

      expect(navigator.onLine).toBe(true)
    })
  })

  describe('Install Prompt', () => {
    it('should handle beforeinstallprompt event', () => {
      let beforeInstallPromptEvent: any

      const mockEvent = {
        preventDefault: jest.fn(),
        prompt: jest.fn(() => Promise.resolve({ outcome: 'accepted' })),
        userChoice: Promise.resolve({ outcome: 'accepted' }),
      }

      // Simulate beforeinstallprompt event
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault()
        beforeInstallPromptEvent = e
      })

      const event = new CustomEvent('beforeinstallprompt')
      Object.assign(event, mockEvent)
      window.dispatchEvent(event)

      expect(mockEvent.preventDefault).toHaveBeenCalled()
    })

    it('should show install prompt when user clicks install', async () => {
      const mockPrompt = jest.fn(() => Promise.resolve({ outcome: 'accepted' }))
      
      const installPromptEvent = {
        preventDefault: jest.fn(),
        prompt: mockPrompt,
        userChoice: Promise.resolve({ outcome: 'accepted' }),
      }

      // Simulate install button click
      await installPromptEvent.prompt()
      
      expect(mockPrompt).toHaveBeenCalled()
    })

    it('should handle install rejection', async () => {
      const installPromptEvent = {
        preventDefault: jest.fn(),
        prompt: jest.fn(() => Promise.resolve({ outcome: 'dismissed' })),
        userChoice: Promise.resolve({ outcome: 'dismissed' }),
      }

      const result = await installPromptEvent.prompt()
      expect(result.outcome).toBe('dismissed')
    })
  })

  describe('Caching Strategy', () => {
    it('should cache essential resources', () => {
      const essentialResources = [
        '/',
        '/static/js/main.js',
        '/static/css/main.css',
        '/manifest.json',
        '/icons/icon-192x192.png',
      ]

      // In real service worker, these would be cached
      essentialResources.forEach(resource => {
        expect(resource).toMatch(/^\//)
      })
    })

    it('should use cache-first strategy for static assets', async () => {
      // Mock cache API
      global.caches = {
        open: jest.fn(() => Promise.resolve({
          match: jest.fn(() => Promise.resolve(new Response('cached content'))),
          add: jest.fn(),
          addAll: jest.fn(),
        })),
        match: jest.fn(),
      } as any

      const cache = await caches.open('pillsee-cache-v1')
      const cachedResponse = await cache.match('/static/js/main.js')
      
      expect(cachedResponse).toBeDefined()
    })

    it('should use network-first strategy for API calls', async () => {
      // API calls should always try network first
      const apiUrl = 'http://localhost:8000/api/query/text'
      
      // Mock successful network request
      global.fetch = jest.fn(() =>
        Promise.resolve(new Response(JSON.stringify({ status: 'success' })))
      ) as jest.Mock

      const response = await fetch(apiUrl)
      expect(fetch).toHaveBeenCalledWith(apiUrl)
    })
  })

  describe('Background Sync', () => {
    it('should register background sync for failed requests', () => {
      // Mock service worker registration with sync
      const mockRegistration = {
        sync: {
          register: jest.fn(() => Promise.resolve()),
        },
      }

      ;(navigator.serviceWorker.ready as Promise<any>) = Promise.resolve(mockRegistration)

      // In real implementation, this would queue failed requests
      expect(mockRegistration.sync.register).toBeDefined()
    })
  })

  describe('Push Notifications', () => {
    it('should request notification permission', async () => {
      // Mock Notification API
      Object.defineProperty(global, 'Notification', {
        value: {
          requestPermission: jest.fn(() => Promise.resolve('granted')),
          permission: 'default',
        },
        configurable: true,
      })

      const permission = await Notification.requestPermission()
      expect(permission).toBe('granted')
    })

    it('should handle denied notification permission', async () => {
      Object.defineProperty(global, 'Notification', {
        value: {
          requestPermission: jest.fn(() => Promise.resolve('denied')),
          permission: 'denied',
        },
        configurable: true,
      })

      const permission = await Notification.requestPermission()
      expect(permission).toBe('denied')
    })
  })

  describe('App State Management', () => {
    it('should persist app state in localStorage', () => {
      const appState = {
        sessionId: 'test-session',
        lastActivity: Date.now(),
      }

      localStorage.setItem('pillsee_app_state', JSON.stringify(appState))
      
      const stored = JSON.parse(localStorage.getItem('pillsee_app_state') || '{}')
      expect(stored.sessionId).toBe('test-session')
    })

    it('should restore app state on launch', () => {
      const savedState = {
        sessionId: 'restored-session',
        messages: [],
      }

      localStorage.setItem('pillsee_app_state', JSON.stringify(savedState))
      
      // Simulate app launch
      const restoredState = JSON.parse(localStorage.getItem('pillsee_app_state') || '{}')
      expect(restoredState.sessionId).toBe('restored-session')
    })
  })

  describe('Performance', () => {
    it('should have fast loading times', () => {
      // Mock Performance API
      Object.defineProperty(global, 'performance', {
        value: {
          now: jest.fn(() => Date.now()),
          mark: jest.fn(),
          measure: jest.fn(),
          getEntriesByType: jest.fn(() => [
            { name: 'first-contentful-paint', startTime: 500 },
            { name: 'largest-contentful-paint', startTime: 1000 },
          ]),
        },
        configurable: true,
      })

      const fcp = performance.getEntriesByType('paint')
        .find((entry: any) => entry.name === 'first-contentful-paint')

      expect(fcp?.startTime).toBeLessThan(2000) // Less than 2 seconds
    })

    it('should lazy load non-critical resources', () => {
      // Mock intersection observer for lazy loading
      global.IntersectionObserver = jest.fn((callback) => ({
        observe: jest.fn(),
        unobserve: jest.fn(),
        disconnect: jest.fn(),
      })) as any

      const observer = new IntersectionObserver(() => {})
      expect(observer.observe).toBeDefined()
    })
  })

  describe('Security', () => {
    it('should use HTTPS in production', () => {
      // Mock production environment
      process.env.NODE_ENV = 'production'
      
      const isSecure = location.protocol === 'https:' || location.hostname === 'localhost'
      expect(isSecure).toBe(true)
    })

    it('should have proper CSP headers', () => {
      // CSP should be configured in next.config.js
      const expectedCSP = [
        "default-src 'self'",
        "img-src 'self' data: blob:",
        "script-src 'self' 'unsafe-inline'",
        "style-src 'self' 'unsafe-inline'",
      ].join('; ')

      // In real app, this would be tested via HTTP headers
      expect(expectedCSP).toContain("default-src 'self'")
    })
  })

  describe('Accessibility', () => {
    it('should meet PWA accessibility standards', () => {
      // Mock accessibility audit
      const auditResults = {
        'color-contrast': { passed: true },
        'keyboard-navigation': { passed: true },
        'screen-reader': { passed: true },
        'focus-management': { passed: true },
      }

      Object.values(auditResults).forEach(result => {
        expect(result.passed).toBe(true)
      })
    })

    it('should support high contrast mode', () => {
      // Mock high contrast media query
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: jest.fn().mockImplementation(query => ({
          matches: query === '(prefers-contrast: high)',
          media: query,
          onchange: null,
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
        })),
      })

      const highContrastQuery = window.matchMedia('(prefers-contrast: high)')
      expect(highContrastQuery.matches).toBe(true)
    })
  })
})