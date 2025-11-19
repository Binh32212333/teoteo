import re
import logging
from PIL import Image
import pytesseract
from config import Config

# Try to import easyocr, but make it optional
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageFilter:
    """Filter images containing phone numbers or websites using OCR"""

    def __init__(self, ocr_engine='easyocr'):
        # Default to tesseract if easyocr requested but not available
        if ocr_engine == 'easyocr' and not EASYOCR_AVAILABLE:
            logger.warning("EasyOCR not available. Falling back to Tesseract.")
            ocr_engine = 'tesseract'

        self.ocr_engine = ocr_engine

        if ocr_engine == 'easyocr' and EASYOCR_AVAILABLE:
            logger.info("Initializing EasyOCR...")
            self.reader = easyocr.Reader(Config.OCR_LANGUAGES, gpu=False)
        else:
            self.reader = None

        self.phone_patterns = [re.compile(pattern) for pattern in Config.PHONE_PATTERNS]
        self.website_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in Config.WEBSITE_PATTERNS]

    def extract_text_easyocr(self, image_path):
        """Extract text from image using EasyOCR"""
        try:
            results = self.reader.readtext(image_path)
            text = ' '.join([result[1] for result in results])
            return text
        except Exception as e:
            logger.error(f"EasyOCR error on {image_path}: {e}")
            return ""

    def extract_text_tesseract(self, image_path):
        """Extract text from image using Tesseract"""
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            logger.error(f"Tesseract error on {image_path}: {e}")
            return ""

    def extract_text(self, image_path):
        """Extract text from image using configured OCR engine"""
        if self.ocr_engine == 'easyocr':
            return self.extract_text_easyocr(image_path)
        else:
            return self.extract_text_tesseract(image_path)

    def contains_phone_number(self, text):
        """Check if text contains phone numbers"""
        for pattern in self.phone_patterns:
            if pattern.search(text):
                return True
        return False

    def contains_website(self, text):
        """Check if text contains website URLs"""
        for pattern in self.website_patterns:
            if pattern.search(text):
                return True
        return False

    def should_filter_image(self, image_path):
        """
        Determine if image should be filtered out
        Returns: (should_filter: bool, reason: str, extracted_text: str)
        """
        logger.info(f"Analyzing image: {image_path}")

        text = self.extract_text(image_path)

        if not text.strip():
            logger.info(f"No text found in image: {image_path}")
            return False, "no_text", ""

        logger.info(f"Extracted text: {text[:100]}...")  # Log first 100 chars

        if self.contains_phone_number(text):
            logger.warning(f"Phone number detected in: {image_path}")
            return True, "phone_number", text

        if self.contains_website(text):
            logger.warning(f"Website URL detected in: {image_path}")
            return True, "website", text

        logger.info(f"Image passed filter: {image_path}")
        return False, "passed", text

    def filter_images(self, image_list):
        """
        Filter list of images
        Returns: (passed_images, filtered_images)
        """
        passed = []
        filtered = []

        for image_info in image_list:
            filepath = image_info['filepath']
            should_filter, reason, text = self.should_filter_image(filepath)

            image_info['ocr_text'] = text
            image_info['filter_reason'] = reason

            if should_filter:
                filtered.append(image_info)
            else:
                passed.append(image_info)

        logger.info(f"Filter results: {len(passed)} passed, {len(filtered)} filtered out")
        return passed, filtered
