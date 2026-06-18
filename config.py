from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class settings(BaseSettings):
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    app_version: str = "1.0.0"

settings = settings()