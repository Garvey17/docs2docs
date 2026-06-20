from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class settings(BaseSettings):
    openai_api_key: str
    app_version: str = "1.0.0"
    max_pages: int = 30
    request_delay_seconds: float = 1.0
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "eu-west-2"
    s3_bucket_name: str

    class Config:
        env_file = ".env"

settings = settings()