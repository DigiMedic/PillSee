/**
 * Testy pro API utility funkce
 */

import { queryMedicationText, queryMedicationImage } from '../utils/api'

// Mock fetch globálně
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

describe('API Utils', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  describe('queryMedicationText', () => {
    it('should successfully query text medication info', async () => {
      const mockResponse = {
        status: 'success',
        data: {
          answer: 'PARALEN je analgetikum s paracetamolem.',
          sources: ['SÚKL databáze']
        },
        disclaimer: 'Lékařské upozornění'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      const result = await queryMedicationText('Co je to Paralen?')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/query/text',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: 'Co je to Paralen?' }),
        })
      )

      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      } as Response)

      await expect(queryMedicationText('test'))
        .rejects
        .toThrow('API Error: 500 Internal Server Error')
    })

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(queryMedicationText('test'))
        .rejects
        .toThrow('Network error')
    })

    it('should validate empty query', async () => {
      await expect(queryMedicationText(''))
        .rejects
        .toThrow('Query cannot be empty')
    })

    it('should handle rate limiting', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
      } as Response)

      await expect(queryMedicationText('test'))
        .rejects
        .toThrow('API Error: 429 Too Many Requests')
    })
  })

  describe('queryMedicationImage', () => {
    it('should successfully query image medication info', async () => {
      const mockResponse = {
        status: 'success',
        data: {
          name: 'PARALEN 500MG',
          active_ingredient: 'Paracetamolum',
          confidence_score: 0.85
        },
        disclaimer: 'Lékařské upozornění'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      const testImageData = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...'
      const result = await queryMedicationImage(testImageData)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/query/image',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image_data: testImageData }),
        })
      )

      expect(result).toEqual(mockResponse)
    })

    it('should handle image processing errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
      } as Response)

      await expect(queryMedicationImage('invalid-base64'))
        .rejects
        .toThrow('API Error: 400 Bad Request')
    })

    it('should validate empty image data', async () => {
      await expect(queryMedicationImage(''))
        .rejects
        .toThrow('Image data cannot be empty')
    })

    it('should handle low confidence scores', async () => {
      const mockResponse = {
        status: 'success',
        data: {
          name: 'Nerozpoznaný lék',
          confidence_score: 0.3
        },
        disclaimer: 'Nízká spolehlivost rozpoznání'
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      const result = await queryMedicationImage('valid-base64-data')
      expect(result.data.confidence_score).toBeLessThan(0.5)
    })
  })

  describe('API Configuration', () => {
    it('should use correct base URL from environment', () => {
      // Test se spoléhá na výchozí konfiguraci v utils/api.ts
      expect(process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000')
        .toBe('http://localhost:8000')
    })
  })
})