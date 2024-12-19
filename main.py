from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mailing import send_email
from detection import detect_objects
from pydantic import BaseModel
from dotenv import load_dotenv
import cloudinary.uploader
import os
from uuid import uuid4

load_dotenv()

# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DetectionResponse(BaseModel):
    detectionStatus: str
    emailStatus: dict
    imageUrl: str

@app.post("/process_detection", response_model=DetectionResponse)
async def process_detection(
    province: str = Form(...),
    city: str = Form(...),
    district: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    userId: str = Form(...),
):
    try:
        # Log the start of the process
        print(f"Processing detection for userId: {userId}")

        # Upload image to Cloudinary
        print("Uploading image to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            file=image.file,
            folder="accivision/uploads",
            public_id=f"{userId}_{uuid4()}",
            resource_type="image",
        )
        image_url = upload_result["secure_url"]
        print(f"Image uploaded successfully: {image_url}")

        # Read the file as bytes for YOLO detection
        print("Reading image file for detection...")
        image.file.seek(0)  # Reset file pointer
        image_bytes = await image.read()

        # Perform detection
        print("Performing object detection...")
        detections = detect_objects(image_bytes)  # Pass bytes to detection logic
        print(f"Detections: {detections}")

        detection_status = "detected" if detections and detections[0]["class"] == "car-crash" else "not_detected"
        print(f"Detection status: {detection_status}")

        # Send email
        if detection_status == "detected":
            print("Sending email notification...")
            email_status = send_email({
                "recipient_email": os.getenv("EMAIL_RECEIVER"),
                "province": province,
                "city": city,
                "district": district,
                "description": description,
                "image_url": image_url,
            })
            print(f"Email sent successfully: {email_status}")
        else:
            email_status = {"success": False, "message": "No email sent because no car crash detected."}
            print("No car crash detected; skipping email.")

        return DetectionResponse(
            detectionStatus=detection_status,
            emailStatus=email_status,
            imageUrl=image_url,
        )
    except Exception as e:
        # Log the exception details
        print(f"Error during process_detection: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='localhost', port=8000, reload=True)
