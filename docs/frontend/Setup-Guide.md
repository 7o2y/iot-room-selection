# Frontend Setup Guide

## Prerequisites

Before setting up the frontend, ensure you have the following installed:

- **Node.js:** v18.0.0 or higher
- **npm:** v9.0.0 or higher (comes with Node.js)
- **Git:** For cloning the repository

Check your versions:
```bash
node --version  # Should be v18.0.0+
npm --version   # Should be v9.0.0+
```

---

## Installation

### 1. Clone the Repository

```bash
cd /path/to/your/workspace
git clone <repository-url>
cd iot-room-selection/frontend
```

### 2. Install Dependencies

```bash
npm install
```

This will install:
- React 18
- React Router v7
- Vite
- Tailwind CSS v4
- Axios
- Lucide React (icons)
- Swagger UI React

**Expected output:**
```
added 243 packages, and audited 466 packages in 15s
```

### 3. Environment Configuration

The frontend comes with two environment files:

**`.env.development`** (for local development):
```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK_API=true
```

**`.env.production`** (for production deployment):
```env
VITE_API_URL=https://your-backend-url.com
VITE_USE_MOCK_API=false
```

**Note:** `.env.development` is used by default when running `npm run dev`

---

## Running the Application

### Development Mode

```bash
npm run dev
```

**Output:**
```
  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5174/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Access the app:**
- Open browser to `http://localhost:5174`
- Hot Module Replacement (HMR) is enabled - changes reflect instantly

### Production Build

```bash
npm run build
```

**Output:**
```
vite v5.x.x building for production...
✓ 245 modules transformed.
dist/index.html                   0.45 kB
dist/assets/index-abc123.css     12.34 kB
dist/assets/index-def456.js     250.12 kB
✓ built in 3.45s
```

### Preview Production Build

```bash
npm run preview
```

Access at `http://localhost:4173`

---

## Development Workflow

### Using Mock API (Default)

By default, the frontend uses a mock API that simulates the backend:

**Advantages:**
- ✅ Works without backend running
- ✅ Uses real sensor data from `aggregated_rooms.json`
- ✅ Fast development iteration
- ✅ No database or backend setup needed

**Limitations:**
- ❌ Mock scoring algorithm (simplified AHP)
- ❌ No real-time data updates
- ❌ Limited to static room data

### Switching to Real Backend

When Anthony's FastAPI backend is ready:

**Step 1: Start the backend**
```bash
cd ../backend
uvicorn app.main:app --reload --port 8000
```

**Step 2: Update environment**
```bash
# In frontend/.env.development
VITE_USE_MOCK_API=false
```

**Step 3: Restart dev server**
```bash
npm run dev
```

**Step 4: Verify connection**
- Open browser console (F12)
- Look for: `[API Request] POST /api/evaluate`
- Should see actual backend responses

---

## Project Structure Tour

```
frontend/
├── public/
│   └── mockups/              # HTML/CSS design prototypes
│
├── src/
│   ├── api/                  # API layer
│   │   ├── apiClient.js      # Main API client
│   │   └── mockApi.js        # Mock API for development
│   │
│   ├── components/           # Reusable UI components
│   │   ├── PreferenceMatrix.jsx
│   │   ├── SaatySlider.jsx
│   │   ├── ProfileAdjuster.jsx
│   │   ├── RangeSlider.jsx
│   │   ├── RoomRanking.jsx
│   │   └── ScoreBreakdown.jsx
│   │
│   ├── constants/            # Configuration & constants
│   │   └── euStandards.js    # EU IEQ standards
│   │
│   ├── hooks/                # Custom React hooks
│   │   └── useRoomRanking.js
│   │
│   ├── pages/                # Page components (routes)
│   │   ├── HomePage.jsx
│   │   ├── RoomSelection.jsx
│   │   └── SwaggerDocs.jsx
│   │
│   ├── styles/               # Global styles
│   │   └── index.css         # Tailwind + custom CSS
│   │
│   ├── utils/                # Utility functions
│   │   └── ahpCalculations.js
│   │
│   └── App.jsx               # Main app with routing
│
├── .env.development          # Dev environment config
├── package.json              # Dependencies
├── postcss.config.js         # PostCSS with Tailwind
├── tailwind.config.js        # Tailwind configuration
└── vite.config.js            # Vite configuration
```

