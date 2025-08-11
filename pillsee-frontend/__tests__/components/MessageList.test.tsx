/**
 * Testy pro MessageList komponentu
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { MessageList } from '../../components/MessageList'

const mockMessages = [
  {
    id: '1',
    type: 'user' as const,
    content: 'Co je to Paralen?',
    timestamp: Date.now() - 2000
  },
  {
    id: '2',
    type: 'assistant' as const,
    content: 'PARALEN je analgetikum obsahující paracetamol. Používá se k tlumení bolesti a snížení horečky.',
    timestamp: Date.now() - 1000
  },
  {
    id: '3',
    type: 'image' as const,
    content: 'data:image/jpeg;base64,fake-image-data',
    timestamp: Date.now()
  }
]

describe('MessageList', () => {
  it('should render empty state when no messages', () => {
    render(<MessageList messages={[]} />)
    
    expect(screen.getByText(/zatím žádné zprávy/i)).toBeInTheDocument()
    expect(screen.getByText(/položte první otázku/i)).toBeInTheDocument()
  })

  it('should render all message types', () => {
    render(<MessageList messages={mockMessages} />)
    
    // User message
    expect(screen.getByText('Co je to Paralen?')).toBeInTheDocument()
    
    // Assistant message
    expect(screen.getByText(/PARALEN je analgetikum/)).toBeInTheDocument()
    
    // Image message indicator
    expect(screen.getByText(/obrázek léku/i)).toBeInTheDocument()
  })

  it('should display messages in chronological order', () => {
    render(<MessageList messages={mockMessages} />)
    
    const messages = screen.getAllByRole('article')
    expect(messages).toHaveLength(3)
    
    // First message should be user question
    expect(messages[0]).toHaveTextContent('Co je to Paralen?')
    
    // Second should be assistant response
    expect(messages[1]).toHaveTextContent('PARALEN je analgetikum')
    
    // Third should be image
    expect(messages[2]).toHaveTextContent(/obrázek léku/i)
  })

  it('should show different styling for different message types', () => {
    render(<MessageList messages={mockMessages} />)
    
    const messages = screen.getAllByRole('article')
    
    // User messages should be right-aligned
    expect(messages[0]).toHaveClass('ml-auto')
    
    // Assistant messages should be left-aligned
    expect(messages[1]).toHaveClass('mr-auto')
    
    // Image messages should have special styling
    expect(messages[2]).toHaveClass('mx-auto')
  })

  it('should display timestamps', () => {
    render(<MessageList messages={mockMessages} />)
    
    // Check that timestamps are present (format may vary)
    const timestampElements = screen.getAllByText(/před|ago|:\d{2}/i)
    expect(timestampElements.length).toBeGreaterThanOrEqual(1)
  })

  it('should handle very long messages', () => {
    const longMessage = {
      id: '1',
      type: 'assistant' as const,
      content: 'A'.repeat(1000),
      timestamp: Date.now()
    }
    
    render(<MessageList messages={[longMessage]} />)
    
    const messageElement = screen.getByText(/A{50,}/)
    expect(messageElement).toBeInTheDocument()
    
    // Should have proper word wrapping
    expect(messageElement).toHaveClass('break-words')
  })

  it('should handle markdown in assistant messages', () => {
    const markdownMessage = {
      id: '1',
      type: 'assistant' as const,
      content: '**PARALEN** je analgetikum.\n\n- Obsahuje paracetamol\n- Tlumí bolest\n- Snižuje horečku',
      timestamp: Date.now()
    }
    
    render(<MessageList messages={[markdownMessage]} />)
    
    // Should render markdown formatting
    expect(screen.getByText('PARALEN')).toHaveStyle('font-weight: bold')
    expect(screen.getByText('Obsahuje paracetamol')).toBeInTheDocument()
  })

  it('should display image previews', () => {
    const imageMessage = {
      id: '1',
      type: 'image' as const,
      content: 'data:image/jpeg;base64,fake-image-data',
      timestamp: Date.now()
    }
    
    render(<MessageList messages={[imageMessage]} />)
    
    const image = screen.getByAltText(/obrázek léku/i)
    expect(image).toBeInTheDocument()
    expect(image).toHaveAttribute('src', 'data:image/jpeg;base64,fake-image-data')
  })

  it('should handle image loading errors', () => {
    const imageMessage = {
      id: '1',
      type: 'image' as const,
      content: 'data:image/jpeg;base64,invalid-data',
      timestamp: Date.now()
    }
    
    render(<MessageList messages={[imageMessage]} />)
    
    const image = screen.getByAltText(/obrázek léku/i)
    fireEvent.error(image)
    
    // Should show error state
    expect(screen.getByText(/chyba při načítání/i)).toBeInTheDocument()
  })

  it('should auto-scroll to latest message', () => {
    const scrollIntoViewMock = jest.fn()
    Element.prototype.scrollIntoView = scrollIntoViewMock
    
    const { rerender } = render(<MessageList messages={mockMessages.slice(0, 2)} />)
    
    // Add new message
    rerender(<MessageList messages={mockMessages} />)
    
    // Should scroll to the latest message
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth' })
  })

  it('should show typing indicator for pending messages', () => {
    const pendingMessage = {
      id: 'pending',
      type: 'assistant' as const,
      content: '',
      timestamp: Date.now(),
      pending: true
    }
    
    render(<MessageList messages={[...mockMessages, pendingMessage]} />)
    
    expect(screen.getByText(/píše|typing/i)).toBeInTheDocument()
    expect(screen.getByTestId('typing-dots')).toBeInTheDocument()
  })

  describe('Accessibility', () => {
    it('should have proper ARIA roles', () => {
      render(<MessageList messages={mockMessages} />)
      
      expect(screen.getByRole('log')).toBeInTheDocument()
      expect(screen.getAllByRole('article')).toHaveLength(3)
    })

    it('should have accessible message labels', () => {
      render(<MessageList messages={mockMessages} />)
      
      expect(screen.getByLabelText(/zpráva od uživatele/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/odpověď asistenta/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/obrázek od uživatele/i)).toBeInTheDocument()
    })

    it('should support screen readers', () => {
      render(<MessageList messages={mockMessages} />)
      
      // Should have live region for new messages
      const liveRegion = screen.getByRole('log')
      expect(liveRegion).toHaveAttribute('aria-live', 'polite')
    })

    it('should have keyboard navigation', () => {
      render(<MessageList messages={mockMessages} />)
      
      const messages = screen.getAllByRole('article')
      
      // Messages should be focusable for keyboard users
      messages.forEach(message => {
        expect(message).toHaveAttribute('tabindex', '0')
      })
    })
  })

  describe('Medical Content', () => {
    it('should display medical disclaimers', () => {
      const medicalMessage = {
        id: '1',
        type: 'assistant' as const,
        content: 'Informace o léku...',
        timestamp: Date.now(),
        disclaimer: 'UPOZORNĚNÍ: Informace nenahrazují lékařskou péči'
      }
      
      render(<MessageList messages={[medicalMessage]} />)
      
      expect(screen.getByText(/UPOZORNĚNÍ/)).toBeInTheDocument()
      expect(screen.getByText(/nenahrazují lékařskou péči/)).toBeInTheDocument()
    })

    it('should highlight important medical information', () => {
      const criticalMessage = {
        id: '1',
        type: 'assistant' as const,
        content: 'VAROVÁNÍ: Nepřekračujte doporučené dávkování',
        timestamp: Date.now(),
        severity: 'warning'
      }
      
      render(<MessageList messages={[criticalMessage]} />)
      
      const message = screen.getByText(/VAROVÁNÍ/)
      expect(message).toHaveClass('text-red-600')
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
      
      render(<MessageList messages={mockMessages} />)
      
      const messageList = screen.getByRole('log')
      expect(messageList).toHaveClass('px-4', 'py-2')
      
      // Messages should stack properly on mobile
      const messages = screen.getAllByRole('article')
      messages.forEach(message => {
        expect(message).toHaveClass('max-w-full')
      })
    })

    it('should handle touch interactions', () => {
      render(<MessageList messages={mockMessages} />)
      
      const image = screen.getByAltText(/obrázek léku/i)
      
      // Should handle touch to view full size
      fireEvent.touchStart(image)
      fireEvent.touchEnd(image)
      
      // Modal or expanded view should appear
      // (Implementation dependent)
    })
  })

  describe('Performance', () => {
    it('should handle large number of messages', () => {
      const manyMessages = Array.from({ length: 100 }, (_, i) => ({
        id: `msg-${i}`,
        type: 'user' as const,
        content: `Message ${i}`,
        timestamp: Date.now() - (100 - i) * 1000
      }))
      
      const { container } = render(<MessageList messages={manyMessages} />)
      
      // Should render without performance issues
      expect(container.querySelectorAll('[role="article"]')).toHaveLength(100)
    })

    it('should virtualize long message lists', () => {
      // If virtualization is implemented
      const manyMessages = Array.from({ length: 1000 }, (_, i) => ({
        id: `msg-${i}`,
        type: 'user' as const,
        content: `Message ${i}`,
        timestamp: Date.now() - (1000 - i) * 1000
      }))
      
      render(<MessageList messages={manyMessages} />)
      
      // Only visible messages should be in DOM (if virtualized)
      const visibleMessages = screen.getAllByRole('article')
      expect(visibleMessages.length).toBeLessThanOrEqual(50) // Reasonable viewport size
    })
  })
})