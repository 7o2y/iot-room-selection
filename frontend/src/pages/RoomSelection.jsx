import { useState } from 'react'
import PreferenceMatrix from '../components/PreferenceMatrix'

function RoomSelection() {
  const [preferences, setPreferences] = useState({
    comparisons: {},
    weights: {},
    consistencyRatio: 0,
  })

  const handlePreferencesChange = (newPreferences) => {
    setPreferences(newPreferences)
    console.log('Preferences updated:', newPreferences)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Room Selection
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Panel: Saaty Scale Preferences */}
        <div>
          <PreferenceMatrix onPreferencesChange={handlePreferencesChange} />
        </div>

        {/* Right Panel: Profile Adjustment (Task 28) */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Environmental Thresholds
          </h2>
          <p className="text-sm text-gray-600 mb-6">
            Profile adjustment UI will be added in Task 28
          </p>
          <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">
            <p>Coming soon...</p>
          </div>
        </div>
      </div>

      {/* Room Rankings (Task 29) */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Room Rankings
        </h2>
        <p className="text-sm text-gray-600 mb-6">
          Room ranking display will be added in Task 29
        </p>
        <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">
          <p>Coming soon...</p>
        </div>
      </div>
    </div>
  )
}

export default RoomSelection
