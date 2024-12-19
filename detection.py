import cv2
import numpy as np
from ultralytics import YOLO

def detect_objects(image_bytes):
    # Convert bytes to numpy array
    np_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Load YOLO model
    model = YOLO("best.pt")  # Replace with your YOLOv8 model

    # Perform inference
    results = model(image)

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
