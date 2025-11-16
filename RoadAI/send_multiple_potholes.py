import requests
import cv2
import numpy as np
import time

locations = [
    (40.7128, -74.0060, 'High'),    # Center
    (40.7138, -74.0070, 'Medium'),  # North-West
    (40.7118, -74.0050, 'Low'),     # South-East
    (40.7148, -74.0040, 'High'),    # North-East
    (40.7108, -74.0080, 'Medium'),  # South-West
]

for i, (lat, lon, severity) in enumerate(locations):
    # Create a test image
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    color = (0, 0, 255) if severity == 'High' else (0, 165, 255) if severity == 'Medium' else (255, 0, 0)
    cv2.circle(img, (100, 100), 50, color, -1)
    cv2.putText(img, f'Pothole {i+1}', (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(img, severity, (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Encode image
    _, img_encoded = cv2.imencode('.jpg', img)
    
    # Send to API
    files = {'image': ('pothole.jpg', img_encoded.tobytes(), 'image/jpeg')}
    data = {
        'latitude': lat,
        'longitude': lon,
        'severity': severity
    }
    
    response = requests.post('http://localhost:8000/pothole', files=files, data=data)
    print(f"✅ Pothole {i+1} sent: {severity} at ({lat}, {lon})")
    time.sleep(0.5)

print(f"\n🎉 Sent {len(locations)} potholes!")
print("📍 Check dashboard at http://localhost:3000")
print("🗺️  You should see markers spread around the map")
