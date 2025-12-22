# MongoDB Schema Design

## Design Philosophy

This schema is optimized for:
1. **Time-series queries** - Efficient filtering by timestamp ranges for sensor data
2. **Aggregation** - Easy to compute averages, min/max for decision-making
3. **Scalability** - Individual sensor reading documents for better indexing
4. **Flexibility** - Room facilities can vary without strict schema constraints

---

## Database: `iot_room_selection`

### Collection 1: `sensor_readings`

**Purpose:** Store all sensor measurements across all rooms as time-series data

**Why this design:**
- Individual documents allow efficient time-range queries with indexes
- Single collection for all sensor types simplifies queries and reduces joins
- Supports MongoDB time-series collections (optional optimization)

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "room_name": "Room_1",
  "sensor_type": "temperature",  // "temperature", "co2", "humidity", "sound", "voc", "light_intensity"
  "value": 23.45,
  "unit": "°C",  // "°C", "ppm", "%", "dB", "ppb", "lux"
  "timestamp": ISODate("2024-10-29T06:48:42.987Z"),
  "created_at": ISODate("2024-12-22T10:00:00.000Z")  // When record was inserted
}
```

**Indexes:**
```javascript
// Compound index for efficient queries by room and time range
db.sensor_readings.createIndex({ "room_name": 1, "sensor_type": 1, "timestamp": -1 })

// Index for time-range queries across all rooms
db.sensor_readings.createIndex({ "sensor_type": 1, "timestamp": -1 })
```

**Rationale:**
- `room_name + sensor_type + timestamp` index supports queries like:
  - "Get all temperature readings for Room_1 between 8am-5pm"
  - "Get latest CO2 reading for Room_2"
- Descending timestamp (-1) optimizes recent data queries

---

### Collection 2: `rooms`

**Purpose:** Store room metadata and facilities (semi-static data)

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "name": "Room_1",  // Primary identifier
  "facilities": {
    "videoprojector": true,
    "seating_capacity": 62,
    "computers": 20,  // Optional field
    "robots_for_training": 10,  // Optional field
    "whiteboard": true,  // Optional field
    "audio_system": false  // Optional field
  },
  "building": "Building A",  // Optional metadata
  "floor": 2,
  "updated_at": ISODate("2024-12-22T10:00:00.000Z")
}
```

**Indexes:**
```javascript
// Unique constraint on room name
db.rooms.createIndex({ "name": 1 }, { unique: true })

// Index for facility-based queries (e.g., "find rooms with projectors")
db.rooms.createIndex({ "facilities.videoprojector": 1, "facilities.seating_capacity": 1 })
```

**Rationale:**
- Flexible schema allows different rooms to have different facilities
- Facilities embedded in room document (read-optimized, no joins needed)
- Room name is unique identifier for consistency with sensor data

---

### Collection 3: `calendar_events`

**Purpose:** Store room availability from University calendar (Google Calendar API)

**Document Structure:**
```json
{
  "_id": ObjectId("..."),
  "room_name": "Room_1",
  "event_id": "google_calendar_event_id_123",  // External ID from calendar API
  "title": "CS101 Lecture",
  "start_time": ISODate("2024-12-22T14:00:00.000Z"),
  "end_time": ISODate("2024-12-22T16:00:00.000Z"),
  "status": "confirmed",  // "confirmed", "tentative", "cancelled"
  "organizer": "prof.smith@uni.lu",
  "created_at": ISODate("2024-12-22T10:00:00.000Z"),
  "synced_at": ISODate("2024-12-22T10:00:00.000Z")  // Last sync from calendar API
}
```

**Indexes:**
```javascript
// Query events by room and time range
db.calendar_events.createIndex({ "room_name": 1, "start_time": 1, "end_time": 1 })

// Check room availability at specific time
db.calendar_events.createIndex({ "room_name": 1, "status": 1, "start_time": 1 })

// Unique external event ID to prevent duplicates during sync
db.calendar_events.createIndex({ "event_id": 1 }, { unique: true })
```

**Rationale:**
- Time-range indexes support queries like "Is Room_1 available at 2pm?"
- `event_id` prevents duplicate imports during calendar sync
- `status` field allows filtering out cancelled events

---

## Data Migration Strategy

### Step 1: Import Room Facilities
```javascript
// Transform from JSON structure to MongoDB documents
{
  "rooms": [{ "name": "Room_1", "facilities": {...} }]
}
// Becomes individual documents in `rooms` collection
```

### Step 2: Import Sensor Readings
```javascript
// Transform from nested arrays to flat documents
{
  "rooms": [{
    "name": "Room_1",
    "temperature_values": [{ "timestamp": "...", "temperature": 23.4 }]
  }]
}
// Becomes:
{
  "room_name": "Room_1",
  "sensor_type": "temperature",
  "value": 23.4,
  "unit": "°C",
  "timestamp": ISODate("...")
}
```

---

## Query Examples

### Get average temperature for Room_1 today
```javascript
db.sensor_readings.aggregate([
  {
    $match: {
      room_name: "Room_1",
      sensor_type: "temperature",
      timestamp: {
        $gte: ISODate("2024-12-22T00:00:00Z"),
        $lt: ISODate("2024-12-23T00:00:00Z")
      }
    }
  },
  {
    $group: {
      _id: null,
      avg_temp: { $avg: "$value" },
      min_temp: { $min: "$value" },
      max_temp: { $max: "$value" }
    }
  }
])
```

### Find rooms with projector and >30 seats available at 2pm
```javascript
// Step 1: Find available rooms (no events at 2pm)
const busyRooms = db.calendar_events.distinct("room_name", {
  status: "confirmed",
  start_time: { $lte: ISODate("2024-12-22T14:00:00Z") },
  end_time: { $gte: ISODate("2024-12-22T14:00:00Z") }
})

// Step 2: Query rooms with facilities, excluding busy ones
db.rooms.find({
  "name": { $nin: busyRooms },
  "facilities.videoprojector": true,
  "facilities.seating_capacity": { $gte: 30 }
})
```

---

## Future Optimizations

1. **MongoDB Time-Series Collections** (MongoDB 5.0+)
   - Convert `sensor_readings` to time-series collection for better compression
   - Automatic data expiration policies (e.g., keep only last 6 months)

2. **Caching Layer**
   - Cache frequently accessed aggregations (e.g., average daily temperature per room)
   - Redis for real-time "current" sensor values

3. **Data Retention Policy**
   - Archive old sensor readings (>1 year) to separate collection
   - Keep calendar events only for future + recent past

---

## Validation Rules (Optional)

MongoDB schema validation for data integrity:

```javascript
db.createCollection("sensor_readings", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["room_name", "sensor_type", "value", "timestamp"],
      properties: {
        room_name: { bsonType: "string" },
        sensor_type: { enum: ["temperature", "co2", "humidity", "sound", "voc", "light_intensity"] },
        value: { bsonType: "double" },
        unit: { bsonType: "string" },
        timestamp: { bsonType: "date" }
      }
    }
  }
})
```

This ensures only valid data can be inserted into the database.
