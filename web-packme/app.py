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
    # Convert dimensions from cm to mm
    length_mm = length_cm * 10
    width_mm = width_cm * 10
    height_mm = height_cm * 10
    
    dimensions = [length_mm, width_mm, height_mm]
    
    # Sort dimensions in ascending order for comparison
    dimensions.sort()
    
    # Map box dimensions (length, width, height)
    boxes = {
        "Model Box 12": (130, 80, 90),
        "Model Box 11": (145, 85, 105),
        "Model Box 10": (175, 95, 115),
        "Model Box 9": (195, 105, 135),
        "Model Box 8": (210, 110, 140),
        "Model Box 7": (230, 130, 160),
        "Model Box 6": (260, 150, 180),
        "Model Box 5": (290, 170, 190),
        "Model Box 4": (350, 190, 230),
        "Model Box 3": (430, 210, 270),
        "Model Box 2": (530, 230, 290),
        "Model Box 1": (530, 290, 370),
    }
    
    # Check from the smallest box to largest
    for model, (l, w, h) in boxes.items():
        if (dimensions[0] <= l * 10) and (dimensions[1] <= w * 10) and (dimensions[2] <= h * 10):
            return model
            
    return "Unknown"

@app.route('/predict', methods=['POST'])
def predict():
    if 'length_width_image' not in request.files or 'height_image' not in request.files:
        return jsonify({"error": "Both images are required."}), 400

    if 'unit' not in request.form:
        return jsonify({"error": "Unit is required."}), 400

    lw_image = request.files['length_width_image']
    h_image = request.files['height_image']
    unit = request.form['unit']

    lw_path = UPLOAD_FOLDER / lw_image.filename
    h_path = UPLOAD_FOLDER / h_image.filename
    lw_image.save(lw_path)
    h_image.save(h_path)

    conversion_ratio = 0.0127  # Contoh: 1 piksel = 0.0127 cm

    # Hitung dimensi dan gambar kotak pembatas
    lw_result, length_cm, width_cm, lw_output_image_path = calculate_dimensions(lw_path, conversion_ratio)
    h_result, _, height_cm, h_output_image_path = calculate_dimensions(h_path, conversion_ratio)

    if lw_result is None or h_result is None:
        return jsonify({"error": "Object not detected in one or both images."}), 400

    # Konversi satuan dimensi
    if unit == 'mm':
        length = length_cm * 10      # cm to mm
        width = width_cm * 10        # cm to mm
        height = height_cm * 10      # cm to mm
    elif unit == 'm':
        length = length_cm / 100     # cm to m
        width = width_cm / 100       # cm to m
        height = height_cm / 100     # cm to m
    elif unit == 'inches':
        length = length_cm / 2.54    # cm to inches
        width = width_cm / 2.54      # cm to inches
        height = height_cm / 2.54    # cm to inches
    else:  # default to 'cm'
        length = length_cm
        width = width_cm
        height = height_cm

    # Klasifikasikan dimensi paket
    category = classify_package_dimensions(length, width, height)

    return jsonify({
        "length": round(float(length), 2),
        "width": round(float(width), 2),
        "height": round(float(height), 2),
        "length_width_result": f"uploads/{lw_image.filename}",
        "height_result": f"uploads/{h_image.filename}",
        "bounding_box_image": str(lw_output_image_path.name),  # Kembalikan nama file
        "package_category": category  # Sertakan kategori paket
    })

if __name__ == "__main__":
    app.run(debug=True)