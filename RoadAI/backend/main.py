from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import json
import os
from datetime import datetime
import uuid
import shutil

app = FastAPI()

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("data/images", exist_ok=True)

# Initialize database file
DB_FILE = "data/potholes.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

# Serve static images
app.mount("/images", StaticFiles(directory="data/images"), name="images")

@app.get("/")
def read_root():
    return {"message": "Pothole Detection API is running", "status": "active"}

@app.post("/pothole")
async def receive_pothole(
    latitude: float = Form(...),
    longitude: float = Form(...),
    severity: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        # Generate unique ID
        pothole_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Save image
        image_filename = f"{pothole_id}.jpg"
        image_path = f"data/images/{image_filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Create pothole record
        pothole_data = {
            "id": pothole_id,
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "severity": severity,
            "image_url": f"/images/{image_filename}"
        }
        
        # Load existing data
        with open(DB_FILE, "r") as f:
            potholes = json.load(f)
        
        # Add new pothole
        potholes.append(pothole_data)
        
        # Save to database
        with open(DB_FILE, "w") as f:
            json.dump(potholes, f, indent=2)
        
        print(f"✅ Pothole received: {pothole_id} at ({latitude}, {longitude}) - Severity: {severity}")
        
        return JSONResponse(content={
            "status": "success",
            "message": "Pothole data saved successfully",
            "data": pothole_data
        })
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/potholes")
def get_all_potholes():
    try:
        with open(DB_FILE, "r") as f:
            potholes = json.load(f)
        return {"status": "success", "data": potholes, "count": len(potholes)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/potholes")
def clear_potholes():
    try:
        with open(DB_FILE, "w") as f:
            json.dump([], f)
        # Clear images
        for file in os.listdir("data/images"):
            os.remove(f"data/images/{file}")
        return {"status": "success", "message": "All potholes cleared"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
