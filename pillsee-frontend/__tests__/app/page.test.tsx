/**
 * Testy pro hlavní stránku aplikace
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Page from '../../app/page'

// Mock komponenty
jest.mock('../../components/CameraCapture', () => ({
  CameraCapture: ({ onCapture, isActive }: any) => 
    isActive ? (
      <div data-testid="camera-capture">
        <button onClick={() => onCapture('fake-image-data')}>
          Capture
        </button>
      </div>
    ) : null
}))

jest.mock('../../components/GDPRNotice', () => ({
  GDPRNotice: ({ onAccept }: any) => (
    <div data-testid="gdpr-notice">
      <button onClick={onAccept}>Accept GDPR</button>
    </div>
  )
}))

jest.mock('../../components/MessageList', () => ({
  MessageList: ({ messages }: any) => (
    <div data-testid="message-list">
      {messages.map((msg: any) => (
        <div key={msg.id}>{msg.content}</div>
      ))}
    </div>
  )
}))

jest.mock('../../components/InstallPrompt', () => ({
  InstallPrompt: () => <div data-testid="install-prompt">Install PWA</div>
}))

// Mock API calls
jest.mock('../../utils/api', () => ({
  queryMedicationText: jest.fn(),
  queryMedicationImage: jest.fn(),
}))

// Mock session utils
jest.mock('../../utils/session', () => ({
  createSession: jest.fn(() => 'mock-session-id'),
  getSession: jest.fn(() => null),
  addMessageToSession: jest.fn(),
  clearSession: jest.fn(),
}))

import * as api from '../../utils/api'
import * as session from '../../utils/session'

describe('Main Page', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
    
    // Mock successful API responses
    ;(api.queryMedicationText as jest.Mock).mockResolvedValue({
      status: 'success',
      data: { answer: 'Test response' },
      disclaimer: 'Medical disclaimer'
    })
    
    ;(api.queryMedicationImage as jest.Mock).mockResolvedValue({
      status: 'success',
      data: { name: 'PARALEN 500MG' },
      disclaimer: 'Medical disclaimer'
    })
  })

  it('should render main application interface', async () => {
    render(<Page />)
    
    expect(screen.getByText('PillSee')).toBeInTheDocument()
    expect(screen.getByText(/AI asistent pro informace o lécích/i)).toBeInTheDocument()
  })

  it('should show GDPR notice on first visit', async () => {
    // Mock no GDPR consent
    localStorage.removeItem('pillsee_gdpr_consent')
    
    render(<Page />)
    
    expect(screen.getByTestId('gdpr-notice')).toBeInTheDocument()
  })

  it('should hide GDPR notice after acceptance', async () => {
    render(<Page />)
    
    const gdprNotice = screen.getByTestId('gdpr-notice')
    const acceptButton = screen.getByText('Accept GDPR')
    
    fireEvent.click(acceptButton)
    
    await waitFor(() => {
      expect(gdprNotice).not.toBeInTheDocument()
    })
  })

  it('should have text input for medication queries', async () => {
    // Mock GDPR accepted
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    render(<Page />)
    
    const textInput = screen.getByPlaceholderText(/zeptejte se na lék/i)
    expect(textInput).toBeInTheDocument()
  })

  it('should handle text medication queries', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    render(<Page />)
    
    const textInput = screen.getByPlaceholderText(/zeptejte se na lék/i)
    const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
    
    fireEvent.change(textInput, { target: { value: 'Co je to Paralen?' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(api.queryMedicationText).toHaveBeenCalledWith('Co je to Paralen?')
    })
    
    expect(session.addMessageToSession).toHaveBeenCalled()
  })

  it('should handle camera capture', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    render(<Page />)
    
    const cameraButton = screen.getByRole('button', { name: /kamera|fotoaparát/i })
    fireEvent.click(cameraButton)
    
    const cameraCapture = screen.getByTestId('camera-capture')
    expect(cameraCapture).toBeInTheDocument()
    
    const captureButton = screen.getByText('Capture')
    fireEvent.click(captureButton)
    
    await waitFor(() => {
      expect(api.queryMedicationImage).toHaveBeenCalledWith('fake-image-data')
    })
  })

  it('should show loading state during API calls', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    // Mock delayed API response
    ;(api.queryMedicationText as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    )
    
    render(<Page />)
    
    const textInput = screen.getByPlaceholderText(/zeptejte se na lék/i)
    const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
    
    fireEvent.change(textInput, { target: { value: 'Test query' } })
    fireEvent.click(submitButton)
    
    expect(screen.getByText(/načítání|loading/i)).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.queryByText(/načítání|loading/i)).not.toBeInTheDocument()
    })
  })

  it('should handle API errors gracefully', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    ;(api.queryMedicationText as jest.Mock).mockRejectedValue(
      new Error('API Error')
    )
    
    render(<Page />)
    
    const textInput = screen.getByPlaceholderText(/zeptejte se na lék/i)
    const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
    
    fireEvent.change(textInput, { target: { value: 'Test query' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/chyba|error/i)).toBeInTheDocument()
    })
  })

  it('should clear conversation', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    render(<Page />)
    
    const clearButton = screen.getByRole('button', { name: /vymazat|clear/i })
    fireEvent.click(clearButton)
    
    expect(session.clearSession).toHaveBeenCalled()
  })

  it('should show install prompt for PWA', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    render(<Page />)
    
    expect(screen.getByTestId('install-prompt')).toBeInTheDocument()
  })

  it('should validate input before sending', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    render(<Page />)
    
    const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
    fireEvent.click(submitButton)
    
    // Should not call API with empty input
    expect(api.queryMedicationText).not.toHaveBeenCalled()
    
    expect(screen.getByText(/zadejte otázku/i)).toBeInTheDocument()
  })

  it('should handle rate limiting', async () => {
    localStorage.setItem('pillsee_gdpr_consent', 'accepted')
    
    ;(api.queryMedicationText as jest.Mock).mockRejectedValue(
      new Error('API Error: 429 Too Many Requests')
    )
    
    render(<Page />)
    
    const textInput = screen.getByPlaceholderText(/zeptejte se na lék/i)
    const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
    
    fireEvent.change(textInput, { target: { value: 'Test query' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/příliš mnoho požadavků/i)).toBeInTheDocument()
    })
  })

  describe('Medical Disclaimers', () => {
    it('should show medical disclaimer with every response', async () => {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      
      render(<Page />)
      
      const textInput = screen.getByPlaceholderText(/zeptejte se na lék/i)
      const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
      
      fireEvent.change(textInput, { target: { value: 'Co je to Paralen?' } })
      fireEvent.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/upozornění/i)).toBeInTheDocument()
        expect(screen.getByText(/nenahrazují lékařskou péči/i)).toBeInTheDocument()
      })
    })

    it('should emphasize that information is not medical advice', async () => {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      
      render(<Page />)
      
      expect(screen.getByText(/informace nejsou lékařská rada/i)).toBeInTheDocument()
      expect(screen.getByText(/vždy se poraďte s lékařem/i)).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper heading structure', async () => {
      render(<Page />)
      
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('PillSee')
    })

    it('should have accessible form controls', async () => {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      
      render(<Page />)
      
      const textInput = screen.getByRole('textbox')
      expect(textInput).toHaveAccessibleName()
      
      const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
      expect(submitButton).toHaveAttribute('type', 'submit')
    })

    it('should support keyboard navigation', async () => {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      
      render(<Page />)
      
      const textInput = screen.getByRole('textbox')
      textInput.focus()
      
      // Tab should move to submit button
      fireEvent.keyDown(textInput, { key: 'Tab' })
      
      const submitButton = screen.getByRole('button', { name: /odeslat|poslat/i })
      expect(document.activeElement).toBe(submitButton)
    })

    it('should have screen reader announcements', async () => {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      
      render(<Page />)
      
      // Should have live regions for dynamic content
      expect(screen.getByRole('status')).toBeInTheDocument()
    })
  })

  describe('Mobile PWA Features', () => {
    it('should handle offline state', async () => {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      
      // Mock offline
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      })
      
      render(<Page />)
      
      expect(screen.getByText(/offline režim/i)).toBeInTheDocument()
    })

    it('should be responsive', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })
      
      render(<Page />)
      
      const mainContainer = screen.getByRole('main')
      expect(mainContainer).toHaveClass('container', 'mx-auto', 'px-4')
    })

    it('should handle touch gestures', async () => {
      localStorage.setItem('pillsee_gdpr_consent', 'accepted')
      
      render(<Page />)
      
      const textInput = screen.getByRole('textbox')
      
      // Touch events should work
      fireEvent.touchStart(textInput)
      fireEvent.touchEnd(textInput)
      
      expect(textInput).toHaveFocus()
    })
  })
})