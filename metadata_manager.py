import json
import os
from datetime import datetime
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataManager:
    """Manage metadata for uploaded images"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Config.METADATA_DB_PATH
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        """Load existing metadata from JSON file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('images', []))} images from metadata")
                    return data
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {'images': [], 'tags': {}, 'categories': {}}
        else:
            return {'images': [], 'tags': {}, 'categories': {}}

    def save_metadata(self):
        """Save metadata to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved metadata for {len(self.metadata['images'])} images")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def add_image(self, image_info):
        """Add or update image metadata"""
        # Create metadata entry
        entry = {
            'id': image_info.get('url_hash'),
            'original_url': image_info.get('url'),
            's3_url': image_info.get('s3_url'),
            's3_key': image_info.get('s3_key'),
            'extension': image_info.get('extension'),
            'ocr_text': image_info.get('ocr_text', ''),
            'filter_reason': image_info.get('filter_reason', 'passed'),
            'tags': image_info.get('tags', []),
            'categories': image_info.get('categories', []),
            'description': image_info.get('description', ''),
            'uploaded_at': datetime.now().isoformat(),
            'used_in_posts': []
        }

        # Check if image already exists
        existing_idx = None
        for idx, img in enumerate(self.metadata['images']):
            if img.get('id') == entry['id']:
                existing_idx = idx
                break

        if existing_idx is not None:
            # Update existing entry
            self.metadata['images'][existing_idx] = entry
            logger.info(f"Updated existing image: {entry['id']}")
        else:
            # Add new entry
            self.metadata['images'].append(entry)
            logger.info(f"Added new image: {entry['id']}")

        # Update tags index
        for tag in entry['tags']:
            if tag not in self.metadata['tags']:
                self.metadata['tags'][tag] = []
            if entry['id'] not in self.metadata['tags'][tag]:
                self.metadata['tags'][tag].append(entry['id'])

        # Update categories index
        for category in entry['categories']:
            if category not in self.metadata['categories']:
                self.metadata['categories'][category] = []
            if entry['id'] not in self.metadata['categories'][category]:
                self.metadata['categories'][category].append(entry['id'])

        self.save_metadata()

    def add_images_batch(self, image_list):
        """Add multiple images at once"""
        for image_info in image_list:
            self.add_image(image_info)

    def get_image_by_id(self, image_id):
        """Get image metadata by ID"""
        for img in self.metadata['images']:
            if img.get('id') == image_id:
                return img
        return None

    def search_by_tags(self, tags):
        """Search images by tags"""
        if isinstance(tags, str):
            tags = [tags]

        matching_ids = set()
        for tag in tags:
            if tag in self.metadata['tags']:
                matching_ids.update(self.metadata['tags'][tag])

        return [self.get_image_by_id(img_id) for img_id in matching_ids]

    def search_by_category(self, category):
        """Search images by category"""
        if category in self.metadata['categories']:
            image_ids = self.metadata['categories'][category]
            return [self.get_image_by_id(img_id) for img_id in image_ids]
        return []

    def search_by_text(self, query):
        """Search images by OCR text or description"""
        query_lower = query.lower()
        results = []

        for img in self.metadata['images']:
            ocr_text = img.get('ocr_text', '').lower()
            description = img.get('description', '').lower()

            if query_lower in ocr_text or query_lower in description:
                results.append(img)

        return results

    def mark_image_used(self, image_id, post_id):
        """Mark an image as used in a post"""
        img = self.get_image_by_id(image_id)
        if img and post_id not in img.get('used_in_posts', []):
            for image in self.metadata['images']:
                if image.get('id') == image_id:
                    if 'used_in_posts' not in image:
                        image['used_in_posts'] = []
                    image['used_in_posts'].append(post_id)
                    break
            self.save_metadata()

    def get_all_images(self):
        """Get all images"""
        return self.metadata['images']

    def get_stats(self):
        """Get statistics about stored images"""
        return {
            'total_images': len(self.metadata['images']),
            'total_tags': len(self.metadata['tags']),
            'total_categories': len(self.metadata['categories']),
            'images_used': sum(1 for img in self.metadata['images'] if img.get('used_in_posts'))
        }
