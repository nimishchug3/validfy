import cv2
import pytesseract
import json
from ultralytics import YOLO
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the YOLO model
model = YOLO('H:/TE_project/model.pt')

def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Apply adaptive thresholding for better contrast
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    return thresh

def process_image(image_path):
    # Load the image for OCR
    image = cv2.imread(image_path)
    ocr_results = {}

    # Predict and get results
    results = model.predict(source=image_path, show=False)

    # Process the results
    for result in results:
        print(result.names)  # class names
        for box, conf, class_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
            x1, y1, x2, y2 = map(int, box)
            roi = image[y1:y2, x1:x2]  # Extract region of interest

            # Preprocess the ROI
            processed_roi = preprocess_image(roi)

            # Perform OCR on the preprocessed ROI with updated parameters
            ocr_text = pytesseract.image_to_string(processed_roi, config='--oem 3 --psm 6')

            # Store results in the dictionary
            class_name = result.names[int(class_id)]
            ocr_results[class_name] = ocr_text.strip()

            # Print the OCR text for verification
            print(f"Class: {class_name}, OCR Text: {ocr_text.strip()}")  # Print OCR text

    return ocr_results


def strip_first_word(text):
    # Split the text into words and return everything after the first word
    if not text:
        return ""
    words = text.split()
    return ' '.join(words[1:]) if len(words) > 1 else ""

def clean_aadhar_number(aadhar_number):
    # Remove spaces and any non-numeric characters
    return ''.join(filter(str.isdigit, aadhar_number))

def split_name(full_name):
    # Split full name into first name and last name
    names = full_name.split()
    first_name = names[0]  # First word is the first name
    last_name = names[-1]  # Last word is the last name
    return first_name, last_name, full_name

@app.route('/upload', methods=['POST'])
def process_aadhaar():
    if 'front_image' not in request.files or 'back_image' not in request.files:
        return jsonify({"error": "Both front and back images are required"}), 400

    front_image = request.files['front_image']
    back_image = request.files['back_image']

    # Save images temporarily
    front_image_path = 'front_image.png'
    back_image_path = 'back_image.png'
    front_image.save(front_image_path)
    back_image.save(back_image_path)

    # Process the front image
    front_ocr_results = process_image(front_image_path)

    # Process the back image
    back_ocr_results = process_image(back_image_path)

    # Clean and format the Aadhaar number
    aadhar_number = clean_aadhar_number(front_ocr_results.get("AADHAR_NUMBER", ""))

    # Split and handle the name
    full_name = front_ocr_results.get("NAME", "")
    first_name, last_name, full_name = split_name(full_name)

    # Combine results (adjust according to your needs)
    combined_results = {
        "AADHAR_NUMBER": aadhar_number,
        "ADDRESS": strip_first_word(back_ocr_results.get("ADDRESS", "").strip()),  # Strip first word
        "DATE_OF_BIRTH": front_ocr_results.get("DATE_OF_BIRTH", ""),
        "GENDER": front_ocr_results.get("GENDER", ""),
        "FIRST NAME": first_name,
        "LAST NAME": last_name,
        "FULL NAME": full_name
    }

    return jsonify(combined_results)

if __name__ == '__main__':
    app.run(debug=True)
