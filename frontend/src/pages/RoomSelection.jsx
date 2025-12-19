import { useState } from 'react'
import PreferenceMatrix from '../components/PreferenceMatrix'
import ProfileAdjuster from '../components/ProfileAdjuster'
import RoomRanking from '../components/RoomRanking'
import apiClient from '../api/apiClient'
import { Sparkles, AlertCircle } from 'lucide-react'

function RoomSelection() {
  const [preferences, setPreferences] = useState({
    comparisons: {},
    weights: {},
    consistencyRatio: 0,
  })

  const [profile, setProfile] = useState({})
  const [rankings, setRankings] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePreferencesChange = (newPreferences) => {
    setPreferences(newPreferences)
    console.log('Preferences updated:', newPreferences)
  }

  const handleProfileChange = (newProfile) => {
    setProfile(newProfile)
    console.log('Profile updated:', newProfile)
  }

  const handleEvaluateRooms = async () => {
    setLoading(true)
    setError(null)

    try {
      // Call API to evaluate rooms
      const result = await apiClient.evaluateRooms({
        saaty_preferences: preferences.comparisons,
        weights: preferences.weights,
        profile_adjustments: profile,
      })

      setRankings(result)
      console.log('Rankings received:', result)
    } catch (err) {
      console.error('Error evaluating rooms:', err)
      setError('Failed to evaluate rooms. Please try again.')
    } finally {
      setLoading(false)
    }
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

        {/* Right Panel: Profile Adjustment */}
        <div>
          <ProfileAdjuster onProfileChange={handleProfileChange} />
        </div>
      </div>

      {/* Evaluate Button */}
      <div className="mt-8 flex justify-center">
        <button
          onClick={handleEvaluateRooms}
          disabled={loading}
          className="flex items-center gap-2 px-8 py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white font-semibold rounded-lg shadow-lg transition transform hover:scale-105 disabled:transform-none"
        >
          <Sparkles className="w-5 h-5" />
          {loading ? 'Evaluating Rooms...' : 'Evaluate Rooms'}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Room Rankings */}
      {rankings && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            🏆 Room Rankings
          </h2>
          <RoomRanking
            rankings={rankings.rankings}
            consistencyRatio={rankings.consistency_ratio}
          />
        </div>
      )}
    </div>
  )
}

export default RoomSelection
