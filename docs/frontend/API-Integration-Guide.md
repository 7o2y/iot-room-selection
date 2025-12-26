# API Integration Guide

## Overview

The frontend is designed to work seamlessly with both a **mock API** (for development) and the **real FastAPI backend** (for production). This guide explains how the API client works and how to integrate with Anthony's backend when it's ready.

---

## Architecture

### File Structure
```
frontend/src/api/
├── apiClient.js       # Main API client with mock/real switching
├── mockApi.js         # Mock API using real sensor data
├── .env.development   # Development environment config (uses mock)
└── .env.production    # Production environment config (uses real API)

frontend/src/hooks/
└── useRoomRanking.js  # React hook for room ranking state management
```

### API Client (`apiClient.js`)

The API client uses **axios** and automatically switches between mock and real APIs based on the `VITE_USE_MOCK_API` environment variable.

**Key Features:**
- ✅ Environment-based switching (mock vs real API)
- ✅ Request/response interceptors for logging
- ✅ Global error handling
- ✅ Authentication token support
- ✅ Comprehensive error messages
- ✅ Request validation
- ✅ Health check endpoint

---

## Configuration

### Environment Variables

**`.env.development`** (Mock API - Default)
```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK_API=true
```

**`.env.production`** (Real API)
```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK_API=false
```

### Switching Between Mock and Real API

**Option 1: Change environment file**
```bash
# Development (mock)
npm run dev

# Production (real API)
npm run build && npm run preview
```

**Option 2: Override environment variable**
```bash
# Use real API in development
VITE_USE_MOCK_API=false npm run dev
```

**Option 3: Edit `.env.development`**
```env
VITE_USE_MOCK_API=false  # Change to false
```

---

## API Endpoints

### 1. Get All Rooms
**Endpoint:** `GET /api/rooms`

**Response:**
```json
[
  {
    "room_id": "MSA_4_450",
    "name": "MSA 4.450",
    "temperature": 23.0,
    "co2": 695.3,
    "humidity": 50.2,
    "air_quality": 25.1,
    "seating_capacity": 23,
    "has_projector": true,
    "computers": 20,
    "has_robots": true
  }
]
```

**Frontend Usage:**
```javascript
import apiClient from '../api/apiClient'

const rooms = await apiClient.getRooms()
```

---

### 2. Evaluate and Rank Rooms
**Endpoint:** `POST /api/evaluate`

**Request Payload:**
```json
{
  "saaty_preferences": {
    "Comfort vs Health": 3,
    "Comfort vs Usability": 5,
    "Health vs Usability": 2
  },
  "weights": {
    "Comfort": 0.40,
    "Health": 0.35,
    "Usability": 0.25
  },
  "profile_adjustments": {
    "temperature": { "min": 20, "max": 24 },
    "co2": { "min": 0, "max": 600 },
    "humidity": { "min": 40, "max": 60 },
    "noise": { "min": 0, "max": 35 },
    "light": { "min": 300, "max": 500 }
  }
}
```

**Response:**
```json
{
  "rankings": [
    {
      "rank": 1,
      "room_id": "MSA_4_450",
      "room_name": "MSA 4.450",
      "final_score": 0.92,
      "comfort_score": 0.89,
      "health_score": 0.95,
      "usability_score": 0.91,
      "temperature": 23.0,
      "co2": 695.3,
      "humidity": 50.2,
      "air_quality": 25.1,
      "seating_capacity": 23,
      "has_projector": true,
      "computers": 20,
      "has_robots": true
    }
  ],
  "weights": {
    "Comfort": 0.40,
    "Health": 0.35,
    "Usability": 0.25
  },
  "consistency_ratio": 0.05,
  "is_consistent": true
}
```

**Frontend Usage:**
```javascript
import apiClient from '../api/apiClient'

const result = await apiClient.evaluateRooms({
  saaty_preferences: comparisons,
  weights: weights,
  profile_adjustments: profile
})
```

---

### 3. Get Criteria Hierarchy
**Endpoint:** `GET /api/criteria`

**Response:**
```json
{
  "main": ["Comfort", "Health", "Usability"],
  "comfort": ["Temperature", "Lighting", "Noise", "Humidity"],
  "health": ["CO2", "Air Quality", "VOC"],
  "usability": ["Seating", "Equipment", "AV Facilities"],
  "weights": {
    "main": {
      "Comfort": 0.40,
      "Health": 0.35,
      "Usability": 0.25
    }
  }
}
```

---

### 4. Health Check (Optional)
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Using the `useRoomRanking` Hook

The `useRoomRanking` hook provides state management and error handling for room ranking.

**Example Usage:**
```javascript
import useRoomRanking from '../hooks/useRoomRanking'

function MyComponent() {
  const { rankings, loading, error, evaluateRooms, clearError } = useRoomRanking()

  const handleEvaluate = async () => {
    try {
      await evaluateRooms({
        saaty_preferences: comparisons,
        weights: weights,
        profile_adjustments: profile
      })
    } catch (err) {
      // Error is already handled by the hook
      console.error(err)
    }
  }

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {rankings && <RoomRanking data={rankings} />}
    </div>
  )
}
```

