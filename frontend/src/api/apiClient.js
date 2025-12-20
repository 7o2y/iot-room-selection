import axios from 'axios'
import mockApi from './mockApi'

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const USE_MOCK = import.meta.env.VITE_USE_MOCK_API !== 'false' // Default to true

// Create axios instance for real API calls
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add authentication, logging, etc.
axiosInstance.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, config.data)
    }

    // Add authentication token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors globally
axiosInstance.interceptors.response.use(
  (response) => {
    // Log responses in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.url}`, response.data)
    }
    return response
  },
  (error) => {
    // Log errors
    console.error('[API Response Error]', error)

    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response

      if (status === 401) {
        // Unauthorized - clear auth and redirect to login
        localStorage.removeItem('auth_token')
        // Optionally trigger login redirect
        console.warn('Unauthorized access - authentication required')
      } else if (status === 403) {
        // Forbidden
        console.error('Access forbidden')
      } else if (status === 404) {
        // Not found
        console.error('Resource not found')
      } else if (status >= 500) {
        // Server error
        console.error('Server error:', data)
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server - check if backend is running')
    } else {
      // Other errors
      console.error('Request setup error:', error.message)
    }

    return Promise.reject(error)
  }
)

// API client that switches between mock and real APIs
const apiClient = {
  /**
   * Get all rooms with their sensor data
   * @returns {Promise<Array>} List of rooms
   * @throws {Error} If request fails
   */
  getRooms: async () => {
    if (USE_MOCK) {
      console.log('[API Client] Using mock API for getRooms')
      return mockApi.getRooms()
    }

    try {
      const response = await axiosInstance.get('/api/rooms')
      return response.data
    } catch (error) {
      console.error('[API Client] Error fetching rooms:', error)
      throw new Error(
        error.response?.data?.message ||
        error.message ||
        'Failed to fetch rooms'
      )
    }
  },

  /**
   * Evaluate and rank rooms based on user preferences
   * @param {Object} preferences - User preferences and requirements
   * @param {Object} preferences.saaty_preferences - Saaty scale comparisons
   * @param {Object} preferences.weights - Calculated weights
   * @param {Object} preferences.profile_adjustments - Environmental threshold adjustments
   * @returns {Promise<Object>} Rankings and scores
   * @throws {Error} If request fails or validation fails
   */
  evaluateRooms: async (preferences) => {
    if (USE_MOCK) {
      console.log('[API Client] Using mock API for evaluateRooms')
      return mockApi.evaluateRooms(preferences)
    }

    // Validate preferences before sending
    if (!preferences || typeof preferences !== 'object') {
      throw new Error('Preferences must be an object')
    }

    try {
      const response = await axiosInstance.post('/api/evaluate', preferences)

      // Validate response structure
      if (!response.data || !response.data.rankings) {
        throw new Error('Invalid response format from server')
      }

      return response.data
    } catch (error) {
      console.error('[API Client] Error evaluating rooms:', error)

      // Provide specific error messages
      if (error.response?.status === 400) {
        throw new Error(
          error.response.data?.message ||
          'Invalid preferences data. Please check your inputs.'
        )
      } else if (error.response?.status === 422) {
        throw new Error(
          'Validation error: ' +
          (error.response.data?.detail || 'Invalid request data')
        )
      }

      throw new Error(
        error.response?.data?.message ||
        error.message ||
        'Failed to evaluate rooms'
      )
    }
  },

  /**
   * Get AHP criteria hierarchy and weights
   * @returns {Promise<Object>} Criteria structure
   * @throws {Error} If request fails
   */
  getCriteria: async () => {
    if (USE_MOCK) {
      console.log('[API Client] Using mock API for getCriteria')
      return mockApi.getCriteria()
    }

    try {
      const response = await axiosInstance.get('/api/criteria')
      return response.data
    } catch (error) {
      console.error('[API Client] Error fetching criteria:', error)
      throw new Error(
        error.response?.data?.message ||
        error.message ||
        'Failed to fetch criteria'
      )
    }
  },

  /**
   * Health check - test if backend is available
   * @returns {Promise<Object>} Health status
   */
  healthCheck: async () => {
    if (USE_MOCK) {
      return { status: 'ok', mode: 'mock' }
    }

    try {
      const response = await axiosInstance.get('/health')
      return response.data
    } catch (error) {
      throw new Error('Backend is not available')
    }
  },
}

// Export configuration for debugging
export const apiConfig = {
  baseURL: API_BASE_URL,
  useMock: USE_MOCK,
  isDevelopment: import.meta.env.DEV,
}

export default apiClient
