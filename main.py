import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from pydantic import BaseModel
from urllib.parse import urlparse
from pipeline import run_pipeline
from fastapi import HTTPException
from typing import Optional
from services.s3_service import upload_and_get_url

#Setup logging 
logging.basicConfig(
    level="INFO"
)
logger = logging.getLogger(__name__)

class RequestModel(BaseModel):
    url:str
    package_name: Optional[str]

class ResponseModel(BaseModel):
    status: str
    package_name: str
    download_url: str 
IGNORED_SUBDOMAINS ={
    "docs", "www", "api", "dev"
}
def derive_package_name(url:str)->str:
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()

    parts = [
        part for part in hostname.split('.')
        if part and part not in IGNORED_SUBDOMAINS
    ]

    return parts[0] if parts else "documentation"
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting Docs to Docs.....')
    yield
    logger.info('Stopping Docs 2 Docs....')


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get('/health')
async def healthcheck():
    """Returns to check is the server is health"""

    return {
        "message": "Health check passes, app is healthy", 
        "app name": "Docs to Docs",
        "version": "1.0.0"
    }

pipeline_running = False

@app.post('/generate', response_model=ResponseModel)
async def generate(request: RequestModel):
    global pipeline_running
    if pipeline_running:
        raise HTTPException(
            status_code=429,
            detail="A pipeline run is already in progress. Please wait."
        )
    pipeline_running = True
    try:
        package_name = request.package_name or derive_package_name(request.url)
        presigned_url = await run_pipeline(url=request.url, package_name=package_name)
        return ResponseModel(
            status="200",
            package_name=package_name,
            download_url=presigned_url
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pipeline_running = False


if __name__ == "__main__":
     uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        loop="asyncio"
    )