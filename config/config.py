from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class settings(BaseSettings):
    openai_api_key: str
    app_version: str = "1.0.0"
    max_pages: int = 30
    request_delay_seconds: float = 1.0

    class Config:
        env_file = ".env"

settings = settings()