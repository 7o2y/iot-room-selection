# IoT Communication Protocols Documentation

## System Architecture Overview

The IoT Room Selection system uses a multi-tier architecture with five distinct communication protocols connecting different components:

```
[Sensors] --A--> [Arduino] --B--> [Raspberry Pi] <--C-- [Room Facilities Data]
                                       |
                                       D (Calendar API)
                                       |
                                       v
                                  [MongoDB]
                                       |
                                       E (REST API - FastAPI)
                                       |
                                       v
                            [Frontend / Decision App]
```

---

## Communication Protocol A: Sensors → Arduino

### Protocol: I2C / Analog Signals

**Purpose:** Transfer raw sensor measurements from physical sensors to the Arduino microcontroller.

### Technical Specifications

| Aspect | Details |
|--------|---------|
| **Protocol** | I2C (Inter-Integrated Circuit) for digital sensors, Analog (ADC) for analog sensors |
| **Physical Layer** | Wired connection via GPIO pins |
| **Data Rate** | 100 kHz (Standard I2C) or ADC sampling rate (~1 kHz) |
| **Power** | 3.3V or 5V depending on sensor |
| **Topology** | Multi-drop (I2C bus) or point-to-point (analog) |

### Sensors Used

1. **Temperature Sensor** (e.g., DHT22, DS18B20)
   - Protocol: Digital (1-Wire or I2C)
   - Resolution: 0.1°C
   - Range: -40°C to +80°C

2. **CO2 Sensor** (e.g., MH-Z19, SCD30)
   - Protocol: UART or I2C
   - Range: 400-5000 ppm
   - Accuracy: ±50 ppm

3. **Humidity Sensor** (often integrated with temperature - DHT22)
   - Protocol: Digital
   - Range: 0-100% RH
   - Accuracy: ±2% RH

4. **Sound Sensor** (e.g., Analog microphone module)
   - Protocol: Analog output (ADC)
   - Range: 30-130 dB
   - Output: Voltage proportional to sound level

5. **VOC Sensor** (e.g., SGP30, CCS811)
   - Protocol: I2C
   - Measures: Total Volatile Organic Compounds (tVOC)
   - Range: 0-60000 ppb

6. **Light Intensity Sensor** (e.g., BH1750, TSL2561)
   - Protocol: I2C
   - Range: 1-65535 lux
   - Resolution: 1 lux

### Data Format

For I2C sensors:
```c
// Arduino code example
#include <Wire.h>

void setup() {
  Wire.begin(); // Initialize I2C
}

void loop() {
  Wire.requestFrom(SENSOR_ADDRESS, DATA_LENGTH);
  while (Wire.available()) {
    byte data = Wire.read();
    // Process sensor data
  }
}
```

For analog sensors:
```c
int sensorPin = A0;
int rawValue = analogRead(sensorPin);  // 0-1023
float voltage = rawValue * (5.0 / 1023.0);
float soundLevel = convertToDecibels(voltage);
```

### Justification for Protocol Choice

**Why I2C?**
- ✅ **Multi-device support** - Single bus can handle multiple sensors (up to 127 devices)
- ✅ **Simple wiring** - Only 2 wires (SDA, SCL) + power/ground
- ✅ **Low cost** - Most environmental sensors support I2C
- ✅ **Error detection** - Built-in acknowledgment mechanism
- ✅ **Mature ecosystem** - Extensive Arduino library support

**Why Analog (ADC)?**
- ✅ **Simplicity** - Some sensors (sound) output analog signals directly
- ✅ **Real-time** - No protocol overhead, immediate readings
- ✅ **Compatibility** - Works with any sensor with voltage output

**Alternatives considered:**
- ❌ SPI: Faster but requires more wires (not needed for environmental sensors)
- ❌ 1-Wire: Limited to specific sensors (e.g., DS18B20 temperature)

---

## Communication Protocol B: Arduino → Raspberry Pi

### Protocol: Serial/UART or MQTT over USB

**Purpose:** Transmit aggregated sensor data from Arduino to Raspberry Pi for storage and processing.

### Technical Specifications

| Aspect | Details |
|--------|---------|
| **Protocol** | UART (Serial) or MQTT over USB |
| **Physical Layer** | USB cable (Arduino → Raspberry Pi USB port) |
| **Baud Rate** | 115200 bps (sufficient for low-frequency sensor data) |
| **Data Format** | JSON or CSV |
| **Transmission Frequency** | Every 60 seconds (configurable) |

### Implementation Options

#### Option 1: Serial/UART (Recommended)

