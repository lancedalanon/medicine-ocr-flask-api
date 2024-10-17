from flask import Flask, jsonify, request, abort
from functools import wraps
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
from image_processor import ImageProcessor

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize ImageProcessor
image_processor = ImageProcessor()

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Middleware to check API key
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from headers
        api_key = request.headers.get('X-API-KEY')
        # Check if the API key matches the one in .env
        if api_key and api_key == os.getenv('API_KEY'):
            return f(*args, **kwargs)  # Proceed if the key is valid
        else:
            # Abort with 403 Forbidden if API key is missing or incorrect
            return jsonify({
                'message': 'Forbidden: Invalid or missing API key',
                'data': None
            }), 403
    return decorated_function

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
@require_api_key  # Protect this route with the API key
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
    # Check if running in production environment
    if os.getenv('FLASK_ENV') == 'production':
        # Run with production settings
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
    else:
        # Run with debugging enabled for development
        app.run(debug=True)