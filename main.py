#!/usr/bin/env python3
"""
Main script for automated image management and SEO post enhancement
"""

import argparse
import logging
import sys
from config import Config
from image_downloader import ImageDownloader
from image_filter import ImageFilter
from aws_uploader import AWSUploader
from image_recognizer import ImageRecognizer
from metadata_manager import MetadataManager
from seo_post_manager import SEOPostManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def upload_images_from_csv(csv_file, ocr_engine='easyocr'):
    """
    Complete workflow: Download images from CSV, filter, analyze, and upload to AWS
    """
    logger.info("=== Starting Image Upload Workflow ===")

    # Step 1: Download images
    logger.info("Step 1: Downloading images from CSV...")
    downloader = ImageDownloader()
    downloaded_images = downloader.download_from_csv(csv_file)

    if not downloaded_images:
        logger.error("No images were downloaded. Exiting.")
        return []

    # Step 2: Filter images (remove those with phone numbers or websites)
    logger.info("Step 2: Filtering images with OCR...")
    image_filter = ImageFilter(ocr_engine=ocr_engine)
    passed_images, filtered_images = image_filter.filter_images(downloaded_images)

    logger.info(f"Filtering complete: {len(passed_images)} passed, {len(filtered_images)} filtered out")

    if not passed_images:
        logger.warning("No images passed the filter. Nothing to upload.")
        return []

    # Step 3: Analyze images (recognize content and generate tags)
    logger.info("Step 3: Analyzing images for content recognition...")
    recognizer = ImageRecognizer()
    analyzed_images = recognizer.analyze_batch(passed_images)

    # Step 4: Upload to AWS S3
    logger.info("Step 4: Uploading images to AWS S3...")
    uploader = AWSUploader()

    # Check if bucket exists
    if not uploader.check_bucket_exists():
        logger.error(f"S3 bucket '{Config.AWS_S3_BUCKET}' does not exist or is not accessible")
        return []

    uploaded_images = uploader.upload_images(analyzed_images)

    # Step 5: Save metadata
    logger.info("Step 5: Saving image metadata...")
    metadata_manager = MetadataManager()
    metadata_manager.add_images_batch(uploaded_images)

    logger.info(f"=== Workflow Complete: {len(uploaded_images)} images uploaded successfully ===")
    return uploaded_images


def process_seo_posts(posts_directory, output_directory=None, num_images=5):
    """
    Process SEO posts and automatically insert relevant images
    """
    logger.info("=== Starting SEO Post Processing ===")

    metadata_manager = MetadataManager()
    recognizer = ImageRecognizer()
    post_manager = SEOPostManager(metadata_manager, recognizer)

    processed_count = post_manager.batch_process_posts(
        posts_directory,
        output_directory,
        num_images
    )

    logger.info(f"=== Processed {processed_count} posts ===")
    return processed_count


def show_stats():
    """Show statistics about stored images"""
    metadata_manager = MetadataManager()
    stats = metadata_manager.get_stats()

    print("\n=== Image Database Statistics ===")
    print(f"Total images: {stats['total_images']}")
    print(f"Total tags: {stats['total_tags']}")
    print(f"Total categories: {stats['total_categories']}")
    print(f"Images used in posts: {stats['images_used']}")
    print("=" * 35 + "\n")


def search_images(query=None, tag=None, category=None):
    """Search for images in the database"""
    metadata_manager = MetadataManager()

    if query:
        results = metadata_manager.search_by_text(query)
        print(f"\n=== Search Results for '{query}' ===")
    elif tag:
        results = metadata_manager.search_by_tags(tag)
        print(f"\n=== Images with tag '{tag}' ===")
    elif category:
        results = metadata_manager.search_by_category(category)
        print(f"\n=== Images in category '{category}' ===")
    else:
        results = metadata_manager.get_all_images()
        print("\n=== All Images ===")

    if results:
        for img in results[:10]:  # Show first 10
            print(f"\nID: {img['id']}")
            print(f"URL: {img['s3_url']}")
            print(f"Categories: {', '.join(img.get('categories', []))}")
            print(f"Tags: {', '.join(img.get('tags', []))}")
            print(f"Description: {img.get('description', 'N/A')}")
        if len(results) > 10:
            print(f"\n... and {len(results) - 10} more")
    else:
        print("No images found.")


def main():
    parser = argparse.ArgumentParser(
        description='Automated Image Management and SEO Post Enhancement System'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload images from CSV file')
    upload_parser.add_argument('csv_file', help='Path to CSV file containing image URLs')
    upload_parser.add_argument('--ocr-engine', choices=['easyocr', 'tesseract'],
                               default='easyocr', help='OCR engine to use')

    # Process posts command
    process_parser = subparsers.add_parser('process', help='Process SEO posts and add images')
    process_parser.add_argument('input_dir', help='Directory containing SEO posts')
    process_parser.add_argument('--output-dir', help='Output directory (optional)')
    process_parser.add_argument('--num-images', type=int, default=5,
                               help='Number of images to insert per post')

    # Stats command
    subparsers.add_parser('stats', help='Show image database statistics')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for images')
    search_group = search_parser.add_mutually_exclusive_group()
    search_group.add_argument('--query', help='Search by text query')
    search_group.add_argument('--tag', help='Search by tag')
    search_group.add_argument('--category', help='Search by category')

    args = parser.parse_args()

    # Ensure directories exist
    Config.ensure_directories()

    try:
        if args.command == 'upload':
            upload_images_from_csv(args.csv_file, args.ocr_engine)

        elif args.command == 'process':
            process_seo_posts(args.input_dir, args.output_dir, args.num_images)

        elif args.command == 'stats':
            show_stats()

        elif args.command == 'search':
            search_images(args.query, args.tag, args.category)

        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
