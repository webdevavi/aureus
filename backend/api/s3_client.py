import boto3
from datetime import timedelta
from backend.api.config.settings import get_settings
from botocore.exceptions import ClientError


def get_s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        endpoint_url=settings.s3_endpoint,
    )


def presigned_put_object(
    bucket_name: str,
    object_name: str,
    expires: timedelta,
    content_type: str = "application/octet-stream",
):
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_name,
                "ContentType": content_type,
            },
            ExpiresIn=int(expires.total_seconds()),
        )
        return url
    except ClientError as e:
        raise RuntimeError(f"Failed to generate presigned PUT URL: {e}")


def presigned_get_object(
    bucket_name: str,
    object_name: str,
    expires: timedelta,
    response_headers: dict | None = None,
):
    s3 = get_s3_client()
    try:
        params = {"Bucket": bucket_name, "Key": object_name}
        if response_headers:
            params.update(response_headers)
        url = s3.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=int(expires.total_seconds()),
        )
        return url
    except ClientError as e:
        raise RuntimeError(f"Failed to generate presigned GET URL: {e}")
