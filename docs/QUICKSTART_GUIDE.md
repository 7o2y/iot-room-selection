# Quick Start Guide - IoT Room Selection Backend

This guide will get your backend API running in **5 minutes**.

---

## Prerequisites

- Python 3.11+ installed
- Docker installed (for MongoDB)
- Git repository cloned

---

## Step 1: Set Up MongoDB

Start MongoDB using Docker:

```bash
# Start MongoDB container
docker run -d \
  --name iot-mongodb \
  -p 27017:27017 \
  -v iot_mongodb_data:/data/db \
  mongo:7.0

# Verify it's running
docker ps | grep iot-mongodb
```

---

## Step 2: Set Up Python Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate    # On Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Import Mock Data

```bash
# Run the data import script
python scripts/import_data.py
```

You should see output like:
```
Importing room facilities from room_facilities_data.json...
  ✓ Total rooms in DB: 5

Importing temperature data from temperature_sensor_data.json...
  ✓ Total temperature readings in DB: 51,840
...
✓ Import completed successfully!
```

---

## Step 4: Start the API

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Connected to MongoDB: iot_room_selection
```

---

## Step 5: Test the API

### Open Swagger UI
Visit http://localhost:8000/docs in your browser

### Try these endpoints:

**1. Health Check:**
```bash
curl http://localhost:8000/health
```

**2. Get temperature data for Room_1:**
```bash
curl "http://localhost:8000/api/v1/sensors/Room_1/temperature?limit=5"
```

**3. List all rooms:**
```bash
curl http://localhost:8000/api/v1/rooms/
```

**4. Rank rooms (Decision Support):**
```bash
curl -X POST "http://localhost:8000/api/v1/rank" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria_weights": {
      "temperature": 5,
      "co2": 7,
      "humidity": 3,
      "sound": 5,
      "facilities": 9,
      "availability": 9
    },
    "facility_requirements": {
      "videoprojector": true,
      "min_seating": 30
    }
  }'
```

---

## Step 6: Run Tests (Optional)

```bash
# Run integration tests
pytest -v

# Run with coverage
pytest --cov=app tests/
```

---

## Using Docker Compose (Alternative)

If you prefer to run everything with Docker:

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f backend

# Import data (inside container)
docker-compose exec backend python scripts/import_data.py

# Stop everything
docker-compose down
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (MongoDB URL, etc.)
│   ├── database.py          # MongoDB connection
│   ├── models/              # Pydantic models
│   ├── routers/             # API endpoints
│   └── services/            # Business logic (AHP ranking)
├── scripts/
│   └── import_data.py       # Data import script
├── tests/                   # Integration tests
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

---

## Next Steps

### For Development:

1. **Explore the API**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

2. **Read the Documentation**:
   - MongoDB Schema: `docs/MONGODB_SCHEMA.md`
   - Communication Protocols: `docs/IOT_COMMUNICATION_PROTOCOLS.md`
   - Backend README: `backend/README.md`

3. **Integrate Fede's AHP Algorithm**:
   - Place AHP code in `app/ahp/`
   - Update `app/services/ranking_service.py`
   - See `_calculate_ahp_scores()` method

4. **Add Calendar Integration**:
   - Set up Google Calendar API credentials
   - Create calendar sync script (similar to `scripts/import_data.py`)
   - Run as cron job for periodic sync

### For Deployment:

1. **Deploy to Raspberry Pi**:
   - Follow `backend/README.md` deployment section
   - Use `docker-compose.yml` for easy setup

2. **Configure Production**:
   - Set `DEBUG=False` in `.env`
   - Add JWT authentication (bonus feature)
   - Set up reverse proxy (Nginx)

---

## Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Restart MongoDB
docker restart iot-mongodb

# Check MongoDB logs
docker logs iot-mongodb
```

### Import Script Fails
```bash
# Check file paths exist
ls -la ../docs/project\ info\&data/Project_sensor_data/

# Run with verbose error output
python scripts/import_data.py 2>&1 | tee import.log
```

### Port 8000 Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

### Virtual Environment Issues
```bash
# Deactivate and recreate
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Useful Commands

```bash
# View MongoDB data directly
docker exec -it iot-mongodb mongosh

# Inside mongosh:
use iot_room_selection
db.sensor_readings.countDocuments()
db.rooms.find().pretty()

# Check API logs
tail -f backend.log

# Format code (if using black)
black app/

# Check for errors
pylint app/
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/api/v1/sensors/{room_id}/{sensor_type}` | Get sensor readings |
| GET | `/api/v1/sensors/{room_id}/latest` | Latest readings |
| GET | `/api/v1/rooms/` | List rooms |
| GET | `/api/v1/rooms/{room_id}` | Get room details |
| GET | `/api/v1/calendar/events` | Get calendar events |
| GET | `/api/v1/calendar/availability/{room}` | Check availability |
| POST | `/api/v1/rank` | Rank rooms (Decision Support) |

---

## Support

For issues or questions:
1. Check `docs/MONGODB_SCHEMA.md`
2. Review API docs at `/docs`
3. Run tests with `pytest -v`
4. Check logs with `docker-compose logs`

---

**You're all set! Start building awesome IoT applications! 🚀**
