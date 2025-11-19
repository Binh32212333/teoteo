import re
import os
from bs4 import BeautifulSoup
import logging
from metadata_manager import MetadataManager
from image_recognizer import ImageRecognizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOPostManager:
    """Manage SEO posts and automatically insert relevant images"""

    def __init__(self, metadata_manager=None, image_recognizer=None):
        self.metadata_manager = metadata_manager or MetadataManager()
        self.image_recognizer = image_recognizer or ImageRecognizer()

    def read_post(self, file_path):
        """Read SEO post from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Error reading post {file_path}: {e}")
            return None

    def extract_text_from_html(self, html_content):
        """Extract plain text from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            return html_content

    def analyze_post_content(self, content):
        """
        Analyze post content to extract key topics and sections
        Returns: dict with 'full_text', 'sections', 'keywords'
        """
        # Check if HTML
        is_html = bool(re.search(r'<[^>]+>', content))

        if is_html:
            soup = BeautifulSoup(content, 'html.parser')
            plain_text = self.extract_text_from_html(content)

            # Extract sections based on headings
            sections = []
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                section_title = heading.get_text().strip()
                # Get text after heading until next heading
                section_content = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3']:
                        break
                    section_content.append(sibling.get_text())

                sections.append({
                    'title': section_title,
                    'content': ' '.join(section_content)
                })
        else:
            plain_text = content
            # Simple section detection for plain text
            sections = []
            lines = content.split('\n')
            current_section = {'title': 'Main', 'content': ''}

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Detect potential headings (all caps, short lines, etc.)
                if len(line) < 100 and (line.isupper() or line.endswith(':')):
                    if current_section['content']:
                        sections.append(current_section)
                    current_section = {'title': line, 'content': ''}
                else:
                    current_section['content'] += ' ' + line

            if current_section['content']:
                sections.append(current_section)

        # Extract keywords (simple approach)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', plain_text.lower())
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        keywords = [word for word, freq in keywords]

        return {
            'full_text': plain_text,
            'sections': sections,
            'keywords': keywords,
            'is_html': is_html
        }

    def find_relevant_images(self, post_analysis, num_images=5):
        """Find relevant images for the post"""
        # Get all available images
        all_images = self.metadata_manager.get_all_images()

        if not all_images:
            logger.warning("No images available in database")
            return []

        # Use image recognizer to find similar images
        full_text = post_analysis['full_text'][:1000]  # Limit text length
        relevant_images = self.image_recognizer.find_similar_content_images(
            full_text,
            all_images,
            top_k=num_images
        )

        return relevant_images

    def insert_images_into_html(self, html_content, images, post_id):
        """Insert images into HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find paragraphs to insert images after
            paragraphs = soup.find_all('p')

            if len(paragraphs) < len(images):
                # If not enough paragraphs, insert after headings too
                insertion_points = soup.find_all(['p', 'h2', 'h3'])
            else:
                insertion_points = paragraphs

            # Calculate insertion positions
            if insertion_points and images:
                step = max(1, len(insertion_points) // (len(images) + 1))

                for idx, image in enumerate(images):
                    position = min(step * (idx + 1), len(insertion_points) - 1)
                    insertion_point = insertion_points[position]

                    # Create image tag
                    img_tag = soup.new_tag('img')
                    img_tag['src'] = image['s3_url']
                    img_tag['alt'] = image.get('description', 'Image')
                    img_tag['class'] = 'seo-auto-image'

                    # Wrap in figure for better semantics
                    figure = soup.new_tag('figure')
                    figure.append(img_tag)

                    if image.get('description'):
                        figcaption = soup.new_tag('figcaption')
                        figcaption.string = image['description']
                        figure.append(figcaption)

                    # Insert after the element
                    insertion_point.insert_after(figure)

                    # Mark image as used
                    self.metadata_manager.mark_image_used(image['id'], post_id)

            return str(soup)

        except Exception as e:
            logger.error(f"Error inserting images into HTML: {e}")
            return html_content

    def insert_images_into_text(self, text_content, images, post_id):
        """Insert image markdown references into plain text"""
        lines = text_content.split('\n')
        new_lines = []

        # Calculate insertion positions
        total_lines = len([l for l in lines if l.strip()])
        images_inserted = 0

        if total_lines > 0 and images:
            step = max(1, total_lines // (len(images) + 1))

            line_count = 0
            for line in lines:
                new_lines.append(line)

                if line.strip():
                    line_count += 1

                    # Insert image at calculated positions
                    if images_inserted < len(images) and line_count % step == 0 and line_count > 0:
                        image = images[images_inserted]
                        new_lines.append('')
                        new_lines.append(f"![{image.get('description', 'Image')}]({image['s3_url']})")
                        new_lines.append('')
                        images_inserted += 1

                        # Mark image as used
                        self.metadata_manager.mark_image_used(image['id'], post_id)
        else:
            new_lines = lines

        return '\n'.join(new_lines)

    def process_post(self, input_file, output_file=None, num_images=5, post_id=None):
        """
        Process a SEO post and insert relevant images
        Args:
            input_file: Path to input post file
            output_file: Path to output file (if None, overwrites input)
            num_images: Number of images to insert
            post_id: Unique ID for this post
        """
        # Read post
        content = self.read_post(input_file)
        if not content:
            return False

        # Generate post ID if not provided
        if post_id is None:
            post_id = os.path.basename(input_file)

        # Analyze content
        logger.info(f"Analyzing post: {input_file}")
        analysis = self.analyze_post_content(content)

        # Find relevant images
        logger.info(f"Finding {num_images} relevant images...")
        relevant_images = self.find_relevant_images(analysis, num_images)

        if not relevant_images:
            logger.warning("No relevant images found")
            return False

        logger.info(f"Found {len(relevant_images)} relevant images")

        # Insert images based on content type
        if analysis['is_html']:
            new_content = self.insert_images_into_html(content, relevant_images, post_id)
        else:
            new_content = self.insert_images_into_text(content, relevant_images, post_id)

        # Save output
        output_path = output_file or input_file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Saved updated post to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving post: {e}")
            return False

    def batch_process_posts(self, input_directory, output_directory=None, num_images=5):
        """Process multiple posts in a directory"""
        if output_directory and not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Find all text/html files
        supported_extensions = ['.txt', '.html', '.htm', '.md']
        files = []

        for filename in os.listdir(input_directory):
            if any(filename.endswith(ext) for ext in supported_extensions):
                files.append(filename)

        logger.info(f"Found {len(files)} posts to process")

        processed = 0
        for filename in files:
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename) if output_directory else None

            if self.process_post(input_path, output_path, num_images, post_id=filename):
                processed += 1

        logger.info(f"Successfully processed {processed}/{len(files)} posts")
        return processed
