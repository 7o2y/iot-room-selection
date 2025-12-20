# Component Architecture

## Overview

This document describes the technical architecture and component structure of the IoT Room Selection frontend application.

**Tech Stack:**
- React 18+ (Vite)
- Tailwind CSS v4
- React Router v7
- Axios
- Lucide React (Icons)
- Swagger UI React

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Component Hierarchy](#component-hierarchy)
3. [State Management](#state-management)
4. [Data Flow](#data-flow)
5. [Component Details](#component-details)
6. [Custom Hooks](#custom-hooks)
7. [API Layer](#api-layer)
8. [Utilities](#utilities)

---

## Project Structure

```
frontend/
├── public/
│   └── mockups/              # HTML/CSS mockups (design prototypes)
│       ├── 01-home.html
│       ├── 02-preferences.html
│       ├── 03-results.html
│       └── 04-swagger-tab.html
│
├── src/
│   ├── api/                  # API client and mock data
│   │   ├── apiClient.js      # Main API client with axios
│   │   └── mockApi.js        # Mock API using real sensor data
│   │
│   ├── components/           # Reusable React components
│   │   ├── PreferenceMatrix.jsx    # Saaty scale sliders
│   │   ├── SaatySlider.jsx         # Individual pairwise slider
│   │   ├── ProfileAdjuster.jsx     # Environmental thresholds
│   │   ├── RangeSlider.jsx         # Individual threshold slider
│   │   ├── RoomRanking.jsx         # Rankings table
│   │   └── ScoreBreakdown.jsx      # Expandable score details
│   │
│   ├── constants/            # Constants and configuration
│   │   └── euStandards.js    # EU IEQ standards (EN 16798-1)
│   │
│   ├── hooks/                # Custom React hooks
│   │   └── useRoomRanking.js # Room ranking state management
│   │
│   ├── pages/                # Page components (routes)
│   │   ├── HomePage.jsx      # Landing page
│   │   ├── RoomSelection.jsx # Main room selection page
│   │   └── SwaggerDocs.jsx   # API documentation page
│   │
│   ├── styles/               # Global styles
│   │   └── index.css         # Tailwind imports + custom CSS
│   │
│   ├── utils/                # Utility functions
│   │   └── ahpCalculations.js # AHP weight calculations
│   │
│   ├── App.jsx               # Main app component with routing
│   └── main.jsx              # Entry point
│
├── .env.development          # Development environment config
├── .env.production           # Production environment config
├── package.json              # Dependencies
├── postcss.config.js         # PostCSS with Tailwind plugin
├── tailwind.config.js        # Tailwind CSS configuration
└── vite.config.js            # Vite configuration
```

---

## Component Hierarchy

```
App (Router)
│
├── Navigation (in App.jsx)
│   ├── Link: Home
│   ├── Link: Room Selection
│   └── Link: API Docs
│
└── Routes
    ├── HomePage
    │   └── (static content)
    │
    ├── RoomSelection
    │   ├── PreferenceMatrix
    │   │   ├── SaatySlider (Comfort ↔ Health)
    │   │   ├── SaatySlider (Comfort ↔ Usability)
    │   │   └── SaatySlider (Health ↔ Usability)
    │   │
    │   ├── ProfileAdjuster
    │   │   ├── RangeSlider (Temperature)
    │   │   ├── RangeSlider (CO2)
    │   │   ├── RangeSlider (Humidity)
    │   │   ├── RangeSlider (Noise)
    │   │   └── RangeSlider (Light)
    │   │
    │   └── RoomRanking
    │       └── ScoreBreakdown (expandable, per room)
    │
    └── SwaggerDocs
        └── SwaggerUI (from swagger-ui-react)
```

---

## State Management

### State Architecture

The app uses **React local state** with hooks. No global state management library (Redux, Zustand) is used to keep it simple.

### State Locations

**App-level State:**
- None (router handles navigation)

**Page-level State (`RoomSelection.jsx`):**
```javascript
const [preferences, setPreferences] = useState({
  comparisons: {},      // Raw Saaty values
  weights: {},          // Calculated weights
  consistencyRatio: 0   // CR value
})

const [profile, setProfile] = useState({
  temperature: { min: 20, max: 24 },
  co2: { min: 0, max: 600 },
  // ... other thresholds
})

// From useRoomRanking hook:
const { rankings, loading, error } = useRoomRanking()
```

**Component-level State:**

`PreferenceMatrix.jsx`:
```javascript
const [comparisons, setComparisons] = useState({
  'Comfort vs Health': 1,
  'Comfort vs Usability': 1,
  'Health vs Usability': 1
})
```

`ProfileAdjuster.jsx`:
```javascript
const [profile, setProfile] = useState(getDefaultProfile())
```

`RoomRanking.jsx`:
```javascript
const [expandedRows, setExpandedRows] = useState(new Set())
```

`RangeSlider.jsx` (local):
```javascript
const [localValue, setLocalValue] = useState(value)
```

---

## Data Flow

### Top-Down Data Flow

```
User Interaction
      ↓
Component State Update
      ↓
Parent Callback (onPreferencesChange, onProfileChange)
      ↓
Page State Update (RoomSelection.jsx)
      ↓
Click "Evaluate Rooms"
      ↓
API Call (useRoomRanking hook)
      ↓
Backend/Mock API
      ↓
Rankings State Update
      ↓
RoomRanking Component Re-renders
```

### Example Flow: Adjusting Saaty Slider

```javascript
// 1. User drags slider
SaatySlider.jsx: handleSliderChange(7)
      ↓
// 2. Local state updates
setLocalValue(7)
      ↓
// 3. Parent callback
onChange('Comfort vs Health', 7)
      ↓
// 4. PreferenceMatrix updates
PreferenceMatrix.jsx: setComparisons({ 'Comfort vs Health': 7, ... })
      ↓
// 5. Weights calculated
useEffect → calculateWeights() → weights: { Comfort: 0.54, ... }
      ↓
// 6. Parent notified
onPreferencesChange({ comparisons, weights, consistencyRatio })
      ↓
// 7. Page state updates
RoomSelection.jsx: setPreferences({ ... })
```

---

## Component Details

### Pages

#### `HomePage.jsx`

**Purpose:** Landing page

**Props:** None

**State:** None

**Exports:** `HomePage` (default)

**File:** `/src/pages/HomePage.jsx`

---

#### `RoomSelection.jsx`

**Purpose:** Main page for room selection

**Props:** None

**State:**
```javascript
preferences: {
  comparisons: Object,
  weights: Object,
  consistencyRatio: number
}
profile: Object (environmental thresholds)
```

**Hooks Used:**
- `useState` - Local state
- `useRoomRanking` - Rankings, loading, error

**Event Handlers:**
- `handlePreferencesChange(newPreferences)` - Updates preferences state
- `handleProfileChange(newProfile)` - Updates profile state
- `handleEvaluateRooms()` - Calls API to evaluate rooms

**Exports:** `RoomSelection` (default)

**File:** `/src/pages/RoomSelection.jsx`

---

#### `SwaggerDocs.jsx`

**Purpose:** API documentation page

**Props:** None

**State:** None

**Dependencies:**
- `swagger-ui-react` - Embedded Swagger UI
- `apiConfig` from `apiClient.js` - API configuration

**Exports:** `SwaggerDocs` (default)

**File:** `/src/pages/SwaggerDocs.jsx`

---

### Components

#### `PreferenceMatrix.jsx`

**Purpose:** Manages all Saaty scale pairwise comparisons

**Props:**
```typescript
{
  onPreferencesChange?: (preferences: Object) => void
}
```

**State:**
```javascript
comparisons: {
  'Comfort vs Health': number (1-9),
  'Comfort vs Usability': number (1-9),
  'Health vs Usability': number (1-9)
}
```

**Children:**
- 3x `SaatySlider` components

**Methods:**
- `handleComparisonChange(pairName, value)` - Updates single comparison
- `useEffect` - Calculates weights & CR when comparisons change

**Dependencies:**
- `calculateWeights()` from `utils/ahpCalculations.js`
- `calculateConsistencyRatio()` from `utils/ahpCalculations.js`

**Exports:** `PreferenceMatrix` (default)

**File:** `/src/components/PreferenceMatrix.jsx`

---

#### `SaatySlider.jsx`

**Purpose:** Single Saaty scale slider for pairwise comparison

**Props:**
```typescript
{
  label: string,              // e.g., "Comfort vs Health"
  leftLabel: string,          // e.g., "Comfort"
  rightLabel: string,         // e.g., "Health"
  value: number,              // 1-9
  onChange: (value: number) => void
}
```

**State:**
```javascript
localValue: number  // 1-9, synced with props
```

**Features:**
- Visual scale with 5 labels
- Color-coded sections
- Current value display

**Exports:** `SaatySlider` (default)

**File:** `/src/components/SaatySlider.jsx`

---

#### `ProfileAdjuster.jsx`

**Purpose:** Manages all environmental threshold sliders

**Props:**
```typescript
{
  onProfileChange?: (profile: Object) => void
}
```

**State:**
```javascript
profile: {
  temperature: { min: number, max: number },
  co2: { min: number, max: number },
  humidity: { min: number, max: number },
  noise: { min: number, max: number },
  light: { min: number, max: number }
}
```

**Children:**
- 5x `RangeSlider` components

**Methods:**
- `handleCriterionChange(criterion, value)` - Updates single threshold
- `handleReset()` - Resets all to EU defaults

**Dependencies:**
- `EU_STANDARDS` from `constants/euStandards.js`
- `getDefaultProfile()` from `constants/euStandards.js`

**Exports:** `ProfileAdjuster` (default)

**File:** `/src/components/ProfileAdjuster.jsx`

---

#### `RangeSlider.jsx`

**Purpose:** Single threshold slider with optimal range indicator

**Props:**
```typescript
{
  label: string,              // e.g., "Temperature"
  icon: string,               // Emoji icon
  value: number,              // Current threshold
  min: number,                // Absolute min
  max: number,                // Absolute max
  step: number,               // Increment step
  unit: string,               // e.g., "°C"
  optimalMin: number,         // Optimal range start
  optimalMax: number,         // Optimal range end
  onChange: (value: number) => void,
  euStandard: string          // Description
}
```

**State:**
```javascript
localValue: number  // Synced with props via useEffect
```

**Features:**
- Visual optimal range (green background)
- Dynamic thumb color (green/orange)
- Current value display
- EU standard info box

**Exports:** `RangeSlider` (default)

**File:** `/src/components/RangeSlider.jsx`

---

#### `RoomRanking.jsx`

**Purpose:** Display ranked rooms in table format

**Props:**
```typescript
{
  rankings: Array<Room>,
  consistencyRatio: number
}

type Room = {
  rank: number,
  room_id: string,
  room_name: string,
  final_score: number,
  comfort_score: number,
  health_score: number,
  usability_score: number,
  temperature: number,
  co2: number,
  humidity: number,
  // ... other properties
}
```

**State:**
```javascript
expandedRows: Set<string>  // Set of expanded room_ids
```

**Children:**
- Multiple `ScoreBreakdown` components (expandable)

**Methods:**
- `toggleRow(roomId)` - Expand/collapse score breakdown
- `getRankBadgeClass(rank)` - Returns CSS class for rank badge
- `getStatusBadge(value, min, max)` - Returns status badge config

**Exports:** `RoomRanking` (default)

**File:** `/src/components/RoomRanking.jsx`

---

#### `ScoreBreakdown.jsx`

**Purpose:** Show detailed score breakdown for a room

**Props:**
```typescript
{
  room: Room  // Full room object with scores
}
```

**State:** None

**Features:**
- Score breakdown cards (Comfort, Health, Usability)
- Environmental readings with units
- Progress bars for scores
- Facility badges

**Exports:** `ScoreBreakdown` (default)

**File:** `/src/components/ScoreBreakdown.jsx`

---

## Custom Hooks

### `useRoomRanking()`

**Purpose:** Manage room ranking state and API calls

**Location:** `/src/hooks/useRoomRanking.js`

**Returns:**
```typescript
{
  rankings: Object | null,
  loading: boolean,
  error: string | null,
  evaluateRooms: (preferences: Object) => Promise<Object>,
  clearRankings: () => void,
  clearError: () => void
}
```

**Internal State:**
```javascript
rankings: Object | null
loading: boolean
error: string | null
```

**Methods:**

`evaluateRooms(preferences)`:
- Validates preferences
- Calls `apiClient.evaluateRooms()`
- Handles errors with user-friendly messages
- Updates rankings state

`clearRankings()`:
- Resets rankings to null
- Clears error

`clearError()`:
- Clears error message

**Error Handling:**
- 400: "Invalid preferences"
- 404: "Backend not running"
- 422: "Validation error"
- 500: "Server error"
- Network: "Cannot connect to backend"

**Usage Example:**
```javascript
const { rankings, loading, error, evaluateRooms } = useRoomRanking()

const handleSubmit = async () => {
  await evaluateRooms({
    saaty_preferences: comparisons,
    weights: weights,
    profile_adjustments: profile
  })
}
```

---

## API Layer

### `apiClient.js`

**Location:** `/src/api/apiClient.js`

**Purpose:** Main API client with mock/real API switching

**Configuration:**
```javascript
API_BASE_URL: string  // from VITE_API_URL env var
USE_MOCK: boolean     // from VITE_USE_MOCK_API env var
```

**Axios Instance:**
```javascript
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})
```

**Interceptors:**

Request Interceptor:
- Logs requests in development
- Adds Authorization header if token exists

Response Interceptor:
- Logs responses in development
- Handles authentication errors (401)
- Provides detailed error logging

**Methods:**

`getRooms()`:
```typescript
() => Promise<Array<Room>>
```
- GET /api/rooms
- Returns list of all rooms

`evaluateRooms(preferences)`:
```typescript
(preferences: Object) => Promise<{
  rankings: Array<Room>,
  weights: Object,
  consistency_ratio: number,
  is_consistent: boolean
}>
```
- POST /api/evaluate
- Returns ranked rooms

`getCriteria()`:
```typescript
() => Promise<Object>
```
- GET /api/criteria
- Returns AHP criteria hierarchy

`healthCheck()`:
```typescript
() => Promise<{ status: string }>
```
- GET /health
- Tests backend availability

**Exports:**
```javascript
export default apiClient
export const apiConfig = { baseURL, useMock, isDevelopment }
```

---

### `mockApi.js`

**Location:** `/src/api/mockApi.js`

**Purpose:** Mock API for development (uses real sensor data)

**Data Source:**
```javascript
import roomsData from '../../../docs/project info&data/Project_sensor_data/aggregated_rooms.json'
```

**Scoring Functions:**

`scoreCriterion(value, userMin, userMax, absoluteMin, absoluteMax)`:
- Returns 1.0 if within user's optimal range
- Scales down based on distance from range

`calculateComfortScore(room, profile)`:
- Scores based on temperature, humidity, noise, light
- Weighted: Temp (35%), Humidity (25%), Noise (20%), Light (20%)

`calculateHealthScore(room, profile)`:
- Scores based on CO2, air quality, VOC
- Weighted: CO2 (50%), AQ (30%), VOC (20%)

`calculateUsabilityScore(room)`:
- Scores based on facilities (projector, computers, robots)
- Base score 0.5 + bonuses for equipment

**Methods:**

`getRooms()`:
- Returns raw room data with 300ms delay

`evaluateRooms(preferences)`:
- Uses user's weights and profile
- Calculates comfort/health/usability scores
- Computes weighted final score
- Sorts and returns rankings
- 500ms delay to simulate network

`getCriteria()`:
- Returns mock AHP criteria hierarchy
- 200ms delay

---

## Utilities

### `ahpCalculations.js`

**Location:** `/src/utils/ahpCalculations.js`

**Purpose:** AHP (Analytic Hierarchy Process) calculations

**Functions:**

`calculateWeights(comparisons)`:
```typescript
(comparisons: Object<string, number>) => Object<string, number>
```
- Input: Pairwise comparison values (1-9)
- Uses geometric mean method
- Returns normalized weights
- Example:
  ```javascript
  calculateWeights({
    'Comfort vs Health': 3,
    'Comfort vs Usability': 5,
    'Health vs Usability': 2
  })
  // Returns: { Comfort: 0.54, Health: 0.30, Usability: 0.16 }
  ```

`calculateConsistencyRatio(comparisons, weights)`:
```typescript
(comparisons: Object, weights: Object) => number
```
- Calculates CR (Consistency Ratio)
- CR < 0.1 = Consistent
- CR ≥ 0.1 = Inconsistent (user should revise)
- Uses Random Index (RI) for n=3: 0.58

**Algorithm:**
```
1. Build pairwise matrix from comparisons
2. Multiply matrix by weight vector
3. Calculate λ_max (principal eigenvalue)
4. CI = (λ_max - n) / (n - 1)
5. CR = CI / RI
```

---

### `euStandards.js`

**Location:** `/src/constants/euStandards.js`

**Purpose:** EU Indoor Environmental Quality standards

**Data Structure:**
```javascript
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
    categories: { excellent, good, acceptable }
  },
  // ... co2, humidity, noise, light, voc, airQuality
}
```

**Functions:**

`getDefaultProfile()`:
```typescript
() => Object
```
- Returns profile with optimal values for all criteria

`isOptimal(criterion, value)`:
```typescript
(criterion: string, value: number) => boolean
```
- Checks if value is in optimal range

`getCategory(criterion, value)`:
```typescript
(criterion: string, value: number) => 'excellent' | 'good' | 'acceptable' | 'poor'
```
- Categorizes value based on EU standards

---

## Performance Considerations

### Optimization Techniques

1. **Controlled Components with Local State:**
   - Sliders use `localValue` to avoid parent re-renders on every drag
   - Only notify parent on `onChange` (drag end)

2. **useCallback for Event Handlers:**
   - Prevents unnecessary re-renders in child components

3. **Conditional Rendering:**
   - `ScoreBreakdown` only renders when expanded
   - `SwaggerUI` only loads when on API docs page

4. **Debouncing (Future):**
   - Could debounce slider changes for even better performance

### Bundle Size

Current dependencies:
- React: ~140KB
- React Router: ~11KB
- Axios: ~13KB
- Swagger UI React: ~600KB (only loaded on /api-docs page)
- Lucide React: ~2KB per icon (tree-shaken)
- Tailwind CSS: ~10KB (purged in production)

**Total:** ~800KB (gzipped: ~250KB)

---

## Testing Strategy

### Component Testing (Future)

```javascript
// Example: Testing SaatySlider
import { render, fireEvent } from '@testing-library/react'
import SaatySlider from './SaatySlider'

test('calls onChange when slider value changes', () => {
  const handleChange = jest.fn()
  const { getByRole } = render(
    <SaatySlider
      label="Comfort vs Health"
      leftLabel="Comfort"
      rightLabel="Health"
      value={1}
      onChange={handleChange}
    />
  )

  const slider = getByRole('slider')
  fireEvent.change(slider, { target: { value: '5' } })

  expect(handleChange).toHaveBeenCalledWith(5)
})
```

### Integration Testing

Test user flows:
1. Adjust preferences → Evaluate → See rankings
2. Expand breakdown → See detailed scores
3. Reset profile → Values return to defaults

---

## Deployment

### Build Process

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Environment Variables

**Development (`.env.development`):**
```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK_API=true
```

**Production (`.env.production`):**
```env
VITE_API_URL=https://api.example.com
VITE_USE_MOCK_API=false
```

### Build Output

```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js      # Main bundle
│   ├── index-[hash].css     # Styles
│   └── [vendor]-[hash].js   # Third-party code
└── favicon.ico
```

---

**Document Version:** 1.0
**Last Updated:** 2024-12-20
**Author:** Filip Zekonja
