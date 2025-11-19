import os
import csv
import requests
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image
from io import BytesIO
from config import Config
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageDownloader:
    """Download images from URLs provided in a CSV file"""

    def __init__(self):
        Config.ensure_directories()
        self.temp_path = Config.TEMP_DOWNLOAD_PATH
        self.max_size_bytes = Config.MAX_IMAGE_SIZE_MB * 1024 * 1024

    def read_csv(self, csv_file_path):
        """
        Read CSV file containing image URLs
        Expected format: CSV with a column named 'url' or 'image_url'
        """
        urls = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    url = row.get('url') or row.get('image_url') or row.get('URL')
                    if url:
                        urls.append(url.strip())
            logger.info(f"Found {len(urls)} URLs in CSV file")
            return urls
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return []

    def download_image(self, url, timeout=30):
        """
        Download a single image from URL
        Returns: (image_data, file_extension, url_hash) or (None, None, None) if failed
        """
        try:
            logger.info(f"Downloading: {url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                logger.warning(f"URL is not an image: {url}")
                return None, None, None

            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_size_bytes:
                logger.warning(f"Image too large: {url}")
                return None, None, None

            # Download image data
            image_data = BytesIO(response.content)

            # Verify it's a valid image
            try:
                img = Image.open(image_data)
                img.verify()
                image_data.seek(0)  # Reset pointer after verify
                img = Image.open(image_data)  # Reopen after verify
            except Exception as e:
                logger.error(f"Invalid image file from {url}: {e}")
                return None, None, None

            # Get file extension
            ext = img.format.lower() if img.format else 'jpg'
            if ext not in Config.ALLOWED_IMAGE_FORMATS:
                logger.warning(f"Unsupported format {ext} from {url}")
                return None, None, None

            # Create unique hash for this URL
            url_hash = hashlib.md5(url.encode()).hexdigest()

            # Reset BytesIO pointer
            image_data.seek(0)

            return image_data, ext, url_hash

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            return None, None, None
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            return None, None, None

    def save_temp_image(self, image_data, filename):
        """Save image data to temporary storage"""
        try:
            filepath = os.path.join(self.temp_path, filename)

            # Open and save using PIL to ensure proper format
            img = Image.open(image_data)
            img.save(filepath)

            logger.info(f"Saved temporary image: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving image {filename}: {e}")
            return None

    def download_from_csv(self, csv_file_path):
        """
        Download all images from CSV file
        Returns: list of tuples (filepath, url, url_hash)
        """
        urls = self.read_csv(csv_file_path)
        downloaded_images = []

        for idx, url in enumerate(urls):
            image_data, ext, url_hash = self.download_image(url)

            if image_data:
                filename = f"{url_hash}.{ext}"
                filepath = self.save_temp_image(image_data, filename)

                if filepath:
                    downloaded_images.append({
                        'filepath': filepath,
                        'url': url,
                        'url_hash': url_hash,
                        'extension': ext
                    })

        logger.info(f"Successfully downloaded {len(downloaded_images)}/{len(urls)} images")
        return downloaded_images
