import { useState, useEffect } from 'react'
import RangeSlider from './RangeSlider'
import { EU_STANDARDS, getDefaultProfile } from '../constants/euStandards'
import { RotateCcw } from 'lucide-react'

/**
 * ProfileAdjuster Component
 *
 * Allows users to adjust environmental threshold preferences
 * Shows EU regulation defaults and provides sliders for customization
 */
function ProfileAdjuster({ onProfileChange }) {
  // Initialize with EU optimal values
  const [profile, setProfile] = useState(getDefaultProfile())

  // Main criteria to display (matching AHP structure)
  const displayCriteria = ['temperature', 'co2', 'humidity', 'noise', 'light']

  // Notify parent when profile changes
  useEffect(() => {
    if (onProfileChange) {
      onProfileChange(profile)
    }
  }, [profile])

  // Handle individual criterion change
  const handleCriterionChange = (criterion, value) => {
    setProfile((prev) => ({
      ...prev,
      [criterion]: {
        min: EU_STANDARDS[criterion].optimalMin,
        max: value, // For simplicity, we adjust the max threshold
      },
    }))
  }

  // Reset to EU defaults
  const handleReset = () => {
    setProfile(getDefaultProfile())
  }

  // Get current value for display (using max threshold)
  const getCurrentValue = (criterion) => {
    return profile[criterion]?.max || EU_STANDARDS[criterion].optimalMax
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-6">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Environmental Thresholds
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Adjust your ideal ranges for environmental conditions
            </p>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition"
            title="Reset to EU Standards"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
        </div>
      </div>

      {/* Sliders for each criterion */}
      <div className="space-y-6">
        {displayCriteria.map((criterion) => {
          const standard = EU_STANDARDS[criterion]
          return (
            <RangeSlider
              key={criterion}
              label={standard.label}
              icon={standard.icon}
              value={getCurrentValue(criterion)}
              min={standard.min}
              max={standard.max}
              step={criterion === 'temperature' || criterion === 'humidity' ? 0.5 : 10}
              unit={standard.unit}
              optimalMin={standard.optimalMin}
              optimalMax={standard.optimalMax}
              onChange={(value) => handleCriterionChange(criterion, value)}
              euStandard={standard.description}
            />
          )
        })}
      </div>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">
          About Environmental Thresholds
        </h4>
        <p className="text-xs text-blue-800 leading-relaxed">
          These thresholds define your acceptable ranges for each environmental factor.
          Values are based on European standards (EN 16798-1, EN 12464-1).
          Rooms with readings within your specified ranges will score higher in the evaluation.
        </p>
      </div>

      {/* Profile Summary */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">
          Current Profile Summary
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {displayCriteria.map((criterion) => {
            const standard = EU_STANDARDS[criterion]
            const current = getCurrentValue(criterion)
            const isOptimal = current === standard.optimalMax
            return (
              <div key={criterion} className="flex justify-between items-center">
                <span className="text-gray-600">
                  {standard.icon} {standard.label}:
                </span>
                <span className={`font-medium ${
                  isOptimal ? 'text-green-600' : 'text-blue-600'
                }`}>
                  ≤ {current} {standard.unit}
                  {isOptimal && ' ✓'}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ProfileAdjuster