**Arduino Code:**
```c
void setup() {
  Serial.begin(115200);
}

void loop() {
  // Read all sensors
  float temp = readTemperature();
  float co2 = readCO2();
  float humidity = readHumidity();

  // Send JSON-formatted data
  Serial.print("{");
  Serial.print("\"room\":\"Room_1\",");
  Serial.print("\"timestamp\":\"");
  Serial.print(getTimestamp());
  Serial.print("\",");
  Serial.print("\"temperature\":");
  Serial.print(temp);
  Serial.print(",\"co2\":");
  Serial.print(co2);
  Serial.print(",\"humidity\":");
  Serial.print(humidity);
  Serial.println("}");

  delay(60000); // 1 minute interval
}
```

**Raspberry Pi Code (Python):**
```python
import serial
import json

ser = serial.Serial('/dev/ttyACM0', 115200)

while True:
    line = ser.readline().decode('utf-8').strip()
    try:
        data = json.loads(line)
        # Store in MongoDB
        db.sensor_readings.insert_one({
            "room_name": data["room"],
            "sensor_type": "temperature",
            "value": data["temperature"],
            "timestamp": datetime.fromisoformat(data["timestamp"])
        })
    except json.JSONDecodeError:
        print(f"Invalid JSON: {line}")
```

#### Option 2: MQTT (Alternative for multiple Arduinos)

If using multiple Arduino units (one per room), MQTT provides better scalability:

**Arduino (with WiFi/Ethernet shield):**
```c
#include <PubSubClient.h>

void publishData() {
  String payload = "{\"temperature\":" + String(temp) + "}";
  client.publish("room/Room_1/sensors", payload.c_str());
}
```

**Raspberry Pi (MQTT Broker):**
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    data = json.loads(message.payload.decode())
    # Store in database

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("room/+/sensors")
client.loop_forever()
```

### Data Format Specification

**JSON Structure:**
```json
{
  "room": "Room_1",
  "timestamp": "2024-12-22T14:30:00Z",
  "temperature": 22.5,
  "co2": 650.0,
  "humidity": 45.0,
  "sound": 42.0,
  "voc": 150.0,
  "light_intensity": 450.0
}
```

### Justification for Protocol Choice

**Why Serial/UART?**
- ✅ **Simplicity** - No network configuration required
- ✅ **Reliability** - Direct wired connection, no packet loss
- ✅ **Low latency** - Real-time data transfer
- ✅ **No additional hardware** - Uses built-in USB/Serial
- ✅ **Power efficient** - USB also provides power to Arduino

**Why MQTT (alternative)?**
- ✅ **Scalability** - Easily add more Arduino units for more rooms
- ✅ **Publish/Subscribe** - Multiple subscribers can receive data
- ✅ **Lightweight** - Designed for IoT, minimal overhead
- ✅ **Industry standard** - Widely used in IoT systems

**Our Choice:** **Serial/UART** for prototype with single Arduino. MQTT for production with multiple rooms.

---

## Communication Protocol C: Room Facilities → Database

### Protocol: HTTP POST / Direct Insert

**Purpose:** Import static/semi-static room facility data into MongoDB.

### Technical Specifications

| Aspect | Details |
|--------|---------|
| **Protocol** | HTTP POST (RESTful) or Direct MongoDB Insert |
| **Data Format** | JSON |
| **Frequency** | One-time import + occasional updates |
| **Authentication** | None for local deployment, JWT for remote |

### Implementation

#### Option 1: Direct MongoDB Import (Initial Setup)

```bash
# Import room facilities from JSON file
mongoimport --db iot_room_selection \
            --collection rooms \
            --file room_facilities_data.json \
            --jsonArray
```

#### Option 2: HTTP API (For Updates)

**POST /api/v1/admin/rooms** (Admin endpoint - to be implemented if needed)

**Request:**
```json
{
  "name": "Room_1",
  "facilities": {
    "videoprojector": true,
    "seating_capacity": 62,
    "computers": 20
  },
  "building": "Building A",
  "floor": 2
}
```

**Python Script for Bulk Import:**
```python
import json
import requests

with open('room_facilities_data.json') as f:
    data = json.load(f)

for room in data['rooms']:
    response = requests.post(
        'http://localhost:8000/api/v1/admin/rooms',
        json=room
    )
    print(f"Imported {room['name']}: {response.status_code}")
