/**
 * API utility pro PillSee frontend
 * Abstrakce pro komunikaci s FastAPI backendem
 */

interface ApiResponse {
  status: string
  data: any
  error?: string
  disclaimer?: string
  timestamp?: string
}

interface ApiError extends Error {
  status?: number
  code?: string
}

class ApiClient {
  private readonly baseUrl: string
  private readonly timeout: number

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    this.timeout = 30000 // 30 sekund pro image processing
  }

  async request(endpoint: string, options: RequestInit = {}): Promise<ApiResponse> {
    const url = `${this.baseUrl}${endpoint}`
    
    // Default headers
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': 'PillSee-Frontend/1.0.0',
    }

    // Merge headers
    const headers = {
      ...defaultHeaders,
      ...options.headers,
    }

    // AbortController pro timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      // Kontrola HTTP statusu
      if (!response.ok) {
        throw this.createApiError(`HTTP ${response.status}: ${response.statusText}`, response.status)
      }

      // Parsování odpovědi
      const data = await response.json()
      
      // Validace struktury odpovědi
      if (!data || typeof data.status !== 'string') {
        throw this.createApiError('Neplatná struktura odpovědi od serveru')
      }

      return data

    } catch (error) {
      clearTimeout(timeoutId)

      if ((error as any).name === 'AbortError') {
        throw this.createApiError('Požadavek překročil časový limit (30s)', 408)
      }

      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw this.createApiError('Chyba připojení k serveru. Zkontrolujte internetové připojení.', 0)
      }

      // Re-throw API errors
      if (error instanceof Error && 'status' in error) {
        throw error
      }

      throw this.createApiError(`Neočekávaná chyba: ${(error as any).message || 'Unknown error'}`)
    }
  }

  private createApiError(message: string, status?: number, code?: string): ApiError {
    const error = new Error(message) as ApiError
    error.name = 'ApiError'
    error.status = status
    error.code = code
    return error
  }

  // Health check endpoint
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.request('/health', { method: 'GET' })
      return response.status === 'healthy'
    } catch {
      return false
    }
  }

  // Text query endpoint
  async queryText(query: string): Promise<ApiResponse> {
    if (!query.trim()) {
      throw this.createApiError('Dotaz nemůže být prázdný', 400, 'EMPTY_QUERY')
    }

    if (query.length > 500) {
      throw this.createApiError('Dotaz je příliš dlouhý (max 500 znaků)', 400, 'QUERY_TOO_LONG')
    }

    return await this.request('/api/query/text', {
      method: 'POST',
      body: JSON.stringify({ query })
    })
  }

  // Image query endpoint
  async queryImage(imageData: string): Promise<ApiResponse> {
    if (!imageData.trim()) {
      throw this.createApiError('Obrázek nemůže být prázdný', 400, 'EMPTY_IMAGE')
    }

    // Validace base64 formátu
    if (!this.isValidBase64Image(imageData)) {
      throw this.createApiError('Neplatný formát obrázku', 400, 'INVALID_IMAGE_FORMAT')
    }

    return await this.request('/api/query/image', {
      method: 'POST',
      body: JSON.stringify({ image_data: imageData })
    })
  }

  private isValidBase64Image(data: string): boolean {
    // Základní validace base64 image
    if (typeof data !== 'string') return false
    
    // Odstranění data URL prefixu pokud existuje
    const base64Data = data.includes(',') ? data.split(',')[1] : data
    
    // Kontrola base64 formátu
    const base64Regex = /^[A-Za-z0-9+/]*={0,2}$/
    if (!base64Regex.test(base64Data)) return false
    
    // Kontrola minimální délky (~1KB)
    if (base64Data.length < 1000) return false
    
    // Kontrola maximální velikosti (10MB v base64)
    if (base64Data.length > 13.5 * 1024 * 1024) return false // base64 je ~33% větší
    
    return true
  }
}

// Singleton instance
export const apiClient = new ApiClient()

// Convenience function pro přímé použití
export async function apiCall(endpoint: string, options?: RequestInit): Promise<ApiResponse> {
  return await apiClient.request(endpoint, options)
}

// Utility pro handling API errors v komponentách
export function getApiErrorMessage(error: unknown): string {
  if (error instanceof Error && 'status' in error) {
    const apiError = error as ApiError
    
    switch (apiError.status) {
      case 0:
        return 'Problém s připojením k internetu'
      case 400:
        return 'Neplatný požadavek'
      case 429:
        return 'Překročen limit požadavků. Zkuste to za chvíli.'
      case 500:
        return 'Chyba serveru. Zkuste to prosím později.'
      case 408:
        return 'Požadavek trval příliš dlouho'
      default:
        return apiError.message
    }
  }

  return 'Nastala neočekávaná chyba'
}