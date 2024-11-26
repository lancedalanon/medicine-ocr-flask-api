## Flask Backend for Medicine OCR React Native Application

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![EasyOCR](https://img.shields.io/badge/EasyOCR-005B00?style=for-the-badge&logo=easyocr&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-FF5D5D?style=for-the-badge&logo=pillow&logoColor=white)
![dotenv](https://img.shields.io/badge/dotenv-6B2C00?style=for-the-badge&logo=dotenv&logoColor=white)

This backend application is built using Flask, a lightweight Python web framework, and serves as the backend for the **[Medicine OCR React Native application](https://github.com/lancedalanon/medicine-ocr-react-native)**. 
The backend provides an API for uploading images and extracting text from them using EasyOCR, which is especially useful for scanning and processing text from medicine labels, prescriptions, and packaging.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/lancedalanon/medicine-ocr-mobile.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file to store the environment variables (e.g., API key):
    ```bash
    API_KEY=your_api_key_here
    ```

4. Run the application:
    ```bash
    python app.py
    ```

## Routes

### `GET /ping`

A health check route to ensure the server is running.

**Response:**
```json
{
  "message": "Server is up!",
  "data": null
}
POST /process-image
This route accepts an image file, processes it using EasyOCR, and returns the extracted text.

Request Body:

image: (Required) Image file to be processed.
Response:

json
{
  "message": "Image processed successfully!",
  "data": "Extracted text from the image"
}
```
If an error occurs:

```json
{
  "message": "Error processing the image.",
  "data": "Error details"
}
```

## Key Features
API Key Authentication: The /process-image route is protected by an API key. You must provide the correct API key in the request header X-API-KEY for access.

Image Processing with OCR: The application uses EasyOCR to extract text from images. It supports common image formats like PNG, JPG, and JPEG.

Environment Variables: The application uses a .env file to store configuration settings like the API key.

Concurrency: The application uses Python's ThreadPoolExecutor to process multiple images concurrently for optimized performance.

## Example Usage
To test the server, you can use Postman or curl:

## Ping the Server
```bash
curl http://127.0.0.1:5000/ping
Process an Image
bash
curl -X POST http://127.0.0.1:5000/process-image \
  -H "X-API-KEY: your_api_key_here" \
  -F "image=@path_to_your_image.jpg"
```

## Error Handling
The application provides detailed error messages in case of failure, such as:

Missing or invalid API key
Invalid file format
OCR processing errors
General server errors

## License
This project is licensed under the MIT License.
