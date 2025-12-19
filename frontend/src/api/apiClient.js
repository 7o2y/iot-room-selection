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

// API client that switches between mock and real APIs
const apiClient = {
  /**
   * Get all rooms with their sensor data
   * @returns {Promise<Array>} List of rooms
   */
  getRooms: async () => {
    if (USE_MOCK) {
      return mockApi.getRooms()
    }

    try {
      const response = await axiosInstance.get('/api/rooms')
      return response.data
    } catch (error) {
      console.error('Error fetching rooms:', error)
      throw error
    }
  },

  /**
   * Evaluate and rank rooms based on user preferences
   * @param {Object} preferences - User preferences and requirements
   * @param {Object} preferences.user_requirements - Required seats, equipment, etc.
   * @param {Object} preferences.preferences - Saaty scale comparisons
   * @param {Object} preferences.profile_adjustments - Environmental threshold adjustments
   * @returns {Promise<Object>} Rankings and scores
   */
  evaluateRooms: async (preferences) => {
    if (USE_MOCK) {
      return mockApi.evaluateRooms(preferences)
    }

    try {
      const response = await axiosInstance.post('/api/evaluate', preferences)
      return response.data
    } catch (error) {
      console.error('Error evaluating rooms:', error)
      throw error
    }
  },

  /**
   * Get AHP criteria hierarchy and weights
   * @returns {Promise<Object>} Criteria structure
   */
  getCriteria: async () => {
    if (USE_MOCK) {
      return mockApi.getCriteria()
    }

    try {
      const response = await axiosInstance.get('/api/criteria')
      return response.data
    } catch (error) {
      console.error('Error fetching criteria:', error)
      throw error
    }
  },
}

export default apiClient
