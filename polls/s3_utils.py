"""
Utility functions for AWS S3 file operations
"""

import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings
from typing import Optional, BinaryIO
import uuid

logger = logging.getLogger(__name__)


def get_s3_client():
    """
    Create and return an S3 client using credentials from settings
    """
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        return s3_client
    except NoCredentialsError:
        logger.error("AWS credentials not found")
        raise
    except Exception as e:
        logger.error(f"Error creating S3 client: {str(e)}")
        raise


def upload_file_to_s3(
    file_obj: BinaryIO, filename: str, content_type: Optional[str] = None
) -> dict:
    """
    Upload a file to S3 bucket

    Args:
        file_obj: File object to upload
        filename: Name to save the file as in S3
        content_type: MIME type of the file

    Returns:
        dict: Response containing success status, file_key, and url
    """
    if not settings.AWS_STORAGE_BUCKET_NAME:
        return {"success": False, "error": "S3 bucket name not configured"}

    try:
        s3_client = get_s3_client()

        # Generate unique filename to avoid collisions
        # file_extension = filename.split(".")[-1] if "." in filename else ""
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # Prepare upload parameters
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        # Upload file
        s3_client.upload_fileobj(
            file_obj,
            settings.AWS_STORAGE_BUCKET_NAME,
            unique_filename,
            ExtraArgs=extra_args if extra_args else None,
        )

        # Generate file URL
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{unique_filename}"

        logger.info(f"Successfully uploaded file: {unique_filename}")

        return {
            "success": True,
            "file_key": unique_filename,
            "url": file_url,
            "original_filename": filename,
        }

    except ClientError as e:
        error_msg = f"AWS ClientError: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error uploading file: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


def download_file_from_s3(file_key: str) -> dict:
    """
    Download a file from S3 bucket

    Args:
        file_key: The key (filename) of the file in S3

    Returns:
        dict: Response containing success status, file_content, and metadata
    """
    if not settings.AWS_STORAGE_BUCKET_NAME:
        return {"success": False, "error": "S3 bucket name not configured"}

    try:
        s3_client = get_s3_client()

        # Get file from S3
        response = s3_client.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key
        )

        file_content = response["Body"].read()
        content_type = response.get("ContentType", "application/octet-stream")

        logger.info(f"Successfully downloaded file: {file_key}")

        return {
            "success": True,
            "file_content": file_content,
            "content_type": content_type,
            "file_key": file_key,
        }

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "NoSuchKey":
            error_msg = f"File not found: {file_key}"
        else:
            error_msg = f"AWS ClientError: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error downloading file: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


def delete_file_from_s3(file_key: str) -> dict:
    """
    Delete a file from S3 bucket

    Args:
        file_key: The key (filename) of the file in S3

    Returns:
        dict: Response containing success status
    """
    if not settings.AWS_STORAGE_BUCKET_NAME:
        return {"success": False, "error": "S3 bucket name not configured"}

    try:
        s3_client = get_s3_client()

        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)

        logger.info(f"Successfully deleted file: {file_key}")

        return {"success": True, "file_key": file_key}

    except ClientError as e:
        error_msg = f"AWS ClientError: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error deleting file: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


def list_files_in_s3(prefix: str = "", max_keys: int = 100) -> dict:
    """
    List files in S3 bucket

    Args:
        prefix: Filter results to files starting with this prefix
        max_keys: Maximum number of files to return

    Returns:
        dict: Response containing success status and list of files
    """
    if not settings.AWS_STORAGE_BUCKET_NAME:
        return {"success": False, "error": "S3 bucket name not configured"}

    try:
        s3_client = get_s3_client()

        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=prefix, MaxKeys=max_keys
        )

        files = []
        if "Contents" in response:
            for obj in response["Contents"]:
                files.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat(),
                    }
                )

        logger.info(f"Successfully listed {len(files)} files")

        return {"success": True, "files": files, "count": len(files)}

    except ClientError as e:
        error_msg = f"AWS ClientError: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error listing files: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
