import cv2
from flask import Flask, request, jsonify, send_file, url_for
from ultralytics import YOLO
import os
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Load YOLO model
model = YOLO("models/yolo11n.pt")  # Ensure the model exists in the 'models' folder

# Directory configurations
UPLOAD_FOLDER = Path("uploads")
RESULT_FOLDER = Path("static/results")
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULT_FOLDER.mkdir(exist_ok=True)

def calculate_dimensions(image_path, conversion_ratio):
    results = model(image_path)
    predictions = results[0]

    if not hasattr(predictions, 'boxes') or predictions.boxes is None or len(predictions.boxes) == 0:
        return None, None, None, None

    boxes = predictions.boxes
    xyxy_box = boxes.xyxy.cpu().numpy()[0]  # Get the first bounding box
    x_min, y_min, x_max, y_max = map(float, xyxy_box[:4])

    # Load the image with OpenCV
    img = cv2.imread(str(image_path))
    
    # Draw the bounding box
    cv2.rectangle(img, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

    # Save the processed image with bounding box
    output_image_path = RESULT_FOLDER / (image_path.stem + '_with_bbox.jpg')
    cv2.imwrite(str(output_image_path), img)

    # Convert pixel dimensions to real-world dimensions
    length = (x_max - x_min) * conversion_ratio
    width = (y_max - y_min) * conversion_ratio

    return image_path, length, width, output_image_path

def classify_package_dimensions(length_cm, width_cm, height_cm):
    dimensions = sorted([length_cm, width_cm, height_cm], reverse=True) 
    length, width, height = dimensions  

    if length <= 330 and width <= 230 and height <= 370:
        return "MODEL BOX 1"
    elif length <= 330 and width <= 230 and height <= 300:
        return "MODEL BOX 2"
    elif length <= 430 and width <= 210 and height <= 270:
        return "MODEL BOX 3"
    elif length <= 350 and width <= 190 and height <= 230:
        return "MODEL BOX 4"
    elif length <= 290 and width <= 170 and height <= 190:
        return "MODEL BOX 5"
    elif length <= 260 and width <= 130 and height <= 160:
        return "MODEL BOX 6"
    elif length <= 230 and width <= 130 and height <= 160:
        return "MODEL BOX 7"
    elif length <= 219 and width <= 110 and height <= 140:
        return "MODEL BOX 8"
    elif length <= 195 and width <= 105 and height <= 135:
        return "MODEL BOX 9"
    elif length <= 175 and width <= 95 and height <= 115:
        return "MODEL BOX 10"
    elif length <= 145 and width <= 85 and height <= 105:
        return "MODEL BOX 11"
    elif length <= 130 and width <= 90 and height <= 90:
        return "MODEL BOX 12"
    else:
        return "Unknown"

@app.route('/predict', methods=['POST'])
def predict():
    if 'length_width_image' not in request.files or 'height_image' not in request.files:
        return jsonify({"error": "Both images are required."}), 400

    lw_image = request.files['length_width_image']
    h_image = request.files['height_image']

    lw_path = UPLOAD_FOLDER / lw_image.filename
    h_path = UPLOAD_FOLDER / h_image.filename
    lw_image.save(lw_path)
    h_image.save(h_path)

    conversion_ratio = 0.0127  # Example: 1 pixel = 0.0127 cm

    # Calculate dimensions and draw bounding boxes
    lw_result, length, width, lw_output_image_path = calculate_dimensions(lw_path, conversion_ratio)
    h_result, _, height, h_output_image_path = calculate_dimensions(h_path, conversion_ratio)

    if lw_result is None or h_result is None:
        return jsonify({"error": "Object not detected in one or both images."}), 400

    # Classify the package dimensions
    category = classify_package_dimensions(length, width, height)

    return jsonify({
        "length_cm": round(float(length), 2),
        "width_cm": round(float(width), 2),
        "height_cm": round(float(height), 2),
        "length_width_result": f"uploads/{lw_image.filename}",
        "height_result": f"uploads/{h_image.filename}",
        "bounding_box_image": f"{lw_output_image_path.name}",  # Return filename only
        "package_category": category  # Include the package category
    })

if __name__ == "__main__":
    app.run(debug=True)