# IoT Room Selection Decision Support System

> 🏢 A smart room recommendation system using AHP algorithm, FastAPI, React, and MongoDB.

## 🚀 Quick Links

- **[📊 Project Tracker (Gantt Chart)](https://7o2y.github.io/iot-room-selection/)**
- [API Documentation (Swagger)](#) — *coming soon*
- [Grafana Dashboard](#) — *coming soon*

## 👥 Team

| Role | Member | Responsibilities |
|------|--------|------------------|
| Backend/Database | Person A | FastAPI, MongoDB, REST APIs, Swagger |
| Algorithm/Data | Person B | AHP implementation, EU standards research |
| Frontend/UI | Person C | React UI, Grafana dashboard |

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Protocols | I2C/Analog + MQTT + HTTP REST |
| Database | MongoDB |
| Backend | Python + FastAPI |
| Frontend | React |
| Monitoring | Grafana |
| Auth | JWT *(bonus)* |

## 📁 Project Structure

```
iot-room-selection/
├── docs/                    # Project tracker & documentation
│   ├── index.html          # Gantt chart (GitHub Pages)
│   ├── tasks.json          # Task data
│   ├── assets/             # Images, diagrams
│   └── research/           # Research documents (EU standards, etc.)
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/        # API Endpoints
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── ahp/            # AHP algorithm
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React application
│   ├── src/
│   ├── public/
│   └── package.json
├── database/                # MongoDB setup
│   ├── init/
│   └── mock-data/          # JSON sensor data
├── tests/                   # Unit & Integration tests
│   └── unit/
├── docker-compose.yml
└── README.md
```

## 🏃 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (or Docker)
- Git

### Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/iot-room-selection.git
cd iot-room-selection

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Run Development
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

## 📋 Project Requirements

Based on course BPINFOR-124 (Introduction to IoT):

1. ✅ Communication protocols specification (Comm A, B, C, D)
2. ✅ Database design for sensor + facilities data
3. ✅ Decision criteria based on EU standards (EN 16798-1)
4. ✅ AHP algorithm for room ranking
5. ✅ REST APIs with Swagger documentation
6. ✅ UI1: End-user room selection interface
7. ✅ UI2: Admin monitoring dashboard
8. 🎁 JWT authentication *(bonus)*

## 📊 Updating the Project Tracker

The Gantt chart loads tasks from `docs/tasks.json`. To update:

1. Edit `docs/tasks.json`
2. Commit and push
3. Changes appear on GitHub Pages automatically

```bash
git add docs/tasks.json
git commit -m "Update task status: [task name] done"
git push
```

## 📄 License

MIT License - University of Luxembourg, 2024-2025
