import json
import os
import boto3
from typing import Any, Dict, List, Optional
from botocore.exceptions import ClientError

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class S3StorageService:
    """Service for interacting with AWS S3 as the primary data lake."""

    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET
        self.s3_client = None

        if settings.AWS_ACCESS_KEY and settings.AWS_SECRET_KEY:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY,
                    aws_secret_access_key=settings.AWS_SECRET_KEY,
                    region_name=settings.AWS_REGION
                )
                logger.info(f"Initialized S3 Storage Service for bucket: {self.bucket}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
        else:
            logger.warning("AWS Credentials not fully configured. Using local filesystem fallback.")
            # Use absolute path based on this file's location to avoid getcwd issues
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.local_dir = os.path.join(base_dir, "data", "s3_mock")
            os.makedirs(self.local_dir, exist_ok=True)

    def _is_configured(self) -> bool:
        return self.s3_client is not None

    def upload_json(self, object_key: str, data: Any) -> bool:
        """Uploads a dictionary or list to S3 as a JSON file."""
        json_str = json.dumps(data, default=str)
        if not self._is_configured():
            local_path = os.path.join(self.local_dir, object_key.replace('/', '_'))
            with open(local_path, 'w') as f:
                f.write(json_str)
            return True
            
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=json_str,
                ContentType="application/json"
            )
            logger.debug(f"Successfully uploaded JSON to s3://{self.bucket}/{object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload JSON to S3: {e}")
            return False

    def download_json(self, object_key: str) -> Optional[Any]:
        """Downloads a JSON file from S3 and parses it."""
        if not self._is_configured():
            local_path = os.path.join(self.local_dir, object_key.replace('/', '_'))
            if os.path.exists(local_path):
                with open(local_path, 'r') as f:
                    return json.loads(f.read())
            return None
            
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=object_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except self.s3_client.exceptions.NoSuchKey:
            logger.debug(f"S3 key does not exist: {object_key}")
            return None
        except ClientError as e:
            logger.error(f"Failed to download JSON from S3: {e}")
            return None

    def upload_file(self, object_key: str, file_path: str) -> bool:
        """Uploads a local file to S3."""
        if not self._is_configured():
            return False
            
        if not os.path.exists(file_path):
            logger.error(f"Local file does not exist: {file_path}")
            return False
            
        try:
            self.s3_client.upload_file(file_path, self.bucket, object_key)
            logger.debug(f"Successfully uploaded file to s3://{self.bucket}/{object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return False

    def download_file(self, object_key: str, file_path: str) -> bool:
        """Downloads a file from S3 to a local path."""
        if not self._is_configured():
            return False
            
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.s3_client.download_file(self.bucket, object_key, file_path)
            logger.debug(f"Successfully downloaded file from S3 to {file_path}")
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
        except ClientError as e:
            logger.error(f"Failed to download file from S3: {e}")
            return False

    def list_objects(self, prefix: str) -> List[str]:
        """Lists object keys in S3 under a specific prefix."""
        if not self._is_configured():
            return []
            
        keys = []
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        keys.append(obj['Key'])
            return keys
        except ClientError as e:
            logger.error(f"Failed to list objects in S3: {e}")
            return []
