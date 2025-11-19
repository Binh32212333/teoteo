import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the image management system"""

    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')

    # Image Processing Settings
    MAX_IMAGE_SIZE_MB = int(os.getenv('MAX_IMAGE_SIZE_MB', 10))
    ALLOWED_IMAGE_FORMATS = os.getenv('ALLOWED_IMAGE_FORMATS', 'jpg,jpeg,png,webp').split(',')

    # OCR Settings
    OCR_ENGINE = os.getenv('OCR_ENGINE', 'easyocr')
    OCR_LANGUAGES = os.getenv('OCR_LANGUAGES', 'en').split(',')

    # Storage Paths
    LOCAL_STORAGE_PATH = os.getenv('LOCAL_STORAGE_PATH', './storage/images')
    TEMP_DOWNLOAD_PATH = os.getenv('TEMP_DOWNLOAD_PATH', './temp')
    METADATA_DB_PATH = os.getenv('METADATA_DB_PATH', './storage/metadata.json')

    # Phone number and website detection patterns
    PHONE_PATTERNS = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # US format
        r'\b\d{10}\b',  # 10 digits
        r'\+\d{1,3}[-.\s]?\d{1,14}\b',  # International format
    ]

    WEBSITE_PATTERNS = [
        r'www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}',
        r'https?://[^\s]+',
        r'[a-zA-Z0-9-]+\.com\b',
        r'[a-zA-Z0-9-]+\.net\b',
        r'[a-zA-Z0-9-]+\.org\b',
    ]

    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        os.makedirs(Config.LOCAL_STORAGE_PATH, exist_ok=True)
        os.makedirs(Config.TEMP_DOWNLOAD_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(Config.METADATA_DB_PATH), exist_ok=True)