```

### Justification

**Why HTTP/Direct Insert?**
- ✅ **Simplicity** - Facilities don't change often, no need for complex protocol
- ✅ **Flexibility** - Easy to update individual rooms via API
- ✅ **Standard** - HTTP is universally supported
- ✅ **Direct insert** - Fastest for initial bulk import

---

## Communication Protocol D: University Calendar → Database

### Protocol: HTTP (Google Calendar API)

**Purpose:** Synchronize room availability from University calendar system.

### Technical Specifications

| Aspect | Details |
|--------|---------|
| **Protocol** | HTTPS (Google Calendar API v3) |
| **Authentication** | OAuth 2.0 |
| **Data Format** | JSON |
| **Sync Frequency** | Every 15 minutes (configurable) |
| **API Endpoint** | `https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events` |

### Implementation

**Python Sync Script:**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Authenticate
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar.readonly']
)

service = build('calendar', 'v3', credentials=credentials)

def sync_calendar(room_name, calendar_id):
    """Sync events for a specific room calendar."""

    # Get events for next 7 days
    now = datetime.utcnow().isoformat() + 'Z'
    time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    # Store in MongoDB
    for event in events:
        db.calendar_events.update_one(
            {'event_id': event['id']},
            {
                '$set': {
                    'room_name': room_name,
                    'title': event['summary'],
                    'start_time': datetime.fromisoformat(event['start']['dateTime']),
                    'end_time': datetime.fromisoformat(event['end']['dateTime']),
                    'status': event['status'],
                    'organizer': event.get('organizer', {}).get('email'),
                    'synced_at': datetime.utcnow()
                }
            },
            upsert=True
        )

    print(f"Synced {len(events)} events for {room_name}")

# Sync all room calendars
room_calendars = {
    'Room_1': 'room1@university.lu',
    'Room_2': 'room2@university.lu',
    # ... more rooms
}

for room_name, calendar_id in room_calendars.items():
    sync_calendar(room_name, calendar_id)
```

**Automated Sync (Cron Job on Raspberry Pi):**
```bash
# Add to crontab: crontab -e
# Run every 15 minutes
*/15 * * * * /usr/bin/python3 /path/to/sync_calendar.py >> /var/log/calendar_sync.log 2>&1
```

### API Request Example

**GET Calendar Events:**
```http
GET https://www.googleapis.com/calendar/v3/calendars/room1@university.lu/events?timeMin=2024-12-22T00:00:00Z&timeMax=2024-12-23T00:00:00Z
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "abc123",
      "summary": "CS101 Lecture",
      "start": {"dateTime": "2024-12-22T14:00:00Z"},
      "end": {"dateTime": "2024-12-22T16:00:00Z"},
      "status": "confirmed",
      "organizer": {"email": "prof.smith@uni.lu"}
    }
  ]
}
```

### Justification

**Why Google Calendar API?**
- ✅ **University Integration** - Most universities use Google Workspace
- ✅ **Reliable** - Google's infrastructure ensures high availability
- ✅ **Real-time** - Push notifications available for immediate updates
- ✅ **OAuth 2.0** - Secure authentication
- ✅ **Rich metadata** - Get organizer, attendees, description, etc.

**Alternatives:**
- Microsoft Graph API (if using Outlook/Exchange)
- iCal/CalDAV (if using open-source calendar)

---

## Communication Protocol E: Backend ↔ Frontend (REST API)

### Protocol: HTTP/HTTPS (REST API - FastAPI)

**Purpose:** Provide access to all system data and decision support functionality for end-users and administrators.

### Technical Specifications

| Aspect | Details |
|--------|---------|
| **Protocol** | HTTP/1.1, upgradeable to HTTP/2 |
| **Architecture** | RESTful API |
| **Data Format** | JSON |
| **Documentation** | OpenAPI 3.0 (Swagger) |
| **Authentication** | JWT (optional, for bonus) |
| **CORS** | Enabled for frontend origins |

### API Specification

#### Base URL
```
http://localhost:8000/api/v1
```

#### Endpoints

**1. Sensor Data**
```http
GET /sensors/{room_id}/{sensor_type}?start=...&end=...&limit=100
GET /sensors/{room_id}/{sensor_type}/stats?start=...&end=...
GET /sensors/{room_id}/latest
```

**Example Request:**
```http
GET /api/v1/sensors/Room_1/temperature?start=2024-12-22T08:00:00Z&end=2024-12-22T17:00:00Z
```

**Example Response:**
```json
{
  "room_name": "Room_1",
  "sensor_type": "temperature",
  "readings": [
    {"timestamp": "2024-12-22T08:00:00Z", "value": 20.5},
    {"timestamp": "2024-12-22T09:00:00Z", "value": 21.2}
  ],
  "count": 2,
  "average": 20.85,
  "min_value": 20.5,
  "max_value": 21.2,
  "unit": "°C"
}
```

**2. Rooms & Facilities**
```http
GET /rooms/
GET /rooms/{room_id}?include_conditions=true
GET /rooms/{room_id}/facilities
```

**Example Response:**
```json
{
  "name": "Room_1",
  "facilities": {
    "videoprojector": true,
    "seating_capacity": 62,
    "computers": 20
  },
  "current_conditions": {
    "temperature": 22.5,
    "co2": 650,
    "humidity": 45
  }
}
```

**3. Calendar**
```http
GET /calendar/events?room_name=Room_1&start=...&end=...
GET /calendar/availability/{room_name}?requested_time=...
GET /calendar/availability/{room_name}/range?start_time=...&duration_minutes=120
```

