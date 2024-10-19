import easyocr
import numpy as np
from PIL import Image, ImageFilter
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count

class ImageProcessor:
    _reader = None

    def __init__(self):
        """
        Initialize the EasyOCR reader for the English language.
        Reuses a cached reader if available, reducing initialization overhead.
        """
        if not ImageProcessor._reader:
            # Load the reader once and cache it (use GPU if available for better performance)
            ImageProcessor._reader = easyocr.Reader(['en'], gpu=True)

        self.reader = ImageProcessor._reader

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess the image for better OCR results.
        
        Args:
            image (PIL.Image.Image): The image to preprocess.
        
        Returns:
            PIL.Image.Image: The preprocessed image.
        """
        # Resize the image
        image = image.resize((image.width // 2, image.height // 2))  # Adjust scaling as needed
        
        # Convert to grayscale
        image = image.convert('L')  # 'L' mode is grayscale
        
        # Optionally, apply Gaussian blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=1))

        return image

    def process_image(self, image: Image.Image) -> dict:
        """
        Process the image to extract text using EasyOCR while preserving the layout.

        Args:
            image (PIL.Image.Image): The image to process.

        Returns:
            dict: A dictionary containing the success status and extracted text or error.
        """
        try:
            image = self.preprocess_image(image)  # Preprocess the image

            # Convert the image to a numpy array for EasyOCR
            image_np = np.array(image)

            # Perform OCR on the raw image (no preprocessing)
            result = self.reader.readtext(image_np)

            # If no text is detected, return early with an error message
            if not result:
                return {
                    'success': False,
                    'error': 'No text detected in the image.'
                }

            # Extract text and coordinates using list comprehension
            text_with_coordinates = [
                (bbox[0][1], bbox[0][0], text) for bbox, text, _ in result  # Use (y, x) from top-left corner
            ]

            # Sort by y-coordinate (top-to-bottom), then by x-coordinate (left-to-right)
            text_with_coordinates.sort(key=lambda coord: (coord[0], coord[1]))

            # Group text by lines using more efficient data structures
            lines = []
            current_y = text_with_coordinates[0][0] if text_with_coordinates else None
            current_line = []

            for y, x, text in text_with_coordinates:
                if current_y is None or abs(y - current_y) > 10:  # Tolerance for y-coordinate differences
                    if current_line:
                        lines.append(' '.join(current_line))  # Store the full line
                    current_line = [text]  # Start a new line
                    current_y = y
                else:
                    current_line.append(text)  # Continue with the current line

            # Append the last line
            if current_line:
                lines.append(' '.join(current_line))

            # Join lines with newline characters to maintain formatting
            formatted_text = '\n'.join(lines)

            return {
                'success': True,
                'text': formatted_text
            }

        except easyocr.Reader as e:
            # Handle OCR-specific errors
            return {
                'success': False,
                'error': f'OCR failed: {str(e)}'
            }
        except Exception as e:
            # General error handling
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def process_images_in_parallel(self, images: list) -> list:
        """
        Process multiple images in parallel using ThreadPoolExecutor with optimized thread count.
        
        Args:
            images (list): List of PIL.Image.Image objects to process.
        
        Returns:
            list: List of dictionaries with the results for each image.
        """
        num_workers = cpu_count()  # Get the number of available CPU cores
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(self.process_image, images))

        return results

    def process_images_in_batches(self, images: list, batch_size: int = 10) -> list:
        """
        Process images in batches to optimize performance.
        
        Args:
            images (list): List of PIL.Image.Image objects to process.
            batch_size (int): Number of images to process at a time.
        
        Returns:
            list: List of dictionaries with the results for each image.
        """
        results = []
        for i in range(0, len(images), batch_size):
            batch = images[i:i + batch_size]
            results.extend(self.process_images_in_parallel(batch))
        return results
