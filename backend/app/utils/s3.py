"""
AWS S3 utility functions for file upload and management
"""
import boto3
from botocore.exceptions import ClientError
from app.config import settings
import logging
import os
from typing import Optional
import uuid

logger = logging.getLogger(__name__)


class S3Client:
    """S3 client for file operations"""

    def __init__(self):
        """Initialize S3 client"""
        # Check if AWS credentials are provided
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.use_s3 = True
            logger.info("S3 client initialized with credentials")
        else:
            self.s3_client = None
            self.use_s3 = False
            logger.warning("AWS credentials not found. Using local storage fallback.")

        self.bucket_name = settings.s3_bucket_name
        self.local_storage_path = "uploads"  # Fallback for local development

        # Create local storage directory if using fallback
        if not self.use_s3:
            os.makedirs(self.local_storage_path, exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "videos"), exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "frames"), exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "reports"), exist_ok=True)

    def upload_file(
        self,
        file_path: str,
        object_name: Optional[str] = None,
        folder: str = "videos"
    ) -> str:
        """
        Upload a file to S3 or local storage

        Args:
            file_path: Path to file to upload
            object_name: S3 object name. If not specified, file_path is used
            folder: Folder/prefix in S3 (videos, frames, reports)

        Returns:
            URL of uploaded file
        """
        if object_name is None:
            object_name = os.path.basename(file_path)

        # Add folder prefix
        s3_key = f"{folder}/{object_name}"

        if self.use_s3:
            return self._upload_to_s3(file_path, s3_key)
        else:
            return self._upload_to_local(file_path, s3_key)

    def _upload_to_s3(self, file_path: str, s3_key: str) -> str:
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            logger.info(f"File uploaded to S3: {url}")
            return url
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            raise

    def _upload_to_local(self, file_path: str, s3_key: str) -> str:
        """Upload file to local storage (fallback)"""
        import shutil

        local_path = os.path.join(self.local_storage_path, s3_key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        shutil.copy2(file_path, local_path)
        url = f"/uploads/{s3_key}"
        logger.info(f"File saved locally: {url}")
        return url

    def upload_file_object(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "videos"
    ) -> str:
        """
        Upload file from memory (bytes)

        Args:
            file_content: File content as bytes
            filename: Desired filename
            folder: Folder/prefix

        Returns:
            URL of uploaded file
        """
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        s3_key = f"{folder}/{unique_filename}"

        if self.use_s3:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_content
                )
                url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
                logger.info(f"File uploaded to S3: {url}")
                return url
            except ClientError as e:
                logger.error(f"Error uploading to S3: {e}")
                raise
        else:
            local_path = os.path.join(self.local_storage_path, s3_key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, 'wb') as f:
                f.write(file_content)

            url = f"/uploads/{s3_key}"
            logger.info(f"File saved locally: {url}")
            return url

    def download_file(self, s3_url: str, local_path: str) -> str:
        """
        Download file from S3 or local storage

        Args:
            s3_url: URL or path of file
            local_path: Local path to save file

        Returns:
            Local file path
        """
        if self.use_s3 and s3_url.startswith("https://"):
            # Extract S3 key from URL
            s3_key = s3_url.split(f"{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/")[1]
            try:
                self.s3_client.download_file(self.bucket_name, s3_key, local_path)
                logger.info(f"File downloaded from S3 to {local_path}")
                return local_path
            except ClientError as e:
                logger.error(f"Error downloading from S3: {e}")
                raise
        else:
            # Local storage - copy file
            import shutil
            source_path = s3_url.replace("/uploads/", self.local_storage_path + "/")
            shutil.copy2(source_path, local_path)
            logger.info(f"File copied from local storage to {local_path}")
            return local_path

    def delete_file(self, s3_url: str) -> bool:
        """
        Delete file from S3 or local storage

        Args:
            s3_url: URL or path of file to delete

        Returns:
            True if successful
        """
        if self.use_s3 and s3_url.startswith("https://"):
            s3_key = s3_url.split(f"{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/")[1]
            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                logger.info(f"File deleted from S3: {s3_key}")
                return True
            except ClientError as e:
                logger.error(f"Error deleting from S3: {e}")
                return False
        else:
            # Local storage - delete file
            local_path = s3_url.replace("/uploads/", self.local_storage_path + "/")
            if os.path.exists(local_path):
                os.remove(local_path)
                logger.info(f"File deleted from local storage: {local_path}")
                return True
            return False

    def get_public_url(self, s3_key: str) -> str:
        """
        Get public URL for an S3 object

        Args:
            s3_key: S3 object key

        Returns:
            Public URL
        """
        if self.use_s3:
            return f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
        else:
            return f"/uploads/{s3_key}"


# Global S3 client instance
s3_client = S3Client()
