from flask import Flask, request, jsonify, send_file, url_for
from ultralytics import YOLO
import os
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Load YOLO model
model = YOLO("models/yolo11n.pt")  # Ensure the model exists in the 'models' folder

# Folders for file uploads and results
UPLOAD_FOLDER = "uploads/"
RESULT_FOLDER = "static/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def calculate_dimensions(image_path, conversion_ratio):
    """
    Calculates the dimensions of the detected object in real-world units
    based on the bounding box output of the YOLO model.
    """
    # Run YOLO model inference
    results = model(image_path)

    # Check if results exist and are valid
    if not results or len(results) == 0:
        return None, None, None  # No results

    # Access the first result (assuming single image processing)
    predictions = results[0]

    # Ensure boxes are available
    if not hasattr(predictions, 'boxes') or predictions.boxes is None:
        return None, None, None  # No detections

    # Access the bounding boxes
    boxes = predictions.boxes
    if len(boxes) == 0:
        return None, None, None  # No detected objects

    # Extract the first bounding box
    xyxy_box = boxes.xyxy.cpu().numpy()[0]  # Convert tensor to NumPy
    x_min, y_min, x_max, y_max = map(float, xyxy_box[:4])  # Convert coordinates to float

    # Calculate pixel dimensions
    width_pixels = x_max - x_min
    height_pixels = y_max - y_min

    # Convert pixel dimensions to real-world dimensions
    length = width_pixels * conversion_ratio  # Real-world length (e.g., cm)
    width = height_pixels * conversion_ratio  # Real-world width (e.g., cm)

    # Ensure all returns are serializable
    return image_path, length, width


@app.route('/predict', methods=['POST'])
def predict():
    """
    Perform object detection on two images and calculate real-world dimensions.
    """
    if "length_width_image" not in request.files or "height_image" not in request.files:
        return jsonify({"error": "Both images are required"}), 400

    # Save the uploaded images
    lw_image = request.files["length_width_image"]
    h_image = request.files["height_image"]

    lw_path = os.path.join(UPLOAD_FOLDER, lw_image.filename)
    h_path = os.path.join(UPLOAD_FOLDER, h_image.filename)
    lw_image.save(lw_path)
    h_image.save(h_path)

    # Assume conversion ratio from prior calibration for real-world scaling
    conversion_ratio = 0.01279  # Example: 1 pixel = 0.05 cm

    # Calculate dimensions for both images
    lw_result, length, width = calculate_dimensions(lw_path, conversion_ratio)
    h_result, _, height = calculate_dimensions(h_path, conversion_ratio)

    # Check if dimensions were successfully calculated
    if lw_result is None or h_result is None:
        return jsonify({"error": "Object not detected in one or both images."}), 400

    # Ensure all response data is converted to JSON-serializable types
    return jsonify({
        "length_cm": round(float(length), 2),   # Convert numpy/float32 to native float
        "width_cm": round(float(width), 2),    # Ensure float conversion
        "height_cm": round(float(height), 2),  # Ensure float conversion
        "length_width_result": os.path.relpath(lw_path).replace("\\", "/"),
        "height_result": os.path.relpath(h_path).replace("\\", "/")
    })

if __name__ == "__main__":
    app.run(debug=True)