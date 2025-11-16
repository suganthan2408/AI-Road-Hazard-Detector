# 🚗 AI-Based Pothole Detection System

Complete real-time pothole detection system with AI, cloud API, and dashboard visualization.

## 📁 Project Structure

```
pothole-detection-system/
├── backend/          # FastAPI server
├── camera/           # AI detection system
├── dashboard/        # Web dashboard
└── README.md         # This file
```

## 🚀 Quick Start Guide

### Step 1: Install Python Dependencies

Open 3 separate terminals and run:

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Terminal 2 - Camera:**
```bash
cd camera
pip install -r requirements.txt
```

### Step 2: Start Backend API

In Terminal 1:
```bash
cd backend
python main.py
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

Test it: Open browser → `http://localhost:8000` → Should show API status

### Step 3: Open Dashboard

Simply open `dashboard/index.html` in your web browser (Chrome/Firefox recommended)

Or use a simple HTTP server:
```bash
cd dashboard
python -m http.server 3000
```
Then open: `http://localhost:3000`

### Step 4: Start Camera Detection

In Terminal 2:
```bash
cd camera
python detector.py
```

The webcam window will open and start detecting!

## 🎯 How It Works

1. **Camera** captures video and detects potholes using AI
2. **Detection** marks potholes with bounding boxes
3. **API** receives pothole data (image, location, severity)
4. **Dashboard** displays all potholes on map in real-time

## 🎮 Controls

**Camera Window:**
- Press `q` to quit
- Press `s` to manually capture a pothole

**Dashboard:**
- Auto-refreshes every 5 seconds
- Click markers on map to see details
- Use "Clear All" to reset database

## 📊 Features

✅ Real-time webcam detection
✅ YOLOv8 AI model (with OpenCV fallback)
✅ RESTful API with FastAPI
✅ Interactive map with Leaflet
✅ Severity classification (High/Medium/Low)
✅ Image storage and retrieval
✅ JSON database
✅ Responsive dashboard

## 🔧 Troubleshooting

**Webcam not working?**
- Check if another app is using the camera
- Try changing camera index in detector.py (line 95): `cv2.VideoCapture(1)`

**API connection failed?**
- Make sure backend is running on port 8000
- Check firewall settings

**YOLOv8 not loading?**
- System will automatically use OpenCV detection
- First run downloads YOLOv8 model (~6MB)

## 📝 API Endpoints

- `GET /` - API status
- `POST /pothole` - Submit pothole data
- `GET /potholes` - Get all potholes
- `DELETE /potholes` - Clear all data

## 🎨 Customization

**Change GPS location:**
Edit `camera/detector.py` lines 23-24

**Adjust detection sensitivity:**
Edit `camera/detector.py` line 11 (CONFIDENCE_THRESHOLD)

**Change API port:**
Edit `backend/main.py` line 95

## 💡 Tips

- Move objects in front of camera to trigger detection
- System has 5-second cooldown between detections
- Dashboard updates automatically every 5 seconds
- All data stored in `backend/data/`

## 🌟 Demo Ready!

This system is production-ready for demos and presentations. All components work together seamlessly!
