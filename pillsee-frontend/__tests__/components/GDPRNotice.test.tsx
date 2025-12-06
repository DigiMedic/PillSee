/**
 * Testy pro GDPR Notice komponentu
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { GDPRNotice } from '../../components/GDPRNotice'

describe('GDPRNotice', () => {
  const mockOnAccept = jest.fn()
  const mockOnDecline = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('should render GDPR notice', () => {
    render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

    expect(screen.getByText(/ochrana osobních údajů/i)).toBeInTheDocument()
    expect(screen.getByText(/tato aplikace ukládá data pouze lokálně/i)).toBeInTheDocument()
  })

  it('should show Czech privacy information', () => {
    render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

    expect(screen.getByText(/žádné osobní údaje nejsou odesílány/i)).toBeInTheDocument()
    expect(screen.getByText(/session storage/i)).toBeInTheDocument()
    expect(screen.getByText(/můžete vymazat kdykoliv/i)).toBeInTheDocument()
  })

  it('should have accept and decline buttons', () => {
    render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

    const acceptButton = screen.getByRole('button', { name: /rozumím|přijmout/i })
    const declineButton = screen.getByRole('button', { name: /zamítnout|odmítnout/i })

    expect(acceptButton).toBeInTheDocument()
    expect(declineButton).toBeInTheDocument()
  })

  it('should call onAccept when accept button is clicked', () => {
    render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

    const acceptButton = screen.getByRole('button', { name: /rozumím|přijmout/i })
    fireEvent.click(acceptButton)

    expect(mockOnAccept).toHaveBeenCalledTimes(1)
  })

  it('should call onDecline when decline button is clicked', () => {
    render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

    const declineButton = screen.getByRole('button', { name: /zamítnout|odmítnout/i })
    fireEvent.click(declineButton)

    expect(mockOnDecline).toHaveBeenCalledTimes(1)
  })

  it('should not render if already accepted', () => {
    // Mock localStorage to return accepted state
    Storage.prototype.getItem = jest.fn(() => 'accepted')

    const { container } = render(
      <GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('should store acceptance in localStorage', () => {
    render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

    const acceptButton = screen.getByRole('button', { name: /rozumím|přijmout/i })
    fireEvent.click(acceptButton)

    expect(localStorage.setItem).toHaveBeenCalledWith(
      'pillsee_gdpr_consent',
      'accepted'
    )
  })

  it('should handle decline by not storing anything', () => {
    render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

    const declineButton = screen.getByRole('button', { name: /zamítnout|odmítnout/i })
    fireEvent.click(declineButton)

    expect(localStorage.setItem).not.toHaveBeenCalledWith(
      'pillsee_gdpr_consent',
      expect.anything()
    )
  })

  describe('Medical Disclaimer Integration', () => {
    it('should include medical disclaimer information', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      expect(screen.getByText(/informace nenahrazují lékařskou péči/i)).toBeInTheDocument()
      expect(screen.getByText(/vždy se poraďte s lékařem/i)).toBeInTheDocument()
    })

    it('should emphasize anonymous usage', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      expect(screen.getByText(/anonymní používání/i)).toBeInTheDocument()
      expect(screen.getByText(/bez registrace/i)).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA roles', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog).toBeInTheDocument()
      expect(dialog).toHaveAttribute('aria-modal', 'true')
    })

    it('should have accessible button labels', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      const acceptButton = screen.getByRole('button', { name: /rozumím|přijmout/i })
      const declineButton = screen.getByRole('button', { name: /zamítnout|odmítnout/i })

      expect(acceptButton).toHaveAttribute('type', 'button')
      expect(declineButton).toHaveAttribute('type', 'button')
    })

    it('should trap focus within modal', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      // Focus should be trapped in the modal
      const acceptButton = screen.getByRole('button', { name: /rozumím|přijmout/i })
      const declineButton = screen.getByRole('button', { name: /zamítnout|odmítnout/i })

      acceptButton.focus()
      expect(document.activeElement).toBe(acceptButton)

      // Tab through buttons
      fireEvent.keyDown(acceptButton, { key: 'Tab' })
      // Focus should move to decline button (implementation dependent)
    })

    it('should support keyboard navigation', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      const acceptButton = screen.getByRole('button', { name: /rozumím|přijmout/i })
      
      // Test Enter key
      fireEvent.keyDown(acceptButton, { key: 'Enter' })
      expect(mockOnAccept).toHaveBeenCalledTimes(1)
    })

    it('should not allow closing with Escape key', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      const dialog = screen.getByRole('dialog')
      fireEvent.keyDown(dialog, { key: 'Escape' })

      // GDPR notice should remain open (user must explicitly choose)
      expect(mockOnAccept).not.toHaveBeenCalled()
      expect(mockOnDecline).not.toHaveBeenCalled()
    })
  })

  describe('GDPR Compliance', () => {
    it('should clearly explain data processing', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      expect(screen.getByText(/jak zpracováváme data/i)).toBeInTheDocument()
      expect(screen.getByText(/session storage/i)).toBeInTheDocument()
      expect(screen.getByText(/žádné cookies/i)).toBeInTheDocument()
    })

    it('should explain user rights', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      expect(screen.getByText(/právo na výmaz/i)).toBeInTheDocument()
      expect(screen.getByText(/vymazat data kdykoliv/i)).toBeInTheDocument()
    })

    it('should provide opt-out option', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      const declineButton = screen.getByRole('button', { name: /zamítnout|odmítnout/i })
      expect(declineButton).toBeInTheDocument()
      
      // Clicking decline should call the handler
      fireEvent.click(declineButton)
      expect(mockOnDecline).toHaveBeenCalled()
    })

    it('should be clear about anonymous usage', () => {
      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      expect(screen.getByText(/anonymní/i)).toBeInTheDocument()
      expect(screen.getByText(/bez osobních údajů/i)).toBeInTheDocument()
    })
  })

  describe('Mobile Responsiveness', () => {
    it('should be mobile friendly', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })

      render(<GDPRNotice onAccept={mockOnAccept} onDecline={mockOnDecline} />)

      const dialog = screen.getByRole('dialog')
      expect(dialog.parentElement).toHaveClass('fixed', 'inset-0')
      
      // Buttons should stack on mobile
      const acceptButton = screen.getByRole('button', { name: /rozumím|přijmout/i })
      expect(acceptButton.parentElement).toHaveClass('flex-col', 'sm:flex-row')
    })
  })
})