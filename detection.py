from PIL import Image
from io import BytesIO
import numpy as np
from ultralytics import YOLO

def detect_objects(image_bytes):
    # Convert bytes to a Pillow image
    image = Image.open(BytesIO(image_bytes))
    image_np = np.array(image)

    # Load YOLO model
    model = YOLO("best.pt")  # Replace with your YOLOv8 model

    # Perform inference
    results = model(image_np)

    # Parse results
    detections = []
    for result in results:
        for box in result.boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy.tolist(),
            })

    return detections