**4. Decision Support (Ranking)**
```http
POST /rank
GET /rank/example
```

**Example Ranking Request:**
```json
{
  "criteria_weights": {
    "temperature": 5,
    "co2": 7,
    "humidity": 3,
    "sound": 5,
    "facilities": 9,
    "availability": 9
  },
  "environmental_preferences": {
    "temperature_min": 19.0,
    "temperature_max": 22.0,
    "co2_max": 800.0
  },
  "facility_requirements": {
    "videoprojector": true,
    "min_seating": 30
  },
  "requested_time": "2024-12-22T14:00:00Z",
  "duration_minutes": 120
}
```

**Example Ranking Response:**
```json
{
  "ranked_rooms": [
    {
      "room_name": "Room_3",
      "rank": 1,
      "overall_score": 0.87,
      "criteria_scores": {
        "temperature": 0.92,
        "co2": 0.85,
        "facilities": 0.95,
        "availability": 1.0
      },
      "is_available": true
    }
  ],
  "total_rooms_evaluated": 5,
  "timestamp": "2024-12-22T14:30:00Z"
}
```

### HTTP Methods Used

| Method | Purpose | Idempotent |
|--------|---------|------------|
| GET | Retrieve data | Yes |
| POST | Create/compute (ranking) | No |
| PUT | Update (admin) | Yes |
| DELETE | Remove (admin) | Yes |

### Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET/POST |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid JWT |
| 404 | Not Found | Room/data not found |
| 500 | Server Error | Database/internal error |

### Security

**CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**JWT Authentication (Bonus):**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Justification

**Why REST API?**
- ✅ **Stateless** - Each request contains all necessary information
- ✅ **Cacheable** - HTTP caching improves performance
- ✅ **Universal** - Works with any client (web, mobile, IoT)
- ✅ **Self-documenting** - Swagger/OpenAPI auto-generates docs
- ✅ **Scalable** - Can add rate limiting, load balancing easily

**Why JSON?**
- ✅ **Human-readable** - Easy to debug
- ✅ **Language-agnostic** - Every language has JSON support
- ✅ **Lightweight** - Smaller than XML
- ✅ **JavaScript-native** - Perfect for web frontend

**Why FastAPI?**
- ✅ **Automatic docs** - OpenAPI/Swagger built-in
- ✅ **Type validation** - Pydantic models prevent errors
- ✅ **Async support** - Handle multiple requests efficiently
- ✅ **Modern Python** - Uses type hints, async/await
- ✅ **Performance** - One of the fastest Python frameworks

**Alternatives considered:**
- ❌ GraphQL: Too complex for this use case, REST is sufficient
- ❌ WebSockets: Not needed, polling is acceptable for this data frequency
- ❌ gRPC: Overkill, binary format makes debugging harder

---

## Protocol Summary Table

| Comm | Protocol | Rationale | Data Flow Direction |
|------|----------|-----------|---------------------|
| **A** | I2C / Analog | Multi-sensor support, simple wiring, Arduino library support | Sensors → Arduino |
| **B** | Serial/UART or MQTT | Reliable, low-latency, no network config needed | Arduino → Raspberry Pi |
| **C** | HTTP POST / Direct | Simple, infrequent updates, standard format | External → Database |
| **D** | HTTPS (Google API) | University integration, OAuth security, real-time sync | Calendar API → Database |
| **E** | HTTP REST (FastAPI) | Stateless, cacheable, self-documenting, universal | Backend ↔ Frontend |

---

## EU Standards Referenced

### EN 16798-1: Indoor Environmental Quality

**Relevant to Protocols A & B (Sensor Data)**

The sensor selection and thresholds are based on EU standards for indoor environmental quality:

1. **Temperature**: 19-22°C (Category II - Normal level of expectation)
2. **CO2**: <800 ppm (Good air quality), <1000 ppm (Acceptable)
3. **Humidity**: 30-70% RH (Comfort range)
4. **Sound**: <35 dB (quiet), <50 dB (acceptable for offices/classrooms)

These thresholds are used in the AHP ranking algorithm to score rooms.

---

## Future Enhancements

1. **Protocol B**: Upgrade to MQTT for multi-room scalability
2. **Protocol D**: Add webhook support for real-time calendar updates
3. **Protocol E**: Add WebSocket endpoint for live sensor dashboard
4. **Security**: Implement full JWT authentication across all endpoints
5. **Protocol A**: Add redundancy with multiple sensors per type

---

## References

- I2C Specification: https://www.nxp.com/docs/en/user-guide/UM10204.pdf
- MQTT v5.0: https://mqtt.org/mqtt-specification/
- Google Calendar API: https://developers.google.com/calendar/api/v3/reference
- RESTful API Design: https://restfulapi.net/
- EN 16798-1:2019 - Energy performance of buildings
