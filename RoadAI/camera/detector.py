import cv2
import numpy as np
import requests
import time
from datetime import datetime
import random

# Configuration
API_URL = "http://localhost:8000/pothole"
CONFIDENCE_THRESHOLD = 0.5
USE_YOLO = True  # Set to False to use simple motion detection

# Try to load YOLOv8
try:
    from ultralytics import YOLO
    model = YOLO('yolov8n.pt')  # Nano model for speed
    print("✅ YOLOv8 loaded successfully")
except Exception as e:
    print(f"⚠️ YOLOv8 not available: {e}")
    print("📌 Using OpenCV-based detection instead")
    USE_YOLO = False

# Simulated GPS coordinates (you can integrate real GPS if available)
BASE_LAT = 40.7128
BASE_LON = -74.0060

def get_gps_coordinates():
    """Simulate GPS coordinates (replace with real GPS module if available)"""
    lat = BASE_LAT + random.uniform(-0.01, 0.01)
    lon = BASE_LON + random.uniform(-0.01, 0.01)
    return lat, lon

def detect_pothole_opencv(frame, prev_frame):
    """Simple pothole detection using OpenCV (fallback method)"""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    if prev_frame is None:
        return None, gray
    
    # Compute difference
    frame_delta = cv2.absdiff(prev_frame, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detections = []
    for contour in contours:
        if cv2.contourArea(contour) > 1000:  # Minimum area
            (x, y, w, h) = cv2.boundingRect(contour)
            detections.append((x, y, w, h, 0.7))  # x, y, w, h, confidence
    
    return detections, gray

def detect_pothole_yolo(frame):
    """Detect potholes using YOLOv8"""
    results = model(frame, conf=CONFIDENCE_THRESHOLD)
    detections = []
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = box.conf[0].cpu().numpy()
            cls = int(box.cls[0].cpu().numpy())
            
            # Consider certain classes as potholes (adjust as needed)
            # For demo, we'll detect any object as potential pothole
            w = int(x2 - x1)
            h = int(y2 - y1)
            detections.append((int(x1), int(y1), w, h, float(conf)))
    
    return detections

def calculate_severity(width, height, confidence):
    """Calculate pothole severity based on size and confidence"""
    area = width * height
    if area > 15000 or confidence > 0.8:
        return "High"
    elif area > 8000 or confidence > 0.6:
        return "Medium"
    else:
        return "Low"

def send_to_api(frame, latitude, longitude, severity):
    """Send pothole data to backend API"""
    try:
        # Encode image
        _, img_encoded = cv2.imencode('.jpg', frame)
        
        # Prepare data
        files = {'image': ('pothole.jpg', img_encoded.tobytes(), 'image/jpeg')}
        data = {
            'latitude': latitude,
            'longitude': longitude,
            'severity': severity
        }
        
        # Send POST request
        response = requests.post(API_URL, files=files, data=data, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Pothole sent to API - Severity: {severity}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to send to API: {e}")
        return False

def main():
    print("🚀 Starting Pothole Detection System...")
    print(f"📡 API Endpoint: {API_URL}")
    print(f"🤖 Detection Mode: {'YOLOv8' if USE_YOLO else 'OpenCV'}")
    print("Press 'q' to quit, 's' to manually capture pothole")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open webcam")
        return
    
    prev_frame = None
    last_detection_time = 0
    detection_cooldown = 5  # seconds between detections
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break
        
        display_frame = frame.copy()
        current_time = time.time()
        
        # Detect potholes
        if USE_YOLO:
            detections = detect_pothole_yolo(frame)
        else:
            detections, prev_frame = detect_pothole_opencv(frame, prev_frame)
            if detections is None:
                detections = []
        
        # Process detections
        for (x, y, w, h, conf) in detections:
            # Draw bounding box
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # Calculate severity
            severity = calculate_severity(w, h, conf)
            
            # Display info
            label = f"Pothole: {severity} ({conf:.2f})"
            cv2.putText(display_frame, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Send to API (with cooldown)
            if current_time - last_detection_time > detection_cooldown:
                lat, lon = get_gps_coordinates()
                
                # Crop pothole region
                pothole_crop = frame[y:y+h, x:x+w]
                
                if send_to_api(pothole_crop, lat, lon, severity):
                    last_detection_time = current_time
                    cv2.putText(display_frame, "SENT TO API!", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display info
        cv2.putText(display_frame, f"Detections: {len(detections)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show frame
        cv2.imshow('Pothole Detection System', display_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Manual capture
            lat, lon = get_gps_coordinates()
            send_to_api(frame, lat, lon, "Manual")
            print("📸 Manual capture sent!")
    
    cap.release()
    cv2.destroyAllWindows()
    print("👋 Pothole detection stopped")

if __name__ == "__main__":
    main()
