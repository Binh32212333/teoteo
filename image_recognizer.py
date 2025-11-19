import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageRecognizer:
    """Recognize and tag images for categorization and reuse"""

    def __init__(self):
        logger.info("Initializing image recognition model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Use CLIP for image understanding
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model.to(self.device)

        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass

        # Predefined categories for SEO content
        self.categories = [
            "technology", "business", "finance", "health", "lifestyle",
            "food", "travel", "education", "sports", "entertainment",
            "fashion", "real estate", "automotive", "science", "nature",
            "people", "abstract", "product", "interior", "exterior"
        ]

    def analyze_image(self, image_path):
        """
        Analyze image and generate tags and categories
        Returns: dict with 'tags', 'categories', 'description'
        """
        try:
            logger.info(f"Analyzing image: {image_path}")

            # Load image
            image = Image.open(image_path).convert('RGB')

            # Generate description and categories using CLIP
            categories = self._classify_image(image)
            tags = self._generate_tags(image)
            description = self._generate_description(image, categories, tags)

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

    def _classify_image(self, image):
        """Classify image into predefined categories"""
        try:
            # Prepare inputs for CLIP
            inputs = self.processor(
                text=self.categories,
                images=image,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            # Get top 3 categories
            top_probs, top_indices = torch.topk(probs[0], k=min(3, len(self.categories)))

            selected_categories = []
            for prob, idx in zip(top_probs, top_indices):
                if prob.item() > 0.15:  # Threshold for category selection
                    selected_categories.append(self.categories[idx.item()])

            return selected_categories if selected_categories else [self.categories[top_indices[0].item()]]

        except Exception as e:
            logger.error(f"Error in classification: {e}")
            return []

    def _generate_tags(self, image):
        """Generate descriptive tags for the image"""
        try:
            # Predefined tag options
            tag_options = [
                # Objects
                "person", "people", "man", "woman", "child", "group",
                "building", "house", "office", "city", "landscape",
                "car", "vehicle", "road", "street",
                "food", "meal", "dish", "dessert",
                "computer", "phone", "technology", "device",
                "book", "paper", "document",
                "furniture", "table", "chair",
                "plant", "tree", "flower", "nature",
                "animal", "pet", "dog", "cat",
                # Settings
                "indoor", "outdoor", "urban", "rural",
                "daytime", "nighttime", "sunset", "sunrise",
                # Qualities
                "colorful", "minimal", "modern", "vintage",
                "professional", "casual", "formal",
                "close-up", "wide-angle", "aerial",
                # Activities
                "working", "meeting", "studying", "eating",
                "traveling", "shopping", "exercising"
            ]

            # Use CLIP to score tag relevance
            inputs = self.processor(
                text=tag_options,
                images=image,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            # Get top scoring tags
            top_probs, top_indices = torch.topk(probs[0], k=10)

            tags = []
            for prob, idx in zip(top_probs, top_indices):
                if prob.item() > 0.08:  # Lower threshold for tags
                    tags.append(tag_options[idx.item()])

            return tags[:8]  # Return top 8 tags

        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return []

    def _generate_description(self, image, categories, tags):
        """Generate a text description of the image"""
        description_parts = []

        if categories:
            description_parts.append(f"Image showing {', '.join(categories)} content")

        if tags:
            description_parts.append(f"featuring {', '.join(tags[:3])}")

        return ". ".join(description_parts) if description_parts else "Image content"

    def find_similar_content_images(self, content_text, image_list, top_k=5):
        """
        Find images most relevant to the given content text
        Args:
            content_text: SEO post content
            image_list: List of image metadata dicts
            top_k: Number of images to return
        Returns:
            List of top_k most relevant images
        """
        if not image_list:
            return []

        try:
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

            # Use CLIP for semantic similarity
            # Prepare content text
            content_inputs = self.processor(
                text=[content_text[:500]],  # Limit content length
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            content_inputs = {k: v.to(self.device) for k, v in content_inputs.items()}

            # Get text embedding
            with torch.no_grad():
                text_features = self.model.get_text_features(**content_inputs)

            # For each image, calculate similarity
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

                # Calculate cosine similarity
                similarity = torch.nn.functional.cosine_similarity(
                    text_features,
                    img_features
                ).item()

                scores.append((similarity, idx))

            # Sort by score and return top_k
            scores.sort(reverse=True, key=lambda x: x[0])
            top_images = [image_list[idx] for score, idx in scores[:top_k]]

            logger.info(f"Found {len(top_images)} relevant images for content")
            return top_images

        except Exception as e:
            logger.error(f"Error finding similar images: {e}")
            return image_list[:top_k]  # Fallback to first k images

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

        logger.info(f"Analyzed {len(analyzed)} images")
        return analyzed