**Hook API:**
```javascript
{
  rankings: Object | null,       // Current rankings result
  loading: boolean,               // Loading state
  error: string | null,           // Error message
  evaluateRooms: (prefs) => Promise,  // Evaluate rooms
  clearRankings: () => void,      // Clear rankings
  clearError: () => void          // Clear error message
}
```

---

## Error Handling

### Error Types

The API client and hook handle these error scenarios:

| Status Code | Meaning | User Message |
|------------|---------|--------------|
| 400 | Bad Request | "Invalid preferences. Please check your inputs." |
| 401 | Unauthorized | "Authentication required" |
| 403 | Forbidden | "Access forbidden" |
| 404 | Not Found | "API endpoint not found. Backend may not be running." |
| 422 | Validation Error | "Validation error: [details]" |
| 500 | Server Error | "Server error. Please try again later." |
| 503 | Service Unavailable | "Service unavailable. Backend may be down." |
| No Response | Network Error | "Cannot connect to backend. Please check if the server is running." |

### Custom Error Handling

```javascript
try {
  const result = await apiClient.evaluateRooms(preferences)
} catch (error) {
  if (error.message.includes('not found')) {
    // Backend not running
    console.error('Start the backend server first')
  } else if (error.message.includes('Invalid preferences')) {
    // Validation error
    console.error('Check your input data')
  } else {
    // Generic error
    console.error('Something went wrong')
  }
}
```

---

## Interceptors

### Request Interceptor
- Logs all requests in development mode
- Adds `Authorization: Bearer <token>` header if available
- Can be extended for CSRF tokens, custom headers, etc.

### Response Interceptor
- Logs all responses in development mode
- Handles authentication errors (401)
- Provides detailed error logging

---

## Integration Checklist for Backend Team (Anthony)

When the FastAPI backend is ready, follow these steps:

### 1. Verify API Endpoints Match
Ensure your FastAPI routes match the expected endpoints:
- ✅ `GET /api/rooms` - Returns list of rooms
- ✅ `POST /api/evaluate` - Accepts preferences, returns rankings
- ✅ `GET /api/criteria` - Returns criteria hierarchy
- ✅ `GET /health` - Optional health check

### 2. Verify Response Formats
Check that response structures match the expected format (see API Endpoints section above).

**Key fields required:**
- `rankings` array in `/api/evaluate` response
- `final_score`, `comfort_score`, `health_score`, `usability_score` in each ranking
- `consistency_ratio` in rankings response

### 3. Enable CORS
Add CORS middleware to FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Test Backend Locally
```bash
# Start FastAPI backend
cd backend
uvicorn app.main:app --reload --port 8000

# In another terminal, start frontend with real API
cd frontend
VITE_USE_MOCK_API=false npm run dev
```

### 5. Verify Integration
- Open browser console and check for `[API Request]` logs
- Click "Evaluate Rooms" and verify API call succeeds
- Check that rankings display correctly

### 6. Update Environment Variables
Once backend is confirmed working:
```env
# frontend/.env.production
VITE_API_URL=http://your-backend-url
VITE_USE_MOCK_API=false
```

---

## Testing

### Test Mock API
```bash
# Uses mock API (default)
npm run dev
# Open http://localhost:5174
# Click "Evaluate Rooms" - should work
```

### Test Real API
```bash
# Start backend first (Anthony's work)
cd backend && uvicorn app.main:app --reload

# Start frontend with real API
cd frontend
VITE_USE_MOCK_API=false npm run dev
# Open http://localhost:5174
# Click "Evaluate Rooms" - should call real backend
```

### Debug API Calls
Open browser console and look for:
```
[API Client] Using mock API for evaluateRooms
[API Request] POST /api/evaluate {data}
[API Response] /api/evaluate {response}
```

---

## Troubleshooting

### "Cannot connect to backend"
- ✅ Check if backend is running (`http://localhost:8000/docs`)
- ✅ Verify `VITE_API_URL` in `.env.development`
- ✅ Check CORS is enabled in backend
- ✅ Try using mock API: `VITE_USE_MOCK_API=true`

### "Invalid response format"
- ✅ Check backend response structure matches expected format
- ✅ Verify `rankings` array exists in response
- ✅ Check all required fields are present

### "404 Not Found"
- ✅ Verify backend route is `/api/evaluate` not `/evaluate`
- ✅ Check FastAPI route decorators match expected paths
- ✅ Use Swagger UI to test endpoints: `http://localhost:8000/docs`

### Rankings not displaying
- ✅ Open browser console for errors
- ✅ Check API response contains `rankings` array
- ✅ Verify `final_score` values are between 0 and 1
- ✅ Check React DevTools for state updates

---

## Next Steps

**Current Status:** ✅ Frontend ready for integration
**Waiting On:** Anthony's FastAPI implementation (Tasks 6-10)

**When backend is ready:**
1. Update `.env.production` with backend URL
2. Set `VITE_USE_MOCK_API=false`
3. Run integration tests
4. Deploy frontend and backend together

---

## Contact

**Frontend:** Filip (UI1 implementation)
**Backend:** Anthony (FastAPI + AHP integration)
**Algorithm:** Fede (AHP Python implementation)

---

## References

- [FastAPI CORS Docs](https://fastapi.tiangolo.com/tutorial/cors/)
- [Axios Interceptors](https://axios-http.com/docs/interceptors)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
