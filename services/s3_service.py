import boto3
from pathlib import Path
from config.config import settings
from botocore.exceptions import BotoCoreError, ClientError

def upload_and_get_url(file_path: Path, package_name:str) -> str:

    client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )

    bucket_name = settings.s3_bucket_name

    s3_key = f"guides/{package_name}_guide.docx"

    try:
        client.upload_file(
            Filename=str(file_path),
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={
                "ContentType":(
                    "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.document"
                )
            }
        )

        presigned_url = client.generate_presigned_url(
             ClientMethod="get_object",
            Params={
                "Bucket": bucket_name,
                "Key": s3_key,
            },
            ExpiresIn=3600,
        )
        return presigned_url
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(
            f"Failed to upload '{file_path.name}' "
            f"to s3 bucket '{bucket_name}': {e}"
        ) from e
