# Grafana Dashboard - IoT Room Monitoring

## Overview

This directory contains the Grafana configuration for monitoring IoT room sensors in real-time.

**Purpose:** Admin dashboard for facility managers to monitor all rooms, view trends, and receive alerts.

**Access:**
- **URL:** http://localhost:3000
- **Default Credentials:**
  - Username: `admin`
  - Password: `admin`
  - ⚠️ **CHANGE IN PRODUCTION!**

---

## Quick Start

### Prerequisites

- **Docker:** Installed and running
- **Docker Compose:** v2.0+
- **Backend API:** Running on http://localhost:8000 (optional for testing)

### Start Grafana

```bash
# Navigate to grafana directory
cd grafana

# Start Grafana container
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f grafana
```

**Expected Output:**
```
[+] Running 1/1
 ✔ Container iot-room-grafana  Started
```

### Access Grafana

1. **Open browser:** http://localhost:3000
2. **Login:**
   - Username: `admin`
   - Password: `admin`
3. **You'll be prompted to change password** (skip for development)

### Stop Grafana

```bash
docker-compose down

# To remove data volumes:
docker-compose down -v
```

---

## Architecture

### Components

```
┌─────────────────────────────────────────────┐
│  IoT Sensors                                │
│  (Temperature, CO2, Humidity, etc.)         │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  MongoDB Database                           │
│  (Stores sensor readings)                   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  FastAPI Backend                            │
│  http://localhost:8000                      │
│  Serves data via REST API                   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Grafana Dashboard                          │
│  http://localhost:3000                      │
│  Visualizes data in charts/graphs           │
└─────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Admin/Facility Manager                     │
│  Views dashboards in browser                │
└─────────────────────────────────────────────┘
```

---

## Directory Structure

```
grafana/
├── docker-compose.yml              # Docker configuration
├── provisioning/                   # Auto-configuration
│   ├── datasources/
│   │   └── datasource.yml         # Data source config (FastAPI)
│   └── dashboards/
│       └── dashboard.yml          # Dashboard provisioning
├── dashboards/                    # Dashboard JSON files
│   ├── room-monitoring.json       # Main dashboard (Task 33)
│   ├── facilities.json            # Facilities view (Task 34)
│   └── alerts.json                # Alert panels (Task 35)
└── README.md                      # This file
```

---

## Configuration

### Data Sources

Grafana is pre-configured with these data sources:

1. **FastAPI** (Default)
   - Type: Infinity or SimpleJson
   - URL: http://host.docker.internal:8000
   - Purpose: Fetch sensor data from backend

2. **TestData DB**
   - Type: TestData
   - Purpose: Demo/testing data when backend is not running

### Provisioning

**What is Provisioning?**
- Automatic configuration when Grafana starts
- Data sources and dashboards are pre-configured
- No manual setup needed!

**Files:**
- `provisioning/datasources/datasource.yml` - Defines data sources
- `provisioning/dashboards/dashboard.yml` - Tells Grafana where dashboards are
- `dashboards/*.json` - Actual dashboard definitions

---

## Creating Dashboards

### Option 1: Using the UI (Recommended for Learning)

1. **Login to Grafana:** http://localhost:3000
2. **Click "+" → "Dashboard"**
3. **Click "Add visualization"**
4. **Select data source:** FastAPI or TestData DB
5. **Build your panel:**
   - Choose visualization type (Time series, Bar chart, Table, etc.)
   - Configure query
   - Customize appearance
6. **Save dashboard**
7. **Export as JSON** (Dashboard settings → JSON Model → Copy)
8. **Save to `dashboards/` folder**

### Option 2: Using JSON Files (Pre-configured)

Dashboard JSON files will be created in Tasks 33-35:
- **Task 33:** Sensor data panels (temperature, CO2, humidity charts)
- **Task 34:** Facilities and calendar views
- **Task 35:** Disconnection alerts

---

## Connecting to Backend

### When Backend is Running

Grafana connects to the FastAPI backend at `http://host.docker.internal:8000`.

**Required Backend Endpoints:**

```
GET /api/grafana/query          # Query sensor data
POST /api/grafana/search        # Search available metrics
GET /api/grafana/annotations    # Get events/annotations
```

**Test Backend Connection:**

```bash
# Check if backend is running
curl http://localhost:8000/health

# Test Grafana endpoint (if implemented)
curl http://localhost:8000/api/grafana/query
```

### When Backend is NOT Running (Demo Mode)

Use the **TestData DB** data source:
1. Go to Dashboard
2. Add Panel
3. Select "TestData DB" as data source
4. Choose scenario (Random Walk, CSV, etc.)
5. This generates fake data for demonstration

---

## Common Operations

### View Logs

```bash
docker-compose logs -f grafana
```

### Restart Grafana

```bash
docker-compose restart grafana
```

### Reset Grafana (Delete All Data)

```bash
# Stop and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Change Admin Password

**Method 1: Via UI**
1. Login as admin
2. Click profile icon → Preferences
3. Change Password

**Method 2: Via Environment Variable**
```yaml
# In docker-compose.yml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=new-secure-password
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

---

## Plugins

### Installing Plugins

Some dashboards may require additional plugins:

**Method 1: Environment Variable (docker-compose.yml)**
```yaml
environment:
  - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource,grafana-infinity-datasource
```

**Method 2: Manual Installation**
```bash
# Access container
docker exec -it iot-room-grafana bash

# Install plugin
grafana-cli plugins install grafana-infinity-datasource

# Exit and restart
exit
docker-compose restart grafana
```

### Recommended Plugins

- **Infinity Data Source** - Fetch data from any REST API
- **SimpleJson** - JSON-based data source
- **MongoDB** - Direct MongoDB connection (if not using FastAPI)
- **Clock Panel** - Display current time
- **Stat Panel** - Display single values

