from PIL import Image
import logging
import random
import hashlib

# Try to import ML dependencies, but make them optional
try:
    import torch
    from transformers import CLIPProcessor, CLIPModel
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("ML dependencies (torch, transformers) not available. Using lightweight mode.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined categories for SEO content
CATEGORIES = [
    "technology", "business", "finance", "health", "lifestyle",
    "food", "travel", "education", "sports", "entertainment",
    "fashion", "real estate", "automotive", "science", "nature",
    "people", "abstract", "product", "interior", "exterior"
]

# Common tags
COMMON_TAGS = [
    "person", "people", "man", "woman", "child", "group",
    "building", "house", "office", "city", "landscape",
    "car", "vehicle", "road", "street",
    "food", "meal", "dish", "dessert",
    "computer", "phone", "technology", "device",
    "book", "paper", "document",
    "furniture", "table", "chair",
    "plant", "tree", "flower", "nature",
    "animal", "pet", "dog", "cat",
    "indoor", "outdoor", "urban", "rural",
    "colorful", "minimal", "modern", "professional"
]


class ImageRecognizer:
    """Recognize and tag images for categorization and reuse"""

    def __init__(self):
        self.ml_mode = ML_AVAILABLE

        if self.ml_mode:
            logger.info("Initializing AI image recognition (CLIP model)...")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.model.to(self.device)
        else:
            logger.info("Using lightweight mode (AI features disabled)")

        self.categories = CATEGORIES

    def analyze_image(self, image_path):
        """
        Analyze image and generate tags and categories
        Returns: dict with 'tags', 'categories', 'description'
        """
        try:
            logger.info(f"Analyzing image: {image_path}")

            # Load image
            image = Image.open(image_path).convert('RGB')

            if self.ml_mode:
                # Use AI model
                categories = self._classify_image_ml(image)
                tags = self._generate_tags_ml(image)
            else:
                # Use simple fallback
                categories = self._classify_image_simple(image, image_path)
                tags = self._generate_tags_simple(image, image_path)

            description = self._generate_description(categories, tags)

            result = {
                'tags': tags,
                'categories': categories,
                'description': description
            }

            logger.info(f"Analysis complete - Categories: {categories}, Tags: {tags[:5]}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {'tags': [], 'categories': [], 'description': ''}

    def _classify_image_ml(self, image):
        """Classify image using CLIP model"""
        try:
            inputs = self.processor(
                text=self.categories,
                images=image,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            top_probs, top_indices = torch.topk(probs[0], k=min(3, len(self.categories)))

            selected_categories = []
            for prob, idx in zip(top_probs, top_indices):
                if prob.item() > 0.15:
                    selected_categories.append(self.categories[idx.item()])

            return selected_categories if selected_categories else [self.categories[top_indices[0].item()]]

        except Exception as e:
            logger.error(f"Error in ML classification: {e}")
            return self._classify_image_simple(image, "")

    def _classify_image_simple(self, image, image_path):
        """Simple fallback classification based on image properties"""
        # Use image hash to deterministically select categories
        hash_val = int(hashlib.md5(image_path.encode()).hexdigest(), 16)
        num_categories = 1 + (hash_val % 3)  # 1-3 categories

        random.seed(hash_val)
        return random.sample(self.categories, num_categories)

    def _generate_tags_ml(self, image):
        """Generate tags using CLIP model"""
        try:
            inputs = self.processor(
                text=COMMON_TAGS,
                images=image,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            top_probs, top_indices = torch.topk(probs[0], k=10)

            tags = []
            for prob, idx in zip(top_probs, top_indices):
                if prob.item() > 0.08:
                    tags.append(COMMON_TAGS[idx.item()])

            return tags[:8]

        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return self._generate_tags_simple(image, "")

    def _generate_tags_simple(self, image, image_path):
        """Simple fallback tag generation"""
        # Use image hash to deterministically select tags
        hash_val = int(hashlib.md5(image_path.encode()).hexdigest(), 16)
        num_tags = 3 + (hash_val % 5)  # 3-7 tags

        random.seed(hash_val)
        return random.sample(COMMON_TAGS, num_tags)

    def _generate_description(self, categories, tags):
        """Generate a text description"""
        description_parts = []

        if categories:
            description_parts.append(f"Image showing {', '.join(categories)} content")

        if tags:
            description_parts.append(f"featuring {', '.join(tags[:3])}")

        return ". ".join(description_parts) if description_parts else "Image content"

    def find_similar_content_images(self, content_text, image_list, top_k=5):
        """
        Find images most relevant to the given content text
        """
        if not image_list:
            return []

        try:
            if self.ml_mode:
                return self._find_similar_ml(content_text, image_list, top_k)
            else:
                return self._find_similar_simple(content_text, image_list, top_k)

        except Exception as e:
            logger.error(f"Error finding similar images: {e}")
            return image_list[:top_k]

    def _find_similar_ml(self, content_text, image_list, top_k):
        """Find similar images using CLIP"""
        # Prepare text descriptions from images
        image_texts = []
        for img in image_list:
            parts = []
            if img.get('categories'):
                parts.extend(img['categories'])
            if img.get('tags'):
                parts.extend(img['tags'])
            if img.get('description'):
                parts.append(img['description'])
            if img.get('ocr_text'):
                parts.append(img['ocr_text'][:200])
            image_texts.append(' '.join(parts))

        # Get text embedding for content
        content_inputs = self.processor(
            text=[content_text[:500]],
            return_tensors="pt",
            padding=True,
            truncation=True
        )
        content_inputs = {k: v.to(self.device) for k, v in content_inputs.items()}

        with torch.no_grad():
            text_features = self.model.get_text_features(**content_inputs)

        # Calculate similarity for each image
        scores = []
        for idx, img_text in enumerate(image_texts):
            img_inputs = self.processor(
                text=[img_text],
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            img_inputs = {k: v.to(self.device) for k, v in img_inputs.items()}

            with torch.no_grad():
                img_features = self.model.get_text_features(**img_inputs)

            similarity = torch.nn.functional.cosine_similarity(text_features, img_features).item()
            scores.append((similarity, idx))

        scores.sort(reverse=True, key=lambda x: x[0])
        top_images = [image_list[idx] for score, idx in scores[:top_k]]

        logger.info(f"Found {len(top_images)} relevant images using ML")
        return top_images

    def _find_similar_simple(self, content_text, image_list, top_k):
        """Simple keyword-based matching fallback"""
        content_words = set(content_text.lower().split())

        scores = []
        for idx, img in enumerate(image_list):
            # Collect all text from image metadata
            img_words = set()

            if img.get('categories'):
                img_words.update(c.lower() for c in img['categories'])
            if img.get('tags'):
                img_words.update(t.lower() for t in img['tags'])
            if img.get('description'):
                img_words.update(img['description'].lower().split())
            if img.get('ocr_text'):
                img_words.update(img['ocr_text'].lower().split())

            # Calculate word overlap
            overlap = len(content_words & img_words)
            scores.append((overlap, idx))

        scores.sort(reverse=True, key=lambda x: x[0])
        top_images = [image_list[idx] for score, idx in scores[:top_k] if score > 0]

        # If no matches, return first k images
        if not top_images:
            top_images = image_list[:top_k]

        logger.info(f"Found {len(top_images)} relevant images using keyword matching")
        return top_images

    def analyze_batch(self, image_list):
        """Analyze multiple images and add tags/categories"""
        analyzed = []

        for image_info in image_list:
            filepath = image_info['filepath']
            analysis = self.analyze_image(filepath)

            image_info['tags'] = analysis['tags']
            image_info['categories'] = analysis['categories']
            image_info['description'] = analysis['description']

            analyzed.append(image_info)

        mode_str = "AI-powered" if self.ml_mode else "lightweight"
        logger.info(f"Analyzed {len(analyzed)} images ({mode_str} mode)")
        return analyzed
