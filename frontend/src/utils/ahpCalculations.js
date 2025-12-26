/**
 * AHP (Analytic Hierarchy Process) Calculations
 *
 * This module provides functions for calculating criterion weights and
 * consistency ratios from Saaty scale pairwise comparisons.
 */

// Random Index (RI) values for matrices of different sizes
// Used in consistency ratio calculation
const RANDOM_INDEX = {
  1: 0,
  2: 0,
  3: 0.58,
  4: 0.90,
  5: 1.12,
  6: 1.24,
  7: 1.32,
  8: 1.41,
  9: 1.45,
  10: 1.49,
}

/**
 * Build a pairwise comparison matrix from comparisons object
 * @param {Array<string>} criteria - List of criteria names
 * @param {Object} comparisons - Object with comparison values (e.g., {"Comfort-Health": 3})
 * @returns {Array<Array<number>>} - Pairwise comparison matrix
 */
export function buildComparisonMatrix(criteria, comparisons = {}) {
  const n = criteria.length
  const matrix = Array(n).fill(0).map(() => Array(n).fill(1))

  // Fill diagonal with 1s (already done above)

  // Fill upper triangle based on comparisons
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const key = `${criteria[i]}-${criteria[j]}`
      const reverseKey = `${criteria[j]}-${criteria[i]}`

      if (comparisons[key]) {
        matrix[i][j] = comparisons[key]
        matrix[j][i] = 1 / comparisons[key]
      } else if (comparisons[reverseKey]) {
        matrix[j][i] = comparisons[reverseKey]
        matrix[i][j] = 1 / comparisons[reverseKey]
      } else {
        // Default to equal importance
        matrix[i][j] = 1
        matrix[j][i] = 1
      }
    }
  }

  return matrix
}

/**
 * Calculate priority weights using geometric mean method (simplified AHP)
 * @param {Array<Array<number>>} matrix - Pairwise comparison matrix
 * @returns {Array<number>} - Normalized priority weights
 */
export function calculateWeights(matrix) {
  const n = matrix.length
  const weights = []

  // Calculate geometric mean for each row
  for (let i = 0; i < n; i++) {
    let product = 1
    for (let j = 0; j < n; j++) {
      product *= matrix[i][j]
    }
    weights[i] = Math.pow(product, 1 / n)
  }

  // Normalize weights to sum to 1
  const sum = weights.reduce((acc, w) => acc + w, 0)
  return weights.map(w => w / sum)
}

/**
 * Calculate the maximum eigenvalue (lambda max) of the matrix
 * @param {Array<Array<number>>} matrix - Pairwise comparison matrix
 * @param {Array<number>} weights - Priority weights
 * @returns {number} - Lambda max
 */
function calculateLambdaMax(matrix, weights) {
  const n = matrix.length
  const weightedSum = Array(n).fill(0)

  // Multiply matrix by weights vector
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      weightedSum[i] += matrix[i][j] * weights[j]
    }
  }

  // Calculate lambda max
  let lambdaMax = 0
  for (let i = 0; i < n; i++) {
    lambdaMax += weightedSum[i] / weights[i]
  }

  return lambdaMax / n
}

/**
 * Calculate Consistency Index (CI)
 * @param {number} lambdaMax - Maximum eigenvalue
 * @param {number} n - Matrix size
 * @returns {number} - Consistency Index
 */
function calculateCI(lambdaMax, n) {
  return (lambdaMax - n) / (n - 1)
}

/**
 * Calculate Consistency Ratio (CR)
 * @param {Array<Array<number>>} matrix - Pairwise comparison matrix
 * @param {Array<number>} weights - Priority weights
 * @returns {number} - Consistency Ratio
 */
export function calculateConsistencyRatio(matrix, weights) {
  const n = matrix.length

  // CR is not defined for n < 3
  if (n < 3) return 0

  const lambdaMax = calculateLambdaMax(matrix, weights)
  const CI = calculateCI(lambdaMax, n)
  const RI = RANDOM_INDEX[n] || 1.49

  return CI / RI
}

/**
 * Check if the consistency ratio is acceptable (CR < 0.1)
 * @param {number} cr - Consistency Ratio
 * @returns {boolean} - True if acceptable
 */
export function isConsistent(cr) {
  return cr < 0.1
}

/**
 * Calculate weights and consistency ratio from pairwise comparisons
 * @param {Array<string>} criteria - List of criteria names
 * @param {Object} comparisons - Comparison values
 * @returns {Object} - { weights: Object, consistencyRatio: number, isConsistent: boolean }
 */
export function calculateAHPWeights(criteria, comparisons) {
  const matrix = buildComparisonMatrix(criteria, comparisons)
  const weightArray = calculateWeights(matrix)
  const cr = calculateConsistencyRatio(matrix, weightArray)

  // Convert weight array to object with criterion names
  const weights = {}
  criteria.forEach((criterion, index) => {
    weights[criterion] = weightArray[index]
  })

  return {
    weights,
    consistencyRatio: cr,
    isConsistent: isConsistent(cr),
  }
}

/**
 * Get Saaty scale interpretation text
 * @param {number} value - Saaty scale value (1-9)
 * @returns {string} - Interpretation text
 */
export function getSaatyInterpretation(value) {
  const interpretations = {
    1: 'Equal importance',
    2: 'Weak importance',
    3: 'Moderate importance',
    4: 'Moderate plus',
    5: 'Strong importance',
    6: 'Strong plus',
    7: 'Very strong importance',
    8: 'Very strong plus',
    9: 'Extreme importance',
  }
  return interpretations[value] || 'Equal importance'
}