---

## Dashboards Overview

### 1. Room Monitoring Dashboard (Task 33)

**Purpose:** Real-time sensor monitoring

**Panels:**
- Temperature trends (line chart, all rooms)
- CO2 levels (bar chart, current values)
- Humidity trends (area chart)
- Air quality index (gauge)
- Multi-room comparison table

**Refresh:** Every 30 seconds

---

### 2. Facilities Dashboard (Task 34)

**Purpose:** Room availability and facilities

**Panels:**
- Room status table (available/occupied)
- Calendar events (upcoming reservations)
- Facility breakdown (projectors, computers, robots)
- Seating capacity visualization

**Refresh:** Every 5 minutes

---

### 3. Alerts Dashboard (Task 35)

**Purpose:** Sensor health and alerts

**Panels:**
- Disconnected sensors list
- Alert history timeline
- Threshold violations (CO2 > 1000, temp > 26°C)
- Sensor uptime stats

**Alerts:**
- Email/Slack notification when sensor disconnects
- Warning when environmental thresholds exceeded

---

## Troubleshooting

### Issue: Cannot Access Grafana at http://localhost:3000

**Solution:**
```bash
# Check if container is running
docker-compose ps

# If not running, start it
docker-compose up -d

# Check logs for errors
docker-compose logs grafana

# Try accessing on different port
# Edit docker-compose.yml: ports: - "3001:3000"
```

---

### Issue: "Cannot connect to data source"

**Symptoms:** Dashboards show "No data" or connection errors

**Solution:**

**1. Check if backend is running:**
```bash
curl http://localhost:8000/health
```

**2. If backend is not running:**
- Use TestData DB data source for demo
- Start backend: `cd backend && uvicorn app.main:app --reload`

**3. Check data source configuration:**
- Go to Configuration → Data Sources
- Click "FastAPI"
- Click "Test" button
- Should see "Data source is working"

**4. Check Docker network:**
```bash
# Ensure backend is accessible from container
docker exec iot-room-grafana ping host.docker.internal
```

---

### Issue: Dashboards Not Loading

**Solution:**
```bash
# Check provisioning files
ls -la provisioning/dashboards/
ls -la dashboards/

# Check Grafana logs
docker-compose logs grafana | grep -i error

# Restart Grafana
docker-compose restart grafana
```

---

### Issue: Permission Denied Errors

**Solution:**
```bash
# Fix permissions on volumes
chmod -R 777 grafana/dashboards
chmod -R 777 grafana/provisioning

# Or run container as root (not recommended for production)
# In docker-compose.yml:
# user: "0"
```

---

## Security Considerations

### Development

Current setup is fine for development:
- Default admin password
- Anonymous access disabled
- HTTP (not HTTPS)

### Production

For production deployment:

**1. Change Admin Password:**
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
```

**2. Enable HTTPS:**
```yaml
environment:
  - GF_SERVER_PROTOCOL=https
  - GF_SERVER_CERT_FILE=/etc/grafana/ssl/cert.pem
  - GF_SERVER_CERT_KEY=/etc/grafana/ssl/key.pem
```

**3. Restrict Access:**
```yaml
environment:
  - GF_USERS_ALLOW_SIGN_UP=false
  - GF_USERS_ALLOW_ORG_CREATE=false
```

**4. Use Secrets:**
- Don't hardcode passwords in docker-compose.yml
- Use Docker secrets or environment files
- Add `.env` to `.gitignore`

---

## Integration with Backend

### FastAPI Endpoints for Grafana

Anthony's backend should implement these endpoints:

**1. Query Endpoint**
```python
@app.post("/api/grafana/query")
async def grafana_query(request: GrafanaQueryRequest):
    """
    Return time-series data for Grafana

    Request:
    {
      "range": { "from": "2024-12-20T00:00:00Z", "to": "2024-12-20T23:59:59Z" },
      "targets": [{ "target": "temperature", "refId": "A" }]
    }

    Response:
    [
      {
        "target": "Room 1 Temperature",
        "datapoints": [
          [23.5, 1703030400000],  # [value, timestamp_ms]
          [23.7, 1703034000000],
          ...
        ]
      }
    ]
    """
```

**2. Search Endpoint**
```python
@app.post("/api/grafana/search")
async def grafana_search(request: GrafanaSearchRequest):
    """
    Return available metrics/rooms

    Response: ["temperature", "co2", "humidity", "room_1", "room_2", ...]
    """
```

**3. Health Check**
```python
@app.get("/api/grafana/health")
async def grafana_health():
    """
    Check if Grafana integration is working

    Response: { "status": "ok" }
    """
```

---

## Next Steps

### After Setup (Task 32) ✅
- [x] Grafana is running
- [x] Can access at http://localhost:3000
- [x] Data sources are configured

### Task 33: Create Sensor Data Panels
- [ ] Temperature line chart
- [ ] CO2 bar chart
- [ ] Humidity trends
- [ ] Multi-room comparison

### Task 34: Facilities & Calendar
- [ ] Room availability table
- [ ] Calendar integration
- [ ] Facility stats

### Task 35: Alerts
- [ ] Disconnection detection
- [ ] Email alerts
- [ ] Alert dashboard

---

## Resources

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Infinity Data Source](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/)
- [SimpleJson Data Source](https://grafana.com/grafana/plugins/grafana-simple-json-datasource/)

---

**Setup Complete!** 🎉

Access your Grafana dashboard at: **http://localhost:3000**

**Default Login:**
- Username: `admin`
- Password: `admin`

---

**Version:** 1.0
**Last Updated:** 2024-12-20
**Author:** Filip Zekonja
