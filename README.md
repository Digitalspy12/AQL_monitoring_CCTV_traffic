# 🏙️ AI-Powered Digital Twin for Smart Cities

A real-time **Digital Twin** system that uses computer vision (YOLOv8 Nano) to monitor traffic, estimate pollution, and visualize city patterns on an interactive web dashboard — all running on a standard CPU.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Nano-FF6F00?logo=ultralytics&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Features

| Module | Description |
|---|---|
| **Traffic Flow Simulator** | Detects, classifies (cars, bikes, buses, trucks), and counts vehicles in real-time using YOLOv8 Nano + OpenCV |
| **Pollution Heatmap** | Estimates Air Quality Index (AQI) and noise levels from traffic volume, rendered as a dynamic Leaflet heatmap |
| **Live Video Feed** | Annotated video stream with bounding boxes and classification labels |
| **Historical Analytics** | Time-series charts tracking traffic trends over time |
| **WebSocket Streaming** | Sub-second real-time updates from backend to dashboard |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI / CV | YOLOv8 Nano, OpenCV |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite (via aiosqlite) |
| Frontend | React 19, Vite, Leaflet.js, Recharts |
| Real-time | WebSocket (native) |

---

## 📂 Project Structure

```
Digitaltwins/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + WebSocket
│   │   ├── config.py            # All settings (video source, model, map center)
│   │   ├── models/schemas.py    # Pydantic data models
│   │   ├── db/
│   │   │   ├── database.py      # SQLite connection + table init
│   │   │   └── crud.py          # Insert/query traffic & pollution data
│   │   ├── ai/
│   │   │   ├── detector.py      # YOLOv8 vehicle detection pipeline
│   │   │   ├── tracker.py       # Centroid tracker (prevents double-counting)
│   │   │   └── pollution.py     # AQI & noise estimation models
│   │   ├── api/
│   │   │   ├── traffic.py       # GET /api/traffic/history
│   │   │   └── pollution.py     # GET /api/pollution/history
│   │   └── ws/
│   │       └── stream.py        # WebSocket broadcast engine
│   ├── tests/                   # pytest test suite
│   ├── sample_videos/           # ⬅️ PUT YOUR CCTV FOOTAGE HERE
│   │   └── traffic_sample.mp4   # Default expected filename
│   ├── data/                    # Auto-created — SQLite DB lives here
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Dashboard, MapView, TrafficPanel, etc.
│   │   ├── hooks/               # useWebSocket.js
│   │   └── utils/               # pollutionCalc.js
│   ├── package.json
│   └── vite.config.js
├── prd.md                       # Product requirements document
└── README.md                    # ← You are here
```

---

## 🎥 Where to Upload CCTV / Video Footage

The system processes video files to detect vehicles. Here's how to provide footage:

### Option 1: Drop a File (Recommended)

Place your video file in the **`backend/sample_videos/`** folder:

```
backend/
└── sample_videos/
    └── traffic_sample.mp4    ← Drop your CCTV file here
```

> **Default filename:** The system expects `traffic_sample.mp4` by default.  
> If your file has a different name, either **rename it** to `traffic_sample.mp4` or set the environment variable (see Option 2).

**Supported formats:** `.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv` — any format supported by OpenCV.

**Best footage tips:**
- Overhead/elevated angle of a road or intersection
- Resolution: 720p or higher recommended
- Frame rate: 15+ FPS
- Clear visibility of vehicles (daytime footage works best)

### Option 2: Custom Video Path via Environment Variable

Point to **any video file** on your system without moving it:

```powershell
# PowerShell
$env:VIDEO_SOURCE = "C:\path\to\your\cctv_footage.mp4"
uvicorn app.main:app --reload --port 8000
```

```bash
# Bash / Linux / Mac
VIDEO_SOURCE="/path/to/your/cctv_footage.mp4" uvicorn app.main:app --reload --port 8000
```

### Option 3: Use a Live Webcam

Connect to a webcam by setting the source to a device index:

```powershell
$env:VIDEO_SOURCE = "0"    # 0 = default webcam, 1 = second camera, etc.
uvicorn app.main:app --reload --port 8000
```

### Option 4: Use an RTSP / IP Camera Stream

If you have a network CCTV camera with an RTSP URL:

```powershell
$env:VIDEO_SOURCE = "rtsp://username:password@192.168.1.100:554/stream1"
uvicorn app.main:app --reload --port 8000
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** 
- **Node.js 18+**

### 1. Clone & Setup Backend

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### 2. Add Your Video

```powershell
# Copy your CCTV footage into the sample_videos folder
copy "C:\path\to\your\traffic_video.mp4" "backend\sample_videos\traffic_sample.mp4"
```

### 3. Start the Backend

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

> On first run, YOLOv8 Nano weights (~6 MB) will be **auto-downloaded**.

### 4. Start the Frontend

```powershell
# In a new terminal
cd frontend
npm install
npm run dev
```

### 5. Open Dashboard

Navigate to **http://localhost:5173** in your browser.

---

## ⚙️ Configuration

All settings are controlled via **environment variables** or by editing `backend/app/config.py`:

| Variable | Default | Description |
|---|---|---|
| `VIDEO_SOURCE` | `sample_videos/traffic_sample.mp4` | Path to video file, webcam index, or RTSP URL |
| `YOLO_MODEL` | `yolov8n.pt` | YOLO model name (auto-downloads) |
| `CONFIDENCE_THRESHOLD` | `0.35` | Minimum detection confidence (0–1) |
| `FRAME_SKIP` | `2` | Process every Nth frame (higher = faster, less detail) |
| `TARGET_FPS` | `15` | Processing target FPS |
| `DEFAULT_LAT` | `28.6139` | Map center latitude (New Delhi) |
| `DEFAULT_LNG` | `77.2090` | Map center longitude |
| `MAP_ZOOM` | `13` | Default map zoom level |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |
| `WS_PUSH_INTERVAL` | `1.0` | Seconds between WebSocket pushes |

**Example — change map center to Mumbai:**

```powershell
$env:DEFAULT_LAT = "19.0760"
$env:DEFAULT_LNG = "72.8777"
uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Running Tests

```powershell
cd backend
pip install pytest httpx anyio
pytest tests/ -v
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/api/snapshot` | Latest detection + pollution snapshot |
| `GET` | `/api/traffic/history?limit=100` | Historical traffic data |
| `GET` | `/api/pollution/history?limit=100` | Historical pollution data |
| `WS` | `/ws` | Real-time WebSocket stream |

---

## 🧠 How It Works

```
Video Source → OpenCV Capture → YOLOv8 Nano Detection → Centroid Tracker
                                        │
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                  Vehicle Counts    Annotated Frame   Object IDs
                        │               │
                ┌───────┴───────┐       │
                ▼               ▼       ▼
          AQI Estimator   Noise Model   Base64 JPEG
                │               │       │
                └───────┬───────┘       │
                        ▼               ▼
                  Heatmap Points    WebSocket Push ──→ React Dashboard
                        │
                        ▼
                  SQLite (history)
```

---

## 📜 License

This project is for educational and demonstration purposes.  
All open-source dependencies retain their respective licenses.
