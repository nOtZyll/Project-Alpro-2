from flask import Flask, request, render_template, jsonify
from yolov5 import detect
import cv2
import os
import torch
import numpy as np
import pathlib  # Import the pathlib module
import sys
# Add the yolov5 directory to the Python path
sys.path.append(str(pathlib.Path(__file__).resolve().parent / 'yolov5'))

# Now you can import detect from the YOLOv5 application
from detect import run  # Adjust if you need to import a specific function

# Backup the original PosixPath
posix_backup = pathlib.PosixPath
try:
    # Override PosixPath with WindowsPath
    pathlib.PosixPath = pathlib.WindowsPath

    # Inisialisasi Flask
    app = Flask(__name__)
    UPLOAD_FOLDER = "uploads"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Pastikan folder upload ada
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Path ke model YOLO yang sudah Anda latih
    MODEL_PATH = "D:/alpro-finals-web/yolov5/weigths/best.pt" # Update ke path model Anda
    model = torch.hub.load("ultralytics/yolov5", "custom", path=MODEL_PATH, force_reload=True)

    # Path ke template referensi
    REFERENCE_TEMPLATE_PATH = "D:/alpro-finals-web/reference_templates/reference.jpg"

        # Fungsi menghitung dimensi benda
    def calculate_dimensions(img_size, item_bbox, ref_bbox, ref_real_cm):
        """
        Menghitung dimensi benda berdasarkan bounding box dan rasio referensi skala.
        """
        # Ukuran bounding box (dalam piksel)
        # Assume these values are either tensors or numbers (floats/ints).
        item_width_px = item_bbox[2] * img_size
        item_height_px = item_bbox[3] * img_size
        ref_width_px = ref_bbox[2] * img_size

        # Rasio piksel ke ukuran nyata
        scale_ratio = ref_real_cm / ref_width_px  # Use directly, ref_width_px should be an int or float

        # Hitung dimensi benda
        item_real_width = item_width_px * scale_ratio
        item_real_height = item_height_px * scale_ratio

        # Convert to float for rounding if necessary
        return round(float(item_real_width), 2), round(float(item_real_height), 2)

    # Template matching dengan OpenCV jika YOLO gagal
    def detect_reference_with_template(image_path):
        ref_real_cm = 8.56  # Panjang kartu kredit (cm)

        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        template = cv2.imread(REFERENCE_TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)

        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < 0.5:  # Confidence threshold
            return None  # Tidak ada pola referensi yang cocok

        h, w = template.shape
        x, y = max_loc
        ref_bbox = [x, y, w, h]  # Format [x, y, width, height]

        return ref_bbox, ref_real_cm

    # Home route
    @app.route("/")
    def home():
        return render_template("index.html")

    # Route untuk menerima gambar dan menjalankan deteksi
    @app.route("/upload", methods=["POST"])
    def upload_image():
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        # Simpan file di folder uploads
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Jalankan YOLOv5
        results = model(filepath)

        # Parse hasil deteksi
        detections = results.xywh[0]  # Bounding box dalam format [x_center, y_center, width, height, confidence, class]
        items = []
        references = []

        for det in detections:
            class_id = int(det[-1])  # class_id: 0 = item, 1 = reference
            if class_id == 0:
                items.append(det)
            elif class_id == 1:
                references.append(det)

        # Jika referensi tidak terdeteksi, gunakan template matching sebagai fallback
        if len(references) == 0:
            ref_template_match = detect_reference_with_template(filepath)
            if ref_template_match:
                ref_bbox, ref_real_cm = ref_template_match
            else:
                # Tidak ada referensi, gunakan fallback berdasarkan ukuran gambar
                img_size = results.xywh[0].shape[1] if results.xywh else None
                ref_real_cm = 8.56  # Default panjang referensi kartu kredit
                ref_bbox = [0, 0, img_size, 0]  # Anggap seluruh width gambar sebagai referensi
        else:
            ref_bbox = references[0]  # Ambil referensi dengan confidence tertinggi dari YOLO
            ref_real_cm = 8.56  # Panjang kartu kredit (asumsi)

        # Ambil bounding box item
        if len(items) == 0:
            return "Failed to detect item in the image", 400
        item_bbox = items[0]

        # Hitung dimensi
        img_size = results.xywh[0].shape[1] if results.xywh else None
        item_width, item_height = calculate_dimensions(img_size, item_bbox, ref_bbox, ref_real_cm)

        # Hasil JSON dikirim ke frontend
        result = {
            "item_width": item_width,
            "item_height": item_height,
        }
        return jsonify(result)

finally:
    # Restore the original PosixPath
    pathlib.PosixPath = posix_backup

if __name__ == "__main__":
    app.run(debug=True)