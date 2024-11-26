from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from functools import wraps
from PIL import Image
from io import BytesIO
from image_processor import ImageProcessor
import requests
from pathlib import Path
import socket

# Initialize Flask app
app = Flask(__name__)

# Apply CORS to the entire app
CORS(app)

# Initialize ImageProcessor
image_processor = ImageProcessor()

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Get the local IP address
def get_local_ip():
    try:
        # Create a socket and connect to an external address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Using Google's public DNS server as an external address
        local_ip = s.getsockname()[0]  # Get the local IP address
    except Exception as e:
        local_ip = '127.0.0.1'  # Fallback to localhost if an error occurs
    finally:
        s.close()
    return local_ip

# Helper function to check allowed file types
def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Health check route - GET method
@app.route('/ping', methods=['GET'])
def ping():
    """
    Health check route to ensure the server is running.

    Returns:
        JSON response with a message and empty data.
    """
    return jsonify({
        'message': 'Server is up!',
        'data': None
    }), 200

# Process image route - POST method
@app.route('/process-image', methods=['POST'])
def process_image():
    """
    Handles image uploads in memory and processes them using EasyOCR to extract text.

    Returns:
        JSON response with the extracted text or an error message.
    """
    
    # Check if the request contains a file part
    if 'image' not in request.files:
        return jsonify({
            'message': 'No image file provided.',
            'data': None
        }), 400

    file = request.files['image']
    
    # If the user does not select a file, the browser may submit an empty part
    if file.filename == '':
        return jsonify({
            'message': 'No image selected for uploading.',
            'data': None
        }), 400

    # Check if the file has an allowed extension
    if file and allowed_file(file.filename):
        try:
            # Open the image from memory using Pillow (PIL)
            image = Image.open(BytesIO(file.read()))

            # Process the image using the ImageProcessor class
            ocr_result = image_processor.process_image(image)

            if ocr_result['success']:
                return jsonify({
                    'message': 'Image processed successfully!',
                    'data': ocr_result['text']
                }), 200
            else:
                return jsonify({
                    'message': 'Error processing the image.',
                    'data': ocr_result['error']
                }), 500
        except Exception as e:
            return jsonify({
                'message': 'Error opening or processing image.',
                'data': str(e)
            }), 500
    else:
        return jsonify({
            'message': 'Invalid file format. Allowed types are: png, jpg, jpeg.',
            'data': None
        }), 400

# Run the app
if __name__ == '__main__':
    ip_address = get_local_ip()
    app.run(host=ip_address, port=5000, debug=True)

    # Make a GET request to /ping to check if the server is running
    try:
        response = requests.get(f"http://{ip_address}:5000/ping") 
        print(response.json())  # Print the response to the console
    except Exception as e:
        print(f"Error making request to /ping: {str(e)}")
