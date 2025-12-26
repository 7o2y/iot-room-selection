/**
 * EU Indoor Environmental Quality (IEQ) Standards
 *
 * Based on:
 * - EN 16798-1: Energy performance of buildings - Ventilation for buildings
 * - EN 12464-1: Light and lighting - Lighting of work places
 */

export const EU_STANDARDS = {
  temperature: {
    min: 18,
    max: 26,
    optimalMin: 20,
    optimalMax: 24,
    unit: '°C',
    label: 'Temperature',
    icon: '🌡️',
    description: 'Optimal thermal comfort range based on EN 16798-1',
    categories: {
      excellent: { min: 20, max: 24 },
      good: { min: 19, max: 25 },
      acceptable: { min: 18, max: 26 },
    },
  },
  co2: {
    min: 0,
    max: 1000,
    optimalMin: 0,
    optimalMax: 600,
    unit: 'ppm',
    label: 'CO2 Level',
    icon: '💨',
    description: 'Indoor air quality standard (EN 16798-1)',
    categories: {
      excellent: { max: 400 },
      good: { max: 600 },
      acceptable: { max: 1000 },
    },
  },
  humidity: {
    min: 30,
    max: 70,
    optimalMin: 40,
    optimalMax: 60,
    unit: '%',
    label: 'Humidity',
    icon: '💧',
    description: 'Relative humidity for comfort and health (EN 16798-1)',
    categories: {
      excellent: { min: 40, max: 60 },
      good: { min: 35, max: 65 },
      acceptable: { min: 30, max: 70 },
    },
  },
  noise: {
    min: 0,
    max: 45,
    optimalMin: 0,
    optimalMax: 35,
    unit: 'dBA',
    label: 'Noise Level',
    icon: '🔇',
    description: 'Acceptable noise levels for concentration',
    categories: {
      excellent: { max: 30 },
      good: { max: 35 },
      acceptable: { max: 45 },
    },
  },
  light: {
    min: 200,
    max: 750,
    optimalMin: 300,
    optimalMax: 500,
    unit: 'lux',
    label: 'Light Level',
    icon: '💡',
    description: 'Illuminance for office work (EN 12464-1)',
    categories: {
      excellent: { min: 300, max: 500 },
      good: { min: 250, max: 600 },
      acceptable: { min: 200, max: 750 },
    },
  },
  voc: {
    min: 0,
    max: 400,
    optimalMin: 0,
    optimalMax: 200,
    unit: 'ppb',
    label: 'VOC Level',
    icon: '🌫️',
    description: 'Volatile Organic Compounds for air quality',
    categories: {
      excellent: { max: 100 },
      good: { max: 200 },
      acceptable: { max: 400 },
    },
  },
  airQuality: {
    min: 0,
    max: 100,
    optimalMin: 0,
    optimalMax: 50,
    unit: 'AQI',
    label: 'Air Quality Index',
    icon: '🍃',
    description: 'Overall air quality indicator',
    categories: {
      excellent: { max: 25 },
      good: { max: 50 },
      acceptable: { max: 100 },
    },
  },
}

/**
 * Get default profile based on EU standards (optimal values)
 */
export function getDefaultProfile() {
  const profile = {}

  Object.keys(EU_STANDARDS).forEach((key) => {
    const standard = EU_STANDARDS[key]
    profile[key] = {
      min: standard.optimalMin,
      max: standard.optimalMax,
    }
  })

  return profile
}

/**
 * Check if a value is within optimal range
 */
export function isOptimal(criterion, value) {
  const standard = EU_STANDARDS[criterion]
  if (!standard) return false

  if (standard.optimalMin !== undefined && value < standard.optimalMin) return false
  if (standard.optimalMax !== undefined && value > standard.optimalMax) return false

  return true
}

/**
 * Get category for a value (excellent, good, acceptable, poor)
 */
export function getCategory(criterion, value) {
  const standard = EU_STANDARDS[criterion]
  if (!standard) return 'unknown'

  const { categories } = standard

  // Check excellent
  if (categories.excellent) {
    const { min, max } = categories.excellent
    if ((min === undefined || value >= min) && (max === undefined || value <= max)) {
      return 'excellent'
    }
  }

  // Check good
  if (categories.good) {
    const { min, max } = categories.good
    if ((min === undefined || value >= min) && (max === undefined || value <= max)) {
      return 'good'
    }
  }

  // Check acceptable
  if (categories.acceptable) {
    const { min, max } = categories.acceptable
    if ((min === undefined || value >= min) && (max === undefined || value <= max)) {
      return 'acceptable'
    }
  }

  return 'poor'
}
