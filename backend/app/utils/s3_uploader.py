"""
S3 file upload utility for media files.
"""
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import uuid
import mimetypes


class S3Uploader:
    """Upload files to AWS S3"""

    def __init__(self):
        if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY]):
            self.client = None
            return

        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_BUCKET_NAME

    def upload_file(self, file_obj, folder: str = "uploads") -> str:
        """
        Upload file to S3 and return URL.

        Args:
            file_obj: File object to upload
            folder: S3 folder path

        Returns:
            str: Public URL of uploaded file
        """
        if not self.client:
            raise Exception("S3 client not configured")

        # Generate unique filename
        file_ext = file_obj.filename.split(".")[-1] if "." in file_obj.filename else ""
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        s3_key = f"{folder}/{unique_filename}"

        # Determine content type
        content_type, _ = mimetypes.guess_type(file_obj.filename)
        if not content_type:
            content_type = "application/octet-stream"

        try:
            # Upload file
            self.client.upload_fileobj(
                file_obj.file,
                self.bucket,
                s3_key,
                ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
            )

            # Generate public URL
            url = f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            return url

        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3.

        Args:
            s3_key: S3 object key

        Returns:
            bool: True if successful
        """
        if not self.client:
            return False

        try:
            self.client.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Failed to delete file: {str(e)}")
            return False

    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for private file access.

        Args:
            s3_key: S3 object key
            expiration: URL expiration in seconds

        Returns:
            str: Presigned URL
        """
        if not self.client:
            raise Exception("S3 client not configured")

        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")


# Global instance
s3_uploader = S3Uploader()
