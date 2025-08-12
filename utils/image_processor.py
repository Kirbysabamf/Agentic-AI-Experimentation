import base64
import requests
from PIL import Image
from io import BytesIO
from typing import Optional, Dict, Any
import os

class ImageProcessor:
    """Handles image processing and analysis for marketing A/B tests"""
    
    @staticmethod
    def load_image_from_url(url: str) -> Optional[Image.Image]:
        """Load an image from a URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            print(f"Error loading image from URL: {e}")
            return None
    
    @staticmethod
    def load_image_from_file(file_path: str) -> Optional[Image.Image]:
        """Load an image from a local file"""
        try:
            if not os.path.exists(file_path):
                print(f"Image file not found: {file_path}")
                return None
            image = Image.open(file_path)
            return image
        except Exception as e:
            print(f"Error loading image from file: {e}")
            return None
    
    @staticmethod
    def encode_image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """Convert PIL Image to base64 string for API usage"""
        buffered = BytesIO()
        image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/{format.lower()};base64,{img_str}"
    
    @staticmethod
    def resize_image(image: Image.Image, max_size: tuple = (1024, 1024)) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def validate_image_url(url: str) -> bool:
        """Validate if URL points to a valid image"""
        try:
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('content-type', '')
            return content_type.startswith('image/')
        except:
            return False
    
    @classmethod
    def prepare_image_for_analysis(cls, image_source: str) -> Optional[str]:
        """
        Prepare image for analysis - handles both URLs and file paths
        Returns base64 encoded image URL or original URL if valid
        """
        if image_source.startswith('http'):
            # It's a URL - validate and return if valid
            if cls.validate_image_url(image_source):
                return image_source
            else:
                print(f"Invalid image URL: {image_source}")
                return None
        else:
            # It's a file path - load and encode
            image = cls.load_image_from_file(image_source)
            if image:
                # Resize if too large
                image = cls.resize_image(image)
                return cls.encode_image_to_base64(image)
            return None
    
    @staticmethod
    def extract_image_metadata(image: Image.Image) -> Dict[str, Any]:
        """Extract basic metadata from image"""
        return {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "aspect_ratio": round(image.width / image.height, 2)
        }