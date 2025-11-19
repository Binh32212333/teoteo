import boto3
from botocore.exceptions import ClientError
import logging
import os
from pathlib import Path
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AWSUploader:
    """Upload images to AWS S3"""

    def __init__(self):
        self.s3_client = None
        self.bucket_name = Config.AWS_S3_BUCKET
        self._initialize_s3()

    def _initialize_s3(self):
        """Initialize S3 client with credentials"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_REGION
            )
            logger.info("AWS S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS S3 client: {e}")
            raise

    def upload_file(self, file_path, s3_key=None, metadata=None):
        """
        Upload a file to S3
        Args:
            file_path: Local path to the file
            s3_key: S3 key (path) for the file. If None, uses filename
            metadata: Optional metadata dict to attach to the file
        Returns:
            S3 URL if successful, None otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return None

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        # Use filename as S3 key if not provided
        if s3_key is None:
            s3_key = os.path.basename(file_path)

        # Ensure S3 key starts with 'images/'
        if not s3_key.startswith('images/'):
            s3_key = f'images/{s3_key}'

        try:
            extra_args = {}

            # Set content type based on file extension
            ext = Path(file_path).suffix.lower()
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            if ext in content_types:
                extra_args['ContentType'] = content_types[ext]

            # Add metadata if provided
            if metadata:
                extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}

            # Make uploaded images publicly readable
            extra_args['ACL'] = 'public-read'

            # Upload file
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            # Construct S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{Config.AWS_REGION}.amazonaws.com/{s3_key}"

            logger.info(f"Successfully uploaded {file_path} to {s3_url}")
            return s3_url

        except ClientError as e:
            logger.error(f"Failed to upload {file_path} to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading {file_path}: {e}")
            return None

    def upload_images(self, image_list):
        """
        Upload multiple images to S3
        Args:
            image_list: List of dicts with 'filepath' and other metadata
        Returns:
            List of dicts with added 's3_url' field
        """
        uploaded_images = []

        for image_info in image_list:
            filepath = image_info['filepath']
            url_hash = image_info.get('url_hash', 'unknown')
            extension = image_info.get('extension', 'jpg')

            # Create S3 key
            s3_key = f"{url_hash}.{extension}"

            # Prepare metadata
            metadata = {
                'original_url': image_info.get('url', ''),
                'ocr_text': image_info.get('ocr_text', '')[:2000],  # S3 metadata has size limits
                'filter_reason': image_info.get('filter_reason', 'passed')
            }

            # Upload to S3
            s3_url = self.upload_file(filepath, s3_key, metadata)

            if s3_url:
                image_info['s3_url'] = s3_url
                image_info['s3_key'] = s3_key
                uploaded_images.append(image_info)

        logger.info(f"Successfully uploaded {len(uploaded_images)}/{len(image_list)} images to S3")
        return uploaded_images

    def check_bucket_exists(self):
        """Check if the configured S3 bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False