---

## Common Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code (if ESLint is configured)
npm run lint

# Format code (if Prettier is configured)
npm run format
```

---

## Troubleshooting

### Issue: "Port 5174 is already in use"

**Solution:**
```bash
# Kill process using port 5174
# macOS/Linux:
lsof -ti:5174 | xargs kill -9

# Windows:
netstat -ano | findstr :5174
taskkill /PID <PID> /F

# Or use a different port:
npm run dev -- --port 3000
```

---

### Issue: "Module not found"

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

### Issue: Tailwind styles not applying

**Solution:**
1. Check `postcss.config.js` has `@tailwindcss/postcss` plugin
2. Verify `src/styles/index.css` imports Tailwind:
   ```css
   @import "tailwindcss";
   ```
3. Restart dev server

---

### Issue: "Cannot connect to backend"

**Symptoms:** Error message "Cannot connect to backend" after clicking "Evaluate Rooms"

**Solution:**

**Option 1: Use mock API**
```bash
# In .env.development
VITE_USE_MOCK_API=true
```

**Option 2: Start backend**
```bash
cd ../backend
uvicorn app.main:app --reload
# Then restart frontend
```

**Option 3: Check CORS**
- Backend must allow `http://localhost:5174` origin
- Check FastAPI CORS middleware

---

### Issue: Hot reload not working

**Solution:**
```bash
# Restart dev server
# If still broken, try:
npm run dev -- --force
```

---

## IDE Setup

### VS Code (Recommended)

**Extensions:**
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- ES7+ React/Redux/React-Native snippets

**Settings (`.vscode/settings.json`):**
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "tailwindCSS.experimental.classRegex": [
    ["className\\s*=\\s*['\"]([^'\"]*)['\"]", "([^'\"]*)"]
  ]
}
```

---

## Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` | `https://api.example.com` |
| `VITE_USE_MOCK_API` | Use mock API instead of real backend | `true` | `false` |

**Access in code:**
```javascript
import.meta.env.VITE_API_URL
import.meta.env.VITE_USE_MOCK_API
```

---

## Deployment

### Deploying to Netlify

```bash
# Build the app
npm run build

# Deploy dist folder
# Option 1: Netlify CLI
npm install -g netlify-cli
netlify deploy --prod --dir=dist

# Option 2: Drag & drop
# Go to https://app.netlify.com/drop
# Drag the 'dist' folder
```

**Environment Variables on Netlify:**
- Go to Site Settings → Environment Variables
- Add: `VITE_API_URL` = `https://your-backend.com`
- Add: `VITE_USE_MOCK_API` = `false`

---

### Deploying to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts
# Set environment variables in Vercel dashboard
```

---

### Deploying to GitHub Pages

**1. Update `vite.config.js`:**
```javascript
export default defineConfig({
  base: '/iot-room-selection/',  // Your repo name
  // ... rest of config
})
```

**2. Build and deploy:**
```bash
npm run build

# Install gh-pages
npm install --save-dev gh-pages

# Add to package.json scripts:
"deploy": "gh-pages -d dist"

# Deploy
npm run deploy
```

**3. Enable GitHub Pages:**
- Go to repo Settings → Pages
- Source: `gh-pages` branch
- Access at: `https://yourusername.github.io/iot-room-selection/`

---

## Next Steps

After setup:

1. ✅ **Test the app:** Navigate to `http://localhost:5174`
2. ✅ **Explore features:** Try adjusting Saaty sliders and environmental thresholds
3. ✅ **Read documentation:**
   - [UI/UX Documentation](./UI-UX-Documentation.md)
   - [Component Architecture](./Component-Architecture.md)
   - [API Integration Guide](./API-Integration-Guide.md)
4. ✅ **Start developing:** Make changes and see them live with HMR

---

## Getting Help

**Issues?**
- Check [Troubleshooting](#troubleshooting) section above
- Review [Component Architecture](./Component-Architecture.md) for technical details
- Check browser console for error messages

**Contact:**
- **Frontend:** Filip Zekonja
- **Backend:** Anthony Stassart
- **Algorithm:** Fede Newton

---

**Last Updated:** 2025-12-20
**Version:** 1.0
