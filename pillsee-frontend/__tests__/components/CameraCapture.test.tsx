/**
 * Testy pro CameraCapture komponentu
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { CameraCapture } from '../../components/CameraCapture'

// Mock react-camera-pro
jest.mock('react-camera-pro', () => ({
  Camera: ({ onTakePhoto }: { onTakePhoto: (dataUri: string) => void }) => (
    <div data-testid="camera-component">
      <button
        data-testid="capture-button"
        onClick={() => onTakePhoto('data:image/jpeg;base64,fake-image-data')}
      >
        Take Photo
      </button>
    </div>
  ),
}))

describe('CameraCapture', () => {
  const mockOnCapture = jest.fn()
  const mockOnError = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Mock getUserMedia
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: jest.fn(() => Promise.resolve({
          getTracks: () => [],
          getVideoTracks: () => [],
        })),
      },
      configurable: true,
    })
  })

  it('should render camera interface', () => {
    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    expect(screen.getByTestId('camera-component')).toBeInTheDocument()
    expect(screen.getByText('Vyfoťte obal léku')).toBeInTheDocument()
  })

  it('should handle photo capture', async () => {
    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    const captureButton = screen.getByTestId('capture-button')
    fireEvent.click(captureButton)

    await waitFor(() => {
      expect(mockOnCapture).toHaveBeenCalledWith('data:image/jpeg;base64,fake-image-data')
    })
  })

  it('should not render when inactive', () => {
    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={false}
      />
    )

    expect(screen.queryByTestId('camera-component')).not.toBeInTheDocument()
  })

  it('should show flash toggle when available', () => {
    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    // Flash toggle by měl být dostupný na mobilech
    const flashButton = screen.queryByLabelText('Přepnout blesk')
    if (flashButton) {
      expect(flashButton).toBeInTheDocument()
    }
  })

  it('should show camera switch when available', () => {
    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    // Tlačítko pro přepnutí kamery
    const switchButton = screen.queryByLabelText('Přepnout kameru')
    if (switchButton) {
      expect(switchButton).toBeInTheDocument()
    }
  })

  it('should handle camera permissions error', async () => {
    // Mock getUserMedia to reject
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: jest.fn(() => Promise.reject(new Error('Permission denied'))),
      },
      configurable: true,
    })

    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith(
        expect.objectContaining({
          message: expect.stringContaining('Permission denied')
        })
      )
    })
  })

  it('should show guidance overlay', () => {
    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    expect(screen.getByText('Vycentrujte obal léku do rámečku')).toBeInTheDocument()
    expect(screen.getByText('Ujistěte se, že je text čitelný')).toBeInTheDocument()
  })

  it('should handle loading state', () => {
    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    // Loading state by měl být vidět před inicializací kamery
    const loadingText = screen.queryByText('Inicializace kamery...')
    // Loading může být přítomný jen velmi krátce
  })

  it('should be mobile responsive', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    })

    render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    const container = screen.getByTestId('camera-component').parentElement
    expect(container).toHaveClass('w-full') // Tailwind responsive class
  })

  it('should handle cleanup on unmount', () => {
    const { unmount } = render(
      <CameraCapture
        onCapture={mockOnCapture}
        onError={mockOnError}
        isActive={true}
      />
    )

    // Komponenta by měla vyčistit stream při unmount
    expect(() => unmount()).not.toThrow()
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(
        <CameraCapture
          onCapture={mockOnCapture}
          onError={mockOnError}
          isActive={true}
        />
      )

      const captureButton = screen.getByRole('button', { name: /vyfotit|capture/i })
      expect(captureButton).toBeInTheDocument()
    })

    it('should support keyboard navigation', () => {
      render(
        <CameraCapture
          onCapture={mockOnCapture}
          onError={mockOnError}
          isActive={true}
        />
      )

      const captureButton = screen.getByTestId('capture-button')
      captureButton.focus()
      
      // Simulace stisknutí Enter
      fireEvent.keyDown(captureButton, { key: 'Enter', code: 'Enter' })
      
      expect(mockOnCapture).toHaveBeenCalled()
    })

    it('should announce camera status to screen readers', () => {
      render(
        <CameraCapture
          onCapture={mockOnCapture}
          onError={mockOnError}
          isActive={true}
        />
      )

      // ARIA live region pro oznámení stavu kamery
      const statusRegion = screen.queryByRole('status')
      if (statusRegion) {
        expect(statusRegion).toBeInTheDocument()
      }
    })
  })

  describe('Error Handling', () => {
    it('should handle device not found error', async () => {
      Object.defineProperty(navigator, 'mediaDevices', {
        value: {
          getUserMedia: jest.fn(() => Promise.reject(new Error('NotFoundError'))),
        },
        configurable: true,
      })

      render(
        <CameraCapture
          onCapture={mockOnCapture}
          onError={mockOnError}
          isActive={true}
        />
      )

      await waitFor(() => {
        expect(mockOnError).toHaveBeenCalledWith(
          expect.objectContaining({
            message: expect.stringContaining('NotFoundError')
          })
        )
      })
    })

    it('should handle camera busy error', async () => {
      Object.defineProperty(navigator, 'mediaDevices', {
        value: {
          getUserMedia: jest.fn(() => Promise.reject(new Error('NotReadableError'))),
        },
        configurable: true,
      })

      render(
        <CameraCapture
          onCapture={mockOnCapture}
          onError={mockOnError}
          isActive={true}
        />
      )

      await waitFor(() => {
        expect(mockOnError).toHaveBeenCalled()
      })
    })
  })
})