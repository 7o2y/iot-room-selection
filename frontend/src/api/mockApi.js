// Mock API using real sensor data from docs/project info&data/Project_sensor_data/aggregated_rooms.json
// This simulates what the FastAPI backend will do

// Import room data from project data
// Note: In production, this will be fetched from the backend
import roomsData from '../../../docs/project info&data/Project_sensor_data/aggregated_rooms.json'

// Simple scoring function (simplified version of AHP)
const scoreRoom = (room, userProfile = {}) => {
  let score = 0
  let count = 0

  // Temperature scoring (optimal: 20-24°C)
  if (room.temperature) {
    const tempScore = room.temperature >= 20 && room.temperature <= 24 ? 1 :
                     room.temperature >= 18 && room.temperature <= 26 ? 0.7 : 0.3
    score += tempScore
    count++
  }

  // CO2 scoring (optimal: < 600 ppm)
  if (room.co2) {
    const co2Score = room.co2 < 600 ? 1 :
                    room.co2 < 1000 ? 0.6 : 0.2
    score += co2Score
    count++
  }

  // Humidity scoring (optimal: 40-60%)
  if (room.humidity) {
    const humidityScore = room.humidity >= 40 && room.humidity <= 60 ? 1 :
                         room.humidity >= 30 && room.humidity <= 70 ? 0.7 : 0.3
    score += humidityScore
    count++
  }

  // Air quality scoring (optimal: < 50 AQI)
  if (room.air_quality) {
    const aqScore = room.air_quality < 50 ? 1 :
                   room.air_quality < 100 ? 0.6 : 0.2
    score += aqScore
    count++
  }

  return count > 0 ? score / count : 0
}

export const mockApi = {
  // GET /api/rooms - List all rooms with their data
  getRooms: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(roomsData)
      }, 300) // Simulate network delay
    })
  },

  // POST /api/evaluate - Evaluate and rank rooms based on preferences
  evaluateRooms: async (preferences = {}) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Score each room
        const scoredRooms = roomsData.map((room) => ({
          ...room,
          final_score: scoreRoom(room, preferences.profile_adjustments),
          comfort_score: scoreRoom(room) * 0.9 + Math.random() * 0.1,
          health_score: scoreRoom(room) * 0.95 + Math.random() * 0.05,
          usability_score: room.has_projector ? 0.9 : 0.6,
        }))

        // Sort by score (descending)
        const ranked = scoredRooms
          .sort((a, b) => b.final_score - a.final_score)
          .map((room, index) => ({
            rank: index + 1,
            room_id: room.room_id,
            room_name: room.name,
            final_score: room.final_score,
            comfort_score: room.comfort_score,
            health_score: room.health_score,
            usability_score: room.usability_score,
            temperature: room.temperature,
            co2: room.co2,
            humidity: room.humidity,
            air_quality: room.air_quality,
            seating_capacity: room.seating_capacity,
            has_projector: room.has_projector,
            computers: room.computers,
            has_robots: room.has_robots,
          }))

        resolve({
          rankings: ranked,
          weights: {
            Comfort: 0.40,
            Health: 0.35,
            Usability: 0.25,
          },
          consistency_ratio: 0.05,
          is_consistent: true,
        })
      }, 500) // Simulate network delay
    })
  },

  // GET /api/criteria - Get AHP criteria hierarchy
  getCriteria: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          main: ['Comfort', 'Health', 'Usability'],
          comfort: ['Temperature', 'Lighting', 'Noise', 'Humidity'],
          health: ['CO2', 'Air Quality', 'VOC'],
          usability: ['Seating', 'Equipment', 'AV Facilities'],
          weights: {
            main: {
              Comfort: 0.40,
              Health: 0.35,
              Usability: 0.25,
            },
            comfort: {
              Temperature: 0.35,
              Lighting: 0.25,
              Noise: 0.25,
              Humidity: 0.15,
            },
            health: {
              CO2: 0.50,
              'Air Quality': 0.30,
              VOC: 0.20,
            },
            usability: {
              Seating: 0.50,
              Equipment: 0.30,
              'AV Facilities': 0.20,
            },
          },
        })
      }, 200)
    })
  },
}

export default mockApi
