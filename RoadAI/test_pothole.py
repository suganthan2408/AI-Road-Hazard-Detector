import requests
import cv2
import numpy as np

# Create a test image
img = np.zeros((200, 200, 3), dtype=np.uint8)
cv2.putText(img, 'TEST POTHOLE', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
cv2.circle(img, (100, 100), 50, (0, 0, 255), -1)

# Encode image
_, img_encoded = cv2.imencode('.jpg', img)

# Send to API
files = {'image': ('pothole.jpg', img_encoded.tobytes(), 'image/jpeg')}
data = {
    'latitude': 40.7128,
    'longitude': -74.0060,
    'severity': 'High'
}

response = requests.post('http://localhost:8000/pothole', files=files, data=data)
print(f"Response: {response.status_code}")
print(f"Data: {response.json()}")
print("\n✅ Test pothole sent! Check dashboard at http://localhost:3000")
